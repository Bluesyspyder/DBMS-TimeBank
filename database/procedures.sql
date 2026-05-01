-- ============================================================
-- TimeBank: Stored Procedures and Functions
-- ============================================================

-- ============================================================
-- FUNCTION 1: Calculate Member Credit Balance
-- Returns the current credit balance for a given member
-- ============================================================
CREATE OR REPLACE FUNCTION fn_get_credit_balance(p_member_id INT)
RETURNS DECIMAL(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance DECIMAL(10,2);
BEGIN
    SELECT credit_balance INTO v_balance
    FROM Member
    WHERE member_id = p_member_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Member with ID % not found', p_member_id;
    END IF;

    RETURN v_balance;
END;
$$;

-- ============================================================
-- FUNCTION 2: Calculate Average Feedback Rating for a Member
-- Returns AVG rating for a member as a reviewee
-- ============================================================
CREATE OR REPLACE FUNCTION fn_avg_feedback_rating(p_member_id INT)
RETURNS DECIMAL(3,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_avg_rating DECIMAL(3,2);
BEGIN
    SELECT COALESCE(AVG(rating), 0.00) INTO v_avg_rating
    FROM Feedback
    WHERE reviewee_id = p_member_id;

    RETURN v_avg_rating;
END;
$$;

-- ============================================================
-- FUNCTION 3: Get Total Hours Served by a Member
-- ============================================================
CREATE OR REPLACE FUNCTION fn_total_hours_served(p_member_id INT)
RETURNS DECIMAL(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_hours DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(hours_spent), 0.00) INTO v_total_hours
    FROM Service_Transaction
    WHERE provider_id = p_member_id
      AND status = 'Completed';

    RETURN v_total_hours;
END;
$$;

-- ============================================================
-- PROCEDURE 1: Complete a Service Transaction
-- This procedure:
--   1. Validates provider has the required skill
--   2. Checks requester has sufficient credits
--   3. Creates the transaction record
--   4. Updates the service request status
--   (Credit updates happen via TRIGGER on transaction completion)
-- ============================================================
CREATE OR REPLACE PROCEDURE sp_complete_service_transaction(
    p_request_id    INT,
    p_provider_id   INT,
    p_hours_spent   DECIMAL(5,2),
    p_notes         TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_requester_id      INT;
    v_skill_id          INT;
    v_credits           DECIMAL(10,2);
    v_requester_balance DECIMAL(10,2);
    v_transaction_id    INT;
    v_has_skill         BOOLEAN;
BEGIN
    -- Step 1: Get request details
    SELECT requester_id, skill_id
    INTO v_requester_id, v_skill_id
    FROM Service_Request
    WHERE request_id = p_request_id
      AND status IN ('Open', 'Assigned', 'In Progress');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Service request % not found or not in valid status', p_request_id;
    END IF;

    -- Step 2: Ensure provider is not the requester
    IF p_provider_id = v_requester_id THEN
        RAISE EXCEPTION 'Provider cannot be the same as requester';
    END IF;

    -- Step 3: Verify provider has the required skill
    SELECT EXISTS(
        SELECT 1 FROM Member_Skill
        WHERE member_id = p_provider_id
          AND skill_id = v_skill_id
          AND is_active = TRUE
    ) INTO v_has_skill;

    IF NOT v_has_skill THEN
        RAISE EXCEPTION 'Provider % does not have the required skill', p_provider_id;
    END IF;

    -- Step 4: Calculate credits (1 hour = 1 credit)
    v_credits := p_hours_spent;

    -- Step 5: Check requester has enough credits
    SELECT credit_balance INTO v_requester_balance
    FROM Member
    WHERE member_id = v_requester_id;

    IF v_requester_balance < v_credits THEN
        RAISE EXCEPTION 'Requester has insufficient credits. Required: %, Available: %',
            v_credits, v_requester_balance;
    END IF;

    -- Step 6: Insert the transaction record (status = 'Completed')
    INSERT INTO Service_Transaction (
        request_id, provider_id, requester_id, skill_id,
        hours_spent, credits_exchanged, status, completed_at, notes
    ) VALUES (
        p_request_id, p_provider_id, v_requester_id, v_skill_id,
        p_hours_spent, v_credits, 'Completed', CURRENT_TIMESTAMP, p_notes
    )
    RETURNING transaction_id INTO v_transaction_id;

    -- Step 7: Update service request status to 'Completed'
    UPDATE Service_Request
    SET status = 'Completed',
        updated_at = CURRENT_TIMESTAMP
    WHERE request_id = p_request_id;

    -- NOTE: Credit transfers and ledger entries are handled by
    -- the trigger trg_after_transaction_complete (see triggers.sql)

    RAISE NOTICE 'Transaction % completed successfully. % credits transferred.',
        v_transaction_id, v_credits;
END;
$$;

-- ============================================================
-- PROCEDURE 2: Register a New Member
-- ============================================================
CREATE OR REPLACE PROCEDURE sp_register_member(
    p_first_name    VARCHAR(50),
    p_last_name     VARCHAR(50),
    p_email         VARCHAR(100),
    p_password_hash VARCHAR(255),
    p_phone         VARCHAR(20) DEFAULT NULL,
    p_dob           DATE DEFAULT NULL,
    p_address       TEXT DEFAULT NULL,
    p_city          VARCHAR(50) DEFAULT NULL,
    p_state         VARCHAR(50) DEFAULT NULL,
    p_zip           VARCHAR(10) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_member_id INT;
BEGIN
    -- Check if email already exists
    IF EXISTS (SELECT 1 FROM Member WHERE email = p_email) THEN
        RAISE EXCEPTION 'Email % is already registered', p_email;
    END IF;

    -- Insert new member with 5 starter credits
    INSERT INTO Member (
        first_name, last_name, email, password_hash, phone, date_of_birth,
        address, city, state, zip_code, credit_balance
    ) VALUES (
        p_first_name, p_last_name, p_email, p_password_hash, p_phone, p_dob,
        p_address, p_city, p_state, p_zip, 5.00
    )
    RETURNING member_id INTO v_member_id;

    -- Record the starter credit bonus in the ledger
    INSERT INTO Time_Credit_Ledger (
        member_id, credit_type, amount, balance_after, description
    ) VALUES (
        v_member_id, 'BONUS', 5.00, 5.00, 'Welcome bonus: 5 starter credits'
    );

    RAISE NOTICE 'Member % registered successfully with ID %', p_email, v_member_id;
END;
$$;

-- ============================================================
-- PROCEDURE 3: Create a Service Request
-- ============================================================
CREATE OR REPLACE PROCEDURE sp_create_service_request(
    p_requester_id  INT,
    p_skill_id      INT,
    p_title         VARCHAR(200),
    p_description   TEXT,
    p_est_hours     DECIMAL(5,2),
    p_urgency       VARCHAR(10) DEFAULT 'Normal'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance       DECIMAL(10,2);
    v_request_id    INT;
BEGIN
    -- Check if member exists and is verified
    SELECT credit_balance INTO v_balance
    FROM Member
    WHERE member_id = p_requester_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Member % not found', p_requester_id;
    END IF;

    -- Check sufficient credits
    IF v_balance < p_est_hours THEN
        RAISE EXCEPTION 'Insufficient credits. Required: %, Available: %',
            p_est_hours, v_balance;
    END IF;

    -- Check skill exists
    IF NOT EXISTS (SELECT 1 FROM Skill WHERE skill_id = p_skill_id) THEN
        RAISE EXCEPTION 'Skill % not found', p_skill_id;
    END IF;

    -- Create the request
    INSERT INTO Service_Request (
        requester_id, skill_id, title, description,
        estimated_hours, urgency
    ) VALUES (
        p_requester_id, p_skill_id, p_title, p_description,
        p_est_hours, p_urgency
    )
    RETURNING request_id INTO v_request_id;

    RAISE NOTICE 'Service request % created successfully', v_request_id;
END;
$$;

-- ============================================================
-- PROCEDURE 4: Update Service Request Status
-- ============================================================
CREATE OR REPLACE PROCEDURE sp_update_request_status(
    p_request_id    INT,
    p_new_status    VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validate the new status
    IF p_new_status NOT IN ('Open', 'Assigned', 'In Progress', 'Completed', 'Cancelled') THEN
        RAISE EXCEPTION 'Invalid status: %', p_new_status;
    END IF;

    UPDATE Service_Request
    SET status = p_new_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE request_id = p_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Service request % not found', p_request_id;
    END IF;

    RAISE NOTICE 'Request % status updated to %', p_request_id, p_new_status;
END;
$$;

-- ============================================================
-- PROCEDURE 5: Submit Feedback
-- ============================================================
CREATE OR REPLACE PROCEDURE sp_submit_feedback(
    p_transaction_id INT,
    p_reviewer_id    INT,
    p_rating         INT,
    p_comment        TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_provider_id   INT;
    v_requester_id  INT;
    v_reviewee_id   INT;
BEGIN
    -- Get transaction details
    SELECT provider_id, requester_id
    INTO v_provider_id, v_requester_id
    FROM Service_Transaction
    WHERE transaction_id = p_transaction_id
      AND status = 'Completed';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Completed transaction % not found', p_transaction_id;
    END IF;

    -- Determine reviewee (if reviewer is provider, reviewee is requester and vice versa)
    IF p_reviewer_id = v_provider_id THEN
        v_reviewee_id := v_requester_id;
    ELSIF p_reviewer_id = v_requester_id THEN
        v_reviewee_id := v_provider_id;
    ELSE
        RAISE EXCEPTION 'Reviewer % is not part of transaction %', p_reviewer_id, p_transaction_id;
    END IF;

    -- Validate rating
    IF p_rating < 1 OR p_rating > 5 THEN
        RAISE EXCEPTION 'Rating must be between 1 and 5';
    END IF;

    -- Insert feedback
    INSERT INTO Feedback (
        transaction_id, reviewer_id, reviewee_id, rating, comment
    ) VALUES (
        p_transaction_id, p_reviewer_id, v_reviewee_id, p_rating, p_comment
    );

    RAISE NOTICE 'Feedback submitted successfully for transaction %', p_transaction_id;
END;
$$;

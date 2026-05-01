-- ============================================================
-- TimeBank: Database Triggers
-- ============================================================

-- ============================================================
-- TRIGGER 1: After Transaction Completion
-- When a transaction status changes to 'Completed':
--   1. Add credits to the provider's balance
--   2. Deduct credits from the requester's balance
--   3. Insert CREDIT entry into ledger for provider
--   4. Insert DEBIT entry into ledger for requester
-- ============================================================

CREATE OR REPLACE FUNCTION fn_trg_after_transaction_complete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_provider_balance  DECIMAL(10,2);
    v_requester_balance DECIMAL(10,2);
BEGIN
    -- Only fire when status changes to 'Completed'
    IF NEW.status = 'Completed' AND (OLD.status IS NULL OR OLD.status <> 'Completed') THEN

        -- Update provider's credit balance (ADD credits)
        UPDATE Member
        SET credit_balance = credit_balance + NEW.credits_exchanged,
            updated_at = CURRENT_TIMESTAMP
        WHERE member_id = NEW.provider_id
        RETURNING credit_balance INTO v_provider_balance;

        -- Update requester's credit balance (DEDUCT credits)
        UPDATE Member
        SET credit_balance = credit_balance - NEW.credits_exchanged,
            updated_at = CURRENT_TIMESTAMP
        WHERE member_id = NEW.requester_id
        RETURNING credit_balance INTO v_requester_balance;

        -- Insert CREDIT entry for provider in ledger
        INSERT INTO Time_Credit_Ledger (
            member_id, transaction_id, credit_type, amount,
            balance_after, description
        ) VALUES (
            NEW.provider_id, NEW.transaction_id, 'CREDIT',
            NEW.credits_exchanged, v_provider_balance,
            'Earned ' || NEW.credits_exchanged || ' credits for providing service (Transaction #' || NEW.transaction_id || ')'
        );

        -- Insert DEBIT entry for requester in ledger
        INSERT INTO Time_Credit_Ledger (
            member_id, transaction_id, credit_type, amount,
            balance_after, description
        ) VALUES (
            NEW.requester_id, NEW.transaction_id, 'DEBIT',
            NEW.credits_exchanged, v_requester_balance,
            'Spent ' || NEW.credits_exchanged || ' credits for receiving service (Transaction #' || NEW.transaction_id || ')'
        );

        RAISE NOTICE 'Credits transferred: % credits from member % to member %',
            NEW.credits_exchanged, NEW.requester_id, NEW.provider_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_after_transaction_complete
    AFTER INSERT OR UPDATE ON Service_Transaction
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_after_transaction_complete();

-- ============================================================
-- TRIGGER 2: Validate Transaction Insert
-- Before inserting a transaction, validate:
--   1. Provider has the required skill
--   2. Requester has sufficient credits
--   3. Provider and requester are different members
-- ============================================================

CREATE OR REPLACE FUNCTION fn_trg_validate_transaction_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_requester_balance DECIMAL(10,2);
    v_has_skill         BOOLEAN;
BEGIN
    -- Check provider <> requester
    IF NEW.provider_id = NEW.requester_id THEN
        RAISE EXCEPTION 'Provider and requester cannot be the same member';
    END IF;

    -- Check provider has the skill
    SELECT EXISTS(
        SELECT 1 FROM Member_Skill
        WHERE member_id = NEW.provider_id
          AND skill_id = NEW.skill_id
          AND is_active = TRUE
    ) INTO v_has_skill;

    IF NOT v_has_skill THEN
        RAISE EXCEPTION 'Provider (ID: %) does not have the required skill (ID: %)',
            NEW.provider_id, NEW.skill_id;
    END IF;

    -- Check requester has enough credits (only for completed transactions)
    IF NEW.status = 'Completed' THEN
        SELECT credit_balance INTO v_requester_balance
        FROM Member
        WHERE member_id = NEW.requester_id;

        IF v_requester_balance < NEW.credits_exchanged THEN
            RAISE EXCEPTION 'Requester (ID: %) has insufficient credits. Required: %, Available: %',
                NEW.requester_id, NEW.credits_exchanged, v_requester_balance;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_transaction_insert
    BEFORE INSERT ON Service_Transaction
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_validate_transaction_insert();

-- ============================================================
-- TRIGGER 3: Auto-update Timestamps
-- Automatically updates `updated_at` for Member and
-- Service_Request tables on any UPDATE
-- ============================================================

CREATE OR REPLACE FUNCTION fn_trg_update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_member_update_timestamp
    BEFORE UPDATE ON Member
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_update_timestamp();

CREATE TRIGGER trg_request_update_timestamp
    BEFORE UPDATE ON Service_Request
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_update_timestamp();

-- ============================================================
-- TRIGGER 4: Prevent Negative Credit Balance
-- Before updating member credit_balance, ensure it won't go
-- below zero
-- ============================================================

CREATE OR REPLACE FUNCTION fn_trg_prevent_negative_balance()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.credit_balance < 0 THEN
        RAISE EXCEPTION 'Credit balance cannot be negative for member % (attempted: %)',
            NEW.member_id, NEW.credit_balance;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_negative_balance
    BEFORE UPDATE OF credit_balance ON Member
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_prevent_negative_balance();

-- ============================================================
-- TRIGGER 5: Auto-mark Request as 'Completed' When Transaction Completes
-- When a transaction is marked as 'Completed', automatically
-- update the associated service request status
-- ============================================================

CREATE OR REPLACE FUNCTION fn_trg_auto_complete_request()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'Completed' AND (OLD.status IS NULL OR OLD.status <> 'Completed') THEN
        UPDATE Service_Request
        SET status = 'Completed'
        WHERE request_id = NEW.request_id
          AND status <> 'Completed';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auto_complete_request
    AFTER INSERT OR UPDATE ON Service_Transaction
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_auto_complete_request();

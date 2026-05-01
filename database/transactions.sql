-- ============================================================
-- TimeBank: Transaction Control (COMMIT, ROLLBACK, SAVEPOINT)
-- Demonstrates ACID Properties
-- ============================================================

-- ============================================================
-- ACID Properties Demonstration
-- ============================================================
-- Atomicity:    Entire booking is all-or-nothing
-- Consistency:  Constraints ensure valid state after each transaction
-- Isolation:    Each transaction executes independently
-- Durability:   COMMIT ensures changes persist

-- ============================================================
-- EXAMPLE 1: Successful Service Booking Transaction
-- Demonstrates: COMMIT, SAVEPOINT
-- Scenario: Member 2 requests tutoring from Member 1
-- ============================================================

BEGIN;

    -- SAVEPOINT after verifying members exist
    SAVEPOINT sp_member_check;

    -- Verify both members exist
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM Member WHERE member_id = 1) THEN
            RAISE EXCEPTION 'Provider member not found';
        END IF;
        IF NOT EXISTS (SELECT 1 FROM Member WHERE member_id = 2) THEN
            RAISE EXCEPTION 'Requester member not found';
        END IF;
    END $$;

    -- SAVEPOINT before creating the service request
    SAVEPOINT sp_request_creation;

    -- Step 1: Create a service request
    INSERT INTO Service_Request (
        requester_id, skill_id, title, description,
        estimated_hours, urgency
    ) VALUES (
        2, 1, 'Need Math Tutoring Session',
        'Looking for help with calculus for 2 hours',
        2.00, 'Normal'
    );

    -- SAVEPOINT before creating the transaction
    SAVEPOINT sp_transaction_creation;

    -- Step 2: Create and complete the transaction
    -- (This triggers automatic credit transfer via trigger)
    INSERT INTO Service_Transaction (
        request_id, provider_id, requester_id, skill_id,
        hours_spent, credits_exchanged, status, completed_at, notes
    ) VALUES (
        (SELECT MAX(request_id) FROM Service_Request WHERE requester_id = 2),
        1, 2, 1,
        2.00, 2.00, 'Completed', CURRENT_TIMESTAMP,
        'Completed tutoring session successfully'
    );

    -- If everything succeeded, COMMIT the transaction
COMMIT;

-- ============================================================
-- EXAMPLE 2: Failed Transaction with ROLLBACK
-- Demonstrates: ROLLBACK
-- Scenario: Booking fails due to insufficient credits
-- ============================================================

BEGIN;

    -- SAVEPOINT at the start
    SAVEPOINT sp_booking_start;

    -- Attempt to create a large request
    INSERT INTO Service_Request (
        requester_id, skill_id, title, description,
        estimated_hours, urgency
    ) VALUES (
        3, 2, 'Need Extensive Web Development Help',
        'Full website redesign project',
        100.00, 'High'  -- This will fail because max is 40 hours
    );

    -- This should fail due to CHECK constraint (max 40 hours)
    -- ROLLBACK to undo everything

ROLLBACK;

-- ============================================================
-- EXAMPLE 3: Partial Rollback with SAVEPOINT
-- Demonstrates: SAVEPOINT, ROLLBACK TO SAVEPOINT, COMMIT
-- Scenario: Multiple operations where one fails but
--           earlier operations should be preserved
-- ============================================================

BEGIN;

    -- Phase 1: Register a new skill (should succeed)
    SAVEPOINT sp_add_skill;

    INSERT INTO Skill (skill_name, category, description)
    VALUES ('Data Analysis', 'Technology', 'Statistical data analysis and visualization')
    ON CONFLICT (skill_name) DO NOTHING;

    -- Phase 2: Create a member-skill mapping
    SAVEPOINT sp_add_member_skill;

    -- This tries to add a skill for an existing member
    INSERT INTO Member_Skill (member_id, skill_id, proficiency)
    VALUES (
        1,
        (SELECT skill_id FROM Skill WHERE skill_name = 'Data Analysis'),
        'Advanced'
    )
    ON CONFLICT (member_id, skill_id) DO NOTHING;

    -- Phase 3: Attempt an invalid operation
    SAVEPOINT sp_invalid_operation;

    -- Try to insert feedback for a non-existent transaction
    -- This will fail, so we rollback only this phase
    DO $$
    BEGIN
        BEGIN
            INSERT INTO Feedback (transaction_id, reviewer_id, reviewee_id, rating, comment)
            VALUES (99999, 1, 2, 5, 'Great work on data analysis!');
        EXCEPTION
            WHEN foreign_key_violation THEN
                RAISE NOTICE 'Feedback insertion failed: invalid transaction ID. Rolling back to savepoint.';
        END;
    END $$;

    -- Rollback only Phase 3 (the failed feedback insertion)
    ROLLBACK TO SAVEPOINT sp_invalid_operation;

    -- Phase 1 and Phase 2 are still intact
    -- Commit the successful operations
COMMIT;

-- ============================================================
-- EXAMPLE 4: Concurrent Transaction Safety
-- Demonstrates: Isolation level and conflict handling
-- ============================================================

-- Transaction A: Complete a service
BEGIN;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    SAVEPOINT sp_service_start;

    -- Lock the member rows to prevent concurrent modifications
    SELECT credit_balance FROM Member WHERE member_id = 1 FOR UPDATE;
    SELECT credit_balance FROM Member WHERE member_id = 2 FOR UPDATE;

    -- Create the transaction (if service request exists)
    DO $$
    DECLARE
        v_request_id INT;
    BEGIN
        SELECT request_id INTO v_request_id
        FROM Service_Request
        WHERE requester_id = 2
          AND status = 'Open'
        ORDER BY created_at DESC
        LIMIT 1;

        IF v_request_id IS NOT NULL THEN
            INSERT INTO Service_Transaction (
                request_id, provider_id, requester_id, skill_id,
                hours_spent, credits_exchanged, status, completed_at
            ) VALUES (
                v_request_id, 1, 2,
                (SELECT skill_id FROM Service_Request WHERE request_id = v_request_id),
                1.00, 1.00, 'Completed', CURRENT_TIMESTAMP
            );
            RAISE NOTICE 'Transaction completed under SERIALIZABLE isolation';
        ELSE
            RAISE NOTICE 'No open requests found, skipping';
        END IF;
    END $$;

COMMIT;

-- ============================================================
-- SUMMARY OF TRANSACTION CONCEPTS DEMONSTRATED
-- ============================================================
-- 1. BEGIN / COMMIT    : Start and persist a transaction
-- 2. ROLLBACK          : Undo entire transaction on failure
-- 3. SAVEPOINT         : Create restore points within a transaction
-- 4. ROLLBACK TO       : Partial rollback to a savepoint
-- 5. ISOLATION LEVEL   : SERIALIZABLE for concurrent safety
-- 6. FOR UPDATE        : Row-level locking for conflict prevention
-- 7. Exception Handling: PL/pgSQL EXCEPTION blocks for error recovery

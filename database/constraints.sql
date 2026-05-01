-- ============================================================
-- TimeBank: Additional Constraints (ALTER TABLE)
-- ============================================================
-- These constraints supplement the inline constraints in schema.sql
-- Demonstrates ALTER TABLE usage for adding constraints post-creation

-- ============================================================
-- 1. Member Table - Additional Constraints
-- ============================================================

-- Ensure email follows a basic pattern
ALTER TABLE Member
    ADD CONSTRAINT chk_member_email_format
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ensure phone number is at least 10 characters
ALTER TABLE Member
    ADD CONSTRAINT chk_member_phone_length
    CHECK (phone IS NULL OR LENGTH(phone) >= 10);

-- Date of birth must be in the past and member must be at least 16
ALTER TABLE Member
    ADD CONSTRAINT chk_member_dob
    CHECK (date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE - INTERVAL '16 years');

-- Credit balance cannot go negative
ALTER TABLE Member
    ADD CONSTRAINT chk_member_credit_positive
    CHECK (credit_balance >= 0);

-- ============================================================
-- 2. Skill Table - Additional Constraints
-- ============================================================

-- Category must be from a predefined list
ALTER TABLE Skill
    ADD CONSTRAINT chk_skill_category
    CHECK (category IN (
        'Technology', 'Education', 'Home & Garden', 'Health & Wellness',
        'Creative Arts', 'Business', 'Language', 'Sports & Fitness',
        'Cooking', 'Music', 'Transportation', 'Other'
    ));

-- Skill name must be at least 3 characters
ALTER TABLE Skill
    ADD CONSTRAINT chk_skill_name_length
    CHECK (LENGTH(skill_name) >= 3);

-- ============================================================
-- 3. Service_Request Table - Additional Constraints
-- ============================================================

-- Estimated hours should be reasonable (max 40 hours per request)
ALTER TABLE Service_Request
    ADD CONSTRAINT chk_sr_max_hours
    CHECK (estimated_hours <= 40.00);

-- Title must be at least 5 characters
ALTER TABLE Service_Request
    ADD CONSTRAINT chk_sr_title_length
    CHECK (LENGTH(title) >= 5);

-- ============================================================
-- 4. Service_Transaction Table - Additional Constraints
-- ============================================================

-- Hours spent should not exceed 40 for a single transaction
ALTER TABLE Service_Transaction
    ADD CONSTRAINT chk_st_max_hours
    CHECK (hours_spent <= 40.00);

-- Completed_at must be after started_at
ALTER TABLE Service_Transaction
    ADD CONSTRAINT chk_st_dates
    CHECK (completed_at IS NULL OR completed_at >= started_at);

-- ============================================================
-- 5. Feedback Table - Additional Constraints
-- ============================================================

-- Comment must be at least 10 characters if provided
ALTER TABLE Feedback
    ADD CONSTRAINT chk_fb_comment_length
    CHECK (comment IS NULL OR LENGTH(comment) >= 10);

-- ============================================================
-- 6. Time_Credit_Ledger - Additional Constraints
-- ============================================================

-- Description is mandatory for non-transaction entries
-- (transactions auto-generate descriptions via triggers)
ALTER TABLE Time_Credit_Ledger
    ADD CONSTRAINT chk_tcl_description
    CHECK (transaction_id IS NOT NULL OR description IS NOT NULL);

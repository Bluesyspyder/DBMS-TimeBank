-- ============================================================
-- TimeBank: Community Skill & Resource Exchange Database System
-- Schema Definition (DDL) - PostgreSQL
-- ============================================================

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS Feedback CASCADE;
DROP TABLE IF EXISTS Time_Credit_Ledger CASCADE;
DROP TABLE IF EXISTS Service_Transaction CASCADE;
DROP TABLE IF EXISTS Service_Request CASCADE;
DROP TABLE IF EXISTS Member_Skill CASCADE;
DROP TABLE IF EXISTS Skill CASCADE;
DROP TABLE IF EXISTS Member CASCADE;

-- ============================================================
-- 1. Member Table
-- Stores registered community members
-- ============================================================
CREATE TABLE Member (
    member_id       SERIAL PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    date_of_birth   DATE,
    address         TEXT,
    city            VARCHAR(50),
    state           VARCHAR(50),
    zip_code        VARCHAR(10),
    is_verified     BOOLEAN DEFAULT FALSE,
    credit_balance  DECIMAL(10,2) DEFAULT 5.00,  -- New members get 5 starter credits
    role            VARCHAR(10) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    password_hash   VARCHAR(255) NOT NULL,
    joined_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. Skill Table
-- Master list of skills/services available on the platform
-- ============================================================
CREATE TABLE Skill (
    skill_id        SERIAL PRIMARY KEY,
    skill_name      VARCHAR(100) NOT NULL UNIQUE,
    category        VARCHAR(50) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. Member_Skill Table (Bridge / Many-to-Many)
-- Maps members to skills they can offer
-- ============================================================
CREATE TABLE Member_Skill (
    member_skill_id SERIAL PRIMARY KEY,
    member_id       INT NOT NULL,
    skill_id        INT NOT NULL,
    proficiency     VARCHAR(20) DEFAULT 'Intermediate'
                    CHECK (proficiency IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')),
    hourly_rate     DECIMAL(5,2) DEFAULT 1.00 CHECK (hourly_rate > 0),
    is_active       BOOLEAN DEFAULT TRUE,
    added_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ms_member FOREIGN KEY (member_id) REFERENCES Member(member_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ms_skill FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
        ON DELETE CASCADE,
    CONSTRAINT uq_member_skill UNIQUE (member_id, skill_id)
);

-- ============================================================
-- 4. Service_Request Table
-- Service requests posted by members seeking help
-- ============================================================
CREATE TABLE Service_Request (
    request_id      SERIAL PRIMARY KEY,
    requester_id    INT NOT NULL,
    skill_id        INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    estimated_hours DECIMAL(5,2) NOT NULL CHECK (estimated_hours > 0),
    status          VARCHAR(20) DEFAULT 'Open'
                    CHECK (status IN ('Open', 'Assigned', 'In Progress', 'Completed', 'Cancelled')),
    urgency         VARCHAR(10) DEFAULT 'Normal'
                    CHECK (urgency IN ('Low', 'Normal', 'High', 'Urgent')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sr_requester FOREIGN KEY (requester_id) REFERENCES Member(member_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_sr_skill FOREIGN KEY (skill_id) REFERENCES Skill(skill_id)
        ON DELETE SET NULL
);

-- ============================================================
-- 5. Service_Transaction Table
-- Records completed service exchanges between members
-- ============================================================
CREATE TABLE Service_Transaction (
    transaction_id  SERIAL PRIMARY KEY,
    request_id      INT NOT NULL,
    provider_id     INT NOT NULL,
    requester_id    INT NOT NULL,
    skill_id        INT NOT NULL,
    hours_spent     DECIMAL(5,2) NOT NULL CHECK (hours_spent > 0),
    credits_exchanged DECIMAL(10,2) NOT NULL CHECK (credits_exchanged > 0),
    status          VARCHAR(20) DEFAULT 'Pending'
                    CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Disputed', 'Cancelled')),
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    notes           TEXT,

    CONSTRAINT fk_st_request FOREIGN KEY (request_id) REFERENCES Service_Request(request_id),
    CONSTRAINT fk_st_provider FOREIGN KEY (provider_id) REFERENCES Member(member_id),
    CONSTRAINT fk_st_requester FOREIGN KEY (requester_id) REFERENCES Member(member_id),
    CONSTRAINT fk_st_skill FOREIGN KEY (skill_id) REFERENCES Skill(skill_id),
    CONSTRAINT chk_different_members CHECK (provider_id <> requester_id)
);

-- ============================================================
-- 6. Time_Credit_Ledger Table
-- Immutable audit trail of all credit movements
-- ============================================================
CREATE TABLE Time_Credit_Ledger (
    ledger_id       SERIAL PRIMARY KEY,
    member_id       INT NOT NULL,
    transaction_id  INT,
    credit_type     VARCHAR(10) NOT NULL
                    CHECK (credit_type IN ('CREDIT', 'DEBIT', 'BONUS', 'PENALTY')),
    amount          DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    balance_after   DECIMAL(10,2) NOT NULL,
    description     VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tcl_member FOREIGN KEY (member_id) REFERENCES Member(member_id),
    CONSTRAINT fk_tcl_transaction FOREIGN KEY (transaction_id) REFERENCES Service_Transaction(transaction_id)
);

-- ============================================================
-- 7. Feedback Table
-- Ratings and reviews after service completion
-- ============================================================
CREATE TABLE Feedback (
    feedback_id     SERIAL PRIMARY KEY,
    transaction_id  INT NOT NULL,
    reviewer_id     INT NOT NULL,
    reviewee_id     INT NOT NULL,
    rating          INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fb_transaction FOREIGN KEY (transaction_id) REFERENCES Service_Transaction(transaction_id),
    CONSTRAINT fk_fb_reviewer FOREIGN KEY (reviewer_id) REFERENCES Member(member_id),
    CONSTRAINT fk_fb_reviewee FOREIGN KEY (reviewee_id) REFERENCES Member(member_id),
    CONSTRAINT uq_feedback UNIQUE (transaction_id, reviewer_id),
    CONSTRAINT chk_fb_different CHECK (reviewer_id <> reviewee_id)
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX idx_member_email ON Member(email);
CREATE INDEX idx_member_skill_member ON Member_Skill(member_id);
CREATE INDEX idx_member_skill_skill ON Member_Skill(skill_id);
CREATE INDEX idx_service_request_requester ON Service_Request(requester_id);
CREATE INDEX idx_service_request_skill ON Service_Request(skill_id);
CREATE INDEX idx_service_request_status ON Service_Request(status);
CREATE INDEX idx_transaction_provider ON Service_Transaction(provider_id);
CREATE INDEX idx_transaction_requester ON Service_Transaction(requester_id);
CREATE INDEX idx_transaction_status ON Service_Transaction(status);
CREATE INDEX idx_ledger_member ON Time_Credit_Ledger(member_id);
CREATE INDEX idx_feedback_reviewee ON Feedback(reviewee_id);

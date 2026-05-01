-- ============================================================
-- TimeBank: Analytical Queries
-- Demonstrates: JOINs, Subqueries, Aggregations,
--               GROUP BY, HAVING, Views
-- ============================================================

-- ============================================================
-- VIEW 1: Member Credit View
-- Shows each member's current credit balance with stats
-- ============================================================
CREATE OR REPLACE VIEW Member_Credit_View AS
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS full_name,
    m.email,
    m.credit_balance,
    m.is_verified,
    COALESCE(
        (SELECT SUM(amount) FROM Time_Credit_Ledger
         WHERE member_id = m.member_id AND credit_type = 'CREDIT'), 0
    ) AS total_credits_earned,
    COALESCE(
        (SELECT SUM(amount) FROM Time_Credit_Ledger
         WHERE member_id = m.member_id AND credit_type = 'DEBIT'), 0
    ) AS total_credits_spent,
    COALESCE(
        (SELECT COUNT(*) FROM Service_Transaction
         WHERE provider_id = m.member_id AND status = 'Completed'), 0
    ) AS services_provided,
    COALESCE(
        (SELECT COUNT(*) FROM Service_Transaction
         WHERE requester_id = m.member_id AND status = 'Completed'), 0
    ) AS services_received,
    COALESCE(fn_avg_feedback_rating(m.member_id), 0) AS avg_rating
FROM Member m
ORDER BY m.credit_balance DESC;

-- ============================================================
-- VIEW 2: Transaction Summary View
-- Detailed view of all transactions with member and skill info
-- ============================================================
CREATE OR REPLACE VIEW Transaction_Summary_View AS
SELECT
    st.transaction_id,
    st.started_at,
    st.completed_at,
    st.status AS transaction_status,
    st.hours_spent,
    st.credits_exchanged,
    -- Provider details (JOIN)
    p.member_id AS provider_id,
    p.first_name || ' ' || p.last_name AS provider_name,
    p.email AS provider_email,
    -- Requester details (JOIN)
    r.member_id AS requester_id,
    r.first_name || ' ' || r.last_name AS requester_name,
    r.email AS requester_email,
    -- Skill details (JOIN)
    s.skill_name,
    s.category AS skill_category,
    -- Request details (JOIN)
    sr.title AS request_title,
    sr.urgency,
    st.notes
FROM Service_Transaction st
    INNER JOIN Member p ON st.provider_id = p.member_id
    INNER JOIN Member r ON st.requester_id = r.member_id
    INNER JOIN Skill s ON st.skill_id = s.skill_id
    INNER JOIN Service_Request sr ON st.request_id = sr.request_id
ORDER BY st.started_at DESC;

-- ============================================================
-- QUERY 1: JOIN - All Transactions with Full Details
-- Uses INNER JOIN across 4 tables
-- ============================================================
SELECT
    st.transaction_id,
    p.first_name || ' ' || p.last_name AS provider,
    r.first_name || ' ' || r.last_name AS requester,
    s.skill_name,
    st.hours_spent,
    st.credits_exchanged,
    st.status,
    st.completed_at
FROM Service_Transaction st
    INNER JOIN Member p ON st.provider_id = p.member_id
    INNER JOIN Member r ON st.requester_id = r.member_id
    INNER JOIN Skill s ON st.skill_id = s.skill_id
ORDER BY st.completed_at DESC;

-- ============================================================
-- QUERY 2: LEFT JOIN - All Members with Their Skills
-- Shows members even if they haven't listed any skills
-- ============================================================
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    COALESCE(s.skill_name, 'No skills listed') AS skill_name,
    COALESCE(ms.proficiency, '-') AS proficiency,
    m.credit_balance
FROM Member m
    LEFT JOIN Member_Skill ms ON m.member_id = ms.member_id
    LEFT JOIN Skill s ON ms.skill_id = s.skill_id
ORDER BY m.member_id, s.skill_name;

-- ============================================================
-- QUERY 3: SUBQUERY - Top Credit Holders
-- Members with above-average credit balance
-- ============================================================
SELECT
    member_id,
    first_name || ' ' || last_name AS member_name,
    credit_balance
FROM Member
WHERE credit_balance > (
    SELECT AVG(credit_balance) FROM Member
)
ORDER BY credit_balance DESC;

-- ============================================================
-- QUERY 4: SUBQUERY - Most Requested Skills
-- Skills that appear in more than 2 service requests
-- ============================================================
SELECT
    s.skill_id,
    s.skill_name,
    s.category,
    (SELECT COUNT(*) FROM Service_Request sr WHERE sr.skill_id = s.skill_id) AS request_count
FROM Skill s
WHERE s.skill_id IN (
    SELECT skill_id
    FROM Service_Request
    GROUP BY skill_id
    HAVING COUNT(*) >= 2
)
ORDER BY request_count DESC;

-- ============================================================
-- QUERY 5: AGGREGATE - Total Credits Exchanged per Skill
-- Uses SUM, COUNT, GROUP BY
-- ============================================================
SELECT
    s.skill_name,
    s.category,
    COUNT(st.transaction_id) AS total_transactions,
    SUM(st.hours_spent) AS total_hours,
    SUM(st.credits_exchanged) AS total_credits,
    ROUND(AVG(st.hours_spent), 2) AS avg_hours_per_transaction
FROM Skill s
    INNER JOIN Service_Transaction st ON s.skill_id = st.skill_id
WHERE st.status = 'Completed'
GROUP BY s.skill_id, s.skill_name, s.category
ORDER BY total_credits DESC;

-- ============================================================
-- QUERY 6: GROUP BY + HAVING - Active Members
-- Members who have completed more than 1 transaction (as provider)
-- ============================================================
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    COUNT(st.transaction_id) AS completed_services,
    SUM(st.hours_spent) AS total_hours_served,
    SUM(st.credits_exchanged) AS total_credits_earned
FROM Member m
    INNER JOIN Service_Transaction st ON m.member_id = st.provider_id
WHERE st.status = 'Completed'
GROUP BY m.member_id, m.first_name, m.last_name
HAVING COUNT(st.transaction_id) > 1
ORDER BY total_credits_earned DESC;

-- ============================================================
-- QUERY 7: Monthly Transaction Summary
-- Aggregate transactions by month
-- ============================================================
SELECT
    DATE_TRUNC('month', st.completed_at) AS month,
    COUNT(st.transaction_id) AS transactions_count,
    SUM(st.hours_spent) AS total_hours,
    SUM(st.credits_exchanged) AS total_credits,
    COUNT(DISTINCT st.provider_id) AS unique_providers,
    COUNT(DISTINCT st.requester_id) AS unique_requesters
FROM Service_Transaction st
WHERE st.status = 'Completed'
  AND st.completed_at IS NOT NULL
GROUP BY DATE_TRUNC('month', st.completed_at)
ORDER BY month DESC;

-- ============================================================
-- QUERY 8: Top Rated Members (with minimum 2 reviews)
-- Uses HAVING to filter
-- ============================================================
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    COUNT(f.feedback_id) AS review_count,
    ROUND(AVG(f.rating), 2) AS avg_rating,
    MIN(f.rating) AS min_rating,
    MAX(f.rating) AS max_rating
FROM Member m
    INNER JOIN Feedback f ON m.member_id = f.reviewee_id
GROUP BY m.member_id, m.first_name, m.last_name
HAVING COUNT(f.feedback_id) >= 2
ORDER BY avg_rating DESC, review_count DESC;

-- ============================================================
-- QUERY 9: Skill Popularity by Category
-- Uses GROUP BY with category aggregation
-- ============================================================
SELECT
    s.category,
    COUNT(DISTINCT s.skill_id) AS skills_available,
    COUNT(DISTINCT ms.member_id) AS members_offering,
    COUNT(DISTINCT sr.request_id) AS total_requests,
    COALESCE(SUM(
        CASE WHEN sr.status = 'Completed' THEN 1 ELSE 0 END
    ), 0) AS completed_requests
FROM Skill s
    LEFT JOIN Member_Skill ms ON s.skill_id = ms.skill_id
    LEFT JOIN Service_Request sr ON s.skill_id = sr.skill_id
GROUP BY s.category
ORDER BY total_requests DESC;

-- ============================================================
-- QUERY 10: Member Activity Report
-- Comprehensive member activity using multiple subqueries
-- ============================================================
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    m.credit_balance,
    m.joined_date,
    -- Subquery: Services provided
    (SELECT COUNT(*) FROM Service_Transaction
     WHERE provider_id = m.member_id AND status = 'Completed') AS services_provided,
    -- Subquery: Services received
    (SELECT COUNT(*) FROM Service_Transaction
     WHERE requester_id = m.member_id AND status = 'Completed') AS services_received,
    -- Subquery: Open requests
    (SELECT COUNT(*) FROM Service_Request
     WHERE requester_id = m.member_id AND status = 'Open') AS open_requests,
    -- Subquery: Average rating
    (SELECT ROUND(COALESCE(AVG(rating), 0), 2) FROM Feedback
     WHERE reviewee_id = m.member_id) AS avg_rating,
    -- Subquery: Skills count
    (SELECT COUNT(*) FROM Member_Skill
     WHERE member_id = m.member_id AND is_active = TRUE) AS skills_count
FROM Member m
ORDER BY m.credit_balance DESC;

-- ============================================================
-- QUERY 11: Credit Ledger History for a Specific Member
-- Shows full credit history with running balance
-- ============================================================
SELECT
    tcl.ledger_id,
    tcl.credit_type,
    tcl.amount,
    tcl.balance_after,
    tcl.description,
    tcl.created_at,
    COALESCE(
        p.first_name || ' ' || p.last_name,
        'System'
    ) AS related_party
FROM Time_Credit_Ledger tcl
    LEFT JOIN Service_Transaction st ON tcl.transaction_id = st.transaction_id
    LEFT JOIN Member p ON (
        CASE
            WHEN tcl.credit_type = 'CREDIT' THEN st.requester_id
            WHEN tcl.credit_type = 'DEBIT' THEN st.provider_id
        END
    ) = p.member_id
WHERE tcl.member_id = 1  -- Change member_id as needed
ORDER BY tcl.created_at DESC;

-- ============================================================
-- QUERY 12: Unmatched Service Requests
-- Requests where no member with the required skill is available
-- ============================================================
SELECT
    sr.request_id,
    sr.title,
    s.skill_name,
    m.first_name || ' ' || m.last_name AS requester_name,
    sr.estimated_hours,
    sr.urgency,
    sr.created_at
FROM Service_Request sr
    INNER JOIN Skill s ON sr.skill_id = s.skill_id
    INNER JOIN Member m ON sr.requester_id = m.member_id
WHERE sr.status = 'Open'
  AND sr.skill_id NOT IN (
      SELECT ms.skill_id
      FROM Member_Skill ms
      WHERE ms.member_id <> sr.requester_id
        AND ms.is_active = TRUE
  )
ORDER BY sr.created_at ASC;

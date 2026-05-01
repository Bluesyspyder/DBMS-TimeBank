"""
TimeBank - SQL Query Execution Layer
Raw SQL functions that execute queries against the database.
All SQL logic is kept in the database; this module only executes and returns results.
"""

from app.db import execute_query, execute_function


# ============================================================
# MEMBER QUERIES
# ============================================================

def get_all_members():
    """Fetch all registered members."""
    return execute_query("""
        SELECT member_id, first_name, last_name, email, phone,
               city, state, is_verified, credit_balance, role, joined_date
        FROM Member
        ORDER BY member_id
    """)


def get_member_by_id(member_id):
    """Fetch a single member by ID."""
    result = execute_query("""
        SELECT * FROM Member WHERE member_id = %s
    """, (member_id,))
    return result[0] if result else None


def get_member_by_email(email):
    """Fetch a single member by email."""
    result = execute_query("""
        SELECT * FROM Member WHERE email = %s
    """, (email,))
    return result[0] if result else None


def search_members(search_term):
    """Search members by name or email."""
    return execute_query("""
        SELECT member_id, first_name, last_name, email, credit_balance
        FROM Member
        WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s
        ORDER BY first_name
    """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))


# ============================================================
# SKILL QUERIES
# ============================================================

def get_all_skills():
    """Fetch all available skills."""
    return execute_query("""
        SELECT skill_id, skill_name, category, description
        FROM Skill
        ORDER BY category, skill_name
    """)


def get_skills_by_category(category):
    """Fetch skills filtered by category."""
    return execute_query("""
        SELECT skill_id, skill_name, category, description
        FROM Skill
        WHERE category = %s
        ORDER BY skill_name
    """, (category,))


def get_skill_categories():
    """Fetch all unique skill categories."""
    return execute_query("""
        SELECT DISTINCT category FROM Skill ORDER BY category
    """)


def get_member_skills(member_id):
    """Fetch skills offered by a specific member."""
    return execute_query("""
        SELECT ms.member_skill_id, s.skill_name, s.category,
               ms.proficiency, ms.is_active
        FROM Member_Skill ms
        INNER JOIN Skill s ON ms.skill_id = s.skill_id
        WHERE ms.member_id = %s
        ORDER BY s.skill_name
    """, (member_id,))


# ============================================================
# SERVICE REQUEST QUERIES
# ============================================================

def get_all_requests(status_filter=None):
    """Fetch all service requests with member and skill details."""
    if status_filter:
        return execute_query("""
            SELECT sr.request_id, sr.title, sr.description,
                   sr.estimated_hours, sr.status, sr.urgency, sr.created_at,
                   m.first_name || ' ' || m.last_name AS requester_name,
                   s.skill_name, s.category
            FROM Service_Request sr
            INNER JOIN Member m ON sr.requester_id = m.member_id
            INNER JOIN Skill s ON sr.skill_id = s.skill_id
            WHERE sr.status = %s
            ORDER BY sr.created_at DESC
        """, (status_filter,))
    else:
        return execute_query("""
            SELECT sr.request_id, sr.title, sr.description,
                   sr.estimated_hours, sr.status, sr.urgency, sr.created_at,
                   m.first_name || ' ' || m.last_name AS requester_name,
                   s.skill_name, s.category
            FROM Service_Request sr
            INNER JOIN Member m ON sr.requester_id = m.member_id
            INNER JOIN Skill s ON sr.skill_id = s.skill_id
            ORDER BY sr.created_at DESC
        """)


def get_open_requests():
    """Fetch only open service requests."""
    return get_all_requests(status_filter='Open')


# ============================================================
# TRANSACTION QUERIES
# ============================================================

def get_all_transactions():
    """Fetch all transactions using the Transaction_Summary_View."""
    return execute_query("""
        SELECT * FROM Transaction_Summary_View
    """)


def get_transactions_by_member(member_id):
    """Fetch transactions involving a specific member."""
    return execute_query("""
        SELECT * FROM Transaction_Summary_View
        WHERE provider_id = %s OR requester_id = %s
        ORDER BY started_at DESC
    """, (member_id, member_id))


# ============================================================
# CREDIT & LEDGER QUERIES
# ============================================================

def get_member_credit_view():
    """Fetch the Member Credit View."""
    return execute_query("""
        SELECT * FROM Member_Credit_View
    """)


def get_credit_ledger(member_id):
    """Fetch credit history for a specific member."""
    return execute_query("""
        SELECT ledger_id, credit_type, amount, balance_after,
               description, created_at
        FROM Time_Credit_Ledger
        WHERE member_id = %s
        ORDER BY created_at DESC
    """, (member_id,))


def get_credit_balance(member_id):
    """Get the credit balance for a member using the stored function."""
    return execute_function("fn_get_credit_balance", (member_id,))


# ============================================================
# FEEDBACK QUERIES
# ============================================================

def get_feedback_for_member(member_id):
    """Fetch all feedback received by a member."""
    return execute_query("""
        SELECT f.feedback_id, f.rating, f.comment, f.created_at,
               m.first_name || ' ' || m.last_name AS reviewer_name,
               st.transaction_id
        FROM Feedback f
        INNER JOIN Member m ON f.reviewer_id = m.member_id
        INNER JOIN Service_Transaction st ON f.transaction_id = st.transaction_id
        WHERE f.reviewee_id = %s
        ORDER BY f.created_at DESC
    """, (member_id,))


def get_avg_rating(member_id):
    """Get the average feedback rating using the stored function."""
    return execute_function("fn_avg_feedback_rating", (member_id,))


# ============================================================
# ANALYTICS QUERIES
# ============================================================

def get_top_credit_holders(limit=10):
    """Fetch top members by credit balance (uses subquery)."""
    return execute_query("""
        SELECT member_id, first_name || ' ' || last_name AS member_name,
               credit_balance
        FROM Member
        WHERE credit_balance > (SELECT AVG(credit_balance) FROM Member)
        ORDER BY credit_balance DESC
        LIMIT %s
    """, (limit,))


def get_popular_skills():
    """Fetch most requested skills (uses GROUP BY + HAVING)."""
    return execute_query("""
        SELECT s.skill_name, s.category,
               COUNT(sr.request_id) AS request_count,
               COALESCE(SUM(CASE WHEN sr.status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed
        FROM Skill s
        LEFT JOIN Service_Request sr ON s.skill_id = sr.skill_id
        GROUP BY s.skill_id, s.skill_name, s.category
        HAVING COUNT(sr.request_id) >= 1
        ORDER BY request_count DESC
    """)


def get_revenue_per_skill():
    """Fetch total credits exchanged per skill (aggregation)."""
    return execute_query("""
        SELECT s.skill_name, s.category,
               COUNT(st.transaction_id) AS total_transactions,
               SUM(st.hours_spent) AS total_hours,
               SUM(st.credits_exchanged) AS total_credits
        FROM Skill s
        INNER JOIN Service_Transaction st ON s.skill_id = st.skill_id
        WHERE st.status = 'Completed'
        GROUP BY s.skill_id, s.skill_name, s.category
        ORDER BY total_credits DESC
    """)


def get_monthly_stats():
    """Fetch monthly transaction statistics."""
    return execute_query("""
        SELECT DATE_TRUNC('month', completed_at) AS month,
               COUNT(*) AS transactions,
               SUM(hours_spent) AS total_hours,
               SUM(credits_exchanged) AS total_credits
        FROM Service_Transaction
        WHERE status = 'Completed' AND completed_at IS NOT NULL
        GROUP BY DATE_TRUNC('month', completed_at)
        ORDER BY month DESC
    """)


def get_top_rated_members(min_reviews=1):
    """Fetch top-rated members with minimum review count."""
    return execute_query("""
        SELECT m.member_id,
               m.first_name || ' ' || m.last_name AS member_name,
               COUNT(f.feedback_id) AS review_count,
               ROUND(AVG(f.rating), 2) AS avg_rating
        FROM Member m
        INNER JOIN Feedback f ON m.member_id = f.reviewee_id
        GROUP BY m.member_id, m.first_name, m.last_name
        HAVING COUNT(f.feedback_id) >= %s
        ORDER BY avg_rating DESC, review_count DESC
    """, (min_reviews,))


def get_skill_category_stats():
    """Fetch statistics grouped by skill category."""
    return execute_query("""
        SELECT s.category,
               COUNT(DISTINCT s.skill_id) AS skills_count,
               COUNT(DISTINCT ms.member_id) AS providers_count,
               COUNT(DISTINCT sr.request_id) AS requests_count
        FROM Skill s
        LEFT JOIN Member_Skill ms ON s.skill_id = ms.skill_id
        LEFT JOIN Service_Request sr ON s.skill_id = sr.skill_id
        GROUP BY s.category
        ORDER BY requests_count DESC
    """)


def get_database_stats():
    """Fetch general database statistics (table counts)."""
    return execute_query("""
        SELECT relname as table_name, n_live_tup as row_count
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY row_count DESC;
    """)

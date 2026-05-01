"""
TimeBank - Business Logic / Service Layer
Calls stored procedures and handles transaction flows.
All core logic resides in SQL procedures and triggers;
this module only invokes them.
"""

from app.db import execute_procedure, execute_query, execute_function
import hashlib


# ============================================================
# MEMBER SERVICES
# ============================================================

def register_member(first_name, last_name, email, password, phone=None,
                    dob=None, address=None, city=None, state=None, zip_code=None):
    """
    Register a new member using the stored procedure.
    The procedure handles:
      - Duplicate email check
      - 5 starter credits assignment
      - Welcome bonus ledger entry
    """
    hashed_pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()
    execute_procedure("sp_register_member", (
        first_name, last_name, email, hashed_pwd, phone, dob,
        address, city, state, zip_code
    ))
    return {"status": "success", "message": f"Member {email} registered successfully"}


def add_member_skill(member_id, skill_id, proficiency="Intermediate"):
    """Add a skill to a member's profile."""
    execute_query("""
        INSERT INTO Member_Skill (member_id, skill_id, proficiency)
        VALUES (%s, %s, %s)
        ON CONFLICT (member_id, skill_id) DO UPDATE
        SET proficiency = EXCLUDED.proficiency, is_active = TRUE
    """, (member_id, skill_id, proficiency), fetch=False)
    return {"status": "success", "message": "Skill added successfully"}


# ============================================================
# SERVICE REQUEST SERVICES
# ============================================================

def create_service_request(requester_id, skill_id, title, description,
                           estimated_hours, urgency="Normal"):
    """
    Create a new service request using the stored procedure.
    The procedure handles:
      - Member existence check
      - Credit sufficiency validation
      - Skill existence validation
    """
    execute_procedure("sp_create_service_request", (
        requester_id, skill_id, title, description,
        estimated_hours, urgency
    ))
    return {"status": "success", "message": "Service request created successfully"}


def update_request_status(request_id, new_status):
    """
    Update a service request status using the stored procedure.
    Valid statuses: Open, Assigned, In Progress, Completed, Cancelled
    """
    execute_procedure("sp_update_request_status", (request_id, new_status))
    return {"status": "success", "message": f"Request status updated to {new_status}"}


# ============================================================
# TRANSACTION SERVICES
# ============================================================

def complete_service_transaction(request_id, provider_id, hours_spent, notes=None):
    """
    Complete a service transaction using the stored procedure.
    The procedure handles:
      - Skill verification for provider
      - Credit sufficiency check for requester
      - Transaction record creation
      - Request status update
    The trigger handles:
      - Credit transfer (provider +, requester -)
      - Ledger entries for both parties
    """
    execute_procedure("sp_complete_service_transaction", (
        request_id, provider_id, hours_spent, notes
    ))
    return {"status": "success", "message": "Transaction completed successfully"}


# ============================================================
# FEEDBACK SERVICES
# ============================================================

def submit_feedback(transaction_id, reviewer_id, rating, comment=None):
    """
    Submit feedback for a completed transaction using the stored procedure.
    The procedure handles:
      - Transaction completion validation
      - Reviewer participation validation
      - Reviewee determination (auto)
      - Rating range validation (1-5)
    """
    execute_procedure("sp_submit_feedback", (
        transaction_id, reviewer_id, rating, comment
    ))
    return {"status": "success", "message": "Feedback submitted successfully"}


# ============================================================
# CREDIT SERVICES
# ============================================================

def get_member_balance(member_id):
    """Get current credit balance using the stored function."""
    balance = execute_function("fn_get_credit_balance", (member_id,))
    return {"member_id": member_id, "credit_balance": float(balance)}


def get_member_rating(member_id):
    """Get average feedback rating using the stored function."""
    rating = execute_function("fn_avg_feedback_rating", (member_id,))
    return {"member_id": member_id, "avg_rating": float(rating)}


def get_member_hours(member_id):
    """Get total hours served using the stored function."""
    hours = execute_function("fn_total_hours_served", (member_id,))
    return {"member_id": member_id, "total_hours_served": float(hours)}

"""
TimeBank - Streamlit Frontend Application
Minimal UI with forms and tables for interacting with the database.
"""

import streamlit as st
import pandas as pd
from datetime import date
import sys
import os
import hashlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import queries, services

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="TimeBank - Community Skill Exchange",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS (Better Stack Theme)
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Global App Background - Dark Deep Radial Gradient */
    .stApp {
        background: radial-gradient(circle at top, #1e1e2d 0%, #0d0d14 100%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default header/sidebar chrome */
    .stApp > header,
    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Add top padding to main content so it doesn't hide behind the fixed navbar */
    .stApp .block-container {
        padding-top: 6rem !important;
    }

    /* ── FIXED TOP NAVBAR ──────────────────────────────────────────── */
    [data-testid="stRadio"] {
        position: fixed !important;
        top: 0.6rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 9999 !important;
        background: rgba(20, 20, 35, 0.82) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        padding: 0.3rem 1.5rem !important;  /* reduced vertical padding */
        border-radius: 50px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
        margin: 0 !important;
        width: auto !important;
        white-space: nowrap !important;  /* prevent wrapping */
    }
    /* Force the inner radio group to stay on one row */
    [data-testid="stRadio"] > div,
    [data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0 !important;
    }
    
    /* Hide the default radio circle robustly */
    [role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    
    /* Style the label container */
    [role="radiogroup"] label {
        padding: 0.3rem 0.8rem !important;  /* tighter vertical padding */
        margin-bottom: 0 !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        cursor: pointer !important;
        box-shadow: none !important;
        white-space: nowrap !important;
    }
    
    /* Base text styling for navbar items */
    [role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        transition: all 0.3s ease !important;
        font-size: 0.92rem;  /* slightly smaller to fit all items */
    }
    
    /* Hover effect: White Text Glow and slight shift */
    [role="radiogroup"] label:hover {
        background: transparent !important;
        transform: translateY(-2px) !important;
    }
    [role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Active/Selected state: Intense White Text Glow */
    [role="radiogroup"] label:has(input:checked) {
        background: transparent !important;
    }
    [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.9), 0 0 5px rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    /* Hero section styling */
    .hero-container {
        text-align: center;
        margin-top: 4rem;
        margin-bottom: 4rem;
    }
    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 1rem;
        line-height: 1.1;
        letter-spacing: -1.5px;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #94a3b8;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }
    
    /* Custom Button styling - Indigo/Purple Accent */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
        padding: 0.6rem 2rem;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stDateInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 1px #8b5cf6;
    }
    
    /* Hide 'Press Enter to submit' text in forms */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Custom List Row — no backdrop-filter to prevent scroll jitter */
    .list-row-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.07);
        margin-bottom: 0.8rem;
        /* backdrop-filter removed intentionally: causes GPU repaint wobble on scroll */
    }
    .list-row-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 0.4rem;
    }
    .list-row-detail {
        color: #94a3b8;
        font-size: 0.95rem;
    }
    
    /* Testimonial Section override if used */
    .testimonial-box {
        background: rgba(255, 255, 255, 0.02);
        padding: 2.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid #8b5cf6;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Top Bar Auth Status — now inline, no absolute positioning */
    .top-auth-status {
        font-size: 0.9rem;
        color: #94a3b8;
        text-align: right;
        padding-right: 0.5rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #8b5cf6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTION
# ============================================================

# Sensitive columns to hide from regular users
SENSITIVE_COLS = [
    'member_id', 'provider_id', 'requester_id', 'reviewee_id', 'reviewer_id',
    'provider_email', 'requester_email', 'email', 'phone', 'address',
    'password_hash', 'transaction_id', 'request_id', 'ledger_id', 'feedback_id',
    'skill_id'
]

def show_dataframe(data, title=None, exclude_sensitive=True):
    # Fallback for admin screens where native dataframe is preferred
    if data:
        if title:
            st.subheader(title)
        df = pd.DataFrame(data)
        if exclude_sensitive:
            cols_to_drop = [col for col in SENSITIVE_COLS if col in df.columns]
            df = df.drop(columns=cols_to_drop)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available.")

@st.dialog("Select Proficiency Level")
def add_skill_dialog(skill_id, skill_name, user_id):
    st.write(f"What is your proficiency level in **{skill_name}**?")
    proficiency = st.select_slider("Proficiency Level",
        options=["Beginner", "Intermediate", "Advanced", "Expert"], value="Intermediate")
    if st.button("Submit", use_container_width=True):
        try:
            result = services.add_member_skill(user_id, skill_id, proficiency)
            st.session_state[f"skill_added_{skill_id}"] = True
            st.success(f"✅ {result['message']}")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to add skill: {e}")

def render_interactive_list(data, title=None, action_type=None, user_id=None):
    if title:
        st.subheader(title)
        
    if not data:
        st.info("No items found.")
        return

    for idx, item in enumerate(data):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # Determine the best key to use as the title
            title_key = None
            for candidate in ['title', 'skill_name', 'request_title', 'provider_name', 'requester_name', 'description']:
                if candidate in item and item[candidate]:
                    title_key = candidate
                    break
            
            # Fallback to the first non-sensitive key if no title key matched
            if not title_key:
                for k in item.keys():
                    if k not in SENSITIVE_COLS:
                        title_key = k
                        break

            content_html = f"<div class='list-row-title'>{item.get(title_key, 'Item')}</div><div class='list-row-detail'>"
            
            for k, v in item.items():
                if k not in SENSITIVE_COLS and k != title_key:
                    # Clean up the key name for display
                    display_key = str(k).replace('_', ' ').title()
                    content_html += f"<strong>{display_key}:</strong> {v} &nbsp;&nbsp;|&nbsp;&nbsp; "
            
            # Remove trailing separator and close div
            if content_html.endswith("&nbsp;&nbsp;|&nbsp;&nbsp; "):
                content_html = content_html[:-24]
            content_html += "</div>"
            
            st.markdown(f"<div class='list-row-card'>{content_html}</div>", unsafe_allow_html=True)
            
        with col2:
            st.write("") # Vertical alignment spacing
            if action_type == 'add_skill':
                added_key = f"skill_added_{item['skill_id']}"
                if st.session_state.get(added_key, False):
                    st.button("✅ Skill Added", key=f"add_skill_disabled_{idx}", disabled=True)
                else:
                    if st.button("➕ Add", key=f"add_skill_{idx}"):
                        add_skill_dialog(item['skill_id'], item.get(title_key, 'Skill'), user_id)
            elif action_type == 'complete_request':
                if st.button("✓ Finish", key=f"comp_req_{idx}"):
                    st.info("Please fill out the form above to log hours for this request.")
            elif action_type == 'rate_transaction':
                if st.button("⭐ Rate", key=f"rate_txn_{idx}"):
                    st.info("Please use the feedback form above to rate this transaction.")
        
        # Add a tiny gap between rows outside the card css
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

# ============================================================
# AUTHENTICATION STATE
# ============================================================
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

# Separate page-tracking state (never bound to a widget key)
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

def logout():
    st.session_state['logged_in_user'] = None
    st.session_state['current_page'] = 'Home'
    st.rerun()

def navigate(target):
    """Safe navigation callback — called BEFORE next render."""
    st.session_state['current_page'] = target

# ============================================================
# TOP NAVIGATION
# ============================================================
user = st.session_state['logged_in_user']

if user is None:
    nav_options = ["Home", "Login", "Sign Up"]
else:
    nav_options = [
        "Home", 
        "Add Skill",
        "Request Service", 
        "Complete Transaction",
        "View Credits", 
        "Give Feedback"
    ]
    if user['role'] == 'admin':
        nav_options.append("Admin Dashboard")
        nav_options.append("Analytics")

# Ensure current_page is valid for current nav_options
if st.session_state['current_page'] not in nav_options:
    st.session_state['current_page'] = nav_options[0]

current_idx = nav_options.index(st.session_state['current_page'])

# Radio widget has NO key — index drives the selection, result syncs back
page = st.radio(
    "Navigation", nav_options,
    index=current_idx,
    horizontal=True,
    label_visibility="collapsed"
)
# Sync radio result back into our state variable
st.session_state['current_page'] = page

# Display user info + logout in a clean row below the fixed navbar
if user is not None:
    auth_col1, auth_col2 = st.columns([8, 1])
    with auth_col1:
        st.markdown(
            f"<div class='top-auth-status'>👤 <b>{user['first_name']}</b> &nbsp;|&nbsp; ⏱ Credits: <b>{user['credit_balance']}</b></div>",
            unsafe_allow_html=True
        )
    with auth_col2:
        st.button("Logout", on_click=logout, use_container_width=True)

st.write("")  # Some spacing

# ============================================================
# PAGE: HOME
# ============================================================
if page == "Home":
    st.markdown("""
    <div class="hero-container">
        <div style="color: #94a3b8; font-weight: 600; letter-spacing: 1px; margin-bottom: 1rem; text-transform: uppercase; font-size: 0.9rem;">
            ▵ TimeBank Community
        </div>
        <div class="hero-title">Radically better<br>skill exchange platform</div>
        <div class="hero-subtitle">Trade your time, not your money. Empower your local community by offering what you know and receiving what you need.</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if user is None:
        st.write("")
        c1, c2, c3, c4, c5 = st.columns([2, 1, 0.2, 1, 2])
        with c2:
            st.button("🔑  Login", use_container_width=True,
                      on_click=navigate, args=("Login",))
        with c4:
            st.button("✨  Sign Up", use_container_width=True,
                      on_click=navigate, args=("Sign Up",))
    else:
        st.markdown('<h3 style="text-align: center; margin-bottom: 2rem;">Quick Actions</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="list-row-card" style="text-align: center;">
                <h3 style="color: #8b5cf6; margin-bottom: 0.5rem;">Earn Credits</h3>
                <p style="color: #94a3b8;">Add your skills to your profile and start fulfilling requests.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="list-row-card" style="text-align: center;">
                <h3 style="color: #8b5cf6; margin-bottom: 0.5rem;">Request Help</h3>
                <p style="color: #94a3b8;">Need a hand? Spend your credits by requesting a service.</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="list-row-card" style="text-align: center;">
                <h3 style="color: #8b5cf6; margin-bottom: 0.5rem;">Build Trust</h3>
                <p style="color: #94a3b8;">Complete transactions and give feedback to grow your reputation.</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# PAGE: LOGIN
# ============================================================
elif page == "Login":
    st.markdown('<div class="hero-container"><div class="hero-title">Welcome Back</div><div class="hero-subtitle">Login to your TimeBank account</div></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if email and password:
                    member = queries.get_member_by_email(email)
                    if member:
                        hashed_input = hashlib.sha256(password.encode('utf-8')).hexdigest()
                        if member.get('password_hash') == hashed_input:
                            st.session_state['logged_in_user'] = member
                            st.session_state['current_page'] = 'Home'
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid password.")
                    else:
                        st.error("User not found. Please sign up.")
                else:
                    st.error("Please enter email and password.")

# ============================================================
# PAGE: SIGN UP
# ============================================================
elif page == "Sign Up":
    st.markdown('<div class="hero-container"><div class="hero-title">Join TimeBank</div><div class="hero-subtitle">Register a new account to start exchanging skills</div></div>', unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", max_chars=50)
            email = st.text_input("Email *", max_chars=100)
            password = st.text_input("Password *", type="password")
            phone = st.text_input("Phone", max_chars=20)
            dob = st.date_input("Date of Birth", value=None, min_value=date(1950, 1, 1), max_value=date(2010, 1, 1))
        with col2:
            last_name = st.text_input("Last Name *", max_chars=50)
            confirm_password = st.text_input("Confirm Password *", type="password")
            address = st.text_input("Address")
            city = st.text_input("City", max_chars=50)
            state_val = st.text_input("State", max_chars=50)

        zip_code = st.text_input("ZIP Code", max_chars=10)
        submitted = st.form_submit_button("Register Member", use_container_width=True)

        if submitted:
            if not first_name or not last_name or not email or not password:
                st.error("❌ First name, last name, email, and password are required.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                try:
                    result = services.register_member(
                        first_name, last_name, email, password, phone or None,
                        str(dob) if dob else None, address or None,
                        city or None, state_val or None, zip_code or None
                    )
                    st.success(f"✅ {result['message']}")
                    st.info("You can now go to Login.")
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")

# ============================================================
# PAGE: ADD SKILL
# ============================================================
elif page == "Add Skill":
    st.header("Add Skill to Profile")
    try:
        user_skills = queries.get_member_skills(user['member_id']) or []
        if user_skills:
            render_interactive_list(user_skills, title="Your Added Skills", action_type=None)
            st.markdown("---")

        skills = queries.get_all_skills() or []
        if not skills:
            st.warning("Please ensure skills exist in the database.")
        else:
            # Pre-mark skills the user already has
            for us in user_skills:
                for s in skills:
                    if s['skill_name'] == us['skill_name']:
                        st.session_state[f"skill_added_{s['skill_id']}"] = True

            render_interactive_list(skills, title="Available Skills", action_type='add_skill', user_id=user['member_id'])
    except Exception as e:
        st.error(f"Error: {e}")


# ============================================================
# PAGE: REQUEST SERVICE
# ============================================================
elif page == "Request Service":
    st.header("Request a Service")
    try:
        skills = queries.get_all_skills()
        if not skills:
            st.warning("Please ensure skills exist in the database.")
        else:
            with st.form("request_form", clear_on_submit=True):
                skill_options = {f"{s['skill_name']} [{s['category']}]": s['skill_id'] for s in skills}
                selected_skill = st.selectbox("Skill Needed", list(skill_options.keys()))
                title = st.text_input("Request Title *", max_chars=200)
                description = st.text_area("Description")
                estimated_hours = st.number_input("Estimated Hours *", min_value=0.5, value=1.0, step=0.5)
                urgency = st.selectbox("Urgency", ["Low", "Normal", "High", "Urgent"], index=1)
                submitted = st.form_submit_button("Submit Request", use_container_width=True)

                if submitted:
                    if not title or len(title) < 5:
                        st.error("❌ Title must be at least 5 characters.")
                    else:
                        try:
                            result = services.create_service_request(
                                user['member_id'], skill_options[selected_skill],
                                title, description or None, estimated_hours, urgency
                            )
                            st.success(f"✅ {result['message']}")
                        except Exception as e:
                            st.error(f"❌ Request failed: {e}")

        st.markdown("---")
        render_interactive_list(queries.get_all_requests(), title="All Service Requests")
    except Exception as e:
        st.error(f"Error: {e}")


# ============================================================
# PAGE: COMPLETE TRANSACTION
# ============================================================
elif page == "Complete Transaction":
    st.header("Complete a Service Transaction")
    try:
        open_requests = queries.get_open_requests()
        if not open_requests:
            st.info("No open service requests available.")
        else:
            with st.form("transaction_form", clear_on_submit=True):
                request_options = {
                    f"#{r['request_id']} - {r['title']} ({r['requester_name']}, {r['estimated_hours']}h)": r['request_id']
                    for r in open_requests
                }
                selected_request = st.selectbox("Select Open Request", list(request_options.keys()))
                hours_spent = st.number_input("Actual Hours Spent", min_value=0.5, value=1.0, step=0.5)
                notes = st.text_area("Notes (optional)")
                submitted = st.form_submit_button("Complete Transaction", use_container_width=True)

                if submitted:
                    try:
                        result = services.complete_service_transaction(
                            request_options[selected_request], user['member_id'], hours_spent, notes or None
                        )
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Transaction failed: {e}")

        st.markdown("---")
        render_interactive_list(queries.get_transactions_by_member(user['member_id']), title="My Transaction History", action_type='rate_transaction', user_id=user['member_id'])
    except Exception as e:
        st.error(f"Error: {e}")


# ============================================================
# PAGE: VIEW CREDITS
# ============================================================
elif page == "View Credits":
    st.header("My Credits")
    try:
        balance = queries.get_credit_balance(user['member_id'])
        st.metric("Current Balance", f"{balance} credits")
        st.markdown("#### Transaction Ledger")
        render_interactive_list(queries.get_credit_ledger(user['member_id']))
    except Exception as e:
        st.error(f"Error: {e}")


# ============================================================
# PAGE: GIVE FEEDBACK
# ============================================================
elif page == "Give Feedback":
    st.header("Submit Feedback")
    try:
        transactions = queries.get_all_transactions()
        if not transactions:
            st.info("No completed transactions available.")
        else:
            completed = [t for t in transactions if t.get('transaction_status') == 'Completed']
            if not completed:
                st.info("No completed transactions found.")
            else:
                with st.form("feedback_form", clear_on_submit=True):
                    txn_options = {
                        f"#{t['transaction_id']} - {t['provider_name']} → {t['requester_name']}": t['transaction_id']
                        for t in completed
                    }
                    selected_txn = st.selectbox("Select Transaction", list(txn_options.keys()))
                    rating = st.slider("Rating", 1, 5, 4)
                    comment = st.text_area("Comment (min 10 characters)")
                    submitted = st.form_submit_button("Submit Feedback", use_container_width=True)

                    if submitted:
                        if comment and len(comment) < 10:
                            st.error("❌ Comment must be at least 10 characters.")
                        else:
                            try:
                                result = services.submit_feedback(
                                    txn_options[selected_txn], user['member_id'], rating, comment or None
                                )
                                st.success(f"✅ {result['message']}")
                            except Exception as e:
                                st.error(f"❌ Feedback failed: {e}")
    except Exception as e:
        st.error(f"Error: {e}")


# ============================================================
# PAGE: ADMIN DASHBOARD (Protected)
# ============================================================
elif page == "Admin Dashboard":
    st.header("Admin Dashboard")
    st.markdown("Overview of all users and system database state.")
    
    st.subheader("Registered Members")
    try:
        show_dataframe(queries.get_all_members(), exclude_sensitive=False)
    except Exception as e:
        st.error(f"Could not load members: {e}")
        
    st.markdown("---")
    st.subheader("Database Statistics")
    try:
        stats = queries.get_database_stats()
        show_dataframe(stats, exclude_sensitive=False)
    except Exception as e:
        st.error(f"Could not load database stats: {e}")


# ============================================================
# PAGE: ANALYTICS (Admin Only logic applied in navbar)
# ============================================================
elif page == "Analytics":
    st.header("Analytics Dashboard")
    try:
        tab1, tab2, tab3 = st.tabs(["🏆 Top Members", "🔥 Popular Skills", "📅 Trends"])
        with tab1:
            st.subheader("Top Credit Holders")
            show_dataframe(queries.get_top_credit_holders())
        with tab2:
            st.subheader("Most Requested Skills")
            show_dataframe(queries.get_popular_skills())
        with tab3:
            st.subheader("Monthly Transaction Summary")
            show_dataframe(queries.get_monthly_stats())
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

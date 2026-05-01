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
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS (Dark Theme Vibe)
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Global App Background - Deep Navy/Teal (Fish Hunters Vibe) */
    .stApp {
        background: linear-gradient(135deg, #0b131a 0%, #16222f 100%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    /* Vibe Specific Classes */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .sub-header {
        font-size: 0.9rem;
        color: #74B72E; /* Bright Lime Green Accent */
        margin-bottom: 2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    /* Custom Button styling - Vibrant Coral/Orange */
    .stButton>button {
        background-color: #ff4d4d !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 4px;
        font-weight: 600;
        letter-spacing: 1px;
        padding: 0.5rem 1.5rem;
        box-shadow: 0 4px 6px rgba(255, 77, 77, 0.2);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #e63939 !important;
        box-shadow: 0 6px 12px rgba(255, 77, 77, 0.4);
        transform: translateY(-2px);
    }
    
    /* Testimonial Section */
    .testimonial-box {
        background: rgba(11, 19, 26, 0.6);
        padding: 2.5rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 6px solid #74B72E; /* Lime green quote accent */
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .quote-icon {
        font-size: 4rem;
        color: #74B72E;
        line-height: 0.5;
        font-family: serif;
        font-weight: bold;
    }
    
    /* Dataframes/Tables Fallback */
    [data-testid="stDataFrame"] {
        background: rgba(11, 19, 26, 0.8);
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0b131a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Modernize Sidebar Navigation (Radio Buttons to Glowing Text) */
    /* Hide the default radio circle */
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    /* Style the label container to be transparent */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 0.5rem 0.5rem !important;
        margin-bottom: 0.2rem !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    /* Hover effect: Text Glow and slight shift */
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: transparent !important;
        border-color: transparent !important;
        transform: translateX(8px) !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] {
        color: #ff4d4d !important;
        text-shadow: 0 0 10px rgba(255, 77, 77, 0.6) !important;
    }
    /* Active/Selected state: Intense Text Glow */
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: transparent !important;
        border-color: transparent !important;
        transform: translateX(8px) !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] {
        color: #ff4d4d !important;
        text-shadow: 0 0 15px rgba(255, 77, 77, 0.8), 0 0 5px rgba(255, 77, 77, 0.4) !important;
    }
    
    /* Base text styling for sidebar items */
    [data-testid="stSidebar"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        width: 100%;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stDateInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(22, 34, 47, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #ff4d4d;
        box-shadow: 0 0 0 1px #ff4d4d;
    }
    
    /* Hide 'Press Enter to submit' text in forms */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Adjust text colors inside containers */
    .testimonial-box p { color: #cbd5e1 !important; font-size: 1.1rem; line-height: 1.6; }
    .testimonial-box strong { color: #ffffff !important; }
    
    /* Custom List Row */
    .list-row-card {
        background: rgba(22, 34, 47, 0.5);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 0.5rem;
    }
    .list-row-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.2rem;
    }
    .list-row-detail {
        color: #94a3b8;
        font-size: 0.9rem;
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
                if st.button("➕ Add", key=f"add_skill_{idx}"):
                    try:
                        result = services.add_member_skill(user_id, item['skill_id'], "Intermediate")
                        st.success("Skill added!")
                    except Exception as e:
                        st.error(f"Error: {e}")
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

def logout():
    st.session_state['logged_in_user'] = None
    st.rerun()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.title("⏰ TimeBank")
st.sidebar.markdown("---")

user = st.session_state['logged_in_user']

if user is None:
    page = st.sidebar.radio("Navigate", ["Login", "Sign Up"])
else:
    st.sidebar.write(f"Welcome, **{user['first_name']}**!")
    st.sidebar.write(f"Role: `{user['role']}`")
    st.sidebar.write(f"Credits: **{user['credit_balance']}**")
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.markdown("---")
    
    nav_options = [
        "🏠 Home", 
        "🛠️ Add Skill",
        "📋 Request Service", 
        "✅ Complete Transaction",
        "💰 View Credits", 
        "⭐ Give Feedback"
    ]
    
    if user['role'] == 'admin':
        nav_options.append("🛡️ Admin Dashboard")
        nav_options.append("📊 Analytics")
        
    page = st.sidebar.radio("Navigate", nav_options)

st.sidebar.markdown("---")
st.sidebar.info("**1 Hour = 1 Credit**\nExchange skills, not money!")


# ============================================================
# PAGE: LOGIN
# ============================================================
if page == "Login":
    st.markdown('<div class="main-header">Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Login to your account</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if email and password:
                member = queries.get_member_by_email(email)
                if member:
                    hashed_input = hashlib.sha256(password.encode('utf-8')).hexdigest()
                    if member.get('password_hash') == hashed_input:
                        st.session_state['logged_in_user'] = member
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
    st.markdown('<div class="main-header">Join TimeBank</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Register a new account</div>', unsafe_allow_html=True)

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
            state = st.text_input("State", max_chars=50)

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
                        city or None, state or None, zip_code or None
                    )
                    st.success(f"✅ {result['message']}")
                    st.info("You can now go to Login.")
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")

# ============================================================
# PAGE: HOME (AUTHENTICATED)
# ============================================================
elif page == "🏠 Home":
    st.markdown('<div class="sub-header">TESTIMONIALS</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header">Thousands of Happy Skill Exchangers</div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        # Placeholder for an image in the layout
        st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80", 
                 caption="Community Exchange", use_container_width=True)
                 
    with col2:
        st.markdown("""
        <div class="testimonial-box">
            <span class="quote-icon">"</span>
            <p>
            "Outstanding store for fishing accessories! Top-notch products, user-friendly 
            website, and excellent customer service. They truly care about anglers and provide 
            valuable tips. Highly recommended!"
            </p>
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="https://i.pravatar.cc/150?img=11" style="border-radius: 50%; width: 50px; height: 50px;">
                <div>
                    <strong>Jenny Wilson</strong><br>
                    <span style="color: #94a3b8; font-size: 0.9rem;">Fish Hunter</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Newsletter / Subscribe section mimic
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">TESTIMONIALS</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-bottom: 1rem;">Subscribe for Newsletter</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; max-width: 600px; margin: 0 auto 2rem auto;">With designs that spark conversations and evoke the spirit of adventure, Gill Rush empowers you to wear your passion on your sleeve...back on your chest.</p>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        sub_col1, sub_col2 = st.columns([2, 1])
        with sub_col1:
            st.text_input("", placeholder="Email Address", label_visibility="collapsed")
        with sub_col2:
            st.button("Subscribe Now", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PAGE: ADD SKILL
# ============================================================
elif page == "🛠️ Add Skill":
    st.header("🛠️ Add Skill to Profile")
    try:
        skills = queries.get_all_skills()
        if not skills:
            st.warning("Please ensure skills exist in the database.")
        else:
            with st.form("add_skill_form", clear_on_submit=True):
                skill_options = {f"{s['skill_name']} [{s['category']}]": s['skill_id'] for s in skills}
                selected_skill = st.selectbox("Select Skill", list(skill_options.keys()))
                proficiency = st.select_slider("Proficiency Level",
                    options=["Beginner", "Intermediate", "Advanced", "Expert"], value="Intermediate")
                submitted = st.form_submit_button("Add Skill", use_container_width=True)

                if submitted:
                    try:
                        result = services.add_member_skill(
                            user['member_id'], skill_options[selected_skill], proficiency
                        )
                        st.success(f"✅ {result['message']}")
                    except Exception as e:
                        st.error(f"❌ Failed to add skill: {e}")

        st.markdown("---")
        render_interactive_list(skills, title="Available Skills", action_type='add_skill', user_id=user['member_id'])
    except Exception as e:
        st.error(f"Error: {e}")


# ============================================================
# PAGE: REQUEST SERVICE
# ============================================================
elif page == "📋 Request Service":
    st.header("📋 Request a Service")
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
elif page == "✅ Complete Transaction":
    st.header("✅ Complete a Service Transaction")
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
elif page == "💰 View Credits":
    st.header("💰 My Credits")
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
elif page == "⭐ Give Feedback":
    st.header("⭐ Submit Feedback")
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
elif page == "🛡️ Admin Dashboard":
    st.header("🛡️ Admin Dashboard")
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
# PAGE: ANALYTICS (Admin Only logic applied in sidebar)
# ============================================================
elif page == "📊 Analytics":
    st.header("📊 Analytics Dashboard")
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

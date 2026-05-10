import streamlit as st
import sys
import os
import sqlite3

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="NeXtGen TestBot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CHECK PAYMENT SUCCESS =====
query_params = st.query_params
if "payment" in query_params and query_params["payment"] == "success":
    session_id = query_params.get("session_id", None)
    
    if session_id:
        # Get plan from database
        import stripe
        stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            plan = session.metadata.get('plan', 'basic')
            username = session.metadata.get('username', None)
            
            if username:
                # Update database
                conn = sqlite3.connect('data/users.db')
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET plan = ? WHERE username = ?",
                    (plan, username)
                )
                conn.commit()
                conn.close()
                
                # Set session state for logged in user
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.plan = plan
                st.session_state.email = session.metadata.get('email', f"{username}@example.com")
                st.session_state.page = "Dashboard"
                st.session_state.payment_success = True
                st.session_state.upgraded_plan = plan
                    
                # Clear query params
                st.query_params.clear()
                
        except Exception as e:
            st.error(f"Payment verification error: {e}")

# ===== CSS LOAD KARO =====
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
try:
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS file not found: {e}")

# Add CSS to hide sidebar completely
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    .user-info {
        position: fixed;
        top: 10px;
        right: 20px;
        z-index: 999;
        background: rgba(0,180,255,0.1);
        padding: 8px 15px;
        border-radius: 20px;
        color: white;
        border: 1px solid #00b4ff;
        backdrop-filter: blur(5px);
        box-shadow: 0 0 20px rgba(0,180,255,0.3);
    }
    .success-message {
        background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 20px 0;
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .back-button {
        margin-bottom: 20px;
    }
    .back-button button {
        background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }
</style>
""", unsafe_allow_html=True)

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import page functions
from pages.login import show as Login
from pages.pricing import show as Pricing
from pages.dashboard import show as Dashboard
from pages.configure_test import show as Configure_Test
from pages.results import show as Results
from utils.auth import init_auth, logout

# Initialize authentication
init_auth()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.plan = "basic"
    st.session_state.page = "Login"
    st.session_state.payment_success = False
    st.session_state.upgraded_plan = None

# Navigation based on login state
if not st.session_state.logged_in:
    Login()
else:
    # Show payment success message if just upgraded
    if st.session_state.get('payment_success', False):
        upgraded_plan = st.session_state.get('upgraded_plan', 'premium')
        st.markdown(f"""
        <div class='success-message'>
            <h2>🎉 Congratulations!</h2>
            <p>Your plan has been successfully upgraded to <strong>{upgraded_plan.upper()}</strong>!</p>
            <p>You now have access to all {upgraded_plan.upper()} plan features.</p>
        </div>
        """, unsafe_allow_html=True)
        # Clear the success flag
        st.session_state.payment_success = False
        st.session_state.upgraded_plan = None
    
    # User info in top right
    st.markdown(f"""
    <div class='user-info'>
        👋 {st.session_state.username} | {st.session_state.plan.upper()} Plan
    </div>
    """, unsafe_allow_html=True)
    
    # ===== PAGE NAVIGATION - FIXED =====
    if st.session_state.page == "Dashboard":
        Dashboard()
    
    elif st.session_state.page == "Configure_Test":
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("← Back to Dashboard", key="back_configure_unique"):
            st.session_state.page = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        Configure_Test()
    
    elif st.session_state.page == "Results":
        # ===== FIXED: Sirf results dikhao, test run mat karo =====
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("← Back to Dashboard", key="back_results_unique"):
            st.session_state.page = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Check if we have test results in session
        if 'test_run' in st.session_state:
            # Sirf results dikhao, test run mat karo
            # Results page will read from session state, not run new test
            Results()
        else:
            st.warning("⚠️ No test results available. Please run a test first!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚙️ Configure Test", use_container_width=True):
                    st.session_state.page = "Configure_Test"
                    st.rerun()
            with col2:
                if st.button("🏠 Back to Dashboard", use_container_width=True):
                    st.session_state.page = "Dashboard"
                    st.rerun()
    
    elif st.session_state.page == "Pricing":
        st.markdown('<div class="back-button">', unsafe_allow_html=True)
        if st.button("← Back to Dashboard", key="back_pricing_unique"):
            st.session_state.page = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        Pricing()
    
    else:
        Dashboard()
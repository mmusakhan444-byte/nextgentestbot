import streamlit as st
from utils.auth import check_login, create_user

def show():
    # NEON THEME CSS FOR LOGIN PAGE
    st.markdown("""
    <style>
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgba(0, 180, 255, 0.25) 0%, #0A0A0F 90%);
            font-family: 'Space Grotesk', 'Inter', sans-serif;
        }
        
        .main-container {
            max-width: 480px;
            margin: 20px auto;
            padding: 35px;
            background: rgba(12, 12, 20, 0.85);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(0, 180, 255, 0.4);
            border-radius: 35px;
            box-shadow: 0 30px 70px rgba(0, 0, 0, 0.7), 0 0 50px rgba(0, 180, 255, 0.4);
            animation: slideUp 0.5s ease-out;
            position: relative;
            overflow: hidden;
        }
        
        .main-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00b4ff, #4d4dff, #00b4ff, #4d4dff, #00b4ff);
            border-radius: 35px;
            opacity: 0.4;
            z-index: -1;
            animation: borderGlow 4s infinite;
            background-size: 300% 300%;
        }
        
        @keyframes borderGlow {
            0% { opacity: 0.3; background-position: 0% 50%; }
            50% { opacity: 0.6; background-position: 100% 50%; }
            100% { opacity: 0.3; background-position: 0% 50%; }
        }
        
        .main-container::after {
            content: '';
            position: absolute;
            top: 0;
            left: -50%;
            width: 20%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 180, 255, 0.3), transparent);
            transform: skewX(-25deg);
            animation: scanLight 6s infinite;
        }
        
        @keyframes scanLight {
            0% { left: -50%; }
            100% { left: 150%; }
        }
        
        .logo-container {
            text-align: center;
            margin-bottom: 25px;
            position: relative;
        }
        
        .logo-container::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 20%;
            width: 60%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00b4ff, #4d4dff, #00b4ff, transparent);
            animation: glowLine 3s infinite;
        }
        
        @keyframes glowLine {
            0% { opacity: 0.3; transform: scaleX(0.8); }
            50% { opacity: 1; transform: scaleX(1.2); }
            100% { opacity: 0.3; transform: scaleX(0.8); }
        }
        
        .logo {
            font-size: 52px;
            font-weight: 900;
            background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 50%, #00b4ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
            padding: 10px 25px;
            text-shadow: 0 0 40px rgba(0, 180, 255, 0.7);
            letter-spacing: 3px;
            animation: logoGlow 3s infinite;
        }
        
        @keyframes logoGlow {
            0% { text-shadow: 0 0 30px rgba(0, 180, 255, 0.5); }
            50% { text-shadow: 0 0 60px rgba(0, 180, 255, 0.9), 0 0 30px rgba(77, 77, 255, 0.7); }
            100% { text-shadow: 0 0 30px rgba(0, 180, 255, 0.5); }
        }
        
        .logo-sub {
            font-size: 14px;
            color: #8892b0;
            margin-top: 8px;
            font-weight: 600;
            letter-spacing: 4px;
            text-transform: uppercase;
            text-shadow: 0 0 15px rgba(0, 180, 255, 0.3);
        }
        
        .tagline {
            text-align: center;
            color: #8892b0;
            font-size: 14px;
            margin-bottom: 35px;
            font-weight: 400;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 180, 255, 0.2);
        }
        
        .tab-container {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            padding: 5px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 50px;
            border: 1px solid rgba(0, 180, 255, 0.2);
        }
        
        .stTextInput label {
            color: #00b4ff !important;
            font-weight: 700 !important;
            font-size: 12px !important;
            text-transform: uppercase !important;
            letter-spacing: 2.5px !important;
            margin-bottom: 8px !important;
            display: block !important;
            text-shadow: 0 0 15px rgba(0, 180, 255, 0.5) !important;
        }
        
        .stCheckbox label {
            color: #8892b0 !important;
            font-weight: 500 !important;
            text-shadow: 0 0 10px rgba(0, 180, 255, 0.2) !important;
        }
        
        .stMarkdown {
            color: #8892b0 !important;
        }
        
        .stTextInput input {
            background: rgba(5, 5, 10, 0.9) !important;
            color: #fff !important;
            border: 1px solid rgba(0, 180, 255, 0.4) !important;
            border-radius: 20px !important;
            padding: 14px 18px !important;
            font-size: 15px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 0 20px rgba(0, 180, 255, 0.2), inset 0 0 10px rgba(0, 180, 255, 0.1) !important;
            backdrop-filter: blur(5px);
        }
        
        .stTextInput input:focus {
            border-color: #00b4ff !important;
            box-shadow: 0 0 40px rgba(0, 180, 255, 0.5), inset 0 0 20px rgba(0, 180, 255, 0.2) !important;
            background: rgba(10, 10, 20, 0.95) !important;
            transform: scale(1.02);
        }
        
        .stTextInput input::placeholder {
            color: rgba(136, 146, 176, 0.4) !important;
            font-style: italic;
        }
        
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #00b4ff 0%, #4d4dff 50%, #00b4ff 100%) !important;
            background-size: 200% auto !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 14px 25px !important;
            font-size: 15px !important;
            font-weight: 800 !important;
            letter-spacing: 3px !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 0 40px rgba(0, 180, 255, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.3) !important;
            position: relative;
            overflow: hidden;
            animation: buttonPulse 2s infinite;
        }
        
        @keyframes buttonPulse {
            0% { box-shadow: 0 0 40px rgba(0, 180, 255, 0.5); }
            50% { box-shadow: 0 0 70px rgba(0, 180, 255, 0.8), 0 0 40px rgba(77, 77, 255, 0.6); }
            100% { box-shadow: 0 0 40px rgba(0, 180, 255, 0.5); }
        }
        
        .stButton button[kind="primary"]:hover {
            transform: translateY(-3px) scale(1.02);
            background-position: right center !important;
            box-shadow: 0 0 80px rgba(0, 180, 255, 0.9), inset 0 0 30px rgba(255, 255, 255, 0.4) !important;
        }
        
        .stButton button[kind="secondary"] {
            background: transparent !important;
            color: #00b4ff !important;
            border: 1.5px solid #00b4ff !important;
            border-radius: 25px !important;
            padding: 12px 25px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 0 20px rgba(0, 180, 255, 0.2), inset 0 0 10px rgba(0, 180, 255, 0.1) !important;
            backdrop-filter: blur(5px);
        }
        
        .stButton button[kind="secondary"]:hover {
            background: rgba(0, 180, 255, 0.15) !important;
            color: white !important;
            box-shadow: 0 0 50px rgba(0, 180, 255, 0.5), inset 0 0 20px rgba(0, 180, 255, 0.2) !important;
            transform: translateY(-2px);
            border-color: #4d4dff !important;
        }
        
        .stButton button {
            font-weight: 600 !important;
            margin-bottom: 5px !important;
            border-radius: 25px !important;
        }
        
        h3 {
            color: white !important;
            font-weight: 800 !important;
            font-size: 20px !important;
            margin-bottom: 25px !important;
            margin-top: 10px !important;
            text-shadow: 0 0 30px rgba(0, 180, 255, 0.7) !important;
            letter-spacing: 2px;
            text-align: center;
        }
        
        .stRadio label {
            color: #8892b0 !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            text-shadow: 0 0 10px rgba(0, 180, 255, 0.2) !important;
        }
        
        .stRadio div {
            color: #00b4ff !important;
        }
        
        .stRadio [data-baseweb="radio"] {
            background: rgba(0, 180, 255, 0.2) !important;
            border-color: #00b4ff !important;
        }
        
        .stAlert {
            background: rgba(20, 20, 30, 0.95) !important;
            color: #fff !important;
            border: 1px solid rgba(0, 180, 255, 0.4) !important;
            border-radius: 20px !important;
            padding: 12px !important;
            margin: 15px 0 !important;
            backdrop-filter: blur(5px);
            box-shadow: 0 0 30px rgba(0, 180, 255, 0.3) !important;
            animation: alertGlow 2s infinite;
        }
        
        @keyframes alertGlow {
            0% { box-shadow: 0 0 20px rgba(0, 180, 255, 0.2); }
            50% { box-shadow: 0 0 40px rgba(0, 180, 255, 0.4); }
            100% { box-shadow: 0 0 20px rgba(0, 180, 255, 0.2); }
        }
        
        .stSuccess {
            border-left: 5px solid #00b4ff !important;
        }
        
        .stError {
            border-left: 5px solid #ff4d4d !important;
        }
        
        .stWarning {
            border-left: 5px solid #ffd700 !important;
        }
        
        .footer-text {
            color: rgba(136, 146, 176, 0.8) !important;
            font-size: 12px;
            text-align: center;
            font-weight: 400;
            margin-top: 25px;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 180, 255, 0.2);
        }
        
        hr {
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, #00b4ff, #4d4dff, #00b4ff, transparent) !important;
            margin: 25px 0 !important;
            animation: dividerGlow 3s infinite;
        }
        
        @keyframes dividerGlow {
            0% { opacity: 0.3; }
            50% { opacity: 0.8; }
            100% { opacity: 0.3; }
        }
        
        .stCheckbox {
            color: #8892b0 !important;
        }
        
        .stCheckbox [data-baseweb="checkbox"] {
            background: rgba(0, 180, 255, 0.2) !important;
            border-color: #00b4ff !important;
        }
        
        .stForm {
            background: transparent !important;
        }
        
        div[data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        
        .row-widget {
            margin-bottom: 8px !important;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        .slide-up {
            animation: slideUp 0.5s ease-out;
        }
        
        .weather-info {
            color: rgba(136, 146, 176, 0.7);
            text-align: center;
            font-size: 12px;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(0, 180, 255, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='logo-container'>
        <div class='logo'>⚡ NeXtGen TestBot</div>
        <div class='logo-sub'>AI-POWERED TESTING AGENT</div>
    </div>
    <div class='tagline'>Simple automated testing made easy</div>
    """, unsafe_allow_html=True)
    
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "login"
    
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="tab-container">', unsafe_allow_html=True)
            tab_col1, tab_col2 = st.columns(2)
            
            with tab_col1:
                if st.button(
                    "🔐 LOGIN",
                    key="login_tab",
                    use_container_width=True,
                    type="primary" if st.session_state.auth_tab == "login" else "secondary"
                ):
                    st.session_state.auth_tab = "login"
                    st.rerun()
            
            with tab_col2:
                if st.button(
                    "👤 CREATE ACCOUNT",
                    key="signup_tab",
                    use_container_width=True,
                    type="primary" if st.session_state.auth_tab == "signup" else "secondary"
                ):
                    st.session_state.auth_tab = "signup"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.auth_tab == "login":
                show_login_form()
            else:
                show_signup_form()
            
            st.markdown("---")
            st.markdown("""
            <div class='weather-info'>
                🌤️ 26°C Sunny | 2:12 PM | 3/8/2026
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_login_form():
    with st.form("login_form"):
        st.markdown("<br>", unsafe_allow_html=True)
        
        email = st.text_input(
            "📧 EMAIL ADDRESS",
            placeholder="user@example.com"
        )
        
        password = st.text_input(
            "🔑 PASSWORD",
            type="password",
            placeholder="••••••••"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            remember = st.checkbox("🔷 Remember me")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button(
            "⚡ LOGIN TO DASHBOARD ⚡",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not email or not password:
                st.error("⚠️ Please enter both email and password!")
            else:
                success, username, plan, user_email = check_login(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.email = user_email
                    st.session_state.plan = plan
                    st.session_state.page = "Dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password!")

def show_signup_form():
    with st.form("signup_form"):
        st.markdown("<br>", unsafe_allow_html=True)
        
        username = st.text_input(
            "👤 USERNAME",
            placeholder="Choose a username"
        )
        
        email = st.text_input(
            "📧 EMAIL",
            placeholder="user@example.com"
        )
        
        password = st.text_input(
            "🔑 PASSWORD",
            type="password",
            placeholder="Create a strong password"
        )
        
        confirm_password = st.text_input(
            "🔒 CONFIRM PASSWORD",
            type="password",
            placeholder="Re-enter your password"
        )
        
        if password:
            if len(password) < 8:
                st.warning("⚠️ Password must be at least 8 characters")
        
        if confirm_password and password != confirm_password:
            st.error("❌ Passwords do not match!")
        
        st.markdown("### 💰 SELECT YOUR PLAN")
        
        plan = st.radio(
            "Choose your plan",
            options=["basic", "plus", "premium"],
            format_func=lambda x: {
                "basic": "🔵 BASIC PLAN (Free) - 5 tests",
                "plus": "🟡 PLUS PLAN ($15/mo) - 12 tests",
                "premium": "🔴 PREMIUM PLAN ($29/mo) - 20 tests"
            }[x],
            index=0
        )
        
        terms = st.checkbox("✅ I agree to the Terms of Service")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button(
            "⚡ CREATE ACCOUNT ⚡",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not username or not email or not password or not confirm_password:
                st.error("⚠️ Please fill in all fields!")
            elif password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif len(password) < 8:
                st.error("⚠️ Password must be at least 8 characters!")
            elif not terms:
                st.error("⚠️ Please agree to the Terms of Service!")
            else:
                success, message = create_user(username, email, password, plan)
                if success:
                    st.success("✅ Account created successfully! Please login.")
                    st.session_state.auth_tab = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
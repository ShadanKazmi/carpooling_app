import streamlit as st
from auth.auth_util import authenticate_user, save_user, get_user_by_email, reset_password
from scripts.logger import log_user_action

def show_auth_page():
    # Remove Background Color - Use Default Streamlit Theme
    st.markdown("""
    <style>
        .stApp {
            background-color: transparent !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Dark Theme with Sky Blue Accents
    st.markdown("""
    <style>
        /* Main Container */
        .auth-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
        }
        
        /* Header */
        .auth-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 50px 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
            border-bottom: 4px solid #00d4ff;
        }
        
        .auth-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 10px;
            color: #00d4ff;
        }
        
        .auth-subtitle {
            font-size: 18px;
            opacity: 0.9;
            color: #e0e0e0;
        }
        
        /* Feature Cards in Header */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 40px 0;
        }
        
        .feature-item {
            background: #16213e;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.1);
            border-top: 4px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .feature-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0, 212, 255, 0.2);
            border-top-color: #00d4ff;
        }
        
        .feature-icon {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .feature-title {
            font-weight: 700;
            color: #00d4ff;
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .feature-desc {
            font-size: 13px;
            color: #b0b0b0;
            line-height: 1.5;
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 12px 12px 0 0;
            gap: 5px;
            padding: 10px;
            border-bottom: 3px solid #00d4ff;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 8px;
            color: #b0b0b0;
            font-weight: 600;
            padding: 12px 24px;
        }
        
        .stTabs [aria-selected="true"] {
            background: #00d4ff;
            color: #1a1a2e;
        }
        
        /* Form Card */
        .form-card {
            background: #16213e;
            padding: 35px;
            border-radius: 15px;
            border: 2px solid #00d4ff;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.12);
        }
        
        .form-title {
            font-size: 28px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 8px;
        }
        
        .form-subtitle {
            color: #b0b0b0;
            font-size: 14px;
            margin-bottom: 25px;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stDateInput > div > div {
            border-radius: 10px !important;
            border: 2px solid #00d4ff !important;
            background: #1a1a2e !important;
            color: #e0e0e0 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within,
        .stDateInput > div > div:focus-within {
            border-color: #00d4ff !important;
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2) !important;
        }
        
        /* Submit Button */
        .stButton > button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
            color: #1a1a2e !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 30px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown("""
    <div class="auth-header">
        <div class="auth-title">🚖 CarPoolConnect</div>
        <div class="auth-subtitle">Share Rides, Save Money, Travel Smarter</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Matching</div>
            <div class="feature-desc">Find perfect ride partners instantly</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Save Money</div>
            <div class="feature-desc">Split costs effectively with others</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Safe & Secure</div>
            <div class="feature-desc">Verified users and ratings only</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth Tabs
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🔑 Forgot Password"])
    
    with tab1:
        st.markdown("""
        <div class="form-card">
            <div class="form-title">Welcome Back!</div>
            <div class="form-subtitle">Enter your credentials to access your account</div>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email Address", key="login_email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", key="login_password", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Login", key="login_btn"):
            if not email or not password:
                st.warning("⚠️ Please fill in all fields")
            else:
                with st.spinner("🔄 Authenticating..."):
                    try:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.success(f"✅ Welcome back, {user['name']}!")
                            log_user_action("login", email, user["role"], success=True)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials or inactive account.")
                            log_user_action("login", email, "", success=False, message="Invalid credentials or inactive user")
                    except Exception as e:
                        st.error("❌ Login failed due to a system error.")
                        log_user_action("login", email, "", success=False, message=f"Exception: {e}")
    
    with tab2:
        st.markdown("""
        <div class="form-card">
            <div class="form-title">Create Your Account</div>
            <div class="form-subtitle">Join our community and start carpooling today!</div>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Full Name", key="register_name", placeholder="Enter your full name")
        email = st.text_input("📧 Email Address", key="register_email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", key="register_password", placeholder="Create a strong password")
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("👥 I am a...", ["passenger", "driver"], key="register_role")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✨ Create Account", key="register_btn"):
            if not name or not email or not password:
                st.warning("⚠️ Please fill out all fields.")
            elif len(name.strip()) < 3:
                st.warning("⚠️ Name must be at least 3 characters long.")
            else:
                with st.spinner("🔄 Creating your account..."):
                    try:
                        success = save_user(name, email, password, role)
                        if success:
                            st.success("✅ Account created successfully! You can now log in.")
                            log_user_action("signup", email, role, success=True)
                        else:
                            st.error("❌ Email already registered or an error occurred.")
                            log_user_action("signup", email, role, success=False, message="Email already exists or DB error")
                    except ValueError as ve:
                        st.error(f"❌ Registration failed: {ve}")
                        log_user_action("signup", email, role, success=False, message=f"Validation error: {ve}")
                    except Exception as e:
                        st.error("❌ Unexpected error during registration.")
                        log_user_action("signup", email, role, success=False, message=f"Exception: {e}")
    
    with tab3:
        st.markdown("""
        <div class="form-card">
            <div class="form-title">Forgot Your Password?</div>
            <div class="form-subtitle">Reset your password to regain access to your account</div>
        </div>
        """, unsafe_allow_html=True)
        
        reset_email = st.text_input("📧 Email Address", key="reset_email", placeholder="Enter your registered email")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔍 Find Account", key="find_account_btn"):
            if not reset_email:
                st.warning("⚠️ Please enter your email address")
            else:
                user = get_user_by_email(reset_email)
                if user:
                    st.session_state["reset_user_found"] = True
                    st.session_state["reset_user_email"] = reset_email
                    st.session_state["reset_user_name"] = user["name"]
                    st.success(f"✅ Account found! Welcome {user['name']}")
                else:
                    st.error("❌ No account found with this email address.")
                    log_user_action("forgot_password_attempt", reset_email, "", success=False, message="Email not found")
        
        if st.session_state.get("reset_user_found"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader(f"📝 Reset Password for {st.session_state.get('reset_user_name')}")
            
            new_password = st.text_input("🔒 New Password", type="password", key="new_password", placeholder="Create a new strong password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", key="confirm_password", placeholder="Confirm your new password")
            
            st.markdown("<small style='color: #b0b0b0;'>Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number</small>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🔄 Reset Password", key="reset_password_btn"):
                if not new_password or not confirm_password:
                    st.warning("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                else:
                    with st.spinner("🔄 Resetting password..."):
                        try:
                            success = reset_password(st.session_state["reset_user_email"], new_password)
                            if success:
                                st.success("✅ Password reset successfully! You can now login with your new password.")
                                log_user_action("password_reset", st.session_state["reset_user_email"], "", success=True)
                                st.session_state["reset_user_found"] = False
                                st.session_state["reset_user_email"] = None
                                st.session_state["reset_user_name"] = None
                                st.rerun()
                            else:
                                st.error("❌ Failed to reset password. Try again later.")
                                log_user_action("password_reset", st.session_state["reset_user_email"], "", success=False, message="Reset failed")
                        except ValueError as ve:
                            st.error(f"❌ Password reset failed: {ve}")
                            log_user_action("password_reset", st.session_state["reset_user_email"], "", success=False, message=f"Validation error: {ve}")
                        except Exception as e:
                            st.error("❌ Unexpected error during password reset.")
                            log_user_action("password_reset", st.session_state["reset_user_email"], "", success=False, message=f"Exception: {e}")
    
    # Logged In Section (simple)
    if st.session_state.get("authenticated"):
        user = st.session_state["user"]
        st.info(f"👋 Hello, {user['name']}! Role: {user['role'].upper()}")
        if st.button("🚪 Logout", key="logout_btn"):
            log_user_action("logout", user["email"], user["role"], success=True)
            st.session_state.clear()
            st.success("✅ You've been logged out successfully.")
            st.rerun()

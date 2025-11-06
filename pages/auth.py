import streamlit as st
from auth.auth_util import authenticate_user, save_user
from scripts.logger import log_user_action
 
def show_auth_page():
 
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "Login"
 
    st.title("CarPoolConnect")
    st.subheader("Log in or sign up to start sharing rides")
 
    tab1, tab2 = st.tabs(["Login", "Register"] if st.session_state.auth_tab == "Login"
                         else ["Register", "Login"])
 
    with tab1 if st.session_state.auth_tab == "Login" else tab2:
        st.markdown("### Existing User Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
 
        if st.button("Login"):
            try:
                user = authenticate_user(email, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.success(f"Welcome back, {user['name']}!")
                    log_user_action("login", email, user["role"], success=True)
                    st.rerun()
                else:
                    st.error("Invalid credentials or inactive account.")
            except Exception as e:
                st.error("Login failed due to a system error.")
                log_user_action("login", email, "", success=False, message=f"Exception: {e}")
 
    with tab2 if st.session_state.auth_tab == "Login" else tab1:
        st.markdown("### Create a New Account")
        name = st.text_input("Full Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        role = st.selectbox("I am a...", ["passenger", "driver"], key="register_role")
 
        if st.button("Register"):
            if not name or not email or not password:
                st.warning("Please fill out all fields.")
            elif len(name.strip()) < 3:
                st.warning("Name must be at least 3 characters long.")
            else:
                try:
                    success = save_user(name, email, password, role)
                    if success:
                        st.success("✅ Account created successfully! Redirecting to login...")
                        log_user_action("signup", email, role, success=True)
 
                        st.session_state.auth_tab = "Login"
                        st.rerun()
 
                    else:
                        st.error("Email already registered or database error.")
                        log_user_action("signup", email, role, success=False,
                                        message="Email exists / DB error")
 
                except ValueError as ve:
                    st.error(f"Registration failed: {ve}")
                except Exception as e:
                    st.error("Unexpected error occurred.")
                    log_user_action("signup", email, role, success=False, message=str(e))
 
    if st.session_state.get("authenticated"):
        user = st.session_state["user"]
        st.info(f"Logged in as **{user['name']} ({user['role']})**")
        if st.button("Logout"):
            log_user_action("logout", user["email"], user["role"], success=True)
            st.session_state.clear()
            st.success("You’ve been logged out.")
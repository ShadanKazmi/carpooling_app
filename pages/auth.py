import streamlit as st
from auth.auth_util import authenticate_user, save_user
from utils.setBackground import add_bg_from_local

from utils.logger import log_user_action
from auth.auth_util import authenticate_user, save_user

def show_auth_page():
    st.title("CarPoolConnect")
    st.subheader("Log in or sign up to start sharing rides")
 
    tab1, tab2 = st.tabs(["Login", "Register"])
 
    with tab1:
        st.markdown("### Existing User Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
 
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.success(f"Welcome back, {user['name']}!")
                log_user_action("login", email, user["role"], success=True)
                st.rerun()
            else:
                st.error("Invalid credentials or inactive account.")
 
    with tab2:
        st.markdown("### Create a New Account")
        name = st.text_input("Full Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        role = st.selectbox("I am a...", ["passenger", "driver"], key="register_role")
 
        if st.button("Register"):
            if not name or not email or not password:
                st.warning("Please fill out all fields.")
            else:
                try:
                    success = save_user(name, email, password, role)
                    if success:
                        st.success("Account created successfully! You can now log in.")
                        log_user_action("signup", email, role, success=True)

                    else:
                        st.error("Email already registered or an error occurred.")
                        log_user_action("signup", email, role, success=False, message="Email already exists or DB error")
                except ValueError as ve:
                    st.error(f"Registration failed: {ve}")
                    log_user_action("signup", email, role, success=False, message=str(ve))
 
    if st.session_state.get("authenticated"):
        user = st.session_state["user"]
        st.info(f"Logged in as **{user['name']} ({user['role']})**")
        if st.button("Logout"):
            st.session_state.clear()
            st.success("You’ve been logged out.")
            st.rerun()
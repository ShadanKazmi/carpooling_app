import streamlit as st
from auth.auth_util import authenticate_user, save_user
 
def show_auth_page():
    """Streamlit login/signup page using your auth utils."""
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
                st.rerun()
            else:
                st.error("Invalid credentials or inactive account.")
 
    with tab2:
        st.markdown("### Create a New Account")
        name = st.text_input("Full Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        role = st.selectbox("I am a...", ["passenger", "driver", "both"], key="register_role")
 
        if st.button("Register"):
            if not name or not email or not password:
                st.warning("Please fill out all fields.")
            else:
                success = save_user(name, email, password, role)
                if success:
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Email already registered or an error occurred.")
 
    if st.session_state.get("authenticated"):
        user = st.session_state["user"]
        st.info(f"Logged in as **{user['name']} ({user['role']})**")
 
        if st.button("Logout"):
            st.session_state.clear()
            st.success("You’ve been logged out.")
            st.rerun()
 
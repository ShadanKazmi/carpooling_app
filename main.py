import streamlit as st
from components.navbar import navbar
from views.home import show_home
from views.request import show as show_request
from views.offer import show as show_offer
from views.rides import show as show_rides
from views.profile import show as show_profile
from auth.auth_util import login_user, register_user

# ---- Initialize Database and Session State ----
from utils.setup_database import setup_database
from utils.db_connection import get_connection

# Setup database on startup
setup_database()

# Test database connection
conn = get_connection()
if not conn:
    st.error("⚠️ Database connection failed. Please check your MySQL server and credentials.")
    st.stop()
else:
    conn.close()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

# ---- Page Setup ----
st.set_page_config(
   page_title="CarPoolConnect",
   page_icon="🚗",
   layout="wide",
)

# ---- Authentication Check ----
def check_authentication():
    if not st.session_state.user:
        st.warning("Please login to access this feature")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Login"):
                    result = login_user(email, password)
                    if result["status"] == "success":
                        st.session_state.user = result["user"]
                        st.rerun()
                    else:
                        st.error(result["message"])
            with col2:
                if st.form_submit_button("Register"):
                    username = email.split("@")[0]  # Simple username generation
                    result = register_user(email, username, password)
                    if result["status"] == "success":
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result["message"])
        return False
    return True

# ---- Navbar ----
page = st.query_params.get("page", "Home")

# ---- Routing ----
if page == "Home":
    show_home()
elif page == "Request":
    if check_authentication():
        show_request()
elif page == "Offer":
    if check_authentication():
        show_offer()
elif page == "Rides":
    if check_authentication():
        show_rides()
elif page == "Profile":
    if check_authentication():
        show_profile()
else:
    st.error("❌ Page not found. Please check the URL.")
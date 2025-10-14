import streamlit as st
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
from logic import load_drivers, load_passengers

class ProfilePage:
    def __init__(self):
        self.username = st.session_state.get("username")
        self.role = st.session_state.get("role")
        self.user_data = None

    def require_login(self):
        if not self.username or not self.role:
            st.warning("Please log in first.")
            st.session_state.page = "login"
            st.rerun()
            return False
        return True

    def fetch_user(self):
        if self.role == "driver":
            users = load_drivers()
        else:
            users = load_passengers()
        self.user_data = next((u for u in users if u.get("username") == self.username), None)

    def render_header(self):
        st.header("👤 Profile")

    def render_user_details(self):
        u = self.user_data
        if not u:
            st.error(f"{self.role.capitalize()} profile not found.")
            return

        if self.role == "driver":
            st.subheader("Driver Details")
            st.write(f"**Name:** {u.get('name', '')}")
            st.write(f"**Age:** {u.get('age', '')}")
            st.write(f"**Gender:** {u.get('gender', '')}")
            st.write(f"**Contact:** {u.get('contact', '')}")
            st.write(f"**Vehicle No.:** {u.get('vehicle_no', '')}")
            st.write(f"**Driver ID:** {u.get('driver_id', '')}")
            st.write(f"**National ID:** {u.get('national_id', '')}")
        else:
            st.subheader("Passenger Details")
            st.write(f"**Name:** {u.get('name', '')}")
            st.write(f"**Age:** {u.get('age', '')}")
            st.write(f"**Gender:** {u.get('gender', '')}")
            st.write(f"**Contact:** {u.get('contact', '')}")
            st.write(f"**National ID:** {u.get('national_id', '')}")

    def nav_button(self):
        if st.button("Back to Dashboard"):
            if self.role == "driver":
                st.session_state.page = "driver_dashboard"
            else:
                st.session_state.page = "route_selection"
            st.rerun()

    def show(self):
        self.render_header()
        if not self.require_login():
            return
        self.fetch_user()
        self.render_user_details()
        self.nav_button()

def show():
    ProfilePage().show()
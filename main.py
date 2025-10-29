import streamlit as st
from pages.home import home
from pages.auth import show_auth_page

st.set_page_config(page_title="CarPoolConnect", page_icon="🚗", layout="wide")
 
if "authenticated" in st.session_state and st.session_state["authenticated"]:
    home()
else:
    show_auth_page()
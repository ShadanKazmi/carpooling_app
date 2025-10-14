import streamlit as st
from components.navbar import navbar
from pages.home import show_home

st.set_page_config(page_title="CarPoolConnect", page_icon="🚗", layout="wide")
 
navbar()

query_params = st.experimental_get_query_params()
page = query_params.get("page", ["Home"])[0]

if page == "Home":
    show_home()
elif page == "Request":
    st.write("🚘 Request a Ride Page Coming Soon")
elif page == "Offer":
    st.write("🚗 Offer a Ride Page Coming Soon")
elif page == "Rides":
    st.write("🕓 My Rides Page Coming Soon")
elif page == "Profile":
    st.write("👤 Profile Page Coming Soon")
else:
    st.error("Page not found.")
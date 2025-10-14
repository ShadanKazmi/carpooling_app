import streamlit as st
 
def show_home():
    st.title("Welcome to CarPoolConnect 🚗")
    st.write("Smart, sustainable, and affordable commuting. Join a community that shares rides and reduces traffic!")
 
    st.markdown("### 🌆 Popular Routes")
    cols = st.columns(3)
    routes = [("Delhi ↔ Noida", "2.3k daily rides"), ("Mumbai ↔ Pune", "1.8k daily rides"), ("Bangalore ↔ Mysuru", "1.2k daily rides")]
    for i, (route, stat) in enumerate(routes):
        with cols[i]:
            st.metric(route, stat)
 
    st.markdown("### 🧭 Get Started")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Offer a Ride"):
            st.switch_page("pages/offer_a_ride.py")
    with col2:
        if st.button("Request a Ride"):
            st.switch_page("pages/request_a_ride.py")
 
    st.info("Use the navigation bar above to explore other sections.")
import streamlit as st
from components.navbar import navbar

def show():
    navbar(active_page="Rides")
    st.title("🕓 My Rides")
    
    rides_tab1, rides_tab2 = st.tabs(["Upcoming Rides", "Past Rides"])
    
    with rides_tab1:
        st.subheader("Upcoming Rides")
        # Sample upcoming rides
        if st.session_state.user:
            upcoming_rides = [
                {
                    "from": "Mumbai",
                    "to": "Pune",
                    "date": "2025-10-30",
                    "time": "10:00 AM",
                    "status": "Confirmed",
                    "driver": "Amit Kumar",
                    "vehicle": "Swift Dzire"
                }
            ]
            for ride in upcoming_rides:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**{ride['from']} → {ride['to']}**")
                        st.caption(f"🗓️ {ride['date']} | ⏰ {ride['time']}")
                    with col2:
                        st.markdown(f"🚗 {ride['vehicle']}")
                        st.caption(f"👤 Driver: {ride['driver']}")
                    with col3:
                        st.markdown(f"**{ride['status']}**")
                        if ride['status'] == "Confirmed":
                            if st.button("Cancel", key=f"cancel_{ride['date']}"):
                                st.warning("Ride cancellation requested")
                st.divider()
        else:
            st.info("Please login to view your upcoming rides")
        
    with rides_tab2:
        st.subheader("Past Rides")
        if st.session_state.user:
            past_rides = [
                {
                    "from": "Pune",
                    "to": "Mumbai",
                    "date": "2025-10-20",
                    "driver": "Priya Singh",
                    "fare": "₹600",
                    "rating": 4.5
                }
            ]
            for ride in past_rides:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{ride['from']} → {ride['to']}**")
                        st.caption(f"🗓️ {ride['date']} | 👤 {ride['driver']}")
                        st.caption(f"💰 {ride['fare']} | ⭐ {ride['rating']}/5")
                    with col2:
                        if st.button("Rate", key=f"rate_{ride['date']}"):
                            st.info("Rating feature coming soon!")
                st.divider()
        else:
            st.info("Please login to view your ride history")
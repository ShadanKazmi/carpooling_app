import streamlit as st
from datetime import datetime
from utils.db_connection import get_connection
from utils.ride_utils import create_ride_request, fetch_route_cities, get_matched_ride_details
import pymysql
import time
from utils.setBackground import add_bg_from_local
 
def show():
    add_bg_from_local("assets/image.png")
 
    st.markdown("""
    
    <h1 class="main-title">🚖 Request a Ride</h1>
    <p class="subtitle">Find a comfortable and safe ride by sharing your trip details below.</p>
    """, unsafe_allow_html=True)
 
    from_cities, to_cities = fetch_route_cities()
    if not from_cities or not to_cities:
        st.warning("No routes available yet. Please import routes first.")
        return
 
    st.markdown('<p class="section-header">🗺️ Journey Details</p>', unsafe_allow_html=True)
 
    with st.form("ride_request_form"):
        col1, col2 = st.columns(2)
 
        with col1:
            from_city = st.selectbox("From", from_cities)
            date = st.date_input("Date", datetime.now().date())
 
        with col2:
            to_city = st.selectbox("To", to_cities)
            time_input = st.time_input("Time", datetime.now().time())
 
        passengers = st.slider("Passengers", 1, 6, 1)
 
        with st.expander("⚙️ Preferences", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                pref_family = st.checkbox("Family Friendly")
                pref_women = st.checkbox("Women Only")
 
            with col2:
                pref_non_smoke = st.checkbox("Non-Smoking")
                pref_child = st.checkbox("Child Seat")
 
            additional_notes = st.text_area(
                "Additional Notes (Optional)",
                placeholder="Any special requirements or preferences..."
            )
 
        submitted = st.form_submit_button("Find Rides")
 
        if submitted:
            if from_city and to_city and date and time_input:
                prefs = {
                    "family": pref_family,
                    "women": pref_women,
                    "non_smoke": pref_non_smoke,
                    "child": pref_child,
                    "notes": additional_notes,
                }
 
                user = st.session_state.get("user")
                if not user:
                    st.warning("Please log in to request a ride.")
                    st.stop()
 
                success = create_ride_request(
                    passenger_id=user["user_id"],
                    from_city=from_city,
                    to_city=to_city,
                    date_time=datetime.combine(date, time_input),
                    passengers_count=passengers,
                    preferences=prefs,
                )
 
                if success:
                    st.success("Ride request created successfully!")
                    with st.spinner("Searching for available drivers..."):
                        time.sleep(3)
                    st.info("You’ll be notified once a driver accepts your ride request.")
                    st.markdown("---")
                else:
                    st.error("Could not create ride request. Try again.")
            else:
                st.error("Please fill in all required fields.")
 
    user = st.session_state.get("user")
    if user:
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT request_id, status FROM ride_requests WHERE passenger_id=%s ORDER BY created_at DESC LIMIT 1",
            (user["user_id"],)
        )
        req = cursor.fetchone()
        cursor.close()
        conn.close()
 
        if req and req["status"] == "matched":
            matched = get_matched_ride_details(req["request_id"])
            if matched:
                st.markdown('<p class="section-header">Ride Confirmed!</p>', unsafe_allow_html=True)
                with st.container():
                    st.markdown(
                        f"""
                        <div class="matched-card">
                        <b>Driver:</b> {matched['driver_name']}<br>
                        <b>Rating:</b> {matched['avg_rating']} ({matched['total_rides']} rides)<br>
                        <b>Vehicle:</b> {matched['vehicle_no']}<br>
                        <b>Fare:</b> ₹{matched['estimated_fare']}<br>
                        <b>Seats Reserved:</b> {matched['available_seats']}<br>
                        <b>Departure:</b> {matched['date_time']}<br>
                        <b>Route:</b> {matched['from_city']} → {matched['to_city']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("Your ride has been matched! Details will appear soon.")
 
if __name__ == "__main__":
    show()
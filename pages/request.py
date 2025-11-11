import streamlit as st
from datetime import datetime
import time
import pymysql
from utils.db_connection import get_connection
from utils.ride_utils import create_ride_request, fetch_route_cities, get_matched_ride_details
from streamlit_autorefresh import st_autorefresh
 
def show():
    st.title("🚖 Request a Ride")
    st.write("Share your travel details to get matched with a driver.")
 
    st_autorefresh(interval=5000, key="live_match_poll")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in first.")
        return
 
    # Fetch city list
    from_cities, to_cities = fetch_route_cities()
    if not from_cities or not to_cities:
        st.warning("No routes found in the system. Please import route data first.")
        return
 
    st.subheader("🗺️ Journey Details")
 
    # Ride Request Form
    with st.form("ride_request_form"):
        col1, col2 = st.columns(2)
        with col1:
            from_city = st.selectbox("From", from_cities)
            date = st.date_input("Date", datetime.now().date())
        with col2:
            to_city = st.selectbox("To", to_cities)
            time_input = st.time_input("Time", datetime.now().time())
 
        passengers = st.slider("Passengers", 1, 6, 1)
 
        with st.expander("Preferences (Optional)"):
            pref_family = st.checkbox("Family Friendly")
            pref_women = st.checkbox("Women Only")
            pref_non_smoke = st.checkbox("Non-Smoking")
            pref_child = st.checkbox("Child Seat")
            additional_notes = st.text_area("Additional Notes")
 
        submitted = st.form_submit_button("Request Ride")
 
    if submitted:
        preferences = {
            "family": pref_family,
            "women": pref_women,
            "non_smoke": pref_non_smoke,
            "child": pref_child,
            "notes": additional_notes,
        }
 
        success = create_ride_request(
            passenger_id=user["user_id"],
            from_city=from_city,
            to_city=to_city,
            date_time=datetime.combine(date, time_input),
            passengers_count=passengers,
            preferences=preferences,
        )
 
        if success:
            st.success("✅ Ride request submitted! Waiting for a driver match...")
            st.info("This page updates automatically.")
            st.rerun()
        else:
            st.error("Failed to create request. Try again.")
 
    # 🔍 Live Match Check
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT request_id, status
        FROM ride_requests
        WHERE passenger_id=%s
        ORDER BY created_at DESC LIMIT 1
    """, (user["user_id"],))
    req = cursor.fetchone()
    cursor.close()
    conn.close()
 
    if req and req["status"] == "matched":
        matched = get_matched_ride_details(req["request_id"])
        if matched:
            st.success("🎉 Your ride has been matched!")
            st.markdown(f"""
                <div style="background:black;color:white;padding:16px;border-radius:10px;">
                <b>Driver:</b> {matched['driver_name']}<br>
                <b>⭐ Rating:</b> {matched['avg_rating']} ({matched['total_rides']} rides)<br>
                <b>Vehicle:</b> {matched['vehicle_no']}<br>
                <b>Fare:</b> ₹{matched['estimated_fare']}<br>
                <b>Seats Reserved:</b> {matched['available_seats']}<br>
                <b>Departure:</b> {matched['date_time']}<br>
                <b>Route:</b> {matched['from_city']} → {matched['to_city']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Driver matched — loading details...")
 
if __name__ == "__main__":
    show()
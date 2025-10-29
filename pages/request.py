import streamlit as st
from datetime import datetime
from components.navbar import navbar
from utils.db_connection import get_connection
from utils.ride_utils import create_ride_request
import pymysql
import time
 
 
def fetch_route_cities():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT DISTINCT from_city FROM routes ORDER BY from_city ASC;")
        from_cities = [row["from_city"] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT to_city FROM routes ORDER BY to_city ASC;")
        to_cities = [row["to_city"] for row in cursor.fetchall()]
        return from_cities, to_cities
    except Exception as e:
        st.error(f"Error fetching routes: {e}")
        return [], []
    finally:
        cursor.close()
        conn.close()
 
 
def get_matched_ride_details(request_id):
    """Fetch details of a matched ride (driver, vehicle, fare, etc.)"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
        SELECT
            rr.request_id,
            rr.from_city, rr.to_city, rr.date_time,
            ro.offer_id, ro.vehicle_no, ro.price_per_km, ro.estimated_fare, ro.available_seats,
            u.name AS driver_name, d.avg_rating, d.total_rides
        FROM ride_requests rr
        JOIN ride_offers ro ON rr.request_id = ro.request_id
        JOIN drivers d ON ro.driver_id = d.driver_id
        JOIN users u ON d.user_id = u.user_id
        WHERE rr.request_id = %s;
        """
        cursor.execute(query, (request_id,))
        return cursor.fetchone()
    except Exception as e:
        print("❌ Error fetching matched ride details:", e)
        return None
    finally:
        cursor.close()
        conn.close()
 
 
def show():
    navbar()
    st.title("🚖 Request a Ride")
    st.write("Find a comfortable and safe ride by sharing your trip details below.")
 
    # --- Load routes dynamically ---
    from_cities, to_cities = fetch_route_cities()
    if not from_cities or not to_cities:
        st.warning("⚠️ No routes available yet. Please import routes first.")
        return
 
    # --- Ride request form ---
    with st.form("ride_request_form"):
        st.subheader("Enter Your Journey Details")
        col1, col2 = st.columns(2)
        with col1:
            from_city = st.selectbox("📍 From", from_cities)
            date = st.date_input("📅 Date", datetime.now().date())
        with col2:
            to_city = st.selectbox("🎯 To", to_cities)
            time_input = st.time_input("⏰ Time", datetime.now().time())
        passengers = st.slider("👥 Passengers", 1, 6, 1)
 
        with st.expander("⚙️ Preferences"):
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
 
        submitted = st.form_submit_button("🔍 Find Rides")
 
    # --- Handle form submission ---
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
                st.success("✅ Ride request created successfully!")
                with st.spinner("🚗 Searching for available drivers..."):
                    time.sleep(3)
                st.info("You’ll be notified once a driver accepts your ride request.")
                st.markdown("---")
            else:
                st.error("❌ Could not create ride request. Try again.")
        else:
            st.error("Please fill in all required fields.")
 
    # --- Check if user already has a matched ride ---
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
                st.success("🎉 A driver has accepted your ride request!")
                st.markdown(f"""
                    **👨‍✈️ Driver:** {matched['driver_name']}  
                    **⭐ Rating:** {matched['avg_rating']} ({matched['total_rides']} rides)  
                    **🚘 Vehicle:** {matched['vehicle_no']}  
                    **💰 Fare:** ₹{matched['estimated_fare']}  
                    **🪑 Seats Reserved:** {matched['available_seats']}  
                    **🕒 Departure:** {matched['date_time']}  
                    **📍 Route:** {matched['from_city']} → {matched['to_city']}
                """)
            else:
                st.info("Your ride has been matched! Details will appear soon.")
 
 
if __name__ == "__main__":
    show()
import streamlit as st
from datetime import datetime
import time
from components.navbar import navbar
from utils.ride_utils import create_ride_request, get_open_ride_offers
from utils.db_connection import get_connection
 
 
def fetch_route_cities():
    """Fetch distinct from_city and to_city from routes table."""
    conn = get_connection()
    cursor = conn.cursor()
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
        conn.close()
 
 
def show():
    navbar()
    st.title("Request a Ride")
    st.write("Find a comfortable and safe ride by sharing your trip details below.")
 
    from_cities, to_cities = fetch_route_cities()
    if not from_cities or not to_cities:
        st.warning("No routes available yet. Please import routes first.")
        return
 
    with st.form("ride_request_form"):
        st.subheader("Enter Your Journey Details")
 
        col1, col2 = st.columns(2)
        with col1:
            from_city = st.selectbox("From", from_cities)
            date = st.date_input("📅 Date", datetime.now().date())
        with col2:
            to_city = st.selectbox("To", to_cities)
            time_input = st.time_input("Time", datetime.now().time())
 
        passengers = st.slider("Passengers", 1, 6, 1)
 
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
 
        if st.form_submit_button("🔍 Request Ride"):
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
 
                    with st.spinner("Looking for nearby drivers..."):
                        time.sleep(2.5)
 
                    st.info(
                        "Your ride request has been submitted. "
                        "You’ll get a notification once a driver accepts your request."
                    )
 
                    offers = get_open_ride_offers()
                    nearby_matches = [
                        o for o in offers
                        if o["from_city"].lower() == from_city.lower()
                        or o["to_city"].lower() == to_city.lower()
                    ]
 
                    if nearby_matches:
                        st.write("Meanwhile, here are some open rides on similar routes:")
                        for match in nearby_matches[:3]:
                            with st.container():
                                st.markdown(
                                    f"**{match['from_city']} → {match['to_city']}**  \n"
                                    f"💰 ₹{match['price_per_km']}/km | 🪑 {match['available_seats']} seats"
                                )
                    else:
                        st.info(
                            "Currently, there are no open rides nearby. "
                            "Drivers will be notified of your request soon."
                        )
                else:
                    st.error("Could not create ride request. Try again.")
            else:
                st.error("Please fill in all required fields.")
 
 
if __name__ == "__main__":
    show()
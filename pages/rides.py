import streamlit as st
from components.navbar import navbar
from utils.ride_utils import (
    get_driver_id as _get_driver_id,
    get_passenger_id_by_user,
    get_rides_for_driver,
    get_rides_for_passenger,
    has_user_already_rated,
    save_rating_and_update_averages
)
 
def show():
    st.title("My Rides")
    st.write("Track your ride history, see upcoming trips, and rate completed rides.")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your rides.")
        st.stop()
 
    user_id = int(user["user_id"])
    role = str(user["role"]).lower()
 
    if role == "driver":
        driver_id = _get_driver_id(user_id)
        if not driver_id:
            st.warning("Driver profile not found. Please register as a driver.")
            st.stop()
        rides = get_rides_for_driver(driver_id)
        st.subheader("Rides You've Offered")
    else:
        passenger_id = get_passenger_id_by_user(user_id)
        if not passenger_id:
            st.warning("Passenger profile not found. Please register as a passenger.")
            st.stop()
        rides = get_rides_for_passenger(passenger_id)
        st.subheader("Your Ride Bookings")
 
    if not rides:
        st.info("You have no rides yet. Book or offer a ride to get started.")
        return
 
    for idx, ride in enumerate(rides):
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:black; color:white; border-radius:15px; padding:20px; margin-bottom:16px; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
                    <h4>{ride['from_city']} → {ride['to_city']}</h4>
                    <p><b>Date:</b> {ride['ride_date']}</p>
                    <p><b>Seats:</b> {ride['seats_booked']}</p>
                    <p><b>Fare:</b> ₹{ride['total_fare']}</p>
                    <p><b>Status:</b> {ride['status'].capitalize()}</p>
                    <p><b>Start:</b> {ride['start_time'] or 'Not started'} | <b>End:</b> {ride['end_time'] or 'Not ended'}</p>
                    <p><b>Vehicle:</b> {ride.get('vehicle_no', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
 
        if role == "driver":
            st.markdown(f"**Passenger:** {ride['passenger_name']}")
            rated_user_id = int(ride["passenger_user_id"])
        else:
            st.markdown(f"**Driver:** {ride['driver_name']}")
            rated_user_id = int(ride["driver_user_id"])
 
        if ride["status"] == "completed":
            already = has_user_already_rated(ride_id=int(ride["ride_id"]), rated_by_user_id=user_id)
 
            if not already:
                uniq = f"{ride['ride_id']}_{user_id}_{idx}"
                form_key = f"rate_form_{uniq}"
                rating_key = f"rating_{uniq}"
                feedback_key = f"feedback_{uniq}"
 
                with st.form(key=form_key, clear_on_submit=True):
                    st.markdown("**⭐ Rate this Ride**")
 
                    rating_value = st.radio(
                        "Your Rating",
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: "★" * x,
                        horizontal=True,
                        key=rating_key,
                    )
 
                    feedback_text = st.text_area(
                        "Feedback (optional)",
                        placeholder="How was your experience?",
                        key=feedback_key,
                    )
 
                    submitted = st.form_submit_button("Submit Rating")
 
                if submitted:
                    success = save_rating_and_update_averages(
                        ride_id=int(ride["ride_id"]),
                        rated_by_user_id=user_id,
                        rated_user_id=rated_user_id,
                        rating_value=int(rating_value),
                        feedback_text=feedback_text.strip() if feedback_text else None
                    )
 
                    if success:
                        st.success("Rating submitted!")
                        st.rerun()
                    else:
                        st.error("Could not save rating. Try again.")
 
        st.markdown("---")
 
 
if __name__ == "__main__":
    show()
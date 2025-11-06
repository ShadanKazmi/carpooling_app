import uuid
import streamlit as st
import pymysql
from components.navbar import navbar
from utils.db_connection import get_connection
from utils.ride_utils import get_driver_id as _get_driver_id, get_passenger_id_by_user, get_rides_for_driver, get_rides_for_passenger, has_user_already_rated, save_rating_and_update_averages  # keep your existing util
 

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
 
    for ride in rides:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color:black; color:white; border-radius:15px;
                    padding:20px; margin-bottom:16px; box-shadow:0 2px 6px rgba(0,0,0,0.2);
                ">
                    <h4 style="margin:0 0 8px 0;">{ride['from_city']} → {ride['to_city']}</h4>
                    <p style="margin:4px 0;">Date: {ride['ride_date']}</p>
                    <p style="margin:4px 0;">Seats: {ride['seats_booked']}</p>
                    <p style="margin:4px 0;">Fare: ₹{ride['total_fare']}</p>
                    <p style="margin:4px 0;">Status: <b>{ride['status'].capitalize()}</b></p>
                    <p style="margin:4px 0;">Start: {ride['start_time'] or 'Not started'} | End: {ride['end_time'] or 'Not ended'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
 
            if ride["status"] == "completed":
                # Who is the target of the rating?
                if role == "driver":
                    rated_user_id = int(ride["passenger_user_id"])
                    subject_label = f"Rate passenger"
                else:
                    rated_user_id = int(ride["driver_user_id"])
                    subject_label = f"Rate driver"
 
                already = has_user_already_rated(ride_id=int(ride["ride_id"]), rated_by_user_id=user_id)
 
                if not already:
                    key_prefix = f"{role}_ride_{ride['ride_id']}_by_{user_id}"
 
                    with st.form(key=f"rate_form_{key_prefix}", clear_on_submit=True):
                        st.markdown(f"**⭐ {subject_label} for ride #{ride['ride_id']}**")
 
                        rating_value = st.radio(
                            "Your rating",
                            options=[1, 2, 3, 4, 5],
                            format_func=lambda x: "★" * x,
                            horizontal=True,
                            key=f"rating_{key_prefix}",
                        )
 
                        feedback_text = st.text_area(
                            "Feedback (optional)",
                            placeholder="How was your experience?",
                            key=f"feedback_{key_prefix}",
                        )
 
                        submitted = st.form_submit_button(f"Submit rating")
                        if submitted:
                            ok = save_rating_and_update_averages(
                                ride_id=int(ride["ride_id"]),
                                rated_by_user_id=user_id,
                                rated_user_id=rated_user_id,
                                rating_value=int(rating_value),
                                feedback_text=feedback_text.strip() if feedback_text else None,
                            )
                            if ok:
                                st.success("Rating submitted!")
                                st.rerun()
                            else:
                                st.error("Could not save rating. Please try again.")
 
        st.markdown("---")
 
 
if __name__ == "__main__":
    show()
import streamlit as st
from components.navbar import navbar
from utils.db_connection import get_connection
import pymysql
 
def show():
    navbar()
    st.title("My Rides")
    st.write("Track your ride history, see upcoming trips, and manage your bookings.")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your rides.")
        st.stop()
 
    user_id = user["user_id"]
    role = user["role"]
 
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
 
    if role == "driver":
        query = """
            SELECT
                r.ride_id, r.status, r.seats_booked, r.total_fare,
                r.start_time, r.end_time,
                rr.from_city, rr.to_city, rr.date_time AS ride_date,
                u.name AS passenger_name
            FROM rides r
            JOIN ride_requests rr ON r.offer_id = rr.request_id
            JOIN users u ON rr.passenger_id = u.user_id
            WHERE r.driver_id = %s
            ORDER BY r.start_time DESC;
        """
        cursor.execute(query, (user_id,))
        rides = cursor.fetchall()
        st.subheader("🧭 Rides You've Offered")
    
    else:
        query = """
            SELECT r.ride_id, r.status, r.seats_booked, r.total_fare,
                   r.start_time, r.end_time, rr.from_city, rr.to_city,
                   rr.date_time AS ride_date, u.name AS driver_name
            FROM rides r
            JOIN ride_requests rr ON r.passenger_id = rr.passenger_id
            JOIN users u ON r.driver_id = u.user_id
            WHERE r.passenger_id = %s
            ORDER BY r.start_time DESC;
        """
        cursor.execute(query, (user_id,))
        rides = cursor.fetchall()
        st.subheader("Your Ride Bookings")
 
    cursor.close()
    conn.close()
 
    if not rides:
        st.info("You have no rides yet. Book or offer a ride to get started.")
        return
 
    for ride in rides:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color:black;
                    border-radius:15px;
                    padding:20px;
                    margin-bottom:20px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                    transition:transform 0.2s ease-in-out;
                " onmouseover="this.style.transform='scale(1.01)'"
                  onmouseout="this.style.transform='scale(1)'">
                    <h4 style="margin-bottom:5px;">{ride['from_city']} → {ride['to_city']}</h4>
                    <p style="margin:5px 0;"> Date: {ride['ride_date']}</p>
                    <p style="margin:5px 0;"> Seats: {ride['seats_booked']}</p>
                    <p style="margin:5px 0;">Fare: ₹{ride['total_fare']}</p>
                    <p style="margin:5px 0;">Status: <b>{ride['status'].capitalize()}</b></p>
                    <hr style="border:0;border-top:1px solid #ddd;">
                    <p style="margin:5px 0;">
                    </p>
                    <p style="color:#666;margin-top:10px;font-size:0.9em;">
                        Start: {ride['start_time'] or 'Not started'} |
                        End: {ride['end_time'] or 'Not ended'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
 
    st.markdown("---")
 
if __name__ == "__main__":
    show()
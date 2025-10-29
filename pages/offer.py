import streamlit as st
import pymysql
from datetime import datetime
from components.navbar import navbar
from utils.db_connection import get_connection
from utils.ride_utils import (
    create_ride_offer,
    get_open_ride_requests,
    get_driver_id,
)
 

def fetch_routes():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT route_id, from_city, to_city, distance_km FROM routes ORDER BY from_city ASC;")
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching routes: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
 
def accept_ride_request(driver_id, request_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM ride_requests WHERE request_id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            st.error("Ride request not found.")
            return False
 
        cursor.execute(
            "SELECT route_id, distance_km FROM routes WHERE from_city = %s AND to_city = %s",
            (req["from_city"], req["to_city"]),
        )
        route = cursor.fetchone()
        if not route:
            st.error("No matching route found for this request.")
            return False
 
        distance_km = route["distance_km"]
        price_per_km = 10.0
        estimated_fare = round(distance_km * price_per_km, 2)
 
        cursor.execute(
            """
            INSERT INTO ride_offers
            (driver_id, vehicle_no, route_id, request_id, available_seats, price_per_km, estimated_fare, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'booked', NOW())
            """,
            (
                driver_id,
                f"DRV{driver_id}-REQ{request_id}",
                route["route_id"],
                request_id,
                req["passengers_count"],
                price_per_km,
                estimated_fare,
            ),
        )
 
        offer_id = cursor.lastrowid
 
        cursor.execute(
            """
            INSERT INTO rides (offer_id, passenger_id, driver_id, seats_booked, total_fare, start_time, status)
            VALUES (%s, %s, %s, %s, %s, NOW(), 'booked')
            """,
            (
                offer_id,
                req["passenger_id"],
                driver_id,
                req["passengers_count"],
                estimated_fare,
            ),
        )
 
        cursor.execute(
            "UPDATE ride_requests SET status = 'matched' WHERE request_id = %s",
            (request_id,),
        )
 
        conn.commit()
        return True
 
    except Exception as e:
        conn.rollback()
        st.error(f"Error accepting ride request: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
 

def show():
    navbar()
    st.title("Offer a Ride")
    st.write("Drivers can create ride offers and view passenger ride requests here.")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to create or view ride offers.")
        st.stop()
 
    driver_id = get_driver_id(user["user_id"])
    if not driver_id:
        st.warning("Driver profile not found. Please register as a driver.")
        st.stop()
 
    st.header("Passenger Ride Requests")
 
    requests = get_open_ride_requests()
    if requests:
        for req in requests:
            with st.expander(f"Ride Request #{req['request_id']} — {req['from_city']} → {req['to_city']}"):
                st.markdown(f"**From:** {req['from_city']}")
                st.markdown(f"**To:** {req['to_city']}")
                st.markdown(f"**Date & Time:** {req['date_time']}")
                st.markdown(f"**Passengers:** {req['passengers_count']}")
                st.markdown(f"**Preferences:** {req['preferences']}")
                st.markdown(f"**Status:** {req['status']}")
 
                if st.button(f"Accept Request #{req['request_id']}", key=f"accept_{req['request_id']}"):
                    success = accept_ride_request(driver_id, req["request_id"])
                    if success:
                        st.success("Ride request accepted! Passenger will be notified.")
                    else:
                        st.error("Failed to accept ride request.")
    else:
        st.info("No pending ride requests right now.")
 
    st.markdown("---")
 
    st.header("Create a Ride Offer")
 
    routes = fetch_routes()
    if not routes:
        st.warning("No routes available. Please add some routes first.")
        st.stop()
 
    with st.form("ride_offer_form"):
        st.subheader("Enter Ride Details")
        route_options = [f"{r['from_city']} → {r['to_city']} ({r['distance_km']} km)" for r in routes]
        route_choice = st.selectbox("Route", route_options)
        vehicle_no = st.text_input("Vehicle Number", placeholder="e.g. MH12AB1234")
        available_seats = st.slider("Available Seats", 1, 6, 3)
        price_per_km = st.number_input("Price per KM (₹)", min_value=1.0, value=5.0, step=0.5)
        submitted = st.form_submit_button("Create Ride Offer")
 
        if submitted:
            selected_route = routes[route_options.index(route_choice)]
            route_id = selected_route["route_id"]
            distance_km = selected_route["distance_km"]
            estimated_fare = distance_km * price_per_km
 
            success = create_ride_offer(
                driver_id=driver_id,
                vehicle_no=vehicle_no,
                route_id=route_id,
                available_seats=available_seats,
                price_per_km=price_per_km,
                estimated_fare=estimated_fare,
            )
 
            if success:
                st.success("Ride offer created successfully!")
            else:
                st.error("Failed to create ride offer. Please try again later.")
 
 
if __name__ == "__main__":
    show()
import streamlit as st
from datetime import datetime
from components.navbar import navbar
from utils.db_connection import get_connection
from utils.ride_utils import (
    create_ride_offer,
    get_open_ride_requests,
    get_driver_id,
)
import pymysql

 
def fetch_routes():
    """Fetch all available routes from the database."""
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
 
 
def show():
    navbar()
    st.title("Offer a Ride")
    st.write("Drivers can create ride offers and view passenger ride requests here.")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to create or view ride offers.")
        st.stop()
 
    st.header("📋 Passenger Ride Requests")
    requests = get_open_ride_requests()
 
    if requests:
        for req in requests:
            with st.expander(f"Ride Request #{req['request_id']} - {req['from_city']} → {req['to_city']}"):
                st.markdown(f"**From:** {req['from_city']}")
                st.markdown(f"**To:** {req['to_city']}")
                st.markdown(f"**Date & Time:** {req['date_time']}")
                st.markdown(f"**Passengers:** {req['passengers_count']}")
                st.markdown(f"**Preferences:** {req['preferences']}")
                st.markdown(f"**Status:** {req['status']}")
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
 
            driver_id = get_driver_id(user["user_id"])
            if not driver_id:
                st.error("Driver profile not found. Please register as a driver.")
                st.stop()
 
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
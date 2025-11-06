import streamlit as st
import pymysql
from datetime import datetime
from components.navbar import navbar
from utils.db_connection import get_connection
from utils.ride_utils import (
    accept_ride_request,
    create_ride_offer,
    fetch_routes,
    get_driver_assigned_rides,
    get_open_ride_requests,
    get_driver_id,
    update_ride_status,
)
from utils.setBackground import add_bg_from_local
 
 
def show():
    add_bg_from_local("assets/image.png")
 
    st.title("Offer a Ride")
    st.write("Drivers can create ride offers and accept passenger requests here.")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to create or manage ride offers.")
        st.stop()
 
    driver_id = get_driver_id(user["user_id"])
    if not driver_id:
        st.warning("Driver profile not found. Please register as a driver.")
        st.stop()
 
    st.header("Passenger Ride Requests")
    requests = get_open_ride_requests()
    if requests:
        for req in requests:
            with st.expander(f"Request #{req['request_id']} — {req['from_city']} → {req['to_city']}"):
                st.markdown(f"**From:** {req['from_city']}")
                st.markdown(f"**To:** {req['to_city']}")
                st.markdown(f"**Date & Time:** {req['date_time']}")
                st.markdown(f"**Passengers:** {req['passengers_count']}")
                st.markdown(f"**Preferences:** {req['preferences']}")
                st.markdown(f"**Status:** {req['status']}")
 
                if st.button(f"Accept Request #{req['request_id']}", key=f"accept_{req['request_id']}"):
                    success = accept_ride_request(driver_id, req["request_id"])
                    if success:
                        st.success("Ride request accepted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to accept ride request.")
    else:
        st.info("No active ride requests available right now.")
 
    st.markdown("---")
 
    st.header("Create a Ride Offer")
    routes = fetch_routes()
    if not routes:
        st.warning("No routes available. Please add routes first.")
        st.stop()
 
    with st.form("ride_offer_form"):
        st.subheader("Enter Ride Details")
        route_options = [f"{r['from_city']} → {r['to_city']} ({r['distance_km']} km)" for r in routes]
        route_choice = st.selectbox("Select Route", route_options)
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
                st.error("Failed to create ride offer. Try again later.")
 
    st.markdown("---")
 
    st.header("Your Assigned Rides")
    assigned_rides = get_driver_assigned_rides(driver_id)
    if not assigned_rides:
        st.info("No rides assigned yet.")
        return
 
    for ride in assigned_rides:
        with st.expander(f"Ride #{ride['ride_id']} — {ride['from_city']} → {ride['to_city']} ({ride['status']})"):
            st.markdown(f"**Passenger:** {ride['passenger_name']}")
            st.markdown(f"**From:** {ride['from_city']}")
            st.markdown(f"**To:** {ride['to_city']}")
            st.markdown(f"**Status:** {ride['status'].capitalize()}")
 
            col1, col2, col3 = st.columns(3)
            if ride["status"] == "booked":
                if col1.button("Start Ride", key=f"start_{ride['ride_id']}"):
                    if update_ride_status(ride["ride_id"], "active"):
                        st.success("Ride started successfully!")
                        st.rerun()
            elif ride["status"] == "active":
                if col2.button("Complete Ride", key=f"complete_{ride['ride_id']}"):
                    if update_ride_status(ride["ride_id"], "completed"):
                        st.success("Ride completed successfully!")
                        st.rerun()
            if col3.button("Cancel Ride", key=f"cancel_{ride['ride_id']}"):
                if update_ride_status(ride["ride_id"], "cancelled"):
                    st.warning("Ride cancelled.")
                    st.rerun()
 
 
if __name__ == "__main__":
    show()
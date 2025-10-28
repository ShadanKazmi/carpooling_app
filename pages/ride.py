"""
Ride Page - Active Ride Details & Completion
Path: pages/ride_page.py
Shows ride details after acceptance, role-based actions, and rating system
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
sys.path.append('..')
from utils.db_connection import get_db_connection
from model.rides import get_active_ride, update_ride_status, get_ride_details
from model.ratings import submit_rating, get_ride_rating

# ============================================
# STREAMLIT CONFIG
# ============================================
st.set_page_config(page_title="Ride Details", layout="wide", initial_sidebar_state="collapsed")

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'ride_id' not in st.session_state:
    st.session_state.ride_id = 101  # Default for demo

# ============================================
# FETCH RIDE DATA FROM DATABASE
# ============================================
@st.cache_data(ttl=10)
def fetch_ride_details(ride_id):
    """Fetch ride details from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            r.ride_id, r.status, r.seats_booked, r.total_fare,
            r.start_time, r.end_time,
            rr.from_city, rr.to_city, rt.distance_km,
            p.name as passenger_name, p.email as passenger_email,
            d.name as driver_name, d.email as driver_email, d.avg_rating as driver_rating,
            v.vehicle_name, v.plate_number, v.capacity
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN ride_requests rr ON ro.request_id = rr.request_id
        JOIN routes rt ON ro.route_id = rt.route_id
        JOIN passengers p ON r.passenger_id = p.passenger_id
        JOIN drivers d ON r.driver_id = d.driver_id
        JOIN vehicles v ON ro.vehicle_id = v.vehicle_id
        WHERE r.ride_id = %s
        """
        
        cursor.execute(query, (ride_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "ride_id": result[0],
                "status": result[1],
                "seats_booked": result[2],
                "total_fare": result[3],
                "start_time": result[4],
                "end_time": result[5],
                "from_city": result[6],
                "to_city": result[7],
                "distance_km": result[8],
                "passenger_name": result[9],
                "passenger_email": result[10],
                "driver_name": result[11],
                "driver_email": result[12],
                "driver_rating": result[13],
                "vehicle_name": result[14],
                "plate_number": result[15],
                "vehicle_capacity": result[16]
            }
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# ============================================
# PAGE TITLE
# ============================================
st.title("🚗 Active Ride Details")

# ============================================
# ROLE SELECTION (for demo)
# ============================================
col_role1, col_role2, col_role3 = st.columns(3)
with col_role1:
    if st.button("👤 View as Passenger"):
        st.session_state.user_role = "Passenger"
with col_role2:
    if st.button("🚖 View as Driver"):
        st.session_state.user_role = "Driver"
with col_role3:
    if st.button("🛠 View as Admin"):
        st.session_state.user_role = "Admin"

st.divider()

# Fetch ride data
ride_data = fetch_ride_details(st.session_state.ride_id)

if not ride_data:
    st.error("Ride not found!")
    st.stop()

# ============================================
# RIDE INFORMATION CARDS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Route Information")
    st.metric("From City", ride_data['from_city'])
    st.metric("To City", ride_data['to_city'])
    st.metric("Distance", f"{ride_data['distance_km']} km")
    st.metric("Total Fare", f"₹{ride_data['total_fare']}")
    st.metric("Status", ride_data['status'].upper())

with col2:
    st.subheader("👥 Participant Details")
    st.write(f"**Passenger:** {ride_data['passenger_name']}")
    st.write(f"**Driver:** {ride_data['driver_name']}")
    st.write(f"**Vehicle:** {ride_data['vehicle_name']} ({ride_data['plate_number']})")
    st.write(f"**Seats Booked:** {ride_data['seats_booked']} / {ride_data['vehicle_capacity']}")
    st.write(f"**Driver Rating:** ⭐ {ride_data['driver_rating']}/5.0")

st.divider()

# ============================================
# ROLE-BASED ACTIONS
# ============================================
if st.session_state.user_role == "Passenger":
    st.subheader("✏️ Passenger Actions")
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📞 Contact Driver", use_container_width=True, key="contact_driver"):
            st.info(f"📞 Driver Contact: {ride_data['driver_email']}")
    
    with col_action2:
        if st.button("⏱️ Cancel Ride", use_container_width=True, key="cancel_ride"):
            if update_ride_status(ride_data['ride_id'], 'cancelled'):
                st.warning("❌ Ride has been cancelled")
                st.cache_data.clear()
            else:
                st.error("Failed to cancel ride")
    
    with col_action3:
        if ride_data['status'] == 'completed':
            if st.button("✅ Mark Complete", use_container_width=True, key="mark_complete_passenger"):
                st.success("✅ Ride marked as completed!")

elif st.session_state.user_role == "Driver":
    st.subheader("✏️ Driver Actions")
    col_action1, col_action2 = st.columns(2)
    
    with col_action1:
        if ride_data['status'] == 'active':
            if st.button("🚗 Start Ride", use_container_width=True, key="start_ride"):
                if update_ride_status(ride_data['ride_id'], 'started'):
                    st.info("🚗 Ride has started!")
                    st.cache_data.clear()
    
    with col_action2:
        if ride_data['status'] in ['active', 'started']:
            if st.button("🏁 End Ride", use_container_width=True, key="end_ride"):
                if update_ride_status(ride_data['ride_id'], 'completed'):
                    st.success("🏁 Ride completed successfully!")
                    st.cache_data.clear()

elif st.session_state.user_role == "Admin":
    st.subheader("🛠️ Admin Controls")
    st.warning("⚠️ Admin can monitor and manage rides")
    
    col_admin1, col_admin2 = st.columns(2)
    with col_admin1:
        if st.button("👁️ View Details", use_container_width=True):
            st.json(ride_data)
    
    with col_admin2:
        if st.button("🛑 Force End Ride", use_container_width=True):
            if update_ride_status(ride_data['ride_id'], 'ended'):
                st.error("🛑 Ride forcefully ended by admin")
                st.cache_data.clear()

st.divider()

# ============================================
# RATING SECTION (After Completion)
# ============================================
if ride_data['status'] == 'completed':
    st.subheader("⭐ Rate Your Ride Experience")
    
    col_rating1, col_rating2 = st.columns([1, 2])
    
    with col_rating1:
        rating_value = st.slider("Select Rating", 0.0, 5.0, 4.0, 0.5)
    
    with col_rating2:
        feedback_text = st.text_area("Share Your Feedback", placeholder="Tell us about your experience...", height=100)
    
    if st.button("📤 Submit Rating", use_container_width=True):
        if submit_rating(
            ride_id=ride_data['ride_id'],
            rated_by=st.session_state.user_id or 1,
            rated_user=ride_data['driver_id'] if st.session_state.user_role == "Passenger" else ride_data['passenger_id'],
            rating=rating_value,
            feedback=feedback_text
        ):
            st.success(f"✅ Thank you for your {rating_value}⭐ rating!")
        else:
            st.error("Failed to submit rating")
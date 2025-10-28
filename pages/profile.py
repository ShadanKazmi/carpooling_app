"""
Profile Page - User Profile & Ride History
Path: pages/profile_page.py
Displays past rides, statistics, and ride history for Passenger, Driver, and Admin
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from utils.db_connection import get_db_connection
from model.passengers import get_passenger_details, get_passenger_rides
from model.drivers import get_driver_details, get_driver_rides

# ============================================
# STREAMLIT CONFIG
# ============================================
st.set_page_config(page_title="Profile & History", layout="wide")

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1  # Default for demo
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# ============================================
# FETCH PASSENGER RIDES FROM DATABASE
# ============================================
@st.cache_data(ttl=30)
def fetch_passenger_history(passenger_id):
    """Fetch all rides for a passenger"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            r.ride_id, rr.from_city, rr.to_city, r.start_time, r.status, r.total_fare,
            d.name as driver_name, d.avg_rating, rt.distance_km
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN ride_requests rr ON ro.request_id = rr.request_id
        JOIN routes rt ON ro.route_id = rt.route_id
        JOIN drivers d ON r.driver_id = d.driver_id
        WHERE r.passenger_id = %s
        ORDER BY r.start_time DESC
        """
        
        cursor.execute(query, (passenger_id,))
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return pd.DataFrame(results, columns=[
                'Ride ID', 'From', 'To', 'Date', 'Status', 'Fare',
                'Driver', 'Driver Rating', 'Distance (km)'
            ])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

# ============================================
# FETCH DRIVER RIDES FROM DATABASE
# ============================================
@st.cache_data(ttl=30)
def fetch_driver_history(driver_id):
    """Fetch all rides for a driver"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            r.ride_id, rr.from_city, rr.to_city, r.start_time, r.status, r.total_fare,
            p.name as passenger_name, r.seats_booked, rt.distance_km
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN ride_requests rr ON ro.request_id = rr.request_id
        JOIN routes rt ON ro.route_id = rt.route_id
        JOIN passengers p ON r.passenger_id = p.passenger_id
        WHERE r.driver_id = %s
        ORDER BY r.start_time DESC
        """
        
        cursor.execute(query, (driver_id,))
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return pd.DataFrame(results, columns=[
                'Ride ID', 'From', 'To', 'Date', 'Status', 'Fare',
                'Passenger', 'Seats Booked', 'Distance (km)'
            ])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

# ============================================
# FETCH USER PROFILE DETAILS
# ============================================
@st.cache_data(ttl=30)
def fetch_profile_details(user_id, role):
    """Fetch user profile information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if role == "Passenger":
            query = """
            SELECT name, email, avg_rating, total_rides, created_at, is_active
            FROM passengers WHERE passenger_id = %s
            """
        else:  # Driver
            query = """
            SELECT name, email, avg_rating, total_rides, created_at, is_active
            FROM drivers WHERE driver_id = %s
            """
        
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "name": result[0],
                "email": result[1],
                "avg_rating": result[2],
                "total_rides": result[3],
                "created_at": result[4],
                "is_active": result[5]
            }
    except Exception as e:
        st.error(f"Database Error: {e}")
    
    return None

# ============================================
# PAGE TITLE
# ============================================
st.title("👤 Profile & Ride History")

# ============================================
# ROLE SELECTION (for demo)
# ============================================
col_role1, col_role2, col_role3 = st.columns(3)
with col_role1:
    if st.button("👤 View as Passenger", key="role_passenger"):
        st.session_state.user_role = "Passenger"
        st.session_state.user_id = 1
with col_role2:
    if st.button("🚖 View as Driver", key="role_driver"):
        st.session_state.user_role = "Driver"
        st.session_state.user_id = 1
with col_role3:
    if st.button("🛠 View as Admin", key="role_admin"):
        st.session_state.user_role = "Admin"

st.divider()

# ============================================
# PASSENGER VIEW
# ============================================
if st.session_state.user_role == "Passenger":
    profile = fetch_profile_details(st.session_state.user_id, "Passenger")
    
    if profile:
        st.subheader(f"👤 {profile['name']}")
        
        # Profile Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Total Rides", profile['total_rides'])
        col2.metric("⭐ Average Rating", f"{profile['avg_rating']:.1f}/5.0")
        col3.metric("📧 Email", profile['email'])
        col4.metric("✅ Account Status", "Active" if profile['is_active'] else "Inactive")
        
        st.divider()
        
        # Ride History
        st.subheader("📅 Your Ride History")
        history_df = fetch_passenger_history(st.session_state.user_id)
        
        if not history_df.empty:
            # Filter Options
            with st.expander("🔍 Filter Rides"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    status_filter = st.multiselect("Filter by Status", 
                        ['completed', 'cancelled', 'active'], 
                        default=['completed'])
                with col_f2:
                    city_filter = st.text_input("Search City")
                
                filtered_df = history_df.copy()
                if status_filter:
                    filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
                if city_filter:
                    filtered_df = filtered_df[
                        (filtered_df['From'].str.contains(city_filter, case=False)) | 
                        (filtered_df['To'].str.contains(city_filter, case=False))
                    ]
                
                st.dataframe(filtered_df, use_container_width=True)
            
            # Display all rides
            st.write("**All Rides:**")
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No rides found!")

# ============================================
# DRIVER VIEW
# ============================================
elif st.session_state.user_role == "Driver":
    profile = fetch_profile_details(st.session_state.user_id, "Driver")
    
    if profile:
        st.subheader(f"🚖 {profile['name']}")
        
        # Profile Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🚗 Total Rides", profile['total_rides'])
        col2.metric("⭐ Average Rating", f"{profile['avg_rating']:.1f}/5.0")
        col3.metric("📧 Email", profile['email'])
        col4.metric("✅ Account Status", "Active" if profile['is_active'] else "Inactive")
        
        st.divider()
        
        # Driver Statistics
        st.subheader("📈 Performance Statistics")
        history_df = fetch_driver_history(st.session_state.user_id)
        
        if not history_df.empty:
            completed = len(history_df[history_df['Status'] == 'completed'])
            cancelled = len(history_df[history_df['Status'] == 'cancelled'])
            total_earnings = history_df['Fare'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Completed Rides", completed)
            col2.metric("❌ Cancelled Rides", cancelled)
            col3.metric("💰 Total Earnings", f"₹{total_earnings:,.0f}")
        
        st.divider()
        
        # Ride History
        st.subheader("📅 Your Ride History")
        
        if not history_df.empty:
            # Filter Options
            with st.expander("🔍 Filter Rides"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    status_filter = st.multiselect("Filter by Status", 
                        ['completed', 'cancelled', 'active'], 
                        default=['completed'],
                        key="driver_status")
                with col_f2:
                    city_filter = st.text_input("Search City", key="driver_city")
                
                filtered_df = history_df.copy()
                if status_filter:
                    filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
                if city_filter:
                    filtered_df = filtered_df[
                        (filtered_df['From'].str.contains(city_filter, case=False)) | 
                        (filtered_df['To'].str.contains(city_filter, case=False))
                    ]
                
                st.dataframe(filtered_df, use_container_width=True)
            
            # Display all rides
            st.write("**All Rides:**")
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No rides found!")

# ============================================
# ADMIN VIEW
# ============================================
elif st.session_state.user_role == "Admin":
    st.subheader("🛠️ Admin Dashboard - System Overview")
    
    # Admin Metrics
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM passengers WHERE is_active = TRUE")
        active_passengers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM drivers WHERE is_active = TRUE")
        active_drivers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM rides WHERE status = 'completed'")
        total_completed_rides = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_fare) FROM rides WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0] or 0
        
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Active Passengers", active_passengers)
        col2.metric("🚖 Active Drivers", active_drivers)
        col3.metric("✅ Completed Rides", total_completed_rides)
        col4.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
        
    except Exception as e:
        st.error(f"Error fetching admin metrics: {e}")
    
    st.divider()
    
    # Admin Controls
    st.subheader("📋 Admin Controls")
    
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["View All Rides", "View Users", "System Logs"])
    
    with admin_tab1:
        st.write("**All Rides in System**")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT r.ride_id, p.name, d.name, rr.from_city, rr.to_city, 
                   r.total_fare, r.status, r.start_time
            FROM rides r
            JOIN passengers p ON r.passenger_id = p.passenger_id
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            ORDER BY r.start_time DESC LIMIT 50
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            if results:
                admin_df = pd.DataFrame(results, columns=[
                    'Ride ID', 'Passenger', 'Driver', 'From', 'To', 'Fare', 'Status', 'Date'
                ])
                st.dataframe(admin_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error fetching rides: {e}")
    
    with admin_tab2:
        st.write("**All Users in System**")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Passengers
            st.write("*Passengers:*")
            cursor.execute("""
            SELECT passenger_id, name, email, avg_rating, total_rides, is_active
            FROM passengers LIMIT 20
            """)
            passengers_data = cursor.fetchall()
            if passengers_data:
                st.dataframe(pd.DataFrame(passengers_data, columns=[
                    'ID', 'Name', 'Email', 'Rating', 'Rides', 'Active'
                ]), use_container_width=True)
            
            # Drivers
            st.write("*Drivers:*")
            cursor.execute("""
            SELECT driver_id, name, email, avg_rating, total_rides, is_active
            FROM drivers LIMIT 20
            """)
            drivers_data = cursor.fetchall()
            if drivers_data:
                st.dataframe(pd.DataFrame(drivers_data, columns=[
                    'ID', 'Name', 'Email', 'Rating', 'Rides', 'Active'
                ]), use_container_width=True)
            
            conn.close()
        except Exception as e:
            st.error(f"Error fetching users: {e}")
    
    with admin_tab3:
        st.write("**System Activity Logs**")
        st.info("Activity logging system would be integrated here")
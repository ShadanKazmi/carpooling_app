import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ============================================
# STREAMLIT CONFIG
# ============================================
st.set_page_config(page_title="Profile & History", layout="wide")

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1
if 'user_role' not in st.session_state:
    st.session_state.user_role = "Passenger"

# ============================================
# STATIC DATASET - PASSENGERS
# ============================================
PASSENGERS_DATA = {
    1: {
        "passenger_id": 1,
        "name": "Vandani Singh",
        "email": "vandani@example.com",
        "avg_rating": 4.6,
        "total_rides": 12,
        "created_at": datetime.now() - timedelta(days=365),
        "is_active": True
    },
    2: {
        "passenger_id": 2,
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "avg_rating": 4.8,
        "total_rides": 28,
        "created_at": datetime.now() - timedelta(days=450),
        "is_active": True
    },
    3: {
        "passenger_id": 3,
        "name": "Ananya Gupta",
        "email": "ananya@example.com",
        "avg_rating": 4.7,
        "total_rides": 18,
        "created_at": datetime.now() - timedelta(days=200),
        "is_active": True
    },
    4: {
        "passenger_id": 4,
        "name": "Rohan Desai",
        "email": "rohan@example.com",
        "avg_rating": 4.5,
        "total_rides": 15,
        "created_at": datetime.now() - timedelta(days=300),
        "is_active": True
    }
}

# ============================================
# STATIC DATASET - DRIVERS
# ============================================
DRIVERS_DATA = {
    1: {
        "driver_id": 1,
        "name": "Rahul Mehta",
        "email": "rahul@example.com",
        "avg_rating": 4.7,
        "total_rides": 156,
        "created_at": datetime.now() - timedelta(days=730),
        "is_active": True,
        "vehicle": "Swift Dzire",
        "plate": "RJ14AB1234"
    },
    2: {
        "driver_id": 2,
        "name": "Amit Kumar",
        "email": "amit@example.com",
        "avg_rating": 4.5,
        "total_rides": 98,
        "created_at": datetime.now() - timedelta(days=600),
        "is_active": True,
        "vehicle": "Hyundai Creta",
        "plate": "DL01CD5678"
    },
    3: {
        "driver_id": 3,
        "name": "Vikram Singh",
        "email": "vikram@example.com",
        "avg_rating": 4.9,
        "total_rides": 203,
        "created_at": datetime.now() - timedelta(days=800),
        "is_active": True,
        "vehicle": "Toyota Innova",
        "plate": "KA01EF9012"
    },
    4: {
        "driver_id": 4,
        "name": "Suresh Patel",
        "email": "suresh@example.com",
        "avg_rating": 4.3,
        "total_rides": 87,
        "created_at": datetime.now() - timedelta(days=500),
        "is_active": True,
        "vehicle": "Maruti Ertiga",
        "plate": "MH02GH3456"
    }
}

# ============================================
# STATIC DATASET - RIDES
# ============================================
RIDES_DATA = {
    1: {
        "ride_id": 1,
        "passenger_id": 1,
        "driver_id": 1,
        "from_city": "Jaipur",
        "to_city": "Udaipur",
        "start_time": datetime.now() - timedelta(days=7),
        "status": "completed",
        "fare": 1250.00,
        "driver_name": "Rahul Mehta",
        "distance": 394
    },
    2: {
        "ride_id": 2,
        "passenger_id": 2,
        "driver_id": 2,
        "from_city": "Delhi",
        "to_city": "Agra",
        "start_time": datetime.now() - timedelta(days=1),
        "status": "completed",
        "fare": 2100.00,
        "driver_name": "Amit Kumar",
        "distance": 206
    },
    3: {
        "ride_id": 3,
        "passenger_id": 1,
        "driver_id": 3,
        "from_city": "Jaipur",
        "to_city": "Delhi",
        "start_time": datetime.now() - timedelta(days=14),
        "status": "completed",
        "fare": 1800.00,
        "driver_name": "Vikram Singh",
        "distance": 268
    },
    4: {
        "ride_id": 4,
        "passenger_id": 3,
        "driver_id": 1,
        "from_city": "Bangalore",
        "to_city": "Mysore",
        "start_time": datetime.now() - timedelta(days=3),
        "status": "completed",
        "fare": 850.00,
        "driver_name": "Rahul Mehta",
        "distance": 145
    },
    5: {
        "ride_id": 5,
        "passenger_id": 4,
        "driver_id": 4,
        "from_city": "Mumbai",
        "to_city": "Pune",
        "start_time": datetime.now() - timedelta(days=21),
        "status": "completed",
        "fare": 650.00,
        "driver_name": "Suresh Patel",
        "distance": 180
    },
    6: {
        "ride_id": 6,
        "passenger_id": 2,
        "driver_id": 3,
        "from_city": "Bangalore",
        "to_city": "Coorg",
        "start_time": datetime.now() - timedelta(days=5),
        "status": "completed",
        "fare": 1200.00,
        "driver_name": "Vikram Singh",
        "distance": 254
    },
    7: {
        "ride_id": 7,
        "passenger_id": 1,
        "driver_id": 2,
        "from_city": "Delhi",
        "to_city": "Chandigarh",
        "start_time": datetime.now() - timedelta(days=30),
        "status": "cancelled",
        "fare": 950.00,
        "driver_name": "Amit Kumar",
        "distance": 244
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_passenger_rides(passenger_id):
    """Get all rides for a passenger"""
    rides = [ride for ride in RIDES_DATA.values() if ride['passenger_id'] == passenger_id]
    return sorted(rides, key=lambda x: x['start_time'], reverse=True)

def get_driver_rides(driver_id):
    """Get all rides for a driver"""
    rides = [ride for ride in RIDES_DATA.values() if ride['driver_id'] == driver_id]
    return sorted(rides, key=lambda x: x['start_time'], reverse=True)

def get_passenger_statistics(passenger_id):
    """Calculate statistics for a passenger"""
    rides = get_passenger_rides(passenger_id)
    completed = [r for r in rides if r['status'] == 'completed']
    cancelled = [r for r in rides if r['status'] == 'cancelled']
    
    return {
        'total_rides': len(rides),
        'completed_rides': len(completed),
        'cancelled_rides': len(cancelled),
        'total_spent': sum(r['fare'] for r in completed),
        'average_distance': sum(r['distance'] for r in rides) / len(rides) if rides else 0
    }

def get_driver_statistics(driver_id):
    """Calculate statistics for a driver"""
    rides = get_driver_rides(driver_id)
    completed = [r for r in rides if r['status'] == 'completed']
    
    return {
        'total_rides': len(rides),
        'completed_rides': len(completed),
        'cancelled_rides': len([r for r in rides if r['status'] == 'cancelled']),
        'total_earnings': sum(r['fare'] for r in completed),
        'average_distance': sum(r['distance'] for r in rides) / len(rides) if rides else 0,
        'total_distance': sum(r['distance'] for r in rides)
    }

# ============================================
# PAGE TITLE
# ============================================
st.title("👤 Profile & Ride History")

# ============================================
# ROLE SELECTION
# ============================================
col_role1, col_role2, col_role3 = st.columns(3)
with col_role1:
    if st.button("👤 View as Passenger", key="role_passenger"):
        st.session_state.user_role = "Passenger"
        st.session_state.user_id = 1
        st.rerun()
with col_role2:
    if st.button("🚖 View as Driver", key="role_driver"):
        st.session_state.user_role = "Driver"
        st.session_state.user_id = 1
        st.rerun()
with col_role3:
    if st.button("🛠 View as Admin", key="role_admin"):
        st.session_state.user_role = "Admin"
        st.rerun()

st.divider()

# ============================================
# PASSENGER VIEW
# ============================================
if st.session_state.user_role == "Passenger":
    
    # Passenger selection
    passenger_options = {f"{p['name']} ({p['email']})": pid for pid, p in PASSENGERS_DATA.items()}
    selected_passenger_label = st.sidebar.selectbox("Select Passenger:", list(passenger_options.keys()), key="select_passenger")
    selected_passenger_id = passenger_options[selected_passenger_label]
    
    passenger = PASSENGERS_DATA[selected_passenger_id]
    
    st.subheader(f"👤 {passenger['name']}")
    
    # Profile Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total Rides", passenger['total_rides'])
    col2.metric("⭐ Average Rating", f"{passenger['avg_rating']:.1f}/5.0")
    col3.metric("📧 Email", passenger['email'])
    col4.metric("✅ Account Status", "Active" if passenger['is_active'] else "Inactive")
    
    st.divider()
    
    # Ride History
    st.subheader("📅 Your Ride History")
    history_rides = get_passenger_rides(selected_passenger_id)
    
    if history_rides:
        # Filter Options
        with st.expander("🔍 Filter Rides"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                status_filter = st.multiselect("Filter by Status", 
                    ['completed', 'cancelled', 'active'], 
                    default=['completed'],
                    key="passenger_status_filter")
            with col_f2:
                city_filter = st.text_input("Search City", key="passenger_city_filter")
            
            filtered_rides = history_rides.copy()
            if status_filter:
                filtered_rides = [r for r in filtered_rides if r['status'] in status_filter]
            if city_filter:
                filtered_rides = [r for r in filtered_rides if 
                    city_filter.lower() in r['from_city'].lower() or 
                    city_filter.lower() in r['to_city'].lower()]
            
            if filtered_rides:
                df_filtered = pd.DataFrame(filtered_rides)
                df_filtered['start_time'] = df_filtered['start_time'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df_filtered[['ride_id', 'from_city', 'to_city', 'start_time', 'status', 'fare']], use_container_width=True)
        
        # Display all rides
        st.write("**All Rides:**")
        df_all = pd.DataFrame(history_rides)
        df_all['start_time'] = df_all['start_time'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df_all[['ride_id', 'from_city', 'to_city', 'start_time', 'status', 'fare', 'distance']], use_container_width=True)
    else:
        st.info("No rides found!")

# ============================================
# DRIVER VIEW
# ============================================
elif st.session_state.user_role == "Driver":
    
    # Driver selection
    driver_options = {f"{d['name']} ({d['email']})": did for did, d in DRIVERS_DATA.items()}
    selected_driver_label = st.sidebar.selectbox("Select Driver:", list(driver_options.keys()), key="select_driver")
    selected_driver_id = driver_options[selected_driver_label]
    
    driver = DRIVERS_DATA[selected_driver_id]
    
    st.subheader(f"🚖 {driver['name']}")
    
    # Profile Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚗 Total Rides", driver['total_rides'])
    col2.metric("⭐ Average Rating", f"{driver['avg_rating']:.1f}/5.0")
    col3.metric("📧 Email", driver['email'])
    col4.metric("✅ Account Status", "Active" if driver['is_active'] else "Inactive")
    
    st.divider()
    
    # Driver Statistics
    st.subheader("📈 Performance Statistics")
    history_rides = get_driver_rides(selected_driver_id)
    
    if history_rides:
        stats = get_driver_statistics(selected_driver_id)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("✅ Completed Rides", stats['completed_rides'])
        col2.metric("❌ Cancelled Rides", stats['cancelled_rides'])
        col3.metric("💰 Total Earnings", f"₹{stats['total_earnings']:,.0f}")
        col4.metric("📍 Total Distance", f"{stats['total_distance']:.0f} km")
        
        st.divider()
    
    # Vehicle Information
    st.subheader("🚗 Vehicle Information")
    col_v1, col_v2, col_v3 = st.columns(3)
    col_v1.write(f"**Vehicle:** {driver['vehicle']}")
    col_v2.write(f"**Plate Number:** {driver['plate']}")
    col_v3.write(f"**Member Since:** {driver['created_at'].strftime('%Y-%m-%d')}")
    
    st.divider()
    
    # Ride History
    st.subheader("📅 Your Ride History")
    
    if history_rides:
        # Filter Options
        with st.expander("🔍 Filter Rides"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                status_filter = st.multiselect("Filter by Status", 
                    ['completed', 'cancelled', 'active'], 
                    default=['completed'],
                    key="driver_status_filter")
            with col_f2:
                city_filter = st.text_input("Search City", key="driver_city_filter")
            
            filtered_rides = history_rides.copy()
            if status_filter:
                filtered_rides = [r for r in filtered_rides if r['status'] in status_filter]
            if city_filter:
                filtered_rides = [r for r in filtered_rides if 
                    city_filter.lower() in r['from_city'].lower() or 
                    city_filter.lower() in r['to_city'].lower()]
            
            if filtered_rides:
                df_filtered = pd.DataFrame(filtered_rides)
                df_filtered['start_time'] = df_filtered['start_time'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df_filtered[['ride_id', 'from_city', 'to_city', 'start_time', 'status', 'fare', 'distance']], use_container_width=True)
        
        # Display all rides
        st.write("**All Rides:**")
        df_all = pd.DataFrame(history_rides)
        df_all['start_time'] = df_all['start_time'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df_all[['ride_id', 'from_city', 'to_city', 'start_time', 'status', 'fare', 'distance']], use_container_width=True)
    else:
        st.info("No rides found!")

# ============================================
# ADMIN VIEW
# ============================================
elif st.session_state.user_role == "Admin":
    st.subheader("🛠️ Admin Dashboard - System Overview")
    
    # Calculate system statistics
    total_passengers = len(PASSENGERS_DATA)
    total_drivers = len(DRIVERS_DATA)
    total_rides = len(RIDES_DATA)
    completed_rides = len([r for r in RIDES_DATA.values() if r['status'] == 'completed'])
    total_revenue = sum(r['fare'] for r in RIDES_DATA.values() if r['status'] == 'completed')
    
    # Admin Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👥 Total Passengers", total_passengers)
    col2.metric("🚖 Total Drivers", total_drivers)
    col3.metric("🚗 Total Rides", total_rides)
    col4.metric("✅ Completed Rides", completed_rides)
    col5.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    
    st.divider()
    
    # Admin Controls
    st.subheader("📋 Admin Controls")
    
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(["View All Rides", "View Passengers", "View Drivers", "System Analytics"])
    
    # ============ TAB 1: VIEW ALL RIDES ============
    with admin_tab1:
        st.write("**All Rides in System**")
        
        # Status filter
        ride_status_filter = st.multiselect("Filter by Status", 
            ['completed', 'cancelled', 'active'],
            default=['completed', 'cancelled'],
            key="admin_ride_status")
        
        # Get filtered rides
        admin_rides = [r for r in RIDES_DATA.values() if r['status'] in ride_status_filter]
        
        if admin_rides:
            df_admin_rides = pd.DataFrame(admin_rides)
            df_admin_rides['start_time'] = df_admin_rides['start_time'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_admin_rides, use_container_width=True)
            
            # Download option
            if st.button("📥 Download Rides Data (CSV)", key="download_rides"):
                csv = df_admin_rides.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"rides_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No rides found with selected filters")
    
    # ============ TAB 2: VIEW PASSENGERS ============
    with admin_tab2:
        st.write("**All Passengers in System**")
        
        # Status filter
        passenger_status_filter = st.selectbox("Filter by Status",
            ['All', 'Active', 'Inactive'],
            key="admin_passenger_status")
        
        # Get filtered passengers
        if passenger_status_filter == 'All':
            filtered_passengers = list(PASSENGERS_DATA.values())
        else:
            is_active = passenger_status_filter == 'Active'
            filtered_passengers = [p for p in PASSENGERS_DATA.values() if p['is_active'] == is_active]
        
        if filtered_passengers:
            df_passengers = pd.DataFrame(filtered_passengers)
            df_passengers['created_at'] = df_passengers['created_at'].dt.strftime('%Y-%m-%d')
            st.dataframe(df_passengers[['passenger_id', 'name', 'email', 'avg_rating', 'total_rides', 'is_active']], use_container_width=True)
            
            # Download option
            if st.button("📥 Download Passengers Data (CSV)", key="download_passengers"):
                csv = df_passengers.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"passengers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No passengers found")
    
    # ============ TAB 3: VIEW DRIVERS ============
    with admin_tab3:
        st.write("**All Drivers in System**")
        
        # Status filter
        driver_status_filter = st.selectbox("Filter by Status",
            ['All', 'Active', 'Inactive'],
            key="admin_driver_status")
        
        # Get filtered drivers
        if driver_status_filter == 'All':
            filtered_drivers = list(DRIVERS_DATA.values())
        else:
            is_active = driver_status_filter == 'Active'
            filtered_drivers = [d for d in DRIVERS_DATA.values() if d['is_active'] == is_active]
        
        if filtered_drivers:
            df_drivers = pd.DataFrame(filtered_drivers)
            df_drivers['created_at'] = df_drivers['created_at'].dt.strftime('%Y-%m-%d')
            st.dataframe(df_drivers[['driver_id', 'name', 'email', 'avg_rating', 'total_rides', 'vehicle', 'plate']], use_container_width=True)
            
            # Download option
            if st.button("📥 Download Drivers Data (CSV)", key="download_drivers"):
                csv = df_drivers.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"drivers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No drivers found")
    
    # ============ TAB 4: SYSTEM ANALYTICS ============
    with admin_tab4:
        st.write("**System Analytics & Reports**")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.subheader("📊 Ride Status Distribution")
            ride_status_counts = {}
            for ride in RIDES_DATA.values():
                status = ride['status']
                ride_status_counts[status] = ride_status_counts.get(status, 0) + 1
            
            st.bar_chart(ride_status_counts)
        
        with col_a2:
            st.subheader("⭐ Top Rated Drivers")
            top_drivers = sorted(DRIVERS_DATA.values(), key=lambda x: x['avg_rating'], reverse=True)[:3]
            for i, driver in enumerate(top_drivers, 1):
                st.write(f"{i}. {driver['name']} - ⭐ {driver['avg_rating']}/5.0 ({driver['total_rides']} rides)")
        
        st.divider()
        
        col_a3, col_a4 = st.columns(2)
        
        with col_a3:
            st.subheader("💰 Revenue Analytics")
            revenue_by_status = {}
            for ride in RIDES_DATA.values():
                status = ride['status']
                revenue_by_status[status] = revenue_by_status.get(status, 0) + ride['fare']
            
            st.bar_chart(revenue_by_status)
        
        with col_a4:
            st.subheader("📈 Top Passengers")
            passenger_ride_counts = {}
            for ride in RIDES_DATA.values():
                pid = ride['passenger_id']
                passenger_ride_counts[pid] = passenger_ride_counts.get(pid, 0) + 1
            
            # Sort by ride count
            sorted_passengers = sorted(passenger_ride_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (pid, count) in enumerate(sorted_passengers, 1):
                passenger_name = PASSENGERS_DATA[pid]['name']
                st.write(f"{i}. {passenger_name} - {count} rides")
        
        st.divider()
        
        st.subheader("📋 Key Metrics")
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        avg_rating_drivers = sum(d['avg_rating'] for d in DRIVERS_DATA.values()) / len(DRIVERS_DATA)
        avg_rating_passengers = sum(p['avg_rating'] for p in PASSENGERS_DATA.values()) / len(PASSENGERS_DATA)
        avg_fare = sum(r['fare'] for r in RIDES_DATA.values()) / len(RIDES_DATA) if RIDES_DATA else 0
        completion_rate = (completed_rides / total_rides * 100) if total_rides > 0 else 0
        
        metrics_col1.metric("Avg Driver Rating", f"{avg_rating_drivers:.2f}")
        metrics_col2.metric("Avg Passenger Rating", f"{avg_rating_passengers:.2f}")
        metrics_col3.metric("Avg Fare Amount", f"₹{avg_fare:.0f}")
        metrics_col4.metric("Completion Rate", f"{completion_rate:.1f}%")
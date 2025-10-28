"""
Ride Page - Active Ride Details & Completion
Path: pages/ride_page.py
Shows ride details after acceptance, role-based actions, and rating system
Uses static dataset for demonstration
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ============================================
# STREAMLIT CONFIG
# ============================================
st.set_page_config(page_title="Ride Details", layout="wide", initial_sidebar_state="collapsed")

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1
if 'user_role' not in st.session_state:
    st.session_state.user_role = "Passenger"
if 'ride_id' not in st.session_state:
    st.session_state.ride_id = 1
if 'ratings_submitted' not in st.session_state:
    st.session_state.ratings_submitted = {}

# ============================================
# STATIC DATASET
# ============================================
RIDES_DATA = {
    1: {
        "ride_id": 1,
        "status": "active",
        "seats_booked": 2,
        "total_fare": 1250.00,
        "start_time": datetime.now() - timedelta(minutes=15),
        "end_time": None,
        "from_city": "Jaipur",
        "to_city": "Udaipur",
        "distance_km": 394,
        "passenger_name": "Vandani Singh",
        "passenger_email": "vandani@example.com",
        "passenger_id": 1,
        "driver_name": "Rahul Mehta",
        "driver_email": "rahul@example.com",
        "driver_id": 1,
        "driver_rating": 4.7,
        "vehicle_name": "Swift Dzire",
        "plate_number": "RJ14AB1234",
        "vehicle_capacity": 4
    },
    2: {
        "ride_id": 2,
        "status": "completed",
        "seats_booked": 3,
        "total_fare": 2100.00,
        "start_time": datetime.now() - timedelta(days=1, hours=5),
        "end_time": datetime.now() - timedelta(days=1, hours=2),
        "from_city": "Delhi",
        "to_city": "Agra",
        "distance_km": 206,
        "passenger_name": "Priya Sharma",
        "passenger_email": "priya@example.com",
        "passenger_id": 2,
        "driver_name": "Amit Kumar",
        "driver_email": "amit@example.com",
        "driver_id": 2,
        "driver_rating": 4.5,
        "vehicle_name": "Hyundai Creta",
        "plate_number": "DL01CD5678",
        "vehicle_capacity": 5
    },
    3: {
        "ride_id": 3,
        "status": "active",
        "seats_booked": 1,
        "total_fare": 850.00,
        "start_time": datetime.now() - timedelta(minutes=45),
        "end_time": None,
        "from_city": "Bangalore",
        "to_city": "Mysore",
        "distance_km": 145,
        "passenger_name": "Ananya Gupta",
        "passenger_email": "ananya@example.com",
        "passenger_id": 3,
        "driver_name": "Vikram Singh",
        "driver_email": "vikram@example.com",
        "driver_id": 3,
        "driver_rating": 4.9,
        "vehicle_name": "Toyota Innova",
        "plate_number": "KA01EF9012",
        "vehicle_capacity": 6
    },
    4: {
        "ride_id": 4,
        "status": "completed",
        "seats_booked": 2,
        "total_fare": 650.00,
        "start_time": datetime.now() - timedelta(days=3, hours=2),
        "end_time": datetime.now() - timedelta(days=3),
        "from_city": "Mumbai",
        "to_city": "Pune",
        "distance_km": 180,
        "passenger_name": "Rohan Desai",
        "passenger_email": "rohan@example.com",
        "passenger_id": 4,
        "driver_name": "Suresh Patel",
        "driver_email": "suresh@example.com",
        "driver_id": 4,
        "driver_rating": 4.3,
        "vehicle_name": "Maruti Ertiga",
        "plate_number": "MH02GH3456",
        "vehicle_capacity": 7
    }
}

RATINGS_DATA = {
    2: [
        {
            "rating_id": 1,
            "ride_id": 2,
            "rated_by": 2,
            "rated_user": 2,
            "rating": 4.5,
            "feedback": "Great service and comfortable ride!",
            "created_at": datetime.now() - timedelta(days=1)
        }
    ],
    4: [
        {
            "rating_id": 2,
            "ride_id": 4,
            "rated_by": 4,
            "rated_user": 4,
            "rating": 4.0,
            "feedback": "Good driver, reached on time",
            "created_at": datetime.now() - timedelta(days=3)
        }
    ]
}

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_ride_by_id(ride_id):
    """Get ride details from static data"""
    return RIDES_DATA.get(ride_id, None)

def update_ride_status_local(ride_id, new_status):
    """Update ride status in session state"""
    if ride_id in RIDES_DATA:
        RIDES_DATA[ride_id]["status"] = new_status
        if new_status == "completed":
            RIDES_DATA[ride_id]["end_time"] = datetime.now()
        return True
    return False

def submit_rating_local(ride_id, rated_by, rated_user, rating, feedback):
    """Store rating in session state"""
    if ride_id not in RATINGS_DATA:
        RATINGS_DATA[ride_id] = []
    
    new_rating = {
        "rating_id": len(RATINGS_DATA.get(ride_id, [])) + 1,
        "ride_id": ride_id,
        "rated_by": rated_by,
        "rated_user": rated_user,
        "rating": rating,
        "feedback": feedback,
        "created_at": datetime.now()
    }
    RATINGS_DATA[ride_id].append(new_rating)
    st.session_state.ratings_submitted[ride_id] = True
    return True

# ============================================
# PAGE TITLE
# ============================================
st.title("🚗 Active Ride Details")

# ============================================
# ROLE SELECTION (for demo)
# ============================================
col_role1, col_role2, col_role3 = st.columns(3)
with col_role1:
    if st.button("👤 View as Passenger", key="btn_passenger"):
        st.session_state.user_role = "Passenger"
        st.rerun()
with col_role2:
    if st.button("🚖 View as Driver", key="btn_driver"):
        st.session_state.user_role = "Driver"
        st.rerun()
with col_role3:
    if st.button("🛠 View as Admin", key="btn_admin"):
        st.session_state.user_role = "Admin"
        st.rerun()

# ============================================
# RIDE SELECTION SIDEBAR
# ============================================
st.sidebar.title("📋 Select Ride")
ride_options = {f"Ride #{rid} - {data['from_city']} → {data['to_city']} ({data['status'].upper()})": rid 
                for rid, data in RIDES_DATA.items()}
selected_ride_label = st.sidebar.selectbox("Choose a ride:", list(ride_options.keys()))
st.session_state.ride_id = ride_options[selected_ride_label]

st.divider()

# ============================================
# FETCH RIDE DATA
# ============================================
ride_data = get_ride_by_id(st.session_state.ride_id)

if not ride_data:
    st.error("❌ Ride not found!")
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
    st.metric("Total Fare", f"₹{ride_data['total_fare']:.2f}")
    
    status_color = "🟢" if ride_data['status'] == "active" else "🔴" if ride_data['status'] == "completed" else "🟡"
    st.metric("Status", f"{status_color} {ride_data['status'].upper()}")

with col2:
    st.subheader("👥 Participant Details")
    st.write(f"**👤 Passenger:** {ride_data['passenger_name']}")
    st.write(f"**🚖 Driver:** {ride_data['driver_name']}")
    st.write(f"**🚗 Vehicle:** {ride_data['vehicle_name']} ({ride_data['plate_number']})")
    st.write(f"**💺 Seats Booked:** {ride_data['seats_booked']} / {ride_data['vehicle_capacity']}")
    st.write(f"**⭐ Driver Rating:** {ride_data['driver_rating']}/5.0")

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
            if update_ride_status_local(ride_data['ride_id'], 'cancelled'):
                st.warning("❌ Ride has been cancelled")
                st.rerun()
    
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
                if update_ride_status_local(ride_data['ride_id'], 'started'):
                    st.info("🚗 Ride has started!")
                    st.rerun()
    
    with col_action2:
        if ride_data['status'] in ['active', 'started']:
            if st.button("🏁 End Ride", use_container_width=True, key="end_ride"):
                if update_ride_status_local(ride_data['ride_id'], 'completed'):
                    st.success("🏁 Ride completed successfully!")
                    st.rerun()

elif st.session_state.user_role == "Admin":
    st.subheader("🛠️ Admin Controls")
    st.warning("⚠️ Admin can monitor and manage rides")
    
    col_admin1, col_admin2, col_admin3 = st.columns(3)
    with col_admin1:
        if st.button("👁️ View Details", use_container_width=True):
            st.json(ride_data)
    
    with col_admin2:
        if st.button("🔄 Change Status", use_container_width=True):
            new_status = st.selectbox("Select new status:", ["active", "started", "completed", "cancelled"])
            if st.button("✅ Confirm Change"):
                if update_ride_status_local(ride_data['ride_id'], new_status):
                    st.success(f"✅ Ride status changed to {new_status}")
                    st.rerun()
    
    with col_admin3:
        if st.button("🛑 Force End Ride", use_container_width=True):
            if update_ride_status_local(ride_data['ride_id'], 'completed'):
                st.error("🛑 Ride forcefully ended by admin")
                st.rerun()

st.divider()

# ============================================
# RATING SECTION (After Completion)
# ============================================
if ride_data['status'] == 'completed':
    st.subheader("⭐ Rate Your Ride Experience")
    
    # Show existing ratings
    if ride_data['ride_id'] in RATINGS_DATA and RATINGS_DATA[ride_data['ride_id']]:
        st.info("📊 Existing Ratings:")
        for rating in RATINGS_DATA[ride_data['ride_id']]:
            col_rating_display1, col_rating_display2 = st.columns([1, 3])
            with col_rating_display1:
                st.write(f"⭐ {rating['rating']}")
            with col_rating_display2:
                st.write(f"_{rating['feedback']}_")
    
    st.divider()
    
    # Submit new rating
    if ride_data['ride_id'] not in st.session_state.ratings_submitted:
        st.write("**Submit Your Rating:**")
        col_rating1, col_rating2 = st.columns([1, 2])
        
        with col_rating1:
            rating_value = st.slider("Select Rating", 0.0, 5.0, 4.0, 0.5, key=f"slider_rating_{ride_data['ride_id']}")
        
        with col_rating2:
            feedback_text = st.text_area(
                "Share Your Feedback", 
                placeholder="Tell us about your experience...", 
                height=100,
                key=f"text_feedback_{ride_data['ride_id']}"
            )
        
        if st.button("📤 Submit Rating", use_container_width=True, key=f"btn_submit_rating_{ride_data['ride_id']}"):
            if submit_rating_local(
                ride_id=ride_data['ride_id'],
                rated_by=st.session_state.user_id,
                rated_user=ride_data['driver_id'] if st.session_state.user_role == "Passenger" else ride_data['passenger_id'],
                rating=rating_value,
                feedback=feedback_text
            ):
                st.success(f"✅ Thank you for your {rating_value}⭐ rating!")
                st.rerun()
            else:
                st.error("❌ Failed to submit rating")
    else:
        st.success("✅ You have already rated this ride!")

# ============================================
# RIDE TIMELINE
# ============================================
st.divider()
st.subheader("📅 Ride Timeline")

timeline_data = {
    "Ride Requested": "✅",
    "Driver Accepted": "✅",
    "Ride Started": "✅" if ride_data['status'] in ['started', 'completed'] else "⏳",
    "Ride Completed": "✅" if ride_data['status'] == 'completed' else "⏳"
}

col_timeline1, col_timeline2, col_timeline3, col_timeline4 = st.columns(4)
with col_timeline1:
    st.write(timeline_data["Ride Requested"] + " Requested")
with col_timeline2:
    st.write(timeline_data["Driver Accepted"] + " Accepted")
with col_timeline3:
    st.write(timeline_data["Ride Started"] + " Started")
with col_timeline4:
    st.write(timeline_data["Ride Completed"] + " Completed")
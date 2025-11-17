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

def show():
    # Remove Background Color - Use Default Streamlit Theme
    st.markdown("""
    <style>
        .stApp {
            background-color: transparent !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Dark Theme with Sky Blue Accents
    st.markdown("""
    <style>
        /* Page Header */
        .offer-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            animation: slideIn 0.6s ease-out;
            border-bottom: 3px solid #00d4ff;
        }
        
        .offer-title {
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #00d4ff;
        }
        
        .offer-subtitle {
            font-size: 16px;
            opacity: 0.9;
            color: #e0e0e0;
        }
        
        /* Section Title */
        .section-title {
            font-size: 24px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 3px solid #00d4ff;
            display: inline-block;
        }
        
        /* Request Card */
        .request-card {
            background: #16213e;
            border: 2px solid #00d4ff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.1);
            border-left: 5px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .request-card:hover {
            transform: translateX(5px);
            box-shadow: 0 10px 28px rgba(0, 212, 255, 0.2);
        }
        
        .request-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid #0f3460;
        }
        
        .request-id {
            font-weight: 700;
            color: #00d4ff;
            font-size: 16px;
        }
        
        .request-route {
            font-size: 14px;
            color: #b0b0b0;
        }
        
        .request-detail {
            display: inline-block;
            background: #00d4ff;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 13px;
            color: #1a1a2e;
            margin: 5px 5px 5px 0;
            font-weight: 600;
        }
        
        /* Submit/Action Button */
        .stButton > button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
            color: #1a1a2e !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.25) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4) !important;
        }
        
        /* Form Card */
        .form-section {
            background: linear-gradient(to bottom, #16213e 0%, #0f3460 100%);
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #00d4ff;
            margin-top: 30px;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="offer-header">
        <div class="offer-title">🚗 Offer a Ride</div>
        <div class="offer-subtitle">Manage ride offers and accept passenger requests</div>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.get("user")
    if not user:
        st.warning("⚠️ Please log in to create or manage ride offers.")
        st.stop()
    
    driver_id = get_driver_id(user["user_id"])
    if not driver_id:
        st.warning("⚠️ Driver profile not found. Please register as a driver.")
        st.stop()
    
    # Passenger Ride Requests Section
    st.markdown('<div class="section-title">📢 Passenger Ride Requests</div>', unsafe_allow_html=True)
    
    requests = get_open_ride_requests()
    
    if requests:
        for req in requests:
            st.markdown(f"""
            <div class="request-card">
                <div class="request-header">
                    <div>
                        <div class="request-id">🎯 Request #{req['request_id']}</div>
                        <div class="request-route">{req['from_city']} → {req['to_city']}</div>
                    </div>
                </div>
                <div>
                    <span class="request-detail">📅 {req['date_time']}</span>
                    <span class="request-detail">👥 {req['passengers_count']} passengers</span>
                    <span class="request-detail">📌 {req['status'].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ Accept Request #{req['request_id']}", key=f"accept_{req['request_id']}"):
                with st.spinner("🔄 Accepting request..."):
                    success = accept_ride_request(driver_id, req["request_id"])
                if success:
                    st.success("✅ Ride request accepted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to accept ride request.")
    else:
        st.info("📭 No Active Requests — There are no ride requests available at the moment.")
    
    # Create Ride Offer Section
    st.markdown('<div class="section-title" style="margin-top: 40px;">➕ Create a Ride Offer</div>', unsafe_allow_html=True)
    
    routes = fetch_routes()
    if not routes:
        st.warning("⚠️ No routes available. Please add routes first.")
        st.stop()
    
    with st.form("ride_offer_form"):
        st.markdown("### 📋 Enter Ride Details")
        
        route_options = [f"{r['from_city']} → {r['to_city']} ({r['distance_km']} km)" for r in routes]
        
        col1, col2 = st.columns(2)
        with col1:
            route_choice = st.selectbox("🗺️ Select Route", route_options)
            available_seats = st.slider("💺 Available Seats", 1, 6, 3)
        
        with col2:
            vehicle_no = st.text_input("🚗 Vehicle Number", placeholder="e.g. MH12AB1234")
            price_per_km = st.number_input("💰 Price per KM (₹)", min_value=1.0, value=5.0, step=0.5)
        
        submitted = st.form_submit_button("🚀 Create Ride Offer")
        
        if submitted:
            if not vehicle_no:
                st.warning("⚠️ Please enter vehicle number")
            else:
                selected_route = routes[route_options.index(route_choice)]
                route_id = selected_route["route_id"]
                distance_km = selected_route["distance_km"]
                estimated_fare = distance_km * price_per_km
                
                with st.spinner("🔄 Creating ride offer..."):
                    success = create_ride_offer(
                        driver_id=driver_id,
                        vehicle_no=vehicle_no,
                        route_id=route_id,
                        available_seats=available_seats,
                        price_per_km=price_per_km,
                        estimated_fare=estimated_fare,
                    )
                
                if success:
                    st.success("✅ Ride offer created successfully!")
                else:
                    st.error("❌ Failed to create ride offer. Try again later.")
    
    # Assigned Rides Section
    st.subheader("🎯 Your Assigned Rides")
    
    assigned_rides = get_driver_assigned_rides(driver_id)
    
    if not assigned_rides:
        st.info("🚙 No Assigned Rides — You don't have any assigned rides yet. Accept requests to get started!")
        return
    
    for ride in assigned_rides:
        with st.expander(f"🚗 Ride #{ride['ride_id']} — {ride['from_city']} → {ride['to_city']}", expanded=True):
            st.write(f"**Passenger:** {ride['passenger_name']}")
            st.write(f"**From:** {ride['from_city']}")
            st.write(f"**To:** {ride['to_city']}")
            st.write(f"**Status:** {ride['status']}")
            col1, col2, col3 = st.columns(3)
            if ride["status"] == "booked":
                with col1:
                    if st.button("▶️ Start Ride", key=f"start_{ride['ride_id']}"):
                        if update_ride_status(ride["ride_id"], "active"):
                            st.success("✅ Ride started successfully!")
                            st.rerun()
            elif ride["status"] == "active":
                with col2:
                    if st.button("✅ Complete Ride", key=f"complete_{ride['ride_id']}"):
                        if update_ride_status(ride["ride_id"], "completed"):
                            st.success("✅ Ride completed successfully!")
                            st.rerun()
            with col3:
                if st.button("❌ Cancel Ride", key=f"cancel_{ride['ride_id']}"):
                    if update_ride_status(ride["ride_id"], "cancelled"):
                        st.warning("⚠️ Ride cancelled.")
                        st.rerun()

if __name__ == "__main__":
    show()

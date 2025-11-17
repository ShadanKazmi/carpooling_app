import streamlit as st
from datetime import datetime
import time
import pymysql
from utils.db_connection import get_connection
from utils.ride_utils import create_ride_request, fetch_route_cities, get_matched_ride_details

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
        .request-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            animation: slideDown 0.6s ease-out;
            border-bottom: 3px solid #00d4ff;
        }
        
        .request-title {
            font-size: 40px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #00d4ff;
        }
        
        .request-subtitle {
            font-size: 16px;
            opacity: 0.9;
            color: #e0e0e0;
        }
        
        /* Form Container */
        .form-card {
            background: linear-gradient(to bottom, #16213e 0%, #0f3460 100%);
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #00d4ff;
            margin-bottom: 30px;
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.1);
        }
        
        .form-section-title {
            font-size: 22px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 20px;
            display: inline-block;
            border-bottom: 3px solid #00d4ff;
            padding-bottom: 8px;
        }
        
        /* Match Card */
        .match-card {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
            animation: popIn 0.6s ease-out;
            border: 2px solid #00d4ff;
        }
        
        .match-icon {
            font-size: 60px;
            margin-bottom: 15px;
            animation: bounce 1s infinite;
        }
        
        .match-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #00d4ff;
        }
        
        /* Driver Info Card */
        .driver-card {
            background: #1a1a2e;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.15);
            border-top: 4px solid #00d4ff;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .driver-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0, 212, 255, 0.25);
        }
        
        .driver-label {
            font-size: 14px;
            color: #b0b0b0;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .driver-value {
            font-size: 18px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .driver-rating {
            font-size: 14px;
            color: #b0b0b0;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes popIn {
            0% {
                opacity: 0;
                transform: scale(0.8);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        /* Submit Button */
        .stButton > button {
            background: linear-gradient(135deg, #0366d6 0%, #00d4ff 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 14px 40px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 20px rgba(3, 102, 214, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 30px rgba(3, 102, 214, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="request-header">
        <div class="request-title">🚖 Request a Ride</div>
        <div class="request-subtitle">Share your travel details to get matched with a driver</div>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.get("user")
    if not user:
        st.warning("⚠️ Please log in first.")
        return
    
    # Fetch city list
    from_cities, to_cities = fetch_route_cities()
    
    if not from_cities or not to_cities:
        st.warning("⚠️ No routes found in the system. Please import route data first.")
        return
    
    # Ride Request Form
    st.markdown('<div class="form-section-title">🗺️ Journey Details</div>', unsafe_allow_html=True)
    
    with st.form("ride_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            from_city = st.selectbox("📍 Departure City", from_cities)
            date = st.date_input("📅 Travel Date", datetime.now().date())
        
        with col2:
            to_city = st.selectbox("🎯 Destination City", to_cities)
            time_input = st.time_input("⏰ Departure Time", datetime.now().time())
        
        passengers = st.slider("👥 Number of Passengers", 1, 6, 1)
        
        with st.expander("⚙️ Preferences (Optional)", expanded=False):
            col3, col4 = st.columns(2)
            with col3:
                pref_family = st.checkbox("👨‍👩‍👧 Family Friendly")
                pref_women = st.checkbox("👩 Women Only")
            with col4:
                pref_non_smoke = st.checkbox("🚭 Non-Smoking")
                pref_child = st.checkbox("👶 Child Seat Available")
            
            additional_notes = st.text_area("📝 Additional Notes", placeholder="Any special requirements or notes...")
        
        submitted = st.form_submit_button("🚀 Request Ride")
    
    if submitted:
        preferences = {
            "family": pref_family,
            "women": pref_women,
            "non_smoke": pref_non_smoke,
            "child": pref_child,
            "notes": additional_notes,
        }
        
        with st.spinner("🔄 Submitting your request..."):
            success = create_ride_request(
                passenger_id=user["user_id"],
                from_city=from_city,
                to_city=to_city,
                date_time=datetime.combine(date, time_input),
                passengers_count=passengers,
                preferences=preferences,
            )
        
        if success:
            st.success("✅ Ride request submitted! Waiting for a driver match...")
            st.info("🔄 This page updates automatically every 5 seconds.")
            st.rerun()
        else:
            st.error("❌ Failed to create request. Try again.")
    
    # Live Match Check
    conn = get_connection()
    if not conn:
        st.error("❌ Unable to connect to the database. Please check configuration.")
        return
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT request_id, status
        FROM ride_requests
        WHERE passenger_id=%s
        ORDER BY created_at DESC LIMIT 1
    """, (user["user_id"],))
    req = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if req and req["status"] == "matched":
        matched = get_matched_ride_details(req["request_id"])
        if matched:
            st.markdown("""
            <div class="match-card">
                <div class="match-icon">🎉</div>
                <div class="match-title">Your Ride Has Been Matched!</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="driver-card">
                    <div class="driver-label">👤 DRIVER</div>
                    <div class="driver-value">{matched['driver_name']}</div>
                    <div class="driver-rating">⭐ {matched['avg_rating']}/5.0</div>
                    <div class="driver-rating">{matched['total_rides']} rides completed</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="driver-card">
                    <div class="driver-label">🚗 VEHICLE</div>
                    <div class="driver-value">{matched['vehicle_no']}</div>
                    <div class="driver-rating">💺 {matched['available_seats']} seats reserved</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="driver-card">
                    <div class="driver-label">💰 ESTIMATED FARE</div>
                    <div class="driver-value">₹{matched['estimated_fare']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="driver-card" style="border-top-color: #00d4ff; margin-top: 20px;">
                <div class="driver-label">🗺️ ROUTE DETAILS</div>
                <div style="text-align: left; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                    <div style="margin: 8px 0;"><strong>From:</strong> {matched['from_city']}</div>
                    <div style="margin: 8px 0;"><strong>To:</strong> {matched['to_city']}</div>
                    <div style="margin: 8px 0;"><strong>Departure:</strong> {matched['date_time']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🔄 Driver matched — loading details...")

if __name__ == "__main__":
    show()


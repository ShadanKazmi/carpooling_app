import streamlit as st
from components.navbar import navbar
from utils.ride_utils import (
    get_driver_id as _get_driver_id,
    get_passenger_id_by_user,
    get_rides_for_driver,
    get_rides_for_passenger,
    has_user_already_rated,
    save_rating_and_update_averages
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
        .rides-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            border-bottom: 3px solid #00d4ff;
        }
        
        .rides-title {
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #00d4ff;
        }
        
        .rides-subtitle {
            font-size: 16px;
            opacity: 0.9;
            color: #e0e0e0;
        }
        
        /* Ride Card */
        .ride-card {
            background: #16213e;
            border: 2px solid #00d4ff;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 22px rgba(0, 212, 255, 0.1);
            border-left: 5px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .ride-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0, 212, 255, 0.2);
        }
        
        .ride-route {
            font-size: 24px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 15px;
        }
        
        .ride-detail-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 12px 0;
        }
        
        .ride-detail {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #0f3460;
        }
        
        .ride-detail-label {
            color: #b0b0b0;
            font-weight: 600;
            font-size: 13px;
        }
        
        .ride-detail-value {
            color: #00d4ff;
            font-weight: 700;
        }
        
        .status-badge {
            display: inline-block;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            margin-top: 10px;
        }
        
        .status-completed { background: #0f5c3e; color: #4ade80; }
        .status-cancelled { background: #5c1f1f; color: #f87171; }
        .status-active { background: #1e3a5f; color: #60a5fa; }
        
        /* Rating Section */
        .rating-section {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin-top: 15px;
            border: 2px solid #00d4ff;
        }
        
        /* Submit Button */
        .stButton > button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
            color: #1a1a2e !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 25px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.25) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="rides-header">
        <div class="rides-title">📋 My Rides</div>
        <div class="rides-subtitle">Track your ride history and rate completed rides</div>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.get("user")
    if not user:
        st.warning("⚠️ Please log in to view your rides.")
        st.stop()
    
    user_id = int(user["user_id"])
    role = str(user["role"]).lower()
    
    if role == "driver":
        driver_id = _get_driver_id(user_id)
        if not driver_id:
            st.warning("⚠️ Driver profile not found. Please register as a driver.")
            st.stop()
        rides = get_rides_for_driver(driver_id)
        header_title = "🚗 Rides You've Offered"
    else:
        passenger_id = get_passenger_id_by_user(user_id)
        if not passenger_id:
            st.warning("⚠️ Passenger profile not found. Please register as a passenger.")
            st.stop()
        rides = get_rides_for_passenger(passenger_id)
        header_title = "🎫 Your Ride Bookings"
    
    st.markdown(f'<div style="font-size: 22px; font-weight: 700; color: #0366d6; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 3px solid #00d4ff; display: inline-block;">{header_title}</div>', unsafe_allow_html=True)
    
    if not rides:
        st.info("🚕 No Rides Yet — You have no rides yet. Book or offer a ride to get started!")
        return
    
    for idx, ride in enumerate(rides):
        status_class = f"status-{ride['status'].lower()}"
        st.markdown(f"""
        <div class="ride-card">
            <div class="ride-route">🚗 {ride['from_city']} → {ride['to_city']}</div>
            <div class="ride-detail">
                <span class="ride-detail-label">📅 Date</span>
                <span class="ride-detail-value">{ride['ride_date']}</span>
            </div>
            <div class="ride-detail">
                <span class="ride-detail-label">💺 Seats Booked</span>
                <span class="ride-detail-value">{ride['seats_booked']}</span>
            </div>
            <div class="ride-detail">
                <span class="ride-detail-label">💰 Fare</span>
                <span class="ride-detail-value">₹{ride['total_fare']}</span>
            </div>
            <div class="ride-detail">
                <span class="ride-detail-label">⏱️ Status</span>
                <span class="ride-detail-value"><span class="status-badge {status_class}">{ride['status'].upper()}</span></span>
            </div>
            <div class="ride-detail">
                <span class="ride-detail-label">⏳ Started</span>
                <span class="ride-detail-value">{ride['start_time'] or 'Not started'}</span>
            </div>
            <div class="ride-detail">
                <span class="ride-detail-label">✅ Ended</span>
                <span class="ride-detail-value">{ride['end_time'] or 'Not ended'}</span>
            </div>
            <div class="ride-detail">
                <span class="ride-detail-label">🚙 Vehicle</span>
                <span class="ride-detail-value">{ride.get('vehicle_no', 'N/A')}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Show user info
        if role == "driver":
            st.markdown(f"""
            <div class="ride-detail">
                <span class="ride-detail-label">👤 Passenger</span>
                <span class="ride-detail-value">{ride['passenger_name']}</span>
            </div>
            """, unsafe_allow_html=True)
            rated_user_id = int(ride["passenger_user_id"])
        else:
            st.markdown(f"""
            <div class="ride-detail">
                <span class="ride-detail-label">🚗 Driver</span>
                <span class="ride-detail-value">{ride['driver_name']}</span>
            </div>
            """, unsafe_allow_html=True)
            rated_user_id = int(ride["driver_user_id"])
        
        # Rating section for completed rides
        if ride["status"] == "completed":
            already = has_user_already_rated(ride_id=int(ride["ride_id"]), rated_by_user_id=user_id)
            
            if not already:
                uniq = f"{ride['ride_id']}_{user_id}_{idx}"
                form_key = f"rate_form_{uniq}"
                rating_key = f"rating_{uniq}"
                feedback_key = f"feedback_{uniq}"
                
                st.subheader("⭐ Rate This Ride")
                with st.form(key=form_key, clear_on_submit=True):
                    rating_value = st.radio(
                        "Your Rating",
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: "⭐" * x,
                        horizontal=True,
                        key=rating_key,
                    )
                    feedback_text = st.text_area(
                        "💬 Feedback (optional)",
                        placeholder="Share your experience with this ride...",
                        key=feedback_key,
                    )
                    submitted = st.form_submit_button("🚀 Submit Rating")
                
                if submitted:
                    with st.spinner("🔄 Submitting rating..."):
                        success = save_rating_and_update_averages(
                            ride_id=int(ride["ride_id"]),
                            rated_by_user_id=user_id,
                            rated_user_id=rated_user_id,
                            rating_value=int(rating_value),
                            feedback_text=feedback_text.strip() if feedback_text else None
                        )
                    
                    if success:
                        st.success("✅ Rating submitted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Could not save rating. Try again.")
            else:
                st.success("✅ You have already rated this ride. Thank you!")
        
        st.markdown("<hr style='margin: 30px 0; border: none; border-top: 2px dashed #e0e0e0;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    show()


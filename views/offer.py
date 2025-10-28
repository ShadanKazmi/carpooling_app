import streamlit as st
from datetime import datetime
from components.navbar import navbar

def show():
    navbar(active_page="Offer")
    st.title("🚗 Offer a Ride")
    st.write("Share your upcoming trip and earn by helping passengers reach their destination.")
    
    with st.form("ride_offer_form"):
        st.subheader("Enter Your Journey Details")
        
        col1, col2 = st.columns(2)
        with col1:
            from_city = st.selectbox("📍 From City", ["Indore", "Bhopal", "Jaipur", "Ahmedabad", "Mumbai"])
            date = st.date_input("📅 Departure Date", datetime.now().date())
            vehicle = st.text_input("🚘 Vehicle Number", placeholder="e.g., MP09AB1234")
        with col2:
            to_city = st.selectbox("🎯 To City", ["Bhopal", "Udaipur", "Pune", "Surat", "Nagpur"])
            time = st.time_input("⏰ Departure Time", datetime.now().time())
            available_seats = st.number_input("🪑 Available Seats", min_value=1, max_value=6, value=3)
            
        price_per_seat = st.number_input("💰 Price per Seat (₹)", 
                                        min_value=100, 
                                        max_value=5000,
                                        step=50,
                                        value=500)
        
        with st.expander("⚙️ Preferences (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                music = st.checkbox("🎵 Music Allowed")
                ac = st.checkbox("❄️ Air Conditioned")
            with col2:
                pet = st.checkbox("🐶 Pet Friendly")
                smoking = st.checkbox("🚬 Smoking Allowed")
        
        additional_info = st.text_area("Additional Information", 
                                     placeholder="Any special notes about the journey...")
        
        if st.form_submit_button("🚀 Publish Ride Offer"):
            if from_city and to_city and vehicle:
                st.success(f"🎉 Ride from **{from_city} → {to_city}** published successfully!")
                st.info(f"📅 Departure: {date} at {time} | 💰 Fare ₹{price_per_seat} | Seats: {available_seats}")
                st.balloons()
            else:
                st.error("Please fill in all required fields")
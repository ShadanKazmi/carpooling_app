import streamlit as st
from datetime import datetime
from components.navbar import navbar

def show():
    navbar(active_page="Request")
    st.title("🚖 Request a Ride")
    st.write("Find a comfortable and safe ride by sharing your trip details below.")

    with st.form("ride_request_form"):
        st.subheader("Enter Your Journey Details")
        
        col1, col2 = st.columns(2)
        with col1:
            from_city = st.selectbox("📍 From", ["Indore", "Bhopal", "Jaipur", "Ahmedabad", "Mumbai"])
            date = st.date_input("📅 Date", datetime.now().date())
        with col2:
            to_city = st.selectbox("🎯 To", ["Bhopal", "Udaipur", "Pune", "Surat", "Nagpur"])
            time = st.time_input("⏰ Time", datetime.now().time())

        passengers = st.slider("👥 Passengers", 1, 6, 1)
        
        with st.expander("⚙️ Preferences"):
            col1, col2 = st.columns(2)
            with col1:
                pref_family = st.checkbox("Family Friendly")
                pref_women = st.checkbox("Women Only")
            with col2:
                pref_non_smoke = st.checkbox("Non-Smoking")
                pref_child = st.checkbox("Child Seat")
        
        additional_notes = st.text_area("Additional Notes (Optional)", 
                                      placeholder="Any special requirements or preferences...")
        
        if st.form_submit_button("🔍 Find Rides"):
            if from_city and to_city and date and time:
                st.info("🚗 Searching for best rides nearby...")
                # Placeholder sample results
                matched_rides = [
                    {"driver": "Aman", "vehicle": "Swift Dzire", "fare": 550, "distance": 180, "rating": 4.8},
                    {"driver": "Priya", "vehicle": "Innova", "fare": 740, "distance": 190, "rating": 4.9},
                ]
                st.success(f"✅ Found {len(matched_rides)} rides for you!")
                for match in matched_rides:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        col1.markdown(f"👨‍✈️ **{match['driver']}** ({match['rating']}/5)")
                        col2.markdown(f"🚘 {match['vehicle']}")
                        col3.markdown(f"💰 ₹{match['fare']} | 📏 {match['distance']} km")
                        if col4.button("Book", key=match["driver"]):
                            st.success(f"🎉 Ride booked successfully with {match['driver']}!")
            else:
                st.error("Please fill in all required fields")
import streamlit as st
from components.navbar import navbar

def show():
    navbar(active_page="Profile")
    st.title("👤 Profile")
    
    if "user" in st.session_state and st.session_state.user:
        user = st.session_state.user
        
        # Profile Tabs
        tab1, tab2, tab3 = st.tabs(["Profile Info", "Preferences", "Account Settings"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("User Information")
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Username:** {user['username']}")
                st.write(f"**Role:** {user['role'].capitalize()}")
                st.write(f"**Last Login:** {user['last_login'] if user['last_login'] else 'Never'}")
                
                if st.button("Edit Profile"):
                    st.info("Profile editing feature coming soon!")
            
            with col2:
                st.subheader("Stats")
                st.metric("Total Rides", "5")
                st.metric("Average Rating", "4.8 ⭐")
                st.metric("Distance Traveled", "450 km")
        
        with tab2:
            st.subheader("Ride Preferences")
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("🎵 Music in Car", value=True)
                st.checkbox("🚭 Non-Smoking", value=True)
                st.checkbox("🐕 Pet Friendly")
            with col2:
                st.checkbox("👨‍👩‍👧‍👦 Family Friendly", value=True)
                st.checkbox("👩 Women Only Rides")
                st.checkbox("❄️ AC Required", value=True)
            
            if st.button("Save Preferences"):
                st.success("Preferences saved successfully!")
        
        with tab3:
            st.subheader("Account Settings")
            if st.button("Change Password"):
                st.info("Password change feature coming soon!")
            if st.button("Delete Account"):
                st.error("⚠️ This action cannot be undone!")
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()
    else:
        st.warning("Please login to view your profile")
        st.info("Use the login form above to access your profile")
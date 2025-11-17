import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_connection import run_query

def show():
    st.set_page_config(page_title="Profile & Ride History", layout="wide")
    
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
        /* Profile Header */
        .profile-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 50px 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
            animation: slideIn 0.6s ease-out;
            border-bottom: 4px solid #00d4ff;
        }
        
        .profile-name {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #00d4ff;
        }
        
        .profile-role {
            font-size: 18px;
            opacity: 0.9;
            color: #e0e0e0;
        }
        
        /* Section Title */
        .profile-section-title {
            font-size: 24px;
            font-weight: 700;
            color: #00d4ff;
            margin-top: 30px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 3px solid #00d4ff;
            display: inline-block;
        }
        
        /* Stat Cards */
        .metric-card {
            background: #16213e;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.1);
            border-top: 4px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0, 212, 255, 0.2);
            border-top-color: #00d4ff;
        }
        
        .metric-label {
            font-size: 13px;
            color: #b0b0b0;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #00d4ff;
        }
        
        /* Table Styling */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 18px rgba(0, 212, 255, 0.1);
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    if "user" not in st.session_state:
        st.error("❌ You need to log in to view your profile.")
        st.stop()
    
    user = st.session_state["user"]
    user_id = user["user_id"]
    role = user["role"].lower()
    
    # Profile Header
    role_emoji = "🚗" if role == "driver" else "👤" if role == "passenger" else "👥"
    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-name">{role_emoji} {user['name']}</div>
        <div class="profile-role">{role.title()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # PASSENGER PROFILE
    if role == "passenger" or role == "both":
        passenger = run_query("SELECT * FROM passengers WHERE user_id = %s", (user_id,))
        
        if not passenger:
            st.warning("⚠️ No passenger profile found.")
        else:
            p = passenger[0]
            
            st.markdown('<div class="profile-section-title">👤 Passenger Profile</div>', unsafe_allow_html=True)
            
            # Stats Cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Rating</div>
                    <div class="metric-value">⭐ {p['avg_rating']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                joined_date = p['created_at'].strftime("%b %Y")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Joined</div>
                    <div class="metric-value">{joined_date}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Passenger ID</div>
                    <div class="metric-value">{p['passenger_id']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="profile-section-title">📅 Ride History</div>', unsafe_allow_html=True)
            
            rides = run_query("""
                SELECT r.ride_id, rt.from_city, rt.to_city, r.start_time, r.status, r.total_fare
                FROM rides r
                JOIN routes rt ON r.offer_id = rt.route_id
                WHERE r.passenger_id = %s
                ORDER BY r.start_time DESC
            """, (p["passenger_id"],))
            
            if rides:
                df = pd.DataFrame(rides)
                df["start_time"] = pd.to_datetime(df["start_time"]).dt.strftime("%Y-%m-%d %H:%M")
                df.columns = ["Ride ID", "From", "To", "Date & Time", "Status", "Fare (₹)"]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("🚕 No Rides Yet — Start booking rides to see your history here.")
    
    # DRIVER PROFILE
    if role == "driver" or role == "both":
        driver = run_query("SELECT * FROM drivers WHERE user_id = %s", (user_id,))
        
        if not driver:
            st.warning("⚠️ No driver profile found.")
        else:
            d = driver[0]
            
            st.markdown('<div class="profile-section-title">🚗 Driver Profile</div>', unsafe_allow_html=True)
            
            # Driver Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Rating</div>
                    <div class="metric-value">⭐ {d['avg_rating']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Rides</div>
                    <div class="metric-value">{d['total_rides']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                joined_date = d['created_at'].strftime("%b %Y")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Joined</div>
                    <div class="metric-value">{joined_date}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="profile-section-title">📊 Performance Overview</div>', unsafe_allow_html=True)
            
            stats = run_query("""
                SELECT
                    COUNT(*) AS total_rides,
                    SUM(total_fare) AS total_earnings,
                    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed_rides,
                    SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) AS cancelled_rides
                FROM rides
                WHERE driver_id = %s
            """, (d["driver_id"],))[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Completed Rides</div>
                    <div class="metric-value">{stats["completed_rides"] or 0}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Cancelled</div>
                    <div class="metric-value">{stats["cancelled_rides"] or 0}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                earnings = stats['total_earnings'] or 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Earnings</div>
                    <div class="metric-value">₹{earnings:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">All Rides</div>
                    <div class="metric-value">{stats["total_rides"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="profile-section-title">📅 Ride History</div>', unsafe_allow_html=True)
            
            rides = run_query("""
                SELECT r.ride_id, rt.from_city, rt.to_city, r.start_time, r.status, r.total_fare
                FROM rides r
                JOIN routes rt ON r.offer_id = rt.route_id
                WHERE r.driver_id = %s
                ORDER BY r.start_time DESC
            """, (d["driver_id"],))
            
            if rides:
                df = pd.DataFrame(rides)
                df["start_time"] = pd.to_datetime(df["start_time"]).dt.strftime("%Y-%m-%d %H:%M")
                df.columns = ["Ride ID", "From", "To", "Date & Time", "Status", "Fare (₹)"]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("🚗 No Rides Yet — Start offering rides to see your history here.")
    
    # ADMIN DASHBOARD
    if role == "admin":
        st.markdown('<div class="profile-section-title">🛠 System Overview</div>', unsafe_allow_html=True)
        
        total_users = run_query("SELECT COUNT(*) AS cnt FROM users")[0]["cnt"]
        total_rides = run_query("SELECT COUNT(*) AS cnt FROM rides")[0]["cnt"]
        completed = run_query("SELECT COUNT(*) AS cnt FROM rides WHERE status='completed'")[0]["cnt"]
        total_revenue = run_query("SELECT SUM(total_fare) AS rev FROM rides WHERE status='completed'")[0]["rev"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Users</div>
                <div class="metric-value">{total_users}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Rides</div>
                <div class="metric-value">{total_rides}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Completed</div>
                <div class="metric-value">{completed}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Revenue</div>
                <div class="metric-value">₹{total_revenue or 0:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="profile-section-title">📊 Analytics</div>', unsafe_allow_html=True)
        
        data = run_query("SELECT status, COUNT(*) AS count FROM rides GROUP BY status")
        st.bar_chart(pd.DataFrame(data).set_index("status"))

if __name__ == "__main__":
    show()

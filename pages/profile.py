import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_connection import run_query
 

def show():

    st.set_page_config(page_title="Profile & Ride History", layout="wide")

    if "user" not in st.session_state:
        st.error("You need to log in to view your profile.")
        st.stop()
    
    user = st.session_state["user"]
    user_id = user["user_id"]
    role = user["role"].lower()
    
    st.title("Profile & Ride History")
    st.caption(f"Welcome, {user['name']} ({role.title()})")

    if role == "passenger" or role == "both":
        passenger = run_query("SELECT * FROM passengers WHERE user_id = %s", (user_id,))
        if not passenger:
            st.warning("No passenger profile found.")
        else:
            p = passenger[0]
            st.subheader("Passenger Profile")
            col1, col2 = st.columns(2)
            col1.metric("Avg Rating", f"{p['avg_rating']:.1f}/5.0")
            col2.metric("Joined On", p['created_at'].strftime("%Y-%m-%d"))
    
            st.divider()
            st.subheader("📅 Ride History")
    
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
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No rides found yet.")

    if role == "driver" or role == "both":
        driver = run_query("SELECT * FROM drivers WHERE user_id = %s", (user_id,))
        if not driver:
            st.warning("No driver profile found.")
        else:
            d = driver[0]
            st.subheader("Driver Profile")
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Rating", f"{d['avg_rating']:.1f}/5.0")
            col2.metric("Total Rides", d['total_rides'])
            col3.metric("Joined On", d['created_at'].strftime("%Y-%m-%d"))
    
            st.divider()
            st.subheader("Performance Overview")
    
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
            col1.metric("Completed", stats["completed_rides"] or 0)
            col2.metric("Cancelled", stats["cancelled_rides"] or 0)
            col3.metric("Earnings", f"₹{stats['total_earnings'] or 0:,.0f}")
            col4.metric("Total Rides", stats["total_rides"])
    
            st.divider()
            st.subheader("Ride History")
    
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
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No rides found yet.")
    

    if role == "admin":
        st.subheader("🛠 System Overview")
    
        total_users = run_query("SELECT COUNT(*) AS cnt FROM users")[0]["cnt"]
        total_rides = run_query("SELECT COUNT(*) AS cnt FROM rides")[0]["cnt"]
        completed = run_query("SELECT COUNT(*) AS cnt FROM rides WHERE status='completed'")[0]["cnt"]
        total_revenue = run_query("SELECT SUM(total_fare) AS rev FROM rides WHERE status='completed'")[0]["rev"]
    
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", total_users)
        col2.metric("Total Rides", total_rides)
        col3.metric("Completed Rides", completed)
        col4.metric("Total Revenue", f"₹{total_revenue or 0:,.0f}")
    
        st.divider()
        st.subheader("Analytics")
        data = run_query("SELECT status, COUNT(*) AS count FROM rides GROUP BY status")
        st.bar_chart(pd.DataFrame(data).set_index("status"))

if __name__ == "__main__":
    show()
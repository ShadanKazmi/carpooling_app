import streamlit as st
import time
from utils.db_connection import get_connection
 
 
POLL_EVERY_SEC = 5
now = time.time()
last = st.session_state.get("_notif_last_poll", 0)
if now - last > POLL_EVERY_SEC:
    st.session_state["_notif_last_poll"] = now
    st.rerun()
 

def show():
    st.title("🔔 Notifications")
 
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in.")
        return
 
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT notification_id, message, created_at, is_read
        FROM notifications
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user["user_id"],))
    rows = cursor.fetchall()
 
    if not rows:
        st.info("No notifications yet.")
        return
    
    for n_id, msg, created_at, is_read in rows:
        style = "**" if is_read == 0 else ""
        st.write(f"{style}{msg}{style}")
        st.caption(created_at.strftime('%d %b %Y %I:%M %p'))
 
    if st.button("Mark all as read"):
        cursor.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (user["user_id"],))
        conn.commit()
        st.rerun()
 
    cursor.close()
    conn.close()
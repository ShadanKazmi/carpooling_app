import streamlit as st
from utils.db_connection import get_connection
from utils.ride_utils import get_driver_id
 
def _get_unread_notification_count(user_id: int) -> int:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS unread_count FROM notifications WHERE user_id=%s AND is_read=0",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return 0
        count = row[0]
        return int(count) if count is not None else 0
    except Exception:
        return 0
 
def navbar():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
 
    user = st.session_state.get("user")
    driver_id = get_driver_id(user["user_id"])
 
    unread_count = _get_unread_notification_count(user["user_id"]) if user else 0

    if driver_id:
        pages = ["Home", "Offer", "Rides", "Notifications", "Profile", "Map"]
    else:
        pages = ["Home", "Request", "Rides", "Notifications", "Profile", "Map"]
 
    cols = st.columns(len(pages))
    for i, page in enumerate(pages):
        label = page
        if page == "Notifications":
            if unread_count > 0:
                label = f"🔔 Notifications ({unread_count})"
            else:
                label = "🔔 Notifications"
 
        if cols[i].button(label, key=f"nav_{i}_{page}"):
            st.session_state.page = page
            st.rerun()
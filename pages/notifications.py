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
        .notif-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 50px 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
            animation: slideDown 0.6s ease-out;
            border-bottom: 4px solid #00d4ff;
        }
        
        .notif-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 10px;
            color: #00d4ff;
        }
        
        .notif-subtitle {
            font-size: 16px;
            opacity: 0.9;
            color: #e0e0e0;
        }
        
        /* Notification Card - Unread */
        .notif-unread {
            background: linear-gradient(135deg, #1e4d7b 0%, #16213e 100%);
            color: #00d4ff;
            border-radius: 12px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15);
            border-left: 5px solid #00d4ff;
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease-out;
            position: relative;
        }
        
        .notif-unread::before {
            content: "NEW";
            position: absolute;
            top: 10px;
            right: 10px;
            background: #00d4ff;
            color: #1a1a2e;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        
        .notif-unread:hover {
            transform: translateX(5px);
            box-shadow: 0 12px 35px rgba(0, 212, 255, 0.25);
        }
        
        /* Notification Card - Read */
        .notif-read {
            background: #16213e;
            color: #b0b0b0;
            border-radius: 12px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.08);
            border-left: 5px solid #00d4ff;
            transition: all 0.3s ease;
            opacity: 0.85;
        }
        
        .notif-read:hover {
            transform: translateX(3px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.12);
            opacity: 1;
        }
        
        /* Notification Icon */
        .notif-icon {
            font-size: 32px;
            margin-right: 15px;
            float: left;
        }
        
        /* Notification Message */
        .notif-message {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 10px;
            font-weight: 500;
        }
        
        /* Notification Time */
        .notif-time {
            font-size: 13px;
            opacity: 0.7;
            font-style: italic;
        }
        
        /* Mark Read Button */
        .stButton > button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
            color: #1a1a2e !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 30px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(3, 102, 214, 0.4) !important;
        }
        
        /* Empty State */
        .empty-notif {
            text-align: center;
            padding: 80px 40px;
            background: linear-gradient(135deg, #f0f7ff 0%, #e6f3ff 100%);
            border-radius: 15px;
            margin: 20px 0;
        }
        
        .empty-icon {
            font-size: 100px;
            margin-bottom: 30px;
            opacity: 0.6;
        }
        
        /* Stats Bar */
        .stats-bar {
            background: white;
            padding: 25px 30px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 8px 22px rgba(3, 102, 214, 0.12);
            display: flex;
            justify-content: space-around;
            align-items: center;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: 800;
            color: #0366d6;
        }
        
        .stat-label {
            font-size: 13px;
            color: #999;
            margin-top: 5px;
            font-weight: 600;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Page Header
    st.markdown("""
    <div class="notif-header">
        <div style="font-size: 60px; margin-bottom: 15px;">🔔</div>
        <div class="notif-title">Notifications</div>
        <div class="notif-subtitle">Stay updated with your ride activities</div>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.get("user")
    if not user:
        st.warning("⚠️ Please log in.")
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
        st.markdown("""
        <div class="empty-notif">
            <div class="empty-icon">📭</div>
            <h2 style="font-size: 32px; color: #0366d6; margin-bottom: 15px;">No Notifications</h2>
            <p style="font-size: 16px; color: #666;">You're all caught up! No new notifications at the moment.</p>
        </div>
        """, unsafe_allow_html=True)
        cursor.close()
        conn.close()
        return
    
    # Stats Bar
    total_notifs = len(rows)
    unread_count = sum(1 for r in rows if r[3] == 0)
    read_count = total_notifs - unread_count
    
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number">{total_notifs}</div>
            <div class="stat-label">Total Notifications</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">🔴 {unread_count}</div>
            <div class="stat-label">Unread</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">✓ {read_count}</div>
            <div class="stat-label">Read</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display Notifications
    for n_id, msg, created_at, is_read in rows:
        card_class = "notif-read" if is_read == 1 else "notif-unread"
        icon = "📬" if is_read == 0 else "📭"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="notif-icon">{icon}</div>
            <div class="notif-message">{msg}</div>
            <div class="notif-time">🕐 {created_at.strftime('%d %b %Y, %I:%M %p')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mark as Read Button
    if unread_count > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"✅ Mark All {unread_count} as Read"):
            cursor.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (user["user_id"],))
            conn.commit()
            st.success("✅ Notification marked as read!")
            st.rerun()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    show()

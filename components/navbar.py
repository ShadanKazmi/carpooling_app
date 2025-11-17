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
    
    # Dark Theme with Sky Blue Accents
    st.markdown("""
    <style>
        /* Navbar Container */
        .navbar-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            border-radius: 0;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            margin-bottom: 20px;
            border-bottom: 3px solid #00d4ff;
        }
        
        /* User Badge */
        .user-badge {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: #1a1a2e;
            padding: 15px 25px;
            border-radius: 12px;
            font-weight: 700;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
            margin-bottom: 15px;
            font-size: 16px;
            animation: fadeIn 0.6s ease-in;
        }
        
        /* Navigation Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
            color: #1a1a2e !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 20px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.5) !important;
            background: linear-gradient(135deg, #0099cc 0%, #00d4ff 100%) !important;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    <div class="navbar-container"></div>
    """, unsafe_allow_html=True)
    
    # User Info Badge
    if user:
        role_emoji = "🚗" if driver_id else "👤"
        st.markdown(f"""
        <div class="user-badge">
            {role_emoji} {user['name']} • {user['role'].upper()}
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation Buttons
    if driver_id:
        pages = ["Home", "Offer", "Rides", "Notifications", "Profile", "Map"]
        icons = ["🏠", "🚗", "📋", "🔔", "👤", "🗺️"]
    else:
        pages = ["Home", "Request", "Rides", "Notifications", "Profile", "Map"]
        icons = ["🏠", "🚖", "📋", "🔔", "👤", "🗺️"]
    
    cols = st.columns(len(pages))
    
    for i, (page, icon) in enumerate(zip(pages, icons)):
        label = f"{icon} {page}"
        
        if page == "Notifications" and unread_count > 0:
            label = f"{icon} {page} ({unread_count})"
            if cols[i].button(label, key=f"nav_{i}_{page}"):
                st.session_state.page = page
                st.rerun()
        else:
            if cols[i].button(label, key=f"nav_{i}_{page}"):
                st.session_state.page = page
                st.rerun()


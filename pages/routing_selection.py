import streamlit as st
from datetime import datetime, timedelta

class RouteSelectionPage:
    def __init__(self):
        self.role = st.session_state.get("role", None)D:\new_tEAM\carpooling_app
      
        self.from_location = st.session_state.get("from_location", "")
        self.to_location = st.session_state.get("to_location", "")
        self.route_date = st.session_state.get("route_date", datetime.today().date())
        self.route_time = st.session_state.get("route_time", datetime.now().time().replace(second=0, microsecond=0))

    def add_css(self):
        st.markdown("""
        <style>
        .main .block-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-top: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .main h1 { display: none; }
        .custom-route-header {
            background: linear-gradient(135deg, #5468ff 0%, #9f7aea 100%);
            color: white; padding: 38px 18px 38px 18px;
            border-radius: 22px;
            margin-bottom: 36px; box-shadow: 0 10px 25px 0 rgba(70,90,200,0.22);
            font-size: 2.5rem; font-weight: 800; text-align: center;
            letter-spacing: 0.5px; position: relative; overflow: hidden;
            border: 2.5px solid rgba(255, 255, 255, 0.22);
        }
        .custom-route-header::after {
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle, rgba(255,255,255,0.11) 0%, transparent 80%);
            z-index: 0;
        }
        .custom-route-header .emoji {
            font-size: 2.2rem;
            margin-right: 12px;
            vertical-align: middle;
        }
        .custom-route-header span { position: relative; z-index: 1; }
        .main h3 {
            background: linear-gradient(135deg, #6c6bd0 0%, #8b5cf6 100%);
            color: white !important; padding: 15px 20px; border-radius: 12px;
            margin: 30px 0 20px 0; box-shadow: 0 4px 12px rgba(108, 107, 208, 0.3);
            text-align: center; font-size: 1.4rem; font-weight: 600;
        }
        .stButton > button:not([key^="time_option_"]) {
            background: #6c6bd0; color: white; border: none; padding: 15px 30px;
            border-radius: 12px; font-size: 16px; font-weight: 600;
            transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(108, 107, 208, 0.3);
            margin: 10px 5px; min-width: 120px;
        }
        .stButton > button:not([key^="time_option_"]):hover {
            background: #5a59c7;
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(108, 107, 208, 0.4);
        }
        </style>
        """, unsafe_allow_html=True)

    def render_header(self):
        st.markdown(
            '''
            <div class="custom-route-header">
                <span class="emoji">🗺️</span>
                <span>Route Selection</span>
            </div>
            ''', unsafe_allow_html=True)

    def require_login(self):
        if not self.role:
            st.warning("Please log in first.")
            st.session_state.page = "login"
            st.rerun()
            return False
        return True

    def render_form(self):
        self.from_location = st.text_input("From Location *", value=self.from_location)
        self.to_location = st.text_input("To Location *", value=self.to_location)
        self.route_date = st.date_input("Date *", value=self.route_date)
        self.route_time = st.time_input("Preferred Time *", value=self.route_time)

        # Update session state 
        st.session_state.from_location = self.from_location
        st.session_state.to_location = self.to_location
        st.session_state.route_date = self.route_date
        st.session_state.route_time = self.route_time

    def render_time_options(self):
        st.subheader("Available Time Options")
        base_time = datetime.combine(self.route_date, self.route_time)
        time_options = []
        for offset in range(-4, 5):  # -2 hours to +2 hours in 30-min steps
            delta = timedelta(minutes=30 * offset)
            option_time = (base_time + delta).time()
            time_options.append(option_time)
        cols = st.columns(4)
        for i, option_time in enumerate(time_options):
            with cols[i % 4]:
                if st.button(option_time.strftime("%I:%M %p"), key=f"time_option_{i}", use_container_width=True):
                    st.session_state.route_time = option_time
                    st.rerun()

    def handle_continue(self):
        if not self.from_location.strip() or not self.to_location.strip():
            st.error("Please fill in both From and To locations.")
        else:
            st.session_state.route_info = {
                "from": self.from_location.strip(),
                "to": self.to_location.strip(),
                "date": str(self.route_date),
                "time": self.route_time.strftime("%H:%M:%S"),
            }
            if self.role == "passenger":
                st.session_state.page = "show_drivers"
            else:
                st.session_state.page = "driver_dashboard"
            st.rerun()

    def handle_back(self):
        st.session_state.page = "login"
        st.rerun()

    def show(self):
        self.add_css()
        self.render_header()
        if not self.require_login():
            return
        self.render_form()
        self.render_time_options()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Continue"):
                self.handle_continue()
        with col2:
            if st.button("Back"):
                self.handle_back()

def show():
    RouteSelectionPage().show()
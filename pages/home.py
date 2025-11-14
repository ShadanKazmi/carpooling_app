import streamlit as st
from components.navbar import navbar
 
def home():
    navbar()
 
    page = st.session_state.get("page", "Home")
 
    if page == "Home":
        st.markdown("""
        <style>
            .hero {
                text-align: center;
                padding: 3rem 1rem;
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: white;
                border-radius: 16px;
                margin-bottom: 3rem;
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            .hero h1 { font-size: 3rem; color: #22d3ee; font-weight: 800; }
            .hero p { font-size: 1.2rem; color: #e2e8f0; margin-top: 0.5rem; }
            .features {
                display: flex; justify-content: center; flex-wrap: wrap; gap: 2rem;
            }
            .card {
                background-color: #1e293b;
                border-radius: 12px;
                padding: 1.5rem;
                width: 280px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                transition: transform 0.2s ease;
            }
            .card:hover { transform: translateY(-5px); }
            .card h3 { color: #22d3ee; font-size: 1.3rem; }
        </style>
 
        <div class="hero">
            <h1>🚗 CarPoolConnect</h1>
            <p>Share rides, save money, and travel smarter.</p>
        </div>
 
        <div class="features">
            <div class="card">
                <h3>Smart Matching</h3>
                <p>Find rides based on best routes.</p>
            </div>
            <div class="card">
                <h3>Fair Pricing</h3>
                <p>Transparent fare calculation system.</p>
            </div>
            <div class="card">
                <h3>Safety First</h3>
                <p>Ratings ensure trust and reliability.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
    elif page == "Request":
        from pages.request import show
        show()
 
    elif page == "Offer":
        from pages.offer import show
        show()
 
    elif page == "Rides":
        from pages.rides import show
        show()
 
    elif page == "Profile":
        from pages.profile import show
        show()

    elif page == "Notifications":
        from pages.notifications import show
        show()
 
    elif page == "Map":
        from pages.ride import show
        show()
 
    else:
        st.error("Page not found.")
 
if __name__ == "__main__":
    home()
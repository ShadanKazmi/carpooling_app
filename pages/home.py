import streamlit as st
from components.navbar import navbar
from utils.setBackground import add_bg_from_local


def home():

    add_bg_from_local("assets/image.png")

    navbar()

    query_params = st.query_params
    page = query_params.get("page", ["Home"])[0]
    
    
    if page == "Home":
        st.markdown(
            """
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
            .hero h1 {
                font-size: 3rem;
                color: #22d3ee;
                font-weight: 800;
            }
            .hero p {
                font-size: 1.2rem;
                color: #e2e8f0;
                margin-top: 0.5rem;
            }
            .features {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 2rem;
            }
            .card {
                background-color: #1e293b;
                border-radius: 12px;
                padding: 1.5rem;
                width: 300px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.35);
            }
            .card h3 {
                color: #22d3ee;
                font-size: 1.3rem;
            }
            .cta-buttons {
                margin-top: 2rem;
            }
            .cta-buttons button {
                font-size: 1rem;
                padding: 0.75rem 1.5rem;
                border-radius: 10px;
                background-color: #22d3ee;
                color: #0f172a;
                font-weight: 600;
                border: none;
                cursor: pointer;
                transition: background-color 0.2s ease;
            }
            .cta-buttons button:hover {
                background-color: #0ea5e9;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
        st.markdown(
            """
            <div class="hero">
                <h1>🚗 CarPoolConnect</h1>
                <p>Share rides, save money, and travel smarter across Indian cities.</p>
                <div class="cta-buttons">
                    <a href="?page=Request"><button>Request a Ride</button></a>
                    <a href="?page=Offer"><button>Offer a Ride</button></a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
        st.markdown(
            """
            <div class="features">
                <div class="card">
                    <h3>Smart Route Matching</h3>
                    <p>Automatically match passengers and drivers with optimal routes using real map data.</p>
                </div>
                <div class="card">
                    <h3>Fair Fare Calculation</h3>
                    <p>Transparent fare estimates based on distance, route safety, and number of passengers.</p>
                </div>
                <div class="card">
                    <h3>Safety Insights</h3>
                    <p>Get live updates on dangerous areas along your route and choose safer alternatives.</p>
                </div>
                <div class="card">
                    <h3>Reliable Ratings</h3>
                    <p>Track performance and trust through a rating system for both drivers and passengers.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    elif page == "Request":
        st.title("Request a Ride")
        st.info("Request a ride page coming soon!")
    
    elif page == "Offer":
        st.title(" Offer a Ride")
        st.info("Offer a ride page coming soon!")
    
    elif page == "Rides":
        st.title("My Rides")
        st.info("View your active and past rides here.")
    
    elif page == "Profile":
        st.title("Your Profile")
        st.info("Profile page coming soon!")
    
    elif page == "Map":
        st.title("Route and Dangerous Area Map")
        st.info("Interactive map integration coming soon!")
    
    else:
        st.error("Page not found.")
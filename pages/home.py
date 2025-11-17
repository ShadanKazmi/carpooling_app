import streamlit as st
from components.navbar import navbar

def home():
    navbar()
    
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
        /* Hero Banner - Dark with Sky Blue */
        .hero-banner {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0d3b66 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 0;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
            animation: slideIn 0.8s ease-out;
            border-bottom: 4px solid #00d4ff;
        }
        
        .hero-title {
            font-size: 52px;
            font-weight: 800;
            margin-bottom: 15px;
            letter-spacing: -1px;
            color: #00d4ff;
        }
        
        .hero-subtitle {
            font-size: 20px;
            opacity: 0.9;
            margin-bottom: 30px;
            font-weight: 300;
            color: #e0e0e0;
        }
        
        .hero-cta {
            display: inline-block;
            background: #00d4ff;
            color: #1a1a2e;
            padding: 12px 35px;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        }
        
        .hero-cta:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5);
        }
        
        /* Stats Section - Dark */
        .stats-container {
            display: flex;
            justify-content: space-around;
            padding: 40px 20px;
            margin-bottom: 40px;
            background: linear-gradient(to bottom, #16213e 0%, #0f3460 100%);
            border-radius: 0;
            gap: 20px;
            border: 2px solid #00d4ff;
        }
        
        .stat-card {
            background: #1a1a2e;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            flex: 1;
            border-left: 5px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2);
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #b0b0b0;
            font-weight: 600;
        }
        
        /* Feature Cards - Dark */
        .feature-card {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: all 0.3s ease;
            border-top: 4px solid #00d4ff;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 35px rgba(0, 212, 255, 0.2);
            border-top-color: #00d4ff;
        }
        
        .feature-icon {
            font-size: 42px;
            margin-bottom: 15px;
            display: block;
        }
        
        .feature-title {
            font-size: 18px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .feature-description {
            font-size: 14px;
            color: #b0b0b0;
            line-height: 1.6;
        }
        
        /* Section Headers - Dark */
        .section-header {
            font-size: 32px;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #00d4ff;
            display: inline-block;
        }
        
        /* Testimonial Cards - Dark */
        .testimonial-card {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #00d4ff;
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .testimonial-card:hover {
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.2);
            transform: translateX(5px);
        }
        
        .testimonial-text {
            font-style: italic;
            color: #e0e0e0;
            margin-bottom: 10px;
            font-size: 15px;
            line-height: 1.6;
        }
        
        .testimonial-author {
            font-weight: 600;
            color: #00d4ff;
            font-size: 14px;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    page = st.session_state.get("page", "Home")
    
    if page == "Home":
        # Hero Banner
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">🚗 CarPoolConnect</div>
            <div class="hero-subtitle">Share Rides, Save Money, Travel Smarter</div>
            <a href="#" class="hero-cta">Get Started Now</a>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats Section
        st.markdown("""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">10K+</div>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">50K+</div>
                <div class="stat-label">Rides Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">₹2M+</div>
                <div class="stat-label">Money Saved</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Features Section
        st.markdown('<div class="section-header">🌟 Why Choose Us?</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🎯</span>
                <div class="feature-title">Smart Matching</div>
                <div class="feature-description">Find rides based on best routes and preferences using our intelligent matching algorithm.</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">💰</span>
                <div class="feature-title">Fair Pricing</div>
                <div class="feature-description">Transparent fare calculation system ensures everyone gets the best value for money.</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🛡️</span>
                <div class="feature-title">Safety First</div>
                <div class="feature-description">Ratings and reviews ensure trust and reliability for all our community members.</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional Features
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">📱</span>
                <div class="feature-title">Real-Time Tracking</div>
                <div class="feature-description">Track your ride in real-time with live GPS updates and notifications.</div>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">⭐</span>
                <div class="feature-title">Verified Users</div>
                <div class="feature-description">All users are verified with ratings to ensure safe and reliable rides.</div>
            </div>
            """, unsafe_allow_html=True)
        with col6:
            st.markdown("""
            <div class="feature-card">
                <span class="feature-icon">🌍</span>
                <div class="feature-title">Eco-Friendly</div>
                <div class="feature-description">Reduce carbon footprint by sharing rides and contributing to a greener planet.</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Testimonials
        st.markdown('<div class="section-header">💬 What Our Users Say</div>', unsafe_allow_html=True)
        col7, col8 = st.columns(2)
        with col7:
            st.markdown("""
            <div class="testimonial-card">
                <div class="testimonial-text">"Best carpooling app I've used! Saved me tons of money on my daily commute."</div>
                <div class="testimonial-author">⭐⭐⭐⭐⭐ Priya S., Mumbai</div>
            </div>
            """, unsafe_allow_html=True)
        with col8:
            st.markdown("""
            <div class="testimonial-card">
                <div class="testimonial-text">"Safe, reliable, and easy to use. The matching system is incredibly smart!"</div>
                <div class="testimonial-author">⭐⭐⭐⭐⭐ Rahul K., Delhi</div>
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
        st.error("❌ Page not found.")

if __name__ == "__main__":
    home()

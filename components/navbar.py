import streamlit as st
 
def navbar():
    st.markdown("""
        <style>
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #111827;
            padding: 1rem 2rem;
            color: white;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        .navbar h1 {
            font-size: 1.5rem;
            color: #22d3ee;
        }
        .nav-links {
            display: flex;
            gap: 1.5rem;
        }
        .nav-link {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }
        .nav-link:hover {
            color: #22d3ee;
        }
        </style>
    """, unsafe_allow_html=True)
 
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("<h1>🚗 CarPoolConnect</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="nav-links">
            <a class="nav-link" href="?page=Home">Home</a>
            <a class="nav-link" href="?page=Request">Request a Ride</a>
            <a class="nav-link" href="?page=Offer">Offer a Ride</a>
            <a class="nav-link" href="?page=Rides">My Rides</a>
            <a class="nav-link" href="?page=Profile">Profile</a>
        </div>
        """, unsafe_allow_html=True)
import streamlit as st
 
def navbar():
    st.markdown(
        """
        <style>
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, #0f172a, #1e293b);
            padding: 1rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .navbar h1 {
            font-size: 1.5rem;
            margin: 0;
            color: #22d3ee;
            font-weight: 700;
        }
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        .nav-link {
            color: #e2e8f0;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .nav-link:hover {
            color: #22d3ee;
            transform: scale(1.05);
        }
        .active-link {
            color: #22d3ee;
            border-bottom: 2px solid #22d3ee;
            padding-bottom: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
 
    query_params = st.query_params
    current_page = query_params.get("page", ["Home"])[0]
 
    pages = {
        "Home": "Home",
        "Offer": "Offer Ride",
        "Request": "Request Ride",
        "Profile": "Profile",
        "Map": "Map"
    }
 
    links_html = ""
    for page, label in pages.items():
        active_class = "active-link" if page == current_page else ""
        links_html += f'<a class="nav-link {active_class}" href="?page={page}">{label}</a>'
 
    st.markdown(
        f"""
        <div class="navbar">
            <h1>CarPoolConnect</h1>
            <div class="nav-links">
                {links_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
import streamlit as st
def navbar(active_page="Home"):
   st.markdown("""
<style>
       .navbar {
           display: flex;
           justify-content: space-between;
           align-items: center;
           background-color: #0f172a;
           padding: 1rem 2rem;
           color: white;
           border-radius: 8px;
           margin-bottom: 2rem;
           box-shadow: 0 4px 8px rgba(0,0,0,0.2);
       }
       .navbar h1 {
           font-size: 1.6rem;
           color: #06b6d4;
           margin: 0;
       }
       .nav-links {
           display: flex;
           gap: 1.5rem;
       }
       .nav-link {
           color: #e2e8f0;
           text-decoration: none;
           font-weight: 500;
           padding: 0.4rem 0.8rem;
           border-radius: 5px;
           transition: all 0.3s ease;
       }
       .nav-link:hover {
           background-color: #1e293b;
           color: #06b6d4;
       }
       .active-link {
           background-color: #06b6d4;
           color: white !important;
       }
</style>
   """, unsafe_allow_html=True)
   links = [
       ("Home", "🏠 Home"),
       ("Request", "🚖 Request a Ride"),
       ("Offer", "🚗 Offer a Ride"),
       ("Rides", "🧾 My Rides"),
       ("Profile", "👤 Profile")
   ]
   nav_links_html = ""
   for key, label in links:
       active_class = "active-link" if key == active_page else ""
       nav_links_html += f'<a class="nav-link {active_class}" href="?page={key}">{label}</a>'
   st.markdown(f"""
<div class="navbar">
<h1>🚗 CarPoolConnect</h1>
<div class="nav-links">{nav_links_html}</div>
</div>
   """, unsafe_allow_html=True)
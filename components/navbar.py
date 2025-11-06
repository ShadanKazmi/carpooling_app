import streamlit as st
 
def navbar():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
 
    pages = ["Home", "Request", "Offer", "Rides", "Profile", "Map"]
    
    st.markdown("""
        <style>
            .nav-container {
                display: flex;
                gap: 1.5rem;
                background: #0f172a;
                padding: 1rem 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .nav-button {
                color: #e2e8f0;
                font-weight: 500;
                cursor: pointer;
            }
            .nav-active {
                color: #22d3ee;
                border-bottom: 2px solid #22d3ee;
                padding-bottom: 3px;
                font-weight: 700;
            }
        </style>
    """, unsafe_allow_html=True)
 
    cols = st.columns(len(pages)+2)
    for i, page in enumerate(pages):
        if cols[i].button(page, key=f"nav_{page}"):
            st.session_state.page = page
            st.rerun()
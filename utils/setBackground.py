import base64
from pathlib import Path
import streamlit as st
def add_bg_from_local(image_path):
        image_path = Path(image_path)
        with open(image_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: rgba(0, 0, 0, 0);
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
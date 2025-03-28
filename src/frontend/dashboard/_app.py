import streamlit as st
import os
import sys
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Home | SpeakWise",
    page_icon="📞",
    layout="wide"
)

# Add header to say we're redirecting
st.markdown("# Redirecting to Home...")

# Auto-redirect to Home page 
st.markdown(
    """
    <meta http-equiv="refresh" content="0; url='/?page=Home'" />
    """,
    unsafe_allow_html=True
)
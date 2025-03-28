#!/usr/bin/env python3

import os
import streamlit as st

# Define page names for Streamlit sidebar
PAGES = {
    "Home.py": "Home",
    "pages/call_monitor.py": "Call Monitor",
    "pages/system_config.py": "System Config"
}

# Set environment variables to rename pages
for page_path, display_name in PAGES.items():
    base_name = os.path.basename(page_path).split('.')[0]
    os.environ[f"STREAMLIT_PAGE_NAME_{base_name}"] = display_name

# Hide the "app" entry
st.markdown("""
<style>
    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }
</style>
""", unsafe_allow_html=True)
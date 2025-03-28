#\!/usr/bin/env python3

# Define page names for Streamlit sidebar
# This file is automatically loaded by Streamlit to rename pages

import os

PAGES = {
    "app": "Home",
    "pages/call_monitor": "Call Monitor",
    "pages/system_config": "System Config"
}

def rename_pages():
    for page_ref, display_name in PAGES.items():
        os.environ[f"STREAMLIT_PAGE_NAME_{page_ref}"] = display_name

rename_pages()


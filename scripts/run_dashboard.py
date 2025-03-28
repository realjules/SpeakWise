#!/usr/bin/env python3
"""
Script to run the SpeakWise dashboard.
This starts the Streamlit dashboard application.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_dashboard():
    """Run the Streamlit dashboard application"""
    logger.info("Starting SpeakWise dashboard")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Path to the dashboard app (now renamed to Home.py)
    app_path = script_dir.parent / "src" / "frontend" / "Home.py"
    
    if not app_path.exists():
        logger.error(f"Dashboard app not found at {app_path}")
        return 1
    
    # Run Streamlit
    cmd = ["streamlit", "run", str(app_path), "--server.port", "8501"]
    
    try:
        # Run the process
        process = subprocess.run(cmd)
        return process.returncode
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_dashboard())
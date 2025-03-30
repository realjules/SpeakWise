#!/usr/bin/env python3
"""
Launcher script for the Chainlit SpeakWise Voice Assistant.
This script sets up the environment and launches the Chainlit app.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

def main():
    """Main entry point for the launcher script."""
    # Check if .env file exists
    env_file = ROOT_DIR / "chainlit_app" / ".env"
    env_example = ROOT_DIR / "chainlit_app" / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("No .env file found. Creating from example...")
        with open(env_example, "r") as example, open(env_file, "w") as env:
            env.write(example.read())
        print(f"Created .env file at {env_file}. Please edit it to add your API keys.")
        print("Exiting. Run this script again after configuring your API keys.")
        return
    
    # Launch the Chainlit app
    app_path = ROOT_DIR / "chainlit_app" / "app.py"
    print(f"Starting SpeakWise Voice Assistant at {app_path}...")
    
    try:
        subprocess.run(["chainlit", "run", str(app_path)], check=True)
    except KeyboardInterrupt:
        print("\nShutting down SpeakWise Voice Assistant...")
    except Exception as e:
        print(f"Error running Chainlit app: {e}")
        print("\nMake sure you have installed all dependencies with:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
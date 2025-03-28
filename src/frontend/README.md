# Streamlit Dashboard for SpeakWise

This dashboard provides a web-based interface for monitoring and configuring the SpeakWise system.

## Features

- Real-time dashboard for monitoring system activity
- Call volume and performance metrics
- Call status monitoring and analytics
- System configuration interface
- Hourly distribution and duration analysis

## Setup and Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   # Using the provided script
   python scripts/run_dashboard.py
   
   # Or directly with streamlit
   cd src/frontend
   streamlit run Home.py
   ```

3. Access the dashboard in your browser at `http://localhost:8501`

## Directory Structure

- `Home.py` - Main Streamlit application entry point with dashboard overview
- `pages/` - Additional pages for the dashboard
  - `1_Call Monitor.py` - Real-time call monitoring
  - `2_System Config.py` - System configuration interface
- `static/` - Images and other static assets
  - `images/` - Contains logo and other interface images

## Usage

- The main dashboard shows key metrics and real-time call activity
- Use the sidebar to navigate between different sections
- View call volume trends and completion rates on the overview tab
- Analyze call distributions by hour and duration on the analytics tab
- The System Config page allows modifying system settings
- Call Monitor provides real-time updates on active calls

## Development

To add new pages to the dashboard:

1. Create a new Python file in the `pages/` directory
2. Name it with a number prefix for proper ordering (e.g. `3_New Page.py`)
3. Implement your Streamlit interface in the file
4. The file will automatically appear in the sidebar navigation

## Notes for Deployment

- For production deployment, consider using:
  - Streamlit Cloud for simple hosting
  - Docker container for more controlled environments
  - Nginx as a reverse proxy for custom domains
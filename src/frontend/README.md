# Streamlit Dashboard for SpeakWise

This dashboard provides a web-based interface for monitoring and configuring the SpeakWise system.

## Features

- Real-time dashboard for monitoring system activity
- Call monitoring and management
- Transaction tracking and analysis
- System configuration interface
- User management

## Setup and Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   cd src/frontend/dashboard
   streamlit run app.py
   ```

3. Access the dashboard in your browser at `http://localhost:8501`

## Directory Structure

- `app.py` - Main Streamlit application entry point
- `pages/` - Additional pages for the dashboard
  - `call_monitor.py` - Real-time call monitoring
  - `system_config.py` - System configuration interface
  - `transaction_log.py` - Payment transaction tracking

## Usage

- The main dashboard shows key metrics and real-time activity
- Use the sidebar to navigate between different sections
- The configuration section allows modifying system settings
- Call monitor provides real-time updates on active calls
- Transaction log tracks all payments processed by the system

## Development

To add new pages to the dashboard:

1. Create a new Python file in the `pages/` directory
2. Implement your Streamlit interface in the file
3. The file will automatically appear in the sidebar navigation

## Notes for Deployment

- For production deployment, consider using:
  - Streamlit Cloud for simple hosting
  - Docker container for more controlled environments
  - Nginx as a reverse proxy for custom domains
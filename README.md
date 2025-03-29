# SpeakWise

Voice AI Agent for Irembo e-government services in Rwanda.

## Overview

SpeakWise is a voice-based AI agent that helps users access e-government services in Rwanda through the Irembo platform. The system allows users to make requests by voice, which are then processed by an AI agent that navigates the Irembo website to complete the task.

## System Components

- **Browser Agent**: Automates interactions with the Irembo website
- **SMS Notifications**: Sends status updates to users via SMS
- **Dashboard**: Monitors system activity and performance

## Setup Instructions

### 1. Environment Setup

Create a `.env` file with the following variables:

```
# Authentication credentials
PASSWORD=your_password_here
PHONE_NUMBER=your_phone_number_here
NATIONAL_ID=your_national_id_here

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
PINDO_API_KEY=your_pindo_api_key_here
PINDO_SENDER_ID=SpeakWise

# Optional configuration
HEADLESS=false  # Set to false to see browser when running scripts
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Browser Agent

The browser agent can be run with the following command:

```bash
python scripts/run_browser_agent.py --service birth_certificate --district Gasabo --sector Jali
```

### Available Services

- `birth_certificate`: Apply for a birth certificate
- `driving_license`: Register for a driving license exam

### Command Line Options

- `--service`: Service to run (birth_certificate or driving_license)
- `--for-self`: Whether the birth certificate is for self (default: True)
- `--district`: District for processing office (default: Gasabo)
- `--sector`: Sector for processing office (default: Jali)
- `--reason`: Reason for application (default: Education)
- `--test-type`: Type of driving test
- `--headless`: Run in headless mode
- `--model`: LLM model to use (default: gpt-4o)
- `--verbose`: Enable verbose output
- `--disable-sms`: Disable SMS notifications
- `--disable-dashboard`: Disable dashboard updates

## Running the Dashboard

To start the dashboard:

```bash
python scripts/run_dashboard.py
```

## System Architecture

The SpeakWise system is structured around three main components:

1. **Frontend System**
   - Handles user interactions and administrative interfaces
   - Provides dashboard for monitoring system activity

2. **Core Engine**
   - Processes natural language to determine user intent
   - Coordinates actions between components

3. **Browser-based AI Agent**
   - Interacts with the Irembo website to execute user requests
   - Uses AI to navigate through complex forms

## Integration Features

The system integrates multiple components to provide a seamless experience:

- **SMS Integration**: Automatic notifications are sent when tasks are completed
- **Dashboard Integration**: All activity is tracked and displayed in the dashboard
- **Analytics**: System performance metrics are collected and visualized

## License

This project is proprietary and confidential. All rights reserved.

## Contact

For questions or support, please contact the SpeakWise team.
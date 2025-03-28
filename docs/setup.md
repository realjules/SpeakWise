# SpeakWise Setup Guide

This document provides instructions for setting up and running the SpeakWise system.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- A Pindo account with API key (for telephony and WhatsApp)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/speakwise.git
   cd speakwise
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your configuration:
   ```
   # Pindo API Configuration
   PINDO_API_KEY=your_pindo_api_key
   WHATSAPP_SENDER_ID=your_whatsapp_number
   
   # System Configuration
   FLASK_SECRET_KEY=a_random_secret_key
   DATABASE_URL=sqlite:///speakwise.db
   
   # Environment (development, testing, production)
   ENVIRONMENT=development
   ```

## Running the System

### Dashboard

To run the dashboard:

```bash
python scripts/run_dashboard.py
```

This will start the Streamlit dashboard on port 8501. You can access it at http://localhost:8501

### Telephony API

To run the telephony API server:

```bash
python scripts/run_telephony_api.py
```

This will start the Flask server on port 5000. It will handle incoming calls and webhooks from Pindo.

## Testing the Integration

### Test Telephony

To test making a call:

```bash
python scripts/test_telephony.py --test call --api-key your_pindo_api_key --phone +250712345678
```

To test the webhook handler:

```bash
python scripts/test_telephony.py --test webhook --call-id call_id_from_previous_test
```

To run the telephony API server:

```bash
python scripts/test_telephony.py --test server
```

### Test WhatsApp Integration

To test sending a WhatsApp message:

```bash
python scripts/test_whatsapp.py --test message --api-key your_pindo_api_key --sender-id your_whatsapp_number --recipient +250712345678 --message "Hello from SpeakWise"
```

To test sending a document:

```bash
python scripts/test_whatsapp.py --test document --api-key your_pindo_api_key --sender-id your_whatsapp_number --recipient +250712345678 --document path/to/document.pdf
```

To test sending a receipt:

```bash
python scripts/test_whatsapp.py --test receipt --api-key your_pindo_api_key --sender-id your_whatsapp_number --recipient +250712345678
```

## Pindo Configuration

### API Key

You need to get an API key from Pindo:

1. Sign up at [Pindo](https://pindo.io/)
2. Create an API key in your account dashboard
3. Add the API key to your `.env` file

### Webhook URL

For the telephony integration to work, you need to configure a webhook URL in your Pindo account:

1. Go to your Pindo account dashboard
2. Navigate to Voice > Webhooks
3. Add a new webhook with your SpeakWise API URL (e.g., `https://yourdomain.com/telephony/webhook`)

If you're testing locally, you can use a tool like [ngrok](https://ngrok.com/) to create a public URL:

```bash
ngrok http 5000
```

Then use the ngrok URL (e.g., `https://abc123.ngrok.io/telephony/webhook`) in your Pindo configuration.

## Troubleshooting

### API Connection Issues

If you're having trouble connecting to the Pindo API:

1. Verify your API key is correct
2. Check your internet connection
3. Ensure you have proper permissions in your Pindo account

### WhatsApp Template Issues

If WhatsApp templates aren't working:

1. Make sure your templates are approved in the Pindo dashboard
2. Verify the template names match exactly
3. Check that the number of parameters in your code matches the template

### Dashboard Not Loading

If the dashboard doesn't load:

1. Verify Streamlit is installed (`pip install streamlit`)
2. Check that you're running from the correct directory
3. Look for any error messages in the console
# SpeakWise Telephony Interface Guide

This guide explains how to set up and use the SpeakWise Telephony Interface.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Create a `.env` file in the project root with the following settings:
   ```
   # Pindo API Configuration
   PINDO_API_KEY=your_pindo_api_key
   PINDO_SENDER_ID=PindoTest
   
   # Telephony Configuration
   TELEPHONY_WEBHOOK_URL=https://your-domain.com/telephony/webhook
   ```

3. **Start the API server**:
   ```bash
   # Start the API server on the default port (5000)
   python scripts/run_telephony_api.py
   
   # Or specify a different port
   python scripts/run_telephony_api.py --port 8080
   
   # Provide API key directly
   python scripts/run_telephony_api.py --api-key YOUR_PINDO_API_KEY
   ```

4. **Expose local server (for testing)**:
   To receive webhooks from Pindo, you need a public URL. For local development, use a tool like ngrok:
   ```bash
   ngrok http 5000
   ```
   Then update your Pindo webhook URL to the ngrok URL (e.g., `https://abc123.ngrok.io/telephony/webhook`).

## Using the API

### 1. Making an outbound call

```bash
curl -X POST http://localhost:5000/telephony/call \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+250712345678",
    "metadata": {
      "purpose": "reminder",
      "service": "birth_certificate"
    }
  }'
```

### 2. Ending a call

```bash
curl -X DELETE http://localhost:5000/telephony/call/CALL_ID
```

### 3. Sending DTMF tones

```bash
curl -X POST http://localhost:5000/telephony/call/CALL_ID/dtmf \
  -H "Content-Type: application/json" \
  -d '{
    "digits": "123"
  }'
```

### 4. Playing audio in a call

```bash
curl -X POST http://localhost:5000/telephony/call/CALL_ID/play \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/audio.wav"
  }'
```

### 5. Getting active calls

```bash
curl -X GET http://localhost:5000/telephony/calls
```

### 6. Getting information about a specific call

```bash
curl -X GET http://localhost:5000/telephony/call/CALL_ID
```

## Webhooks

Pindo will send webhooks to the configured URL. The telephony API handles these webhooks automatically.

### Configuring Pindo Webhooks

In your Pindo dashboard:
1. Go to Settings > Webhooks
2. Add a new webhook for voice events
3. Enter the URL: `https://your-domain.com/telephony/webhook`
4. Select the event types to receive (call.initiated, call.answered, call.completed, call.failed)

## Architecture

The Telephony Interface consists of the following components:

1. **PindoAdapter**: Interfaces with the Pindo API for making calls, ending calls, etc.
2. **AudioRouter**: Handles bidirectional audio streaming between callers and the speech processor
3. **CallHandler**: Manages call sessions and coordinates between components
4. **API Layer**: Provides HTTP endpoints for interacting with the Telephony Interface

## Troubleshooting

### Common Issues

1. **Webhook not received**:
   - Check that your webhook URL is publicly accessible
   - Verify that Pindo is properly configured to send webhooks
   - Check logs for any errors in processing webhooks

2. **Call initiation fails**:
   - Verify your Pindo API key is correct
   - Check that you have sufficient credits in your Pindo account
   - Ensure the phone number format is correct (including country code)

3. **Audio not working**:
   - Check that the speech processor is properly initialized
   - Verify audio format compatibility
   - Check logs for any errors in audio processing

### Logs

Logs are written to `telephony_api.log` in the project root directory.

## Integration with SMS

The Telephony Interface works alongside the SMS functionality to provide a complete communication solution:

1. **Voice Conversations**: Users interact with the system via phone calls
2. **SMS Notifications**: Users receive notifications about task completion and document availability via SMS

This dual-channel approach ensures effective communication throughout the service workflow.
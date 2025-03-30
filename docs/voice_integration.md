# SpeakWise Voice Integration

This document explains how to use the OpenAI voice integration features in SpeakWise.

## Overview

SpeakWise now includes integration with OpenAI's models for:
1. Speech-to-text conversion
2. Natural language processing
3. AI-powered responses

This allows for more dynamic and realistic conversation simulations in the Live Conversation dashboard.

## Setup

### Requirements

1. An OpenAI API key is required to use these features
2. Install the required packages:
   ```bash
   pip install openai python-dotenv
   ```

### Configuration

1. Add your OpenAI API key to the `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Verify that `openai_helper.py` exists in the `src/frontend/pages/` directory.
   If it doesn't exist, you can manually copy it there from our repository.

3. Restart the dashboard to apply the changes:
   ```bash
   python scripts/run_dashboard.py
   ```

### Troubleshooting Common Issues

If you encounter any issues:

1. **Import errors**: Try installing specific versions:
   ```bash
   pip install openai==1.6.0 python-dotenv==1.0.0
   ```

2. **"No module named 'openai_helper'"**: Make sure the `openai_helper.py` file is in the same directory as `2_Live Conversation.py` (in `src/frontend/pages/`).

3. **OpenAI API errors**: Check that your API key is valid and correctly formatted in the `.env` file.

4. **"File not found" errors**: Make sure all paths in your installation are correctly set up.

## Using the Voice Integration

### Live Conversation Page

1. Start by simulating a new call with the "Use OpenAI for responses" option checked
2. Navigate to the Voice Integration section at the bottom of the page
3. Click "Record Voice" to simulate voice input (in a real implementation, this would capture actual audio)
4. Click "Stop Recording" to simulate ending the recording
5. Review the transcribed text
6. Click "Send to AI" to process the voice input with OpenAI and generate a response

### Custom Message Input

When sending custom messages in the conversation:
1. If OpenAI is enabled for the call, responses will be generated using the AI
2. If OpenAI is disabled, responses will use the standard simulated pattern

## Technical Implementation

The voice integration is implemented in several components:

- `speech_processor.py`: Handles speech-to-text and text-to-speech conversion using OpenAI
- `2_Live Conversation.py`: Modified to include voice recording interface and OpenAI integration
- `api.py`: Enhanced with methods for handling AI-generated responses

## Limitations

In the current implementation:
- Voice recording is simulated with predefined messages
- Actual audio capture is not implemented (but the code structure supports it)
- Text-to-speech playback is not implemented (but the code supports it)

## Future Enhancements

Potential improvements for the voice integration:
1. Implement actual browser-based audio capture
2. Add text-to-speech playback of AI responses
3. Use WebSockets for streaming voice data
4. Enhance the voice visualization components

## Troubleshooting

Common issues:
- **"OpenAI integration not available"**: Check your API key in the `.env` file
- **Slow responses**: OpenAI API calls can take several seconds to complete
- **Rate limiting**: Be aware of OpenAI API usage limits
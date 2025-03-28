from flask import Flask, request, jsonify
import logging
import os
from typing import Dict, Any

from .call_handler import CallHandler
from ...core.utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize configuration and call handler
config = Config()
call_handler = CallHandler(config)

@app.route('/telephony/webhook', methods=['POST'])
def telephony_webhook():
    """
    Endpoint for receiving telephony webhooks from Pindo.
    This handles incoming calls and call events.
    """
    data = request.json or {}
    logger.info(f"Received webhook: {data}")
    
    # Process the webhook with the call handler
    response = call_handler.handle_incoming_call(data)
    
    return jsonify(response)

@app.route('/telephony/status', methods=['GET'])
def telephony_status():
    """
    Endpoint for checking telephony system status.
    """
    active_calls = len(call_handler.active_calls)
    
    return jsonify({
        "status": "online",
        "active_calls": active_calls,
        "provider": config.get("telephony", "provider", "pindo")
    })

@app.route('/telephony/audio/<call_id>', methods=['POST'])
def audio_stream(call_id: str):
    """
    Endpoint for receiving audio streams from a call.
    """
    if not request.data:
        return jsonify({"error": "No audio data received"}), 400
        
    # Process audio data
    response_audio = call_handler.route_audio(call_id, request.data)
    
    if response_audio:
        return response_audio, 200, {'Content-Type': 'audio/wav'}
    else:
        return "", 204

def start_api(host: str = '0.0.0.0', port: int = 5000):
    """
    Start the telephony API server.
    
    Args:
        host: Host to bind the server to
        port: Port to listen on
    """
    logger.info(f"Starting telephony API on {host}:{port}")
    app.run(host=host, port=port)

if __name__ == '__main__':
    # If run directly, start the API server
    start_api()
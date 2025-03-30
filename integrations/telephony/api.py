import logging
import os
import json
from typing import Dict, Any, Optional
import flask
from flask import Flask, request, jsonify, Response
import threading
import time

from .pindo_adapter import PindoAdapter
from .call_handler import CallHandler
from .audio_router import AudioRouter
from ...core.llm.speech_processor import SpeechProcessor
from ...core.agent.orchestrator import Orchestrator
from ...database.repository import Repository
from ...core.utils.config import Config

logger = logging.getLogger(__name__)

# Flask application
app = Flask(__name__)

# Global telephony components
config = None
telephony_adapter = None
audio_router = None
speech_processor = None
orchestrator = None
repository = None
call_handler = None

def initialize_components():
    """Initialize telephony components"""
    global config, telephony_adapter, audio_router, speech_processor, orchestrator, repository, call_handler
    
    # Load configuration
    config = Config()
    
    # Initialize telephony adapter
    api_key = config.get("telephony", "api_key")
    if not api_key:
        raise ValueError("Telephony API key not configured")
        
    telephony_adapter = PindoAdapter(api_key=api_key)
    
    # Initialize audio router
    audio_router = AudioRouter()
    
    # Initialize speech processor if available
    try:
        from ...core.llm.speech_processor import SpeechProcessor
        speech_processor = SpeechProcessor()
        audio_router.set_speech_processor(speech_processor)
    except ImportError:
        logger.warning("Speech processor not available")
        speech_processor = None
        
    # Initialize orchestrator if available
    try:
        from ...core.agent.orchestrator import Orchestrator
        orchestrator = Orchestrator()
    except ImportError:
        logger.warning("Orchestrator not available")
        orchestrator = None
        
    # Initialize repository if available
    try:
        from ...database.repository import Repository
        repository = Repository()
    except ImportError:
        logger.warning("Repository not available")
        repository = None
        
    # Initialize call handler
    call_handler = CallHandler(
        telephony_adapter=telephony_adapter,
        audio_router=audio_router,
        speech_processor=speech_processor,
        orchestrator=orchestrator,
        repository=repository
    )
    
    logger.info("Telephony components initialized")

def get_call_handler() -> CallHandler:
    """Get the call handler, initializing if necessary"""
    global call_handler
    
    if call_handler is None:
        initialize_components()
        
    return call_handler

# Import analytics utility
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')))
from utils.analytics import AnalyticsManager

# Initialize analytics manager for updating analytics data
analytics_manager = None

def get_analytics_manager():
    """Get the analytics manager, initializing if necessary"""
    global analytics_manager
    
    if analytics_manager is None:
        from utils.analytics import AnalyticsManager
        analytics_manager = AnalyticsManager()
        
    return analytics_manager

# API Routes

@app.route('/telephony/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/telephony/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for telephony events"""
    try:
        # Get webhook data
        if not request.json:
            logger.error("No JSON data in webhook request")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Process webhook
        handler = get_call_handler()
        result = handler.handle_call_event(request.json)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/call', methods=['POST'])
def initiate_call():
    """Initiate an outbound call"""
    try:
        # Get call data
        if not request.json:
            logger.error("No JSON data in call request")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Get phone number
        phone_number = request.json.get('phone_number')
        if not phone_number:
            logger.error("No phone number in call request")
            return jsonify({"status": "error", "message": "Phone number required"}), 400
            
        # Get metadata
        metadata = request.json.get('metadata', {})
        
        # Initiate call
        handler = get_call_handler()
        result = handler.initiate_outbound_call(phone_number, metadata)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/call/<call_id>', methods=['DELETE'])
def end_call(call_id):
    """End an active call"""
    try:
        # End call
        handler = get_call_handler()
        result = handler.end_call(call_id)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/call/<call_id>/dtmf', methods=['POST'])
def send_dtmf(call_id):
    """Send DTMF tones to a call"""
    try:
        # Get DTMF data
        if not request.json:
            logger.error("No JSON data in DTMF request")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Get digits
        digits = request.json.get('digits')
        if not digits:
            logger.error("No digits in DTMF request")
            return jsonify({"status": "error", "message": "Digits required"}), 400
            
        # Send DTMF
        telephony_adapter = get_call_handler().telephony_adapter
        result = telephony_adapter.send_dtmf(call_id, digits)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending DTMF: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/call/<call_id>/play', methods=['POST'])
def play_audio(call_id):
    """Play audio in a call"""
    try:
        # Get audio data
        if not request.json:
            logger.error("No JSON data in play request")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Get audio URL
        audio_url = request.json.get('url')
        if not audio_url:
            logger.error("No audio URL in play request")
            return jsonify({"status": "error", "message": "Audio URL required"}), 400
            
        # Play audio
        telephony_adapter = get_call_handler().telephony_adapter
        result = telephony_adapter.play_audio(call_id, audio_url)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error playing audio: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/audio/<call_id>', methods=['POST'])
def process_audio(call_id):
    """Process audio for a call"""
    try:
        # Get audio data
        audio_data = request.get_data()
        if not audio_data:
            logger.error("No audio data in request")
            return jsonify({"status": "error", "message": "No audio data"}), 400
            
        # Process audio
        handler = get_call_handler()
        response_audio = handler.process_audio(call_id, audio_data)
        
        if response_audio:
            # Return audio data
            return Response(response_audio, mimetype='audio/wav')
        else:
            # No response audio available
            return '', 204
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/calls', methods=['GET'])
def get_active_calls():
    """Get active calls"""
    try:
        # Get active calls
        handler = get_call_handler()
        calls = handler.get_active_calls()
        
        return jsonify({"calls": calls})
    except Exception as e:
        logger.error(f"Error getting active calls: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/analytics/sms', methods=['POST'])
def update_sms_analytics():
    """Update SMS analytics"""
    try:
        # Get SMS data
        if not request.json:
            logger.error("No JSON data in analytics request")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Get SMS record
        sms_record = request.json
        
        # Update analytics
        analytics = get_analytics_manager()
        result = analytics.add_sms_record(sms_record)
        
        if result:
            return jsonify({"status": "success", "message": "SMS analytics updated"})
        else:
            return jsonify({"status": "error", "message": "Failed to update SMS analytics"}), 500
    except Exception as e:
        logger.error(f"Error updating SMS analytics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/analytics/call', methods=['POST'])
def update_call_analytics():
    """Update call analytics"""
    try:
        # Get call data
        if not request.json:
            logger.error("No JSON data in analytics request")
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Get call record
        call_record = request.json
        
        # Update analytics
        analytics = get_analytics_manager()
        result = analytics.update_call_record(call_record)
        
        if result:
            return jsonify({"status": "success", "message": "Call analytics updated"})
        else:
            return jsonify({"status": "error", "message": "Failed to update call analytics"}), 500
    except Exception as e:
        logger.error(f"Error updating call analytics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/telephony/call/<call_id>', methods=['GET'])
def get_call_info(call_id):
    """Get information about a call"""
    try:
        # Get call info
        handler = get_call_handler()
        call_info = handler.get_call_info(call_id)
        
        if call_info:
            return jsonify(call_info)
        else:
            return jsonify({"status": "error", "message": "Call not found"}), 404
    except Exception as e:
        logger.error(f"Error getting call info: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def start_api(host='0.0.0.0', port=5000):
    """Start the telephony API server"""
    # Initialize components before starting
    initialize_components()
    
    # Set up Flask app
    app.config['JSON_SORT_KEYS'] = False
    
    # Start server
    app.run(host=host, port=port)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Start API server
    start_api()
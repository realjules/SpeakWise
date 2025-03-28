import logging
from typing import Dict, Any, Optional, Callable
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

logger = logging.getLogger(__name__)

class TwilioAdapter:
    """
    Adapter for the Twilio telephony API.
    Handles communication with Twilio's services for voice calls.
    """
    
    def __init__(self, account_sid: str, auth_token: str):
        """
        Initialize the Twilio adapter with API credentials.
        
        Args:
            account_sid: The Twilio account SID
            auth_token: The Twilio auth token
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.client = Client(account_sid, auth_token)
        self.callbacks = {}  # Map of call_id to callback functions
        
    def initiate_call(self, to_number: str, from_number: str) -> Dict[str, Any]:
        """
        Initiate a call to a phone number.
        
        Args:
            to_number: The recipient's phone number
            from_number: The caller ID
            
        Returns:
            Call information including call_id
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url="https://api.speakwise.rw/telephony/webhook"
            )
            
            logger.info(f"Call initiated to {to_number}, call_id: {call.sid}")
            
            return {
                "call_id": call.sid,
                "status": call.status
            }
        except Exception as e:
            logger.error(f"Failed to initiate call to {to_number}: {str(e)}")
            raise
            
    def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End an active call.
        
        Args:
            call_id: The unique call identifier
            
        Returns:
            Response from the API
        """
        try:
            call = self.client.calls(call_id).update(status="completed")
            
            logger.info(f"Call {call_id} ended successfully")
            
            return {
                "call_id": call.sid,
                "status": call.status
            }
        except Exception as e:
            logger.error(f"Failed to end call {call_id}: {str(e)}")
            raise
            
    def register_callback(self, call_id: str, callback: Callable) -> None:
        """
        Register a callback function for call events.
        
        Args:
            call_id: The unique call identifier
            callback: Function to call when events happen
        """
        self.callbacks[call_id] = callback
        
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> str:
        """
        Handle an incoming webhook from Twilio.
        
        Args:
            webhook_data: The webhook payload
            
        Returns:
            TwiML response
        """
        call_sid = webhook_data.get("CallSid")
        event_type = webhook_data.get("CallStatus")
        
        logger.info(f"Received webhook for call {call_sid}, event: {event_type}")
        
        # Handle specific event types
        if event_type == "in-progress":
            # Execute callback if registered
            if call_sid in self.callbacks:
                self.callbacks[call_sid](webhook_data)
        elif event_type == "completed":
            # Clean up resources
            if call_sid in self.callbacks:
                del self.callbacks[call_sid]
                
        # Create TwiML response
        response = VoiceResponse()
        response.say("Welcome to SpeakWise. How can I assist you today?")
        
        return str(response)
        
    def stream_audio(self, call_id: str, audio_url: str) -> Dict[str, Any]:
        """
        Stream audio to an active call.
        
        Args:
            call_id: The unique call identifier
            audio_url: URL to the audio file to stream
            
        Returns:
            Response from the API
        """
        try:
            call = self.client.calls(call_id).update(
                twiml=f'<Response><Play>{audio_url}</Play></Response>'
            )
            
            logger.info(f"Streaming audio to call {call_id}")
            
            return {
                "call_id": call.sid,
                "status": call.status
            }
        except Exception as e:
            logger.error(f"Failed to stream audio to call {call_id}: {str(e)}")
            raise
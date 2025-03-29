import logging
import time
import threading
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

logger = logging.getLogger(__name__)

class TwilioAdapter:
    """
    Adapter for the Twilio telephony and SMS API.
    Handles communication with Twilio's services for voice calls and messaging.
    """
    
    def __init__(self, account_sid: str, auth_token: str, default_phone: Optional[str] = None):
        """
        Initialize the Twilio adapter with API credentials.
        
        Args:
            account_sid: The Twilio account SID
            auth_token: The Twilio auth token
            default_phone: Default Twilio phone number for SMS and calls
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.client = Client(account_sid, auth_token)
        self.default_phone = default_phone or os.environ.get("TWILIO_PHONE_NUMBER")
        self.callbacks = {}  # Map of call_id to callback functions
        
    def initiate_call(self, to_number: str, from_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiate a call to a phone number.
        
        Args:
            to_number: The recipient's phone number
            from_number: The caller ID (optional, uses default if not provided)
            
        Returns:
            Call information including call_id
        """
        # Use the provided from_number or fall back to default
        caller_id = from_number or self.default_phone
        if not caller_id:
            raise ValueError("No from_number provided and no default phone number configured")
            
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=caller_id,
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
    
    def send_dtmf(self, call_id: str, digits: str) -> Dict[str, Any]:
        """
        Send DTMF tones to an active call.
        
        Args:
            call_id: The unique call identifier
            digits: The DTMF digits to send
            
        Returns:
            Response from the API
        """
        try:
            # Update the call with TwiML to send DTMF tones
            call = self.client.calls(call_id).update(
                twiml=f'<Response><Play digits="{digits}"/></Response>'
            )
            
            logger.info(f"DTMF digits '{digits}' sent to call {call_id}")
            
            return {
                "call_id": call.sid,
                "status": call.status
            }
        except Exception as e:
            logger.error(f"Failed to send DTMF to call {call_id}: {str(e)}")
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
            
    def send_sms(self, to_number: str, message: str, from_number: Optional[str] = None, 
                service: str = "General", sms_type: str = "notification") -> Dict[str, Any]:
        """
        Send an SMS message and update analytics.
        
        Args:
            to_number: The recipient's phone number
            message: The message content
            from_number: The sender phone number (optional, uses default if not provided)
            service: Service type for analytics (default: General)
            sms_type: SMS type for analytics (default: notification)
            
        Returns:
            Response from the API including message SID
        """
        # Use the provided from_number or fall back to default
        sender = from_number or self.default_phone
        if not sender:
            raise ValueError("No from_number provided and no default phone number configured")
            
        try:
            # Send SMS via Twilio API
            message = self.client.messages.create(
                to=to_number,
                from_=sender,
                body=message
            )
            
            # Generate a unique SMS ID
            sms_id = f"SMS-{message.sid}"
            
            # Log successful send
            logger.info(f"SMS sent to {to_number}, message_id: {sms_id}")
            
            # Prepare result
            result = {
                "sid": message.sid,
                "status": message.status,
                "sms_id": sms_id
            }
            
            # Update analytics asynchronously
            self._update_analytics(to_number, sms_id, service, sms_type, "delivered", result)
            
            return result
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            
            # Log failed attempt to analytics
            sms_id = f"SMS-FAILED-{int(time.time())}"
            self._update_analytics(to_number, sms_id, service, sms_type, "failed", {"error": str(e)})
            
            raise
    
    def _update_analytics(self, recipient: str, sms_id: str, service: str, 
                         sms_type: str, status: str, api_response: Dict[str, Any]) -> None:
        """
        Update analytics with SMS information.
        
        Args:
            recipient: Recipient phone number
            sms_id: SMS ID
            service: Service type
            sms_type: SMS type
            status: Delivery status
            api_response: API response data
        """
        # Create record
        record = {
            "id": sms_id,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat() + "Z",
            "type": sms_type,
            "status": status,
            "service": service,
            "reference": api_response.get('sid', sms_id)
        }
        
        # Update analytics in background thread
        def update_analytics_async():
            try:
                # Make request to analytics endpoint
                analytics_url = "http://localhost:5000/telephony/analytics/sms"
                import requests
                requests.post(
                    analytics_url,
                    json=record,
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"SMS analytics updated for {sms_id}")
            except Exception as e:
                logger.error(f"Failed to update SMS analytics: {str(e)}")
        
        # Start background thread
        threading.Thread(target=update_analytics_async).start()
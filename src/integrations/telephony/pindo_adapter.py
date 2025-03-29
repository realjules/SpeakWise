import logging
import requests
from typing import Dict, Any, Optional, Callable
import json
import os
import time
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class PindoAdapter:
    """
    Adapter for the Pindo telephony and SMS API.
    Handles communication with Pindo's services for voice calls and messaging.
    """
    
    # Base URLs for Pindo API
    BASE_URL = "https://api.pindo.io"
    VOICE_API_URL = f"{BASE_URL}/v1/voice"  # This will be the working endpoint
    SMS_API_URL = f"{BASE_URL}/v1/sms"
    CALL_EVENTS = ["call.initiated", "call.answered", "call.completed", "call.failed"]
    
    def __init__(self, api_key: str, default_sender: str = "PindoTest"):
        """
        Initialize the Pindo adapter with API credentials.
        
        Args:
            api_key: The Pindo API key
            default_sender: Default sender ID for SMS messages (default: PindoTest)
        """
        self.api_key = api_key
        self.default_sender = default_sender or os.environ.get("PINDO_SENDER_ID", "PindoTest")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
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
        data = {
            "to": to_number
        }
        
        if from_number:
            data["from"] = from_number
            
        # Add webhook URL for call events
        data["webhook_url"] = "https://api.speakwise.rw/telephony/webhook"
        
        try:
            response = requests.post(
                f"{self.VOICE_API_URL}/calls",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            call_data = response.json()
            logger.info(f"Call initiated to {to_number}, call_id: {call_data.get('call_id')}")
            return call_data
        except requests.RequestException as e:
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
            response = requests.post(
                f"{self.VOICE_API_URL}/calls/{call_id}/hangup",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Call {call_id} ended successfully")
            return result
        except requests.RequestException as e:
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
        data = {
            "digits": digits
        }
        
        try:
            response = requests.post(
                f"{self.VOICE_API_URL}/calls/{call_id}/dtmf",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"DTMF digits '{digits}' sent to call {call_id}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to send DTMF to call {call_id}: {str(e)}")
            raise
            
    def play_audio(self, call_id: str, audio_url: str) -> Dict[str, Any]:
        """
        Play audio file in an active call.
        
        Args:
            call_id: The unique call identifier
            audio_url: URL to the audio file to play
            
        Returns:
            Response from the API
        """
        data = {
            "url": audio_url
        }
        
        try:
            response = requests.post(
                f"{self.VOICE_API_URL}/calls/{call_id}/play",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Playing audio from {audio_url} on call {call_id}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to play audio on call {call_id}: {str(e)}")
            raise
            
    def register_callback(self, call_id: str, callback: Callable) -> None:
        """
        Register a callback function for call events.
        
        Args:
            call_id: The unique call identifier
            callback: Function to call when events happen
        """
        self.callbacks[call_id] = callback
        
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming webhook from Pindo.
        
        Args:
            webhook_data: The webhook payload
            
        Returns:
            Response to send back to Pindo
        """
        call_id = webhook_data.get("call_id")
        event_type = webhook_data.get("event")
        
        logger.info(f"Received webhook for call {call_id}, event: {event_type}")
        
        # Handle specific event types
        if event_type == "call.initiated":
            pass  # Handle call initiated
        elif event_type == "call.answered":
            # Execute callback if registered
            if call_id in self.callbacks:
                self.callbacks[call_id](webhook_data)
        elif event_type == "call.completed":
            # Clean up resources
            if call_id in self.callbacks:
                del self.callbacks[call_id]
                
        # Default response
        return {
            "status": "success",
            "message": "Webhook processed"
        }
        
    def stream_audio(self, call_id: str, audio_data: bytes) -> None:
        """
        Stream audio data to an active call.
        
        Args:
            call_id: The unique call identifier
            audio_data: Raw audio data to stream
        """
        try:
            response = requests.post(
                f"{self.VOICE_API_URL}/calls/{call_id}/stream",
                headers=self.headers,
                data=audio_data
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to stream audio to call {call_id}: {str(e)}")
            raise
            
    def send_sms(self, to_number: str, message: str, sender_id: Optional[str] = None, 
                service: str = "General", sms_type: str = "notification") -> Dict[str, Any]:
        """
        Send an SMS message and update analytics.
        
        Args:
            to_number: The recipient's phone number
            message: The message content
            sender_id: The sender ID (optional, uses default if not provided)
            service: Service type for analytics (default: General)
            sms_type: SMS type for analytics (default: notification)
            
        Returns:
            Response from the API
        """
        data = {
            "to": to_number,
            "text": message,
            "sender": sender_id or self.default_sender
        }
        
        try:
            # Send SMS via Pindo API
            response = requests.post(
                f"{self.SMS_API_URL}/",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Log successful send
            sms_id = result.get('sms_id', f"SMS-{int(time.time())}")
            logger.info(f"SMS sent to {to_number}, message_id: {sms_id}")
            
            # Update analytics asynchronously
            self._update_analytics(to_number, sms_id, service, sms_type, "delivered", result)
            
            return result
        except requests.RequestException as e:
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
        from datetime import datetime
        import threading
        
        record = {
            "id": sms_id,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat() + "Z",
            "type": sms_type,
            "status": status,
            "service": service,
            "reference": api_response.get('id', sms_id)
        }
        
        # Update analytics in background thread
        def update_analytics_async():
            try:
                # Make request to analytics endpoint
                analytics_url = "http://localhost:5000/telephony/analytics/sms"
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
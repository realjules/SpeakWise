import logging
import os
from datetime import datetime
from typing import Dict, Optional, Any, Callable

from .pindo_adapter import PindoAdapter
from ...core.utils.config import Config
from ...database.models.session import Session

logger = logging.getLogger(__name__)

class CallHandler:
    """
    Handles incoming and outgoing calls for the SpeakWise system.
    This class orchestrates the telephony functionality and routes audio streams.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the call handler with configuration.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.telephony_provider = self._initialize_provider()
        self.active_calls = {}  # Map of call_id to call session
        self.audio_router = None  # Will be initialized separately
        
    def _initialize_provider(self) -> PindoAdapter:
        """
        Initialize the telephony provider based on configuration.
        
        Returns:
            Telephony provider instance
        """
        provider_name = self.config.get("telephony", "provider", "pindo")
        
        if provider_name.lower() == "pindo":
            api_key = self.config.get("telephony", "api_key")
            return PindoAdapter(api_key=api_key)
        else:
            raise ValueError(f"Unsupported telephony provider: {provider_name}")
    
    def handle_incoming_call(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming call webhook request from Pindo.
        
        Args:
            request_data: The webhook data from Pindo
            
        Returns:
            Response to send back to Pindo
        """
        call_id = request_data.get("call_id") or request_data.get("CallSid")
        caller = request_data.get("caller") or request_data.get("From")
        
        logger.info(f"Incoming call from {caller} with ID {call_id}")
        
        # Create a new session for this call
        session = Session(
            call_id=call_id,
            user_phone=caller,
            start_time=datetime.now(),
            status="active"
        )
        
        # Store the session
        self.active_calls[call_id] = session
        
        # Start audio streaming for this call
        self._initialize_audio_stream(call_id)
        
        # Return the initial voice response
        return {
            "response": "voice",
            "message": self.config.get("telephony", "greeting_message", 
                                      "Welcome to SpeakWise. How can I assist you today?")
        }
    
    def _initialize_audio_stream(self, call_id: str) -> None:
        """
        Initialize audio streaming for a specific call.
        
        Args:
            call_id: The unique call identifier
        """
        if not self.audio_router:
            logger.warning("Audio router not initialized, audio streaming not available")
            return
            
        # Set up bidirectional audio streaming
        self.audio_router.register_call(call_id)
        
    def route_audio(self, call_id: str, audio_data: bytes) -> Optional[bytes]:
        """
        Route audio between the telephony system and the core engine.
        
        Args:
            call_id: The unique call identifier
            audio_data: Incoming audio data
            
        Returns:
            Response audio data from the core engine, if available
        """
        if call_id not in self.active_calls:
            logger.warning(f"Received audio for unknown call: {call_id}")
            return None
            
        if not self.audio_router:
            logger.warning("Audio router not initialized, cannot route audio")
            return None
            
        # Route the audio to the core engine
        return self.audio_router.route_audio(call_id, audio_data)
        
    def end_call(self, call_id: str) -> None:
        """
        End an active call.
        
        Args:
            call_id: The unique call identifier
        """
        if call_id not in self.active_calls:
            logger.warning(f"Attempt to end unknown call: {call_id}")
            return
            
        session = self.active_calls[call_id]
        session.end_time = datetime.now()
        session.status = "completed"
        
        # Clean up resources
        if self.audio_router:
            self.audio_router.unregister_call(call_id)
            
        # Remove from active calls
        del self.active_calls[call_id]
        
        logger.info(f"Call {call_id} ended")
        
    def set_audio_router(self, audio_router: Any) -> None:
        """
        Set the audio router component.
        
        Args:
            audio_router: The audio router instance
        """
        self.audio_router = audio_router
        
    def make_call(self, phone_number: str, callback: Optional[Callable] = None) -> str:
        """
        Initiate an outgoing call.
        
        Args:
            phone_number: The phone number to call
            callback: Optional callback function when call is answered
            
        Returns:
            The call ID
        """
        # Use the telephony provider to make the call
        call_data = self.telephony_provider.initiate_call(phone_number)
        call_id = call_data["call_id"]
        
        # Create a new session for this call
        session = Session(
            call_id=call_id,
            user_phone=phone_number,
            start_time=datetime.now(),
            status="active",
            direction="outbound"
        )
        
        # Store the session
        self.active_calls[call_id] = session
        
        # Register the callback if provided
        if callback:
            self.telephony_provider.register_callback(call_id, callback)
            
        return call_id
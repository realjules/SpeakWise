import logging
import uuid
from typing import Dict, Any, Optional, Callable, List
import json
import time
from datetime import datetime

from .pindo_adapter import PindoAdapter
from .audio_router import AudioRouter
from ...core.agent.session import Session
from ...core.llm.speech_processor import SpeechProcessor
from ...core.agent.orchestrator import Orchestrator
from ...database.models.session import SessionModel
from ...database.repository import Repository

logger = logging.getLogger(__name__)

class CallHandler:
    """
    Handles call sessions and manages interactions with telephony provider.
    Coordinates between telephony system, audio router, and agent orchestrator.
    """
    
    def __init__(
        self, 
        telephony_adapter: PindoAdapter,
        audio_router: Optional[AudioRouter] = None,
        speech_processor: Optional[SpeechProcessor] = None,
        orchestrator: Optional[Orchestrator] = None,
        repository: Optional[Repository] = None
    ):
        """
        Initialize the call handler.
        
        Args:
            telephony_adapter: Adapter for telephony provider
            audio_router: Router for audio streams
            speech_processor: Processor for speech (STT/TTS)
            orchestrator: Agent orchestrator
            repository: Data repository for sessions
        """
        self.telephony_adapter = telephony_adapter
        self.audio_router = audio_router or AudioRouter()
        self.speech_processor = speech_processor
        self.orchestrator = orchestrator
        self.repository = repository
        
        # Set speech processor on audio router if provided
        if speech_processor:
            self.audio_router.set_speech_processor(speech_processor)
            
        # Active call sessions
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        
        # Register for telephony events
        self._register_callbacks()
        
    def _register_callbacks(self) -> None:
        """Register callbacks for telephony events"""
        # This would register callbacks with the telephony adapter
        # when events come in via webhooks
        pass
        
    def initiate_outbound_call(
        self, 
        phone_number: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call.
        
        Args:
            phone_number: Phone number to call
            metadata: Additional metadata for the call
            
        Returns:
            Call information including call_id
        """
        try:
            # Make the call via telephony adapter
            result = self.telephony_adapter.initiate_call(phone_number)
            
            # Get call ID
            call_id = result.get("call_id")
            
            if not call_id:
                raise ValueError("No call_id returned from telephony provider")
                
            # Create new session
            session_id = str(uuid.uuid4())
            session = Session(session_id=session_id)
            
            # Store call information
            self.active_calls[call_id] = {
                "phone_number": phone_number,
                "direction": "outbound",
                "start_time": datetime.now(),
                "status": "initiated",
                "session_id": session_id,
                "session": session,
                "metadata": metadata or {}
            }
            
            # Register with audio router
            self.audio_router.register_call(call_id)
            
            # Save session to database if repository available
            if self.repository:
                session_model = SessionModel(
                    id=session_id,
                    call_id=call_id,
                    phone_number=phone_number,
                    direction="outbound",
                    status="initiated",
                    start_time=datetime.now(),
                    metadata=json.dumps(metadata or {})
                )
                self.repository.save_session(session_model)
                
            logger.info(f"Initiated outbound call to {phone_number}, call_id: {call_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to initiate outbound call to {phone_number}: {str(e)}")
            raise
            
    def process_inbound_call(
        self, 
        call_id: str, 
        phone_number: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming call.
        
        Args:
            call_id: Unique call identifier
            phone_number: Caller's phone number
            metadata: Additional metadata for the call
            
        Returns:
            Call information
        """
        # Create new session
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id)
        
        # Store call information
        self.active_calls[call_id] = {
            "phone_number": phone_number,
            "direction": "inbound",
            "start_time": datetime.now(),
            "status": "initiated",
            "session_id": session_id,
            "session": session,
            "metadata": metadata or {}
        }
        
        # Register with audio router
        self.audio_router.register_call(call_id)
        
        # Save session to database if repository available
        if self.repository:
            session_model = SessionModel(
                id=session_id,
                call_id=call_id,
                phone_number=phone_number,
                direction="inbound",
                status="initiated",
                start_time=datetime.now(),
                metadata=json.dumps(metadata or {})
            )
            self.repository.save_session(session_model)
            
        logger.info(f"Processed inbound call from {phone_number}, call_id: {call_id}")
        
        return {
            "call_id": call_id,
            "session_id": session_id,
            "status": "initiated"
        }
        
    def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End an active call.
        
        Args:
            call_id: Unique call identifier
            
        Returns:
            Result of ending the call
        """
        if call_id not in self.active_calls:
            logger.warning(f"Attempted to end unknown call: {call_id}")
            return {"status": "error", "message": "Unknown call ID"}
            
        try:
            # End call via telephony adapter
            result = self.telephony_adapter.end_call(call_id)
            
            # Update call status
            self.active_calls[call_id]["status"] = "completed"
            self.active_calls[call_id]["end_time"] = datetime.now()
            
            # Unregister from audio router
            self.audio_router.unregister_call(call_id)
            
            # Update session in database if repository available
            if self.repository:
                session_id = self.active_calls[call_id]["session_id"]
                session_model = self.repository.get_session(session_id)
                
                if session_model:
                    session_model.status = "completed"
                    session_model.end_time = datetime.now()
                    self.repository.save_session(session_model)
                    
            # Clean up
            call_info = self.active_calls.pop(call_id, None)
            
            logger.info(f"Ended call {call_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to end call {call_id}: {str(e)}")
            
            # Still try to clean up locally even if API call fails
            self.audio_router.unregister_call(call_id)
            self.active_calls.pop(call_id, None)
            
            raise
            
    def handle_call_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call event from webhook.
        
        Args:
            event_data: Event data from telephony provider
            
        Returns:
            Response to webhook
        """
        call_id = event_data.get("call_id")
        event_type = event_data.get("event")
        
        if not call_id or not event_type:
            logger.error(f"Invalid call event: missing call_id or event type")
            return {"status": "error", "message": "Invalid event data"}
            
        logger.info(f"Handling call event {event_type} for call {call_id}")
        
        # Handle based on event type
        if event_type == "call.initiated":
            # Call has been initiated
            phone_number = event_data.get("from", "unknown")
            
            if event_data.get("direction") == "inbound":
                # Inbound call, process it
                self.process_inbound_call(call_id, phone_number)
                
            # Update analytics
            self._update_call_analytics(call_id, phone_number, "In Progress", event_data.get("service", "General"))
                
        elif event_type == "call.answered":
            # Call has been answered
            if call_id in self.active_calls:
                self.active_calls[call_id]["status"] = "in-progress"
                
                # Update session in database if repository available
                if self.repository:
                    session_id = self.active_calls[call_id]["session_id"]
                    session_model = self.repository.get_session(session_id)
                    
                    if session_model:
                        session_model.status = "in-progress"
                        self.repository.save_session(session_model)
                        
                # Start any necessary processes
                # e.g., sending welcome message
                self._handle_call_answered(call_id)
                
                # Update analytics
                phone_number = self.active_calls[call_id]["phone_number"]
                self._update_call_analytics(call_id, phone_number, "In Progress", 
                                           self.active_calls[call_id].get("metadata", {}).get("service", "General"))
                
        elif event_type == "call.completed" or event_type == "call.failed":
            # Call has ended
            if call_id in self.active_calls:
                status = "Completed" if event_type == "call.completed" else "Failed"
                self.active_calls[call_id]["status"] = status
                self.active_calls[call_id]["end_time"] = datetime.now()
                
                # Update session in database if repository available
                if self.repository:
                    session_id = self.active_calls[call_id]["session_id"]
                    session_model = self.repository.get_session(session_id)
                    
                    if session_model:
                        session_model.status = status.lower()
                        session_model.end_time = datetime.now()
                        self.repository.save_session(session_model)
                
                # Calculate call duration
                phone_number = self.active_calls[call_id]["phone_number"]
                start_time = self.active_calls[call_id]["start_time"]
                end_time = self.active_calls[call_id]["end_time"]
                duration_seconds = int((end_time - start_time).total_seconds())
                service = self.active_calls[call_id].get("metadata", {}).get("service", "General")
                
                # Update analytics
                self._update_call_analytics(call_id, phone_number, status, service, duration_seconds)
                
                # Clean up resources
                self.audio_router.unregister_call(call_id)
                self.active_calls.pop(call_id, None)
                
        # Default response
        return {
            "status": "success",
            "message": f"Processed {event_type} event for call {call_id}"
        }
        
    def _handle_call_answered(self, call_id: str) -> None:
        """
        Handle call answered event.
        
        Args:
            call_id: Unique call identifier
        """
        if call_id not in self.active_calls:
            logger.warning(f"Call answered event for unknown call: {call_id}")
            return
            
        # Get welcome message from speech processor
        if self.speech_processor:
            # Generate welcome message based on call direction
            direction = self.active_calls[call_id]["direction"]
            
            if direction == "inbound":
                welcome_text = "Thank you for calling SpeakWise. How can I assist you today?"
            else:
                welcome_text = "Hello, this is SpeakWise calling. How can I assist you today?"
                
            # Convert to speech
            welcome_audio = self.speech_processor.synthesize(welcome_text)
            
            if welcome_audio:
                # Queue for sending to caller
                self.audio_router.queue_outgoing_audio(call_id, welcome_audio)
                
    def process_audio(self, call_id: str, audio_data: bytes) -> Optional[bytes]:
        """
        Process audio for a call.
        
        Args:
            call_id: Unique call identifier
            audio_data: Audio data from caller
            
        Returns:
            Audio response if available
        """
        if call_id not in self.active_calls:
            logger.warning(f"Received audio for unknown call: {call_id}")
            return None
            
        # Process incoming audio
        self.audio_router.process_incoming_audio(call_id, audio_data)
        
        # Get audio to send back to caller
        return self.audio_router.get_outgoing_audio(call_id)
        
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """
        Get information about active calls.
        
        Returns:
            List of active call information
        """
        result = []
        
        for call_id, call_info in self.active_calls.items():
            # Create a copy with sanitized data
            info = {
                "call_id": call_id,
                "phone_number": call_info["phone_number"],
                "direction": call_info["direction"],
                "status": call_info["status"],
                "start_time": call_info["start_time"].isoformat(),
                "session_id": call_info["session_id"]
            }
            
            if "end_time" in call_info:
                info["end_time"] = call_info["end_time"].isoformat()
                
            result.append(info)
            
        return result
        
    def get_call_info(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific call.
        
        Args:
            call_id: Unique call identifier
            
        Returns:
            Call information if found, None otherwise
        """
        if call_id not in self.active_calls:
            return None
            
        call_info = self.active_calls[call_id]
        
        # Create a copy with sanitized data
        info = {
            "call_id": call_id,
            "phone_number": call_info["phone_number"],
            "direction": call_info["direction"],
            "status": call_info["status"],
            "start_time": call_info["start_time"].isoformat(),
            "session_id": call_info["session_id"]
        }
        
        if "end_time" in call_info:
            info["end_time"] = call_info["end_time"].isoformat()
            
        return info
        
    def _update_call_analytics(self, call_id: str, phone_number: str, 
                         status: str, service: str, duration: int = 0) -> None:
        """
        Update analytics with call information.
        
        Args:
            call_id: Call ID
            phone_number: Phone number of caller/callee
            status: Call status (In Progress, Completed, Failed)
            service: Service type (e.g., Business Registration)
            duration: Call duration in seconds (for completed calls)
        """
        import threading
        import requests
        
        # Create record
        record = {
            "call_id": call_id,
            "phone": phone_number,
            "status": status,
            "timestamp": datetime.now().isoformat() + "Z",
            "service": service,
            "duration": duration
        }
        
        # Update analytics in background thread
        def update_analytics_async():
            try:
                # Make request to analytics endpoint
                analytics_url = "http://localhost:5000/telephony/analytics/call"
                requests.post(
                    analytics_url,
                    json=record,
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"Call analytics updated for {call_id}")
            except Exception as e:
                logger.error(f"Failed to update call analytics: {str(e)}")
        
        # Start background thread
        threading.Thread(target=update_analytics_async).start()
        
    def shutdown(self) -> None:
        """Shutdown call handler and clean up resources"""
        logger.info("Shutting down call handler")
        
        # End all active calls
        for call_id in list(self.active_calls.keys()):
            try:
                self.end_call(call_id)
            except Exception as e:
                logger.error(f"Error ending call {call_id} during shutdown: {str(e)}")
                
        # Clean up audio router
        self.audio_router.shutdown()
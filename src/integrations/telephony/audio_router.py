import logging
import asyncio
import threading
import queue
from typing import Dict, Any, Optional, Callable
import io
import wave
import numpy as np

from ...core.llm.speech_processor import SpeechProcessor

logger = logging.getLogger(__name__)

class AudioRouter:
    """
    Routes audio between caller and speech processing system.
    Handles bidirectional audio streams for voice conversations.
    """
    
    # Audio configuration
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 4096
    FORMAT = 'int16'
    
    def __init__(self, speech_processor: Optional[SpeechProcessor] = None):
        """
        Initialize the audio router.
        
        Args:
            speech_processor: Speech processor for audio processing
        """
        self.speech_processor = speech_processor
        
        # Audio queues for bidirectional communication
        self.input_queue = queue.Queue()  # Audio from caller
        self.output_queue = queue.Queue()  # Audio to caller
        
        # Call details
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        
        # Processing flags
        self.should_run = False
        self.processor_thread = None
        
    def register_call(self, call_id: str) -> None:
        """
        Register a new call for audio routing.
        
        Args:
            call_id: Unique call identifier
        """
        self.active_calls[call_id] = {
            "input_buffer": io.BytesIO(),
            "output_buffer": io.BytesIO(),
            "last_activity": asyncio.get_event_loop().time(),
            "is_active": True
        }
        logger.info(f"Registered call {call_id} for audio routing")
        
    def unregister_call(self, call_id: str) -> None:
        """
        Unregister a call and clean up resources.
        
        Args:
            call_id: Unique call identifier
        """
        if call_id in self.active_calls:
            self.active_calls[call_id]["is_active"] = False
            # Clean up any resources
            del self.active_calls[call_id]
            logger.info(f"Unregistered call {call_id} from audio routing")
            
    def process_incoming_audio(self, call_id: str, audio_data: bytes) -> None:
        """
        Process incoming audio from caller.
        
        Args:
            call_id: Unique call identifier
            audio_data: Raw audio bytes
        """
        if call_id not in self.active_calls:
            logger.warning(f"Received audio for unknown call: {call_id}")
            return
            
        call_info = self.active_calls[call_id]
        
        # Update activity timestamp
        if asyncio.get_event_loop().is_running():
            call_info["last_activity"] = asyncio.get_event_loop().time()
            
        # Queue audio for processing
        self.input_queue.put((call_id, audio_data))
        
        # If processor thread isn't running, start it
        if not self.should_run and self.speech_processor is not None:
            self._start_processor()
            
    def get_outgoing_audio(self, call_id: str) -> Optional[bytes]:
        """
        Get audio to send back to caller.
        
        Args:
            call_id: Unique call identifier
            
        Returns:
            Audio bytes if available, None otherwise
        """
        if call_id not in self.active_calls:
            logger.warning(f"Requested audio for unknown call: {call_id}")
            return None
            
        call_info = self.active_calls[call_id]
        output_buffer = call_info["output_buffer"]
        
        # If buffer has data, return it
        if output_buffer.tell() > 0:
            output_buffer.seek(0)
            audio_data = output_buffer.read()
            
            # Clear buffer for next batch
            call_info["output_buffer"] = io.BytesIO()
            
            return audio_data
            
        return None
        
    def queue_outgoing_audio(self, call_id: str, audio_data: bytes) -> None:
        """
        Queue audio to send to caller.
        
        Args:
            call_id: Unique call identifier
            audio_data: Audio bytes to send
        """
        if call_id not in self.active_calls:
            logger.warning(f"Queued audio for unknown call: {call_id}")
            return
            
        call_info = self.active_calls[call_id]
        
        # Write to output buffer
        call_info["output_buffer"].write(audio_data)
        logger.debug(f"Queued {len(audio_data)} bytes of audio for call {call_id}")
        
    def _process_audio_stream(self, call_id: str, audio_data: bytes) -> None:
        """
        Process audio stream through speech processor.
        
        Args:
            call_id: Unique call identifier
            audio_data: Audio bytes to process
        """
        if not self.speech_processor:
            logger.warning("No speech processor available")
            return
            
        try:
            # Convert audio if needed
            processed_audio = self._prepare_audio(audio_data)
            
            # Send to speech processor
            text = self.speech_processor.transcribe(processed_audio)
            
            if text:
                logger.info(f"Transcribed text from call {call_id}: {text}")
                
                # Get response from speech processor
                response_text = self.speech_processor.get_response(text, call_id)
                
                if response_text:
                    # Convert text to speech
                    response_audio = self.speech_processor.synthesize(response_text)
                    
                    if response_audio:
                        # Queue for sending back to caller
                        self.queue_outgoing_audio(call_id, response_audio)
                    else:
                        logger.warning(f"Failed to synthesize response for call {call_id}")
                else:
                    logger.warning(f"Empty response for call {call_id}")
            else:
                logger.debug(f"No transcription for audio from call {call_id}")
                
        except Exception as e:
            logger.error(f"Error processing audio for call {call_id}: {str(e)}")
            
    def _prepare_audio(self, audio_data: bytes) -> bytes:
        """
        Prepare audio for speech processing.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Processed audio bytes
        """
        # For now, just pass through
        # This would handle any format conversion needed
        return audio_data
        
    def _start_processor(self) -> None:
        """Start the audio processor thread"""
        if self.processor_thread is not None and self.processor_thread.is_alive():
            return
            
        self.should_run = True
        self.processor_thread = threading.Thread(target=self._processor_loop)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        logger.info("Started audio processor thread")
        
    def _stop_processor(self) -> None:
        """Stop the audio processor thread"""
        self.should_run = False
        if self.processor_thread:
            self.processor_thread.join(timeout=2.0)
            self.processor_thread = None
        logger.info("Stopped audio processor thread")
        
    def _processor_loop(self) -> None:
        """Main processing loop for audio"""
        logger.info("Audio processor loop started")
        
        while self.should_run:
            try:
                # Get the next audio chunk from the queue
                # Timeout to allow checking should_run periodically
                try:
                    call_id, audio_data = self.input_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                    
                # Check if call is still active
                if call_id not in self.active_calls or not self.active_calls[call_id]["is_active"]:
                    logger.debug(f"Skipping inactive call {call_id}")
                    continue
                    
                # Process the audio
                self._process_audio_stream(call_id, audio_data)
                
                # Mark as done
                self.input_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in processor loop: {str(e)}")
                
        logger.info("Audio processor loop stopped")
        
    def set_speech_processor(self, speech_processor: SpeechProcessor) -> None:
        """
        Set the speech processor.
        
        Args:
            speech_processor: Speech processor to use
        """
        self.speech_processor = speech_processor
        logger.info("Speech processor set")
        
    def shutdown(self) -> None:
        """Shutdown the audio router and clean up resources"""
        logger.info("Shutting down audio router")
        
        # Stop processor loop
        self._stop_processor()
        
        # Clear queues
        while not self.input_queue.empty():
            self.input_queue.get_nowait()
            self.input_queue.task_done()
            
        while not self.output_queue.empty():
            self.output_queue.get_nowait()
            self.output_queue.task_done()
            
        # Clean up call data
        call_ids = list(self.active_calls.keys())
        for call_id in call_ids:
            self.unregister_call(call_id)
import logging
from typing import Dict, Any, Optional, Callable, Tuple
import threading
import queue
import time
import wave
import os
from pathlib import Path
import tempfile

from ...core.utils.config import Config

logger = logging.getLogger(__name__)

class AudioRouter:
    """
    Routes audio streams between the telephony system and the core speech processing system.
    This class handles bidirectional audio streaming for active calls.
    """
    
    def __init__(self, config: Config, speech_processor=None):
        """
        Initialize the audio router with configuration.
        
        Args:
            config: System configuration
            speech_processor: Reference to the speech processor component
        """
        self.config = config
        self.speech_processor = speech_processor
        self.active_streams = {}  # Map of call_id to stream information
        self.audio_queues = {}    # Map of call_id to bidirectional queues
        self.temp_dir = Path(tempfile.gettempdir()) / "speakwise_audio"
        self.temp_dir.mkdir(exist_ok=True)
        
    def register_call(self, call_id: str) -> None:
        """
        Register a new call for audio streaming.
        
        Args:
            call_id: The unique call identifier
        """
        if call_id in self.active_streams:
            logger.warning(f"Call {call_id} already registered for audio streaming")
            return
            
        # Create audio queues for this call
        inbound_queue = queue.Queue()  # Audio from caller to system
        outbound_queue = queue.Queue() # Audio from system to caller
        
        self.audio_queues[call_id] = {
            "inbound": inbound_queue,
            "outbound": outbound_queue
        }
        
        # Start processing thread for this call
        stream_thread = threading.Thread(
            target=self._process_audio_stream,
            args=(call_id,),
            daemon=True
        )
        
        self.active_streams[call_id] = {
            "thread": stream_thread,
            "active": True,
            "last_activity": time.time()
        }
        
        stream_thread.start()
        logger.info(f"Audio streaming registered for call {call_id}")
        
    def unregister_call(self, call_id: str) -> None:
        """
        Unregister a call and stop audio streaming.
        
        Args:
            call_id: The unique call identifier
        """
        if call_id not in self.active_streams:
            logger.warning(f"Call {call_id} not registered for audio streaming")
            return
            
        # Signal the thread to stop
        self.active_streams[call_id]["active"] = False
        
        # Wait for thread to finish
        self.active_streams[call_id]["thread"].join(timeout=5.0)
        
        # Clean up resources
        del self.active_streams[call_id]
        del self.audio_queues[call_id]
        
        logger.info(f"Audio streaming unregistered for call {call_id}")
        
    def route_audio(self, call_id: str, audio_data: bytes) -> Optional[bytes]:
        """
        Route audio data from the telephony system to the core engine.
        
        Args:
            call_id: The unique call identifier
            audio_data: Raw audio data from the telephony system
            
        Returns:
            Response audio data from the core engine, if available
        """
        if call_id not in self.audio_queues:
            logger.warning(f"No audio queues for call {call_id}")
            return None
            
        # Put audio data in the inbound queue
        self.audio_queues[call_id]["inbound"].put(audio_data)
        
        # Update activity timestamp
        if call_id in self.active_streams:
            self.active_streams[call_id]["last_activity"] = time.time()
            
        # Check if there's any response audio available
        try:
            response_audio = self.audio_queues[call_id]["outbound"].get(block=False)
            return response_audio
        except queue.Empty:
            return None
            
    def _process_audio_stream(self, call_id: str) -> None:
        """
        Process audio stream for a specific call.
        This method runs in a separate thread.
        
        Args:
            call_id: The unique call identifier
        """
        logger.info(f"Started audio processing thread for call {call_id}")
        
        # Create temporary files for audio chunks
        temp_input_file = self.temp_dir / f"{call_id}_input.wav"
        temp_output_file = self.temp_dir / f"{call_id}_output.wav"
        
        while self._is_stream_active(call_id):
            # Check if there's audio data in the inbound queue
            try:
                audio_data = self.audio_queues[call_id]["inbound"].get(timeout=0.5)
                
                # Save audio data to temporary file
                self._save_audio(temp_input_file, audio_data)
                
                # Process audio through speech processor
                if self.speech_processor:
                    response_text = self.speech_processor.process_audio(str(temp_input_file))
                    
                    if response_text:
                        # Generate speech from response text
                        self.speech_processor.text_to_speech(response_text, str(temp_output_file))
                        
                        # Read response audio
                        response_audio = self._read_audio(temp_output_file)
                        
                        # Put response in outbound queue
                        self.audio_queues[call_id]["outbound"].put(response_audio)
            except queue.Empty:
                # No data in queue, continue loop
                pass
            except Exception as e:
                logger.error(f"Error processing audio for call {call_id}: {str(e)}")
                
        logger.info(f"Ended audio processing thread for call {call_id}")
        
        # Clean up temporary files
        for temp_file in [temp_input_file, temp_output_file]:
            if temp_file.exists():
                temp_file.unlink()
                
    def _is_stream_active(self, call_id: str) -> bool:
        """
        Check if a call's audio stream is still active.
        
        Args:
            call_id: The unique call identifier
            
        Returns:
            True if the stream is active, False otherwise
        """
        if call_id not in self.active_streams:
            return False
            
        # Check if the stream has been marked as inactive
        if not self.active_streams[call_id]["active"]:
            return False
            
        # Check for activity timeout
        timeout = self.config.get("telephony", "audio_timeout", 30)  # Default 30 seconds
        last_activity = self.active_streams[call_id]["last_activity"]
        
        if time.time() - last_activity > timeout:
            logger.warning(f"Audio stream for call {call_id} timed out due to inactivity")
            self.active_streams[call_id]["active"] = False
            return False
            
        return True
        
    def _save_audio(self, file_path: Path, audio_data: bytes) -> None:
        """
        Save audio data to a WAV file.
        
        Args:
            file_path: Path to save the file
            audio_data: Raw audio data
        """
        # Assumes 8kHz mono 16-bit PCM audio from telephony system
        with wave.open(str(file_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(8000)
            wf.writeframes(audio_data)
            
    def _read_audio(self, file_path: Path) -> bytes:
        """
        Read audio data from a WAV file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Raw audio data as bytes
        """
        with open(file_path, 'rb') as f:
            return f.read()
            
    def set_speech_processor(self, speech_processor: Any) -> None:
        """
        Set the speech processor component.
        
        Args:
            speech_processor: Reference to the speech processor
        """
        self.speech_processor = speech_processor
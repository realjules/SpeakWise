"""
Speech processor module for SpeakWise.
Handles speech-to-text and text-to-speech conversion using OpenAI.
"""

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SpeechProcessor:
    """
    Handles speech processing using OpenAI models.
    Supports speech-to-text and text-to-speech conversion.
    """
    
    def __init__(self, api_key=None, model="gpt-4o"):
        """
        Initialize the speech processor.
        
        Args:
            api_key: OpenAI API key (optional, uses environment if not provided)
            model: Model to use for text generation
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
            
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
    def transcribe(self, audio_data):
        """
        Transcribe speech to text.
        
        Args:
            audio_data: Audio data as bytes or file path
            
        Returns:
            Transcribed text
        """
        try:
            # Save audio data to temporary file if it's bytes
            if isinstance(audio_data, bytes):
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio_data)
                    temp_file = f.name
                    
                # Use the temporary file for transcription
                with open(temp_file, "rb") as audio_file:
                    result = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                # Clean up temporary file
                os.unlink(temp_file)
                
                return result.text
            else:
                # Assume it's a file path
                with open(audio_data, "rb") as audio_file:
                    result = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return result.text
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
            
    def synthesize(self, text):
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Get audio data as bytes
            return response.content
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return None
            
    def process_dialog(self, text):
        """
        Process dialog text and generate a response.
        
        Args:
            text: User input text
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are SpeakWise, a helpful voice assistant for accessing government services in Rwanda through the Irembo platform."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error processing dialog: {str(e)}")
            return "I'm sorry, I encountered an error processing your request."
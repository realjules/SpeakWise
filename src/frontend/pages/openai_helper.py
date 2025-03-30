"""
Enhanced helper module with OpenAI functions for speech processing and conversation.
"""

import os
import logging
import tempfile
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import OpenAI library
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI library not available. Install with: pip install openai")
    OPENAI_AVAILABLE = False

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
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
            self.model = model
        else:
            self.client = None
            self.model = None

    def transcribe(self, audio_file):
        """
        Transcribe speech to text.
        
        Args:
            audio_file: Path to audio file or audio data bytes
            
        Returns:
            Transcribed text
        """
        if not OPENAI_AVAILABLE or not self.client:
            logger.error("OpenAI not available for transcription")
            return "OpenAI not available for transcription"
            
        try:
            # Process different types of audio input
            if isinstance(audio_file, bytes):
                # Create a temporary file from bytes
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(audio_file)
                    temp_path = temp_file.name
                
                # Use the temporary file for transcription
                with open(temp_path, "rb") as audio_data:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_data
                    )
                
                # Clean up the temporary file
                os.unlink(temp_path)
            else:
                # Assume it's a file path
                with open(audio_file, "rb") as audio_data:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_data
                    )
            
            logger.info(f"Transcription successful: {response.text}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            return f"Error in transcription: {str(e)}"

    def synthesize(self, text):
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data bytes
        """
        if not OPENAI_AVAILABLE or not self.client:
            logger.error("OpenAI not available for speech synthesis")
            return None
            
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            logger.info("Speech synthesis successful")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in speech synthesis: {str(e)}")
            return None

    def process_dialog(self, text, service_type=None):
        """
        Process dialog text and generate a response.
        
        Args:
            text: User input text
            service_type: Type of service being discussed
            
        Returns:
            Generated response text
        """
        if not OPENAI_AVAILABLE or not self.client:
            logger.error("OpenAI not available for dialog processing")
            return "I'm sorry, but the AI service is currently unavailable."
            
        try:
            # Create system prompt based on service type
            system_prompt = "You are SpeakWise, a helpful voice assistant for accessing government services in Rwanda through the Irembo platform."
            
            if service_type:
                system_prompt += f" You are currently helping with a {service_type} request."
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in dialog processing: {str(e)}")
            return "I'm sorry, I encountered an error processing your request."

def generate_ai_response(user_message, service_type=None):
    """
    Generate an AI response using OpenAI.
    
    Args:
        user_message: The user's message
        service_type: The type of service being requested
        
    Returns:
        Generated response text
    """
    try:
        # Initialize processor with API key from environment
        processor = SpeechProcessor(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Process dialog and return response
        return processor.process_dialog(user_message, service_type)
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I'm sorry, I encountered an error: {str(e)}"

def is_openai_available():
    """Check if OpenAI integration is available"""
    api_key = os.getenv("OPENAI_API_KEY")
    return OPENAI_AVAILABLE and bool(api_key)
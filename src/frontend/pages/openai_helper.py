"""
Helper module with OpenAI functions for the Live Conversation page.
"""

import os
import logging
import random
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenAI library
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI library not available. Install with: pip install openai")
    OPENAI_AVAILABLE = False

# Load environment variables
load_dotenv()

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

    def process_dialog(self, text):
        """
        Process dialog text and generate a response.
        
        Args:
            text: User input text
            
        Returns:
            Generated response text
        """
        if not OPENAI_AVAILABLE or not self.client:
            return self._fallback_response(text)
            
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
            return self._fallback_response(text)
            
    def _fallback_response(self, text):
        """Generate a fallback response when OpenAI is not available"""
        # Simple service responses
        service_responses = {
            "birth certificate": [
                "To get a birth certificate, I'll need your national ID number.",
                "For a birth certificate, you'll need to provide your district and sector information.",
                "Is this birth certificate for yourself or for a child?",
                "For a birth certificate application, you'll need to provide a reason for the request."
            ],
            "driving license": [
                "For a driving license exam, I'll need to know which test type you're interested in.",
                "You'll need to select a district for your driving license exam.",
                "Would you prefer a provisional license or a full license?",
                "For driving license registration, you'll need to bring your ID and passport photos."
            ],
            "marriage certificate": [
                "For a marriage certificate, I'll need both partners' information.",
                "When is your marriage ceremony planned?",
                "For a marriage certificate, you'll need to provide the location of the ceremony.",
                "Both parties will need to present their national IDs for a marriage certificate."
            ],
            "land transfer": [
                "For land transfer, I'll need both the sender and recipient information.",
                "What is the land title number for this transfer?",
                "You'll need to specify the district where the land is located.",
                "Both parties must be present for the land transfer process."
            ]
        }
        
        # Check text for service keywords
        for service, responses in service_responses.items():
            if service in text.lower():
                return random.choice(responses)
        
        # General fallback responses
        general_responses = [
            "I understand you need assistance. Could you provide more details about your request?",
            "I'd be happy to help with your government service needs. What specific information are you looking for?",
            "To assist you better, I'll need some more information about your request.",
            "I can help you navigate the Irembo platform. What service are you interested in?",
            "I'm your SpeakWise assistant for government services. How can I help you today?"
        ]
        
        return random.choice(general_responses)

# Create a helper function for generating responses
def generate_ai_response(user_message, service_type):
    """
    Generate an AI response using OpenAI if available, otherwise use simulated responses.
    
    Args:
        user_message: The user's message
        service_type: The type of service being requested
        
    Returns:
        Generated response text
    """
    # Try to use OpenAI if available
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and OPENAI_AVAILABLE:
            processor = SpeechProcessor(api_key=api_key)
            context = f"The user is requesting help with {service_type}. "
            return processor.process_dialog(context + user_message)
    except Exception as e:
        logger.error(f"Error using OpenAI: {str(e)}")
    
    # Fallback to simulated responses
    service_responses = {
        "Business Registration": [
            "What type of business is this?",
            "Please provide your business address.",
            "What's your full name as the business owner?",
            "Please provide your national ID number.",
            "I'll now process your business registration. This will take a moment."
        ],
        "Marriage Certificate": [
            "What is your partner's full name?",
            "When do you plan to have the ceremony?",
            "Please provide your national ID number.",
            "Please provide your partner's national ID number.",
            "I'll now process your marriage certificate application."
        ],
        "Land Transfer": [
            "Who are you transferring the land to?",
            "Please provide your national ID number.",
            "Please provide the recipient's national ID number.",
            "What is the land title number?",
            "I'll now process your land transfer request."
        ],
        "Passport Application": [
            "Please provide your date of birth.",
            "What is your current address?",
            "Is this your first passport or a renewal?",
            "We'll need your photo. Have you prepared a digital passport photo?",
            "I'll now process your passport application."
        ]
    }
    
    responses = service_responses.get(service_type, 
        ["I need some more information.", "Please provide additional details.", 
         "Thank you. Just a few more questions.", "Almost done. One last question.",
         "I'll now process your request."])
    
    # Pick a response based on the step or random
    return random.choice(responses)

# Check if OpenAI is available
def is_openai_available():
    """Check if OpenAI is available and configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    return OPENAI_AVAILABLE and bool(api_key)
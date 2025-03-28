#!/usr/bin/env python3
"""
Test script for Pindo WhatsApp integration.
Run this script to test sending WhatsApp messages and documents.
"""

import os
import sys
import json
import logging
from pathlib import Path
import argparse

# Add parent directory to path to import project modules
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.messaging.whatsapp_sender import WhatsAppSender
from src.core.utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockConfig:
    """Mock configuration class for testing"""
    def __init__(self, api_key, sender_id):
        self.api_key = api_key
        self.sender_id = sender_id
    
    def get(self, section, key, default=None):
        if section == "messaging" and key == "api_key":
            return self.api_key
        elif section == "messaging" and key == "whatsapp_sender_id":
            return self.sender_id
        return default

def test_send_message(api_key: str, sender_id: str, recipient: str, message: str):
    """Test sending a WhatsApp message"""
    logger.info(f"Testing sending message to {recipient}")
    
    # Create mock config
    config = MockConfig(api_key, sender_id)
    
    # Initialize WhatsApp sender
    sender = WhatsAppSender(config)
    
    try:
        # Send the message
        result = sender.send_message(recipient, message)
        logger.info(f"Message sent: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

def test_send_document(api_key: str, sender_id: str, recipient: str, document_path: str, caption: str = None):
    """Test sending a document via WhatsApp"""
    logger.info(f"Testing sending document to {recipient}")
    
    # Create mock config
    config = MockConfig(api_key, sender_id)
    
    # Initialize WhatsApp sender
    sender = WhatsAppSender(config)
    
    try:
        # Send the document
        result = sender.send_document(recipient, document_path, caption)
        logger.info(f"Document sent: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Error sending document: {str(e)}")
        return False

def test_send_receipt(api_key: str, sender_id: str, recipient: str):
    """Test sending a formatted receipt"""
    logger.info(f"Testing sending receipt to {recipient}")
    
    # Create mock config
    config = MockConfig(api_key, sender_id)
    
    # Initialize WhatsApp sender
    sender = WhatsAppSender(config)
    
    # Create a sample receipt
    receipt_data = {
        "transaction_id": "TXN-12345",
        "date": "2023-10-30 14:30:00",
        "amount": 15000,
        "currency": "RWF",
        "payment_method": "Mobile Money",
        "payment_id": "PAY-56789",
        "reference_number": "BRR-987654",
        "status": "Completed"
    }
    
    try:
        # Send the receipt
        result = sender.send_receipt(recipient, "Business Registration", receipt_data)
        logger.info(f"Receipt sent: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Error sending receipt: {str(e)}")
        return False

def create_sample_document(output_path: str):
    """Create a sample PDF document for testing"""
    try:
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(output_path)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "SpeakWise Sample Document")
        c.drawString(100, 730, "This is a test document for WhatsApp delivery")
        c.drawString(100, 710, "Transaction ID: TXN-12345")
        c.drawString(100, 690, "Date: 2023-10-30")
        c.save()
        
        logger.info(f"Sample document created at {output_path}")
        return True
    except ImportError:
        logger.error("reportlab package not installed - can't create sample document")
        logger.info("Install with: pip install reportlab")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test Pindo WhatsApp integration")
    parser.add_argument("--api-key", help="Pindo API key")
    parser.add_argument("--sender-id", help="WhatsApp sender ID (phone number)")
    parser.add_argument("--recipient", help="Recipient phone number (with country code)")
    parser.add_argument("--test", choices=["message", "document", "receipt"], help="Test to run")
    parser.add_argument("--message", help="Message to send")
    parser.add_argument("--document", help="Path to document file")
    
    args = parser.parse_args()
    
    # If API key not provided, try to get from environment
    api_key = args.api_key or os.environ.get("PINDO_API_KEY")
    sender_id = args.sender_id or os.environ.get("WHATSAPP_SENDER_ID")
    
    if not api_key:
        logger.error("API key is required. Set PINDO_API_KEY environment variable or use --api-key")
        return 1
    
    if not sender_id:
        logger.error("Sender ID is required. Set WHATSAPP_SENDER_ID environment variable or use --sender-id")
        return 1
    
    if not args.recipient:
        logger.error("Recipient phone number is required")
        return 1
    
    if args.test == "message":
        message = args.message or "This is a test message from SpeakWise"
        test_send_message(api_key, sender_id, args.recipient, message)
    
    elif args.test == "document":
        document_path = args.document
        
        if not document_path:
            # Create a sample document
            document_path = "test_document.pdf"
            if not create_sample_document(document_path):
                return 1
        
        test_send_document(api_key, sender_id, args.recipient, document_path, 
                         "Test document from SpeakWise")
    
    elif args.test == "receipt":
        test_send_receipt(api_key, sender_id, args.recipient)
    
    else:
        logger.error("Please specify a test to run: --test message|document|receipt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Test script for the SMS templates using the SMSSender class.
"""

import os
import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path to import project modules
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.messaging.sms_sender import SMSSender
from src.core.utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockConfig:
    """Mock configuration for testing"""
    def __init__(self, api_key, sender_id="PindoTest"):
        self.config = {
            "messaging": {
                "api_key": api_key,
                "sender_id": sender_id
            }
        }
    
    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)


def test_task_complete_template(api_key, recipient, service_name):
    """Test sending task completion template"""
    logger.info(f"Testing task completion template to {recipient}")
    
    # Create mock config
    config = MockConfig(api_key)
    
    # Initialize SMS sender
    sender = SMSSender(config)
    
    # Create sample transaction data
    transaction_data = {
        "transaction_id": "TXN-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "amount": 25000,
        "currency": "RWF"
    }
    
    try:
        # Send task completion message
        result = sender.send_task_complete(recipient, service_name, transaction_data)
        logger.info(f"Task completion message sent: {result}")
        return True
    except Exception as e:
        logger.error(f"Error sending task completion message: {str(e)}")
        return False

def test_document_ready_template(api_key, recipient, service_name):
    """Test sending document ready template"""
    logger.info(f"Testing document ready template to {recipient}")
    
    # Create mock config
    config = MockConfig(api_key)
    
    # Initialize SMS sender
    sender = SMSSender(config)
    
    # Sample document data
    reference_number = "REF-" + datetime.now().strftime("%Y%m%d-%H%M")
    download_link = f"https://speakwise.rw/documents/{reference_number}"
    
    try:
        # Send document ready message
        result = sender.send_document_ready(recipient, service_name, reference_number, download_link)
        logger.info(f"Document ready message sent: {result}")
        return True
    except Exception as e:
        logger.error(f"Error sending document ready message: {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test SMS templates")
    parser.add_argument("--api-key", help="Pindo API key")
    parser.add_argument("--to", required=True, help="Recipient phone number with country code")
    parser.add_argument("--name", default="Customer", help="Recipient name")
    parser.add_argument("--template", choices=["task_complete", "document_ready", "all"], 
                       required=True, help="Template to test")
    
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("PINDO_API_KEY")
    if not api_key:
        logger.error("API key is required. Set PINDO_API_KEY environment variable or use --api-key")
        return 1
    
    success = True
    
    if args.template == "task_complete" or args.template == "all":
        success = success and test_task_complete_template(api_key, args.to, "Birth Certificate Application")
    
    if args.template == "document_ready" or args.template == "all":
        success = success and test_document_ready_template(api_key, args.to, "Birth Certificate")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
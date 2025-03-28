#!/usr/bin/env python3
"""
Test script for the PindoAdapter class.
Run this script to test the SMS and call functions of the PindoAdapter.
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# Add parent directory to path to import project modules
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.telephony.pindo_adapter import PindoAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_send_sms(api_key, to_number, message, sender_id=None):
    """Test sending an SMS message using PindoAdapter"""
    logger.info(f"Testing SMS sending to {to_number}")
    
    # Initialize PindoAdapter
    adapter = PindoAdapter(api_key=api_key)
    
    try:
        # Send SMS
        result = adapter.send_sms(to_number, message, sender_id)
        logger.info(f"SMS sent successfully: {result}")
        return True
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return False

def test_initiate_call(api_key, to_number):
    """Test initiating a call using PindoAdapter"""
    logger.info(f"Testing call initiation to {to_number}")
    
    # Initialize PindoAdapter
    adapter = PindoAdapter(api_key=api_key)
    
    try:
        # Initiate call
        result = adapter.initiate_call(to_number)
        call_id = result.get("call_id")
        logger.info(f"Call initiated with call_id: {call_id}")
        
        # Ask user if they want to end the call
        if input(f"Call initiated to {to_number}. End the call? (y/n): ").lower() == 'y':
            end_result = adapter.end_call(call_id)
            logger.info(f"Call ended: {end_result}")
            
        return True
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test PindoAdapter functionality")
    parser.add_argument("--api-key", help="Pindo API key")
    parser.add_argument("--to", required=True, help="Recipient phone number with country code")
    parser.add_argument("--message", default="Test message from SpeakWise", help="Message for SMS test")
    parser.add_argument("--sender", help="Sender ID for SMS (default: PindoTest)")
    parser.add_argument("--test", choices=["sms", "call"], required=True, help="Test to run")
    
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("PINDO_API_KEY")
    if not api_key:
        logger.error("API key is required. Set PINDO_API_KEY environment variable or use --api-key")
        return 1
    
    if args.test == "sms":
        success = test_send_sms(api_key, args.to, args.message, args.sender)
    elif args.test == "call":
        success = test_initiate_call(api_key, args.to)
    else:
        logger.error("Invalid test type. Use 'sms' or 'call'")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
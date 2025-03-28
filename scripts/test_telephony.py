#!/usr/bin/env python3
"""
Test script for Pindo telephony integration.
Run this script to test making calls and handling webhooks.
"""

import os
import sys
import json
import logging
from pathlib import Path
import requests
import argparse

# Add parent directory to path to import project modules
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.telephony.pindo_adapter import PindoAdapter
from src.core.utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_make_call(api_key: str, phone_number: str):
    """Test making an outbound call"""
    logger.info(f"Testing outbound call to {phone_number}")
    
    # Initialize Pindo adapter
    adapter = PindoAdapter(api_key=api_key)
    
    try:
        # Make the call
        result = adapter.initiate_call(phone_number)
        logger.info(f"Call initiated: {json.dumps(result, indent=2)}")
        
        # Print instructions
        logger.info("Call initiated! Check your phone.")
        logger.info(f"Call ID: {result.get('call_id')}")
        
        return result.get('call_id')
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        return None

def test_webhook_handler(call_id: str):
    """Test handling an incoming webhook"""
    logger.info(f"Testing webhook handler for call {call_id}")
    
    # Create a sample webhook payload
    webhook_data = {
        "call_id": call_id,
        "event": "call.answered",
        "direction": "outbound",
        "timestamp": "2023-10-30T12:34:56Z",
        "status": "in-progress"
    }
    
    # Print the webhook data
    logger.info(f"Sample webhook data: {json.dumps(webhook_data, indent=2)}")
    
    # Initialize Pindo adapter
    adapter = PindoAdapter(api_key="test_api_key")
    
    # Test handling the webhook
    result = adapter.handle_webhook(webhook_data)
    logger.info(f"Webhook handling result: {json.dumps(result, indent=2)}")

def test_end_call(api_key: str, call_id: str):
    """Test ending a call"""
    logger.info(f"Testing ending call {call_id}")
    
    # Initialize Pindo adapter
    adapter = PindoAdapter(api_key=api_key)
    
    try:
        # End the call
        result = adapter.end_call(call_id)
        logger.info(f"Call ended: {json.dumps(result, indent=2)}")
    except Exception as e:
        logger.error(f"Error ending call: {str(e)}")

def run_telephony_api_server():
    """Run the telephony API server"""
    logger.info("Starting telephony API server...")
    
    try:
        # Import and run the API server
        from src.integrations.telephony.api import start_api
        start_api(host='localhost', port=5000)
    except Exception as e:
        logger.error(f"Error starting API server: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test Pindo telephony integration")
    parser.add_argument("--api-key", help="Pindo API key")
    parser.add_argument("--phone", help="Phone number to call (with country code)")
    parser.add_argument("--test", choices=["call", "webhook", "server"], help="Test to run")
    parser.add_argument("--call-id", help="Call ID for webhook test")
    
    args = parser.parse_args()
    
    # If API key not provided, try to get from environment
    api_key = args.api_key or os.environ.get("PINDO_API_KEY")
    
    if not api_key and args.test != "server":
        logger.error("API key is required. Set PINDO_API_KEY environment variable or use --api-key")
        return 1
    
    if args.test == "call":
        if not args.phone:
            logger.error("Phone number is required for call test")
            return 1
        
        call_id = test_make_call(api_key, args.phone)
        
        if call_id and input("End the call? (y/n): ").lower() == 'y':
            test_end_call(api_key, call_id)
    
    elif args.test == "webhook":
        if not args.call_id:
            logger.error("Call ID is required for webhook test")
            return 1
        
        test_webhook_handler(args.call_id)
    
    elif args.test == "server":
        run_telephony_api_server()
    
    else:
        logger.error("Please specify a test to run: --test call|webhook|server")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
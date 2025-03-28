#!/usr/bin/env python3
"""
Test script to check different potential Pindo voice API endpoints.
"""

import requests
import sys
import logging
import argparse
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_endpoint(api_key, endpoint, phone_number):
    """Test a specific API endpoint"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "to": phone_number
    }
    
    logger.info(f"Testing endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint, headers=headers)
        logger.info(f"GET Status: {response.status_code}")
        logger.info(f"GET Response: {response.text[:100]}...")
    except Exception as e:
        logger.error(f"GET Error: {str(e)}")
    
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        logger.info(f"POST Status: {response.status_code}")
        logger.info(f"POST Response: {response.text[:100]}...")
    except Exception as e:
        logger.error(f"POST Error: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test Pindo voice API endpoints")
    parser.add_argument("--api-key", required=True, help="Pindo API key")
    parser.add_argument("--phone", required=True, help="Recipient phone number with country code")
    
    args = parser.parse_args()
    
    # List of endpoints to test
    endpoints = [
        "https://api.pindo.io/v1/voice",
        "https://api.pindo.io/v1/voice/calls",
        "https://api.pindo.io/v1/call",
        "https://api.pindo.io/v1/calls",
        "https://api.pindo.io/v1/telephony",
        "https://api.pindo.io/v1/telephony/calls"
    ]
    
    for endpoint in endpoints:
        test_endpoint(args.api_key, endpoint, args.phone)
        print("-" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
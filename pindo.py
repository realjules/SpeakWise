#!/usr/bin/env python3
"""
Example script for using Pindo SMS and WhatsApp APIs.
This file serves as a demonstration of how to use the Pindo API.
"""

import requests
import os
import sys
import argparse
import json

def send_sms(api_key, to_number, message, sender="PindoTest"):
    """
    Send a single SMS using Pindo API
    
    Args:
        api_key: Pindo API key
        to_number: Recipient phone number (with country code)
        message: Message content
        sender: Sender ID (default: PindoTest)
        
    Returns:
        API response
    """
    url = 'https://api.pindo.io/v1/sms/'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'to': to_number,
        'text': message, 
        'sender': sender
    }
    
    print(f"Sending SMS to {to_number} using sender ID: {sender}")
    print(f"Message: {message}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status code: {response.status_code}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Example script for Pindo SMS")
    parser.add_argument("--api-key", help="Pindo API key")
    parser.add_argument("--to", required=True, help="Recipient phone number with country code")
    parser.add_argument("--message", default="Hello from SpeakWise", help="Message content")
    parser.add_argument("--sender", default="PindoTest", help="SMS Sender ID")
    
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("PINDO_API_KEY")
    if not api_key:
        print("Error: Pindo API key is required. Set PINDO_API_KEY environment variable or use --api-key")
        return 1
    
    result = send_sms(api_key, args.to, args.message, args.sender)
    print("Response:", json.dumps(result, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
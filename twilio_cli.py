#!/usr/bin/env python3
"""
Example script for using Twilio SMS and Voice APIs.
This file serves as a demonstration of how to use the Twilio API for messaging.
"""

from twilio.rest import Client
import os
import sys
import argparse
import json

def send_sms(account_sid, auth_token, to_number, message, from_number=None):
    """
    Send a single SMS using Twilio API
    
    Args:
        account_sid: Twilio account SID
        auth_token: Twilio auth token
        to_number: Recipient phone number (with country code)
        message: Message content
        from_number: Sender phone number (default: use first Twilio number)
        
    Returns:
        API response
    """
    client = Client(account_sid, auth_token)
    
    # If no from_number is provided, try to get one from the account
    if not from_number:
        try:
            # Get the first phone number from the account
            numbers = client.incoming_phone_numbers.list(limit=1)
            if numbers:
                from_number = numbers[0].phone_number
            else:
                print("Error: No phone numbers found in your Twilio account")
                return {"error": "No phone numbers available"}
        except Exception as e:
            print(f"Error retrieving phone numbers: {str(e)}")
            return {"error": str(e)}
    
    print(f"Sending SMS to {to_number} from {from_number}")
    print(f"Message: {message}")
    
    try:
        # Send the message
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        # Print message SID and status
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        
        # Return a dictionary representation of the message
        return {
            "sid": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
            "date_created": str(message.date_created),
            "price": message.price,
            "error_code": message.error_code,
            "error_message": message.error_message
        }
    except Exception as e:
        return {"error": str(e)}

def make_call(account_sid, auth_token, to_number, from_number=None, twiml_url=None):
    """
    Initiate a voice call using Twilio API
    
    Args:
        account_sid: Twilio account SID
        auth_token: Twilio auth token
        to_number: Recipient phone number (with country code)
        from_number: Caller phone number (default: use first Twilio number)
        twiml_url: URL to TwiML instructions for the call
        
    Returns:
        API response
    """
    client = Client(account_sid, auth_token)
    
    # If no from_number is provided, try to get one from the account
    if not from_number:
        try:
            numbers = client.incoming_phone_numbers.list(limit=1)
            if numbers:
                from_number = numbers[0].phone_number
            else:
                print("Error: No phone numbers found in your Twilio account")
                return {"error": "No phone numbers available"}
        except Exception as e:
            print(f"Error retrieving phone numbers: {str(e)}")
            return {"error": str(e)}
    
    # If no TwiML URL is provided, use a default greeting
    if not twiml_url:
        twiml_url = "http://demo.twilio.com/docs/voice.xml"
    
    print(f"Initiating call to {to_number} from {from_number}")
    
    try:
        # Make the call
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url=twiml_url
        )
        
        # Print call SID and status
        print(f"Call SID: {call.sid}")
        print(f"Status: {call.status}")
        
        # Return a dictionary representation of the call
        return {
            "sid": call.sid,
            "status": call.status,
            "to": call.to,
            "from": call.from_,
            "direction": call.direction,
            "date_created": str(call.date_created),
            "price": call.price,
            "error_code": call.error_code,
            "error_message": call.error_message
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Example script for Twilio SMS and Calls")
    parser.add_argument("--account-sid", help="Twilio Account SID")
    parser.add_argument("--auth-token", help="Twilio Auth Token")
    parser.add_argument("--to", required=True, help="Recipient phone number with country code")
    parser.add_argument("--from", dest="from_number", help="Sender phone number")
    parser.add_argument("--message", help="Message content for SMS")
    parser.add_argument("--call", action="store_true", help="Make a voice call instead of sending SMS")
    parser.add_argument("--twiml-url", help="TwiML URL for voice calls")
    
    args = parser.parse_args()
    
    # Get credentials from arguments or environment
    account_sid = args.account_sid or os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = args.auth_token or os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("Error: Twilio credentials are required. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables or use --account-sid and --auth-token")
        return 1
    
    # Determine whether to make a call or send an SMS
    if args.call:
        result = make_call(account_sid, auth_token, args.to, args.from_number, args.twiml_url)
    else:
        if not args.message:
            args.message = "Hello from SpeakWise!"
        result = send_sms(account_sid, auth_token, args.to, args.message, args.from_number)
    
    print("Response:", json.dumps(result, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
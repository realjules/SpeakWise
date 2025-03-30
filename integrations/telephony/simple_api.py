"""
Simplified telephony API implementation without Flask dependencies.
"""

import logging
import os
import json
import http.server
import socketserver
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse
import threading

from .pindo_adapter import PindoAdapter
from ...core.utils.config import Config

logger = logging.getLogger(__name__)

# Global instance of PindoAdapter
telephony_adapter = None

def initialize_adapter(api_key=None):
    """Initialize the PindoAdapter with the provided API key or from config"""
    global telephony_adapter
    
    if telephony_adapter is not None:
        return telephony_adapter
    
    # If no API key provided, try to get from config
    if api_key is None:
        try:
            config = Config()
            api_key = config.get("telephony", "api_key")
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise ValueError("No API key provided and couldn't load from config")
    
    # Create the adapter
    telephony_adapter = PindoAdapter(api_key=api_key)
    return telephony_adapter

class TelephonyRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler for telephony API"""
    
    def _set_headers(self, status_code=200, content_type="application/json"):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode())
    
    def _get_request_body(self):
        """Get request body as JSON"""
        content_length = int(self.headers["Content-Length"]) if "Content-Length" in self.headers else 0
        if content_length == 0:
            return {}
        
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode("utf-8"))
    
    def _handle_initiate_call(self):
        """Handle request to initiate a call"""
        try:
            # Get request body
            body = self._get_request_body()
            
            # Validate request
            if "phone_number" not in body:
                return self._send_json_response(
                    {"error": "Missing phone_number"}, 400
                )
            
            # Initialize adapter if needed
            adapter = initialize_adapter()
            
            # Make the call
            result = adapter.initiate_call(body["phone_number"])
            
            # Return success response
            return self._send_json_response(result)
        except Exception as e:
            logger.exception("Error initiating call")
            return self._send_json_response(
                {"error": str(e)}, 500
            )
    
    def _handle_end_call(self, call_id):
        """Handle request to end a call"""
        try:
            # Initialize adapter if needed
            adapter = initialize_adapter()
            
            # End the call
            result = adapter.end_call(call_id)
            
            # Return success response
            return self._send_json_response(result)
        except Exception as e:
            logger.exception(f"Error ending call {call_id}")
            return self._send_json_response(
                {"error": str(e)}, 500
            )
    
    def _handle_webhook(self):
        """Handle webhook from Pindo"""
        try:
            # Get request body
            webhook_data = self._get_request_body()
            
            # Validate webhook data
            if "call_id" not in webhook_data or "event" not in webhook_data:
                return self._send_json_response(
                    {"error": "Invalid webhook data"}, 400
                )
            
            # Initialize adapter if needed
            adapter = initialize_adapter()
            
            # Process webhook
            result = adapter.handle_webhook(webhook_data)
            
            # Return success response
            return self._send_json_response(result)
        except Exception as e:
            logger.exception("Error processing webhook")
            return self._send_json_response(
                {"error": str(e)}, 500
            )
    
    def _handle_send_sms(self):
        """Handle request to send an SMS"""
        try:
            # Get request body
            body = self._get_request_body()
            
            # Validate request
            if "to" not in body or "message" not in body:
                return self._send_json_response(
                    {"error": "Missing required fields (to, message)"}, 400
                )
            
            # Initialize adapter if needed
            adapter = initialize_adapter()
            
            # Send SMS
            result = adapter.send_sms(body["to"], body["message"], body.get("sender_id"))
            
            # Return success response
            return self._send_json_response(result)
        except Exception as e:
            logger.exception("Error sending SMS")
            return self._send_json_response(
                {"error": str(e)}, 500
            )
    
    def _handle_health_check(self):
        """Handle health check request"""
        return self._send_json_response({
            "status": "healthy",
            "version": "1.0.0"
        })
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse URL
        url_parts = urlparse(self.path)
        path = url_parts.path
        
        # Route based on path
        if path == "/telephony/health":
            return self._handle_health_check()
        else:
            self._send_json_response({"error": "Not Found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        # Parse URL
        url_parts = urlparse(self.path)
        path = url_parts.path
        
        # Route based on path
        if path == "/telephony/webhook":
            return self._handle_webhook()
        elif path == "/telephony/call":
            return self._handle_initiate_call()
        elif path == "/telephony/sms":
            return self._handle_send_sms()
        else:
            self._send_json_response({"error": "Not Found"}, 404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        # Parse URL
        url_parts = urlparse(self.path)
        path = url_parts.path
        
        # Route based on path
        if path.startswith("/telephony/call/"):
            call_id = path.split("/")[-1]
            return self._handle_end_call(call_id)
        else:
            self._send_json_response({"error": "Not Found"}, 404)

def start_api(host="0.0.0.0", port=5000, api_key=None):
    """Start the telephony API server"""
    # Initialize the adapter
    initialize_adapter(api_key)
    
    # Create and start the server
    handler = TelephonyRequestHandler
    httpd = socketserver.ThreadingTCPServer((host, port), handler)
    
    print(f"Starting telephony API server on {host}:{port}")
    print(f"Use Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Start the server
    start_api()
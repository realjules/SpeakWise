import logging
import requests
import os
from typing import Dict, Any, Optional
from pathlib import Path
import json
import string
from datetime import datetime

from ...core.utils.config import Config

logger = logging.getLogger(__name__)

class SMSSender:
    """
    Handles sending SMS messages using Pindo's API.
    Supports templates and formatted messages.
    """
    
    # Base URL for Pindo API
    BASE_URL = "https://api.pindo.io"
    SMS_API_URL = f"{BASE_URL}/v1/sms"
    
    def __init__(self, config: Config):
        """
        Initialize the SMS sender with configuration.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.api_key = config.get("messaging", "api_key")
        self.sender_id = config.get("messaging", "sender_id", "PindoTest")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Templates directory
        self.templates_dir = Path(__file__).parent / "sms_templates"
        
    def send_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """
        Send a text message via SMS.
        
        Args:
            recipient: The recipient's phone number
            message: The message text
            
        Returns:
            Response from the API
        """
        data = {
            "to": recipient,
            "text": message,
            "sender": self.sender_id
        }
        
        try:
            response = requests.post(
                f"{self.SMS_API_URL}/",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"SMS message sent to {recipient}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to send SMS message to {recipient}: {str(e)}")
            raise
    
    def send_template(self, recipient: str, template_name: str, 
                    context: Dict[str, str]) -> Dict[str, Any]:
        """
        Send a templated SMS message.
        
        Args:
            recipient: The recipient's phone number
            template_name: The name of the template file (without .txt extension)
            context: Dictionary of values to substitute in the template
            
        Returns:
            Response from the API
        """
        template_path = self.templates_dir / f"{template_name}_template.txt"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
            
        with open(template_path, 'r') as f:
            template = f.read()
            
        # Format the template with the provided context
        message = template.format(**context)
        
        return self.send_message(recipient, message)
    
    def send_task_complete(self, recipient: str, service_name: str,
                         transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a task completion notification via SMS.
        
        Args:
            recipient: The recipient's phone number
            service_name: The name of the service
            transaction_data: Transaction data including payment details
            
        Returns:
            Response from the API
        """
        context = {
            "service_name": service_name,
            "transaction_id": transaction_data.get("transaction_id", "N/A"),
            "date": transaction_data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "amount": f"{transaction_data.get('amount', 0):,}",
            "currency": transaction_data.get("currency", "RWF")
        }
        
        return self.send_template(recipient, "task_complete", context)
    
    def send_document_ready(self, recipient: str, service_name: str, 
                          reference_number: str, download_link: str,
                          approval_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a document ready notification with download link via SMS.
        
        Args:
            recipient: The recipient's phone number
            service_name: The name of the service
            reference_number: Reference number for the document
            download_link: URL to download the document
            approval_date: Date when the document was approved (optional)
            
        Returns:
            Response from the API
        """
        
        context = {
            "service_name": service_name,
            "reference_number": reference_number,
            "approval_date": approval_date or datetime.now().strftime("%Y-%m-%d"),
            "download_link": download_link
        }
        
        return self.send_template(recipient, "document_ready", context)
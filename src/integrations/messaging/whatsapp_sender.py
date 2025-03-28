import logging
import requests
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json

from ...core.utils.config import Config

logger = logging.getLogger(__name__)

class WhatsAppSender:
    """
    Handles sending WhatsApp messages and documents using Pindo's API.
    """
    
    # Base URL for Pindo API
    BASE_URL = "https://api.pindo.io"
    WHATSAPP_API_URL = f"{BASE_URL}/v1/whatsapp"
    
    def __init__(self, config: Config):
        """
        Initialize the WhatsApp sender with configuration.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.api_key = config.get("messaging", "api_key")
        self.sender_id = config.get("messaging", "whatsapp_sender_id")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def send_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp.
        
        Args:
            recipient: The recipient's phone number
            message: The message text
            
        Returns:
            Response from the API
        """
        data = {
            "to": recipient,
            "from": self.sender_id,
            "message": message,
            "type": "text"
        }
        
        try:
            response = requests.post(
                f"{self.WHATSAPP_API_URL}/messages",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp message sent to {recipient}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to send WhatsApp message to {recipient}: {str(e)}")
            raise
    
    def send_document(self, recipient: str, document_path: Union[str, Path], 
                     caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a document via WhatsApp.
        
        Args:
            recipient: The recipient's phone number
            document_path: Path to the document file
            caption: Optional caption for the document
            
        Returns:
            Response from the API
        """
        document_path = Path(document_path)
        
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
            
        # First upload the document to get a media ID
        media_id = self._upload_media(document_path)
        
        # Then send the document message
        data = {
            "to": recipient,
            "from": self.sender_id,
            "type": "document",
            "media_id": media_id,
        }
        
        if caption:
            data["caption"] = caption
            
        try:
            response = requests.post(
                f"{self.WHATSAPP_API_URL}/messages",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp document sent to {recipient}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to send WhatsApp document to {recipient}: {str(e)}")
            raise
            
    def _upload_media(self, file_path: Path) -> str:
        """
        Upload media to Pindo and get a media ID.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Media ID from Pindo
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with open(file_path, "rb") as file:
            files = {"file": (file_path.name, file, self._get_mime_type(file_path))}
            
            try:
                response = requests.post(
                    f"{self.WHATSAPP_API_URL}/media",
                    headers=headers,
                    files=files
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Media uploaded: {file_path.name}")
                return result["media_id"]
            except requests.RequestException as e:
                logger.error(f"Failed to upload media {file_path.name}: {str(e)}")
                raise
                
    def _get_mime_type(self, file_path: Path) -> str:
        """
        Get the MIME type based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        extension = file_path.suffix.lower()
        
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".txt": "text/plain"
        }
        
        return mime_types.get(extension, "application/octet-stream")
    
    def send_receipt(self, recipient: str, service_name: str, 
                    receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a formatted receipt via WhatsApp.
        
        Args:
            recipient: The recipient's phone number
            service_name: The name of the service
            receipt_data: Receipt data dictionary
            
        Returns:
            Response from the API
        """
        # Format the receipt as a text message
        message = self._format_receipt(service_name, receipt_data)
        
        return self.send_message(recipient, message)
        
    def _format_receipt(self, service_name: str, receipt_data: Dict[str, Any]) -> str:
        """
        Format receipt data as a text message.
        
        Args:
            service_name: The name of the service
            receipt_data: Receipt data dictionary
            
        Returns:
            Formatted receipt text
        """
        # Build the receipt message
        receipt = f"*SpeakWise Receipt - {service_name}*\n\n"
        
        # Add transaction details
        receipt += f"Transaction ID: {receipt_data.get('transaction_id', 'N/A')}\n"
        receipt += f"Date: {receipt_data.get('date', 'N/A')}\n"
        receipt += f"Amount: {receipt_data.get('amount', 0):,} {receipt_data.get('currency', 'RWF')}\n\n"
        
        # Add service details
        receipt += f"Service: {service_name}\n"
        if 'reference_number' in receipt_data:
            receipt += f"Reference Number: {receipt_data['reference_number']}\n"
            
        # Add payment details
        receipt += f"\nPayment Method: {receipt_data.get('payment_method', 'N/A')}\n"
        if 'payment_id' in receipt_data:
            receipt += f"Payment ID: {receipt_data['payment_id']}\n"
            
        # Add confirmation and thank you message
        receipt += f"\nStatus: {receipt_data.get('status', 'Completed')}\n\n"
        receipt += "Thank you for using SpeakWise for your government services.\n"
        receipt += "For support, call: +250780123456"
        
        return receipt
        
    def send_template(self, recipient: str, template_name: str, 
                     parameters: Dict[str, str]) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp.
        
        Args:
            recipient: The recipient's phone number
            template_name: The name of the template
            parameters: Template parameters
            
        Returns:
            Response from the API
        """
        data = {
            "to": recipient,
            "from": self.sender_id,
            "type": "template",
            "template": {
                "name": template_name,
                "parameters": parameters
            }
        }
        
        try:
            response = requests.post(
                f"{self.WHATSAPP_API_URL}/messages",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp template message sent to {recipient}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to send WhatsApp template to {recipient}: {str(e)}")
            raise
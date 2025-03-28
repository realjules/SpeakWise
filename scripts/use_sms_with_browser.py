#!/usr/bin/env python3
"""
Example script showing how to integrate SMS notifications with the browser agent.
This demonstrates how to send notifications at key points in the workflow.
"""

import os
import sys
import logging
from pathlib import Path
import asyncio
from datetime import datetime

# Add parent directory to path to import project modules
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.messaging.sms_sender import SMSSender
from src.core.utils.config import Config
from scripts.browserUse import BrowserUseAgent  # Import the browser agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserWorkflow:
    """Example workflow integrating browser agent with SMS notifications"""
    
    def __init__(self, api_key=None):
        """Initialize the workflow with configuration"""
        # Load configuration
        self.config = Config()
        
        # Override API key if provided
        if api_key:
            self.config.set("messaging", "api_key", api_key)
            
        # Initialize SMS sender
        self.sms_sender = SMSSender(self.config)
        
        # Initialize browser agent
        self.browser_agent = BrowserUseAgent()
        
    async def run_birth_certificate_workflow(self, recipient_phone, applicant_name):
        """Run the birth certificate application workflow with SMS notifications"""
        logger.info(f"Starting birth certificate workflow for {applicant_name}")
        
        try:
            # 1. Run the browser agent to complete the application
            result = await self.browser_agent.apply_for_birth_certificate(
                for_self=True,
                processing_office={"District": "Gasabo", "Sector": "Remera"},
                reason="Education"
            )
            
            # 2. Check if the application was successful
            if result and "success" in result.lower():
                # Extract transaction details from the result
                # In a real implementation, you would parse the result to get these details
                transaction_data = {
                    "transaction_id": f"BC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": 5000,  # Example amount
                    "currency": "RWF"
                }
                
                # 3. Send task completion notification
                self.sms_sender.send_task_complete(
                    recipient_phone,
                    "Birth Certificate Application",
                    transaction_data
                )
                
                logger.info(f"Birth certificate application completed for {applicant_name}")
                return True
            else:
                logger.error(f"Birth certificate application failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error in birth certificate workflow: {str(e)}")
            return False
    
    def send_document_notification(self, recipient_phone, reference_number, document_url):
        """Send notification that a document is ready for download"""
        try:
            # Send document ready notification
            self.sms_sender.send_document_ready(
                recipient_phone,
                "Birth Certificate",
                reference_number,
                document_url
            )
            
            logger.info(f"Document ready notification sent to {recipient_phone}")
            return True
        except Exception as e:
            logger.error(f"Error sending document notification: {str(e)}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Example Browser Agent + SMS workflow")
    parser.add_argument("--api-key", help="Pindo API key")
    parser.add_argument("--phone", required=True, help="Recipient phone number with country code")
    parser.add_argument("--name", required=True, help="Applicant name")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (skip browser agent)")
    
    args = parser.parse_args()
    
    # Create workflow
    workflow = BrowserWorkflow(args.api_key)
    
    if args.demo:
        # Demo mode - just send SMS notifications
        logger.info("Running in demo mode")
        
        # Simulate task completion
        transaction_data = {
            "transaction_id": f"BC-DEMO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": 5000,
            "currency": "RWF"
        }
        
        # Send task completion notification
        workflow.sms_sender.send_task_complete(
            args.phone,
            "Birth Certificate Application",
            transaction_data
        )
        
        # Simulate document ready (after a short delay)
        import time
        time.sleep(5)  # Wait 5 seconds
        
        reference_number = f"RW-BC-{datetime.now().strftime('%Y%m%d-%H%M')}"
        document_url = f"https://speakwise.rw/documents/{reference_number}"
        
        workflow.send_document_notification(
            args.phone,
            reference_number,
            document_url
        )
    else:
        # Run the full workflow with browser agent
        asyncio.run(workflow.run_birth_certificate_workflow(args.phone, args.name))
    
    return 0

if __name__ == "__main__":
    import argparse
    sys.exit(main())
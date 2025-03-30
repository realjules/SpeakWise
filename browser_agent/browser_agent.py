from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
import asyncio
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
import json
import logging
from enum import Enum
import time
import sys

# Add the project root to the path to allow importing from other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import local modules
from .prompts import BIRTH_CERTIFICATE_TEMPLATE, DRIVING_LICENSE_TEMPLATE
from .analytics_updater import AnalyticsUpdater

# Import SMS sender if available
try:
    from src.integrations.messaging.sms_sender import SMSSender
    from src.core.utils.config import Config
    SMS_AVAILABLE = True
except ImportError:
    logging.warning("SMS functionality not available - continuing without SMS notifications")
    SMS_AVAILABLE = False

class BrowserUseAgent:
    def __init__(self, api_key=None, model="gpt-4o", verbose=True, headless=True, 
                sms_enabled=True, update_dashboard=True):
        """
        Initialize the BrowserUseAgent with API key and model.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None.
            model (str, optional): LLM model to use. Defaults to "gpt-4o".
            verbose (bool, optional): Enable verbose output. Defaults to True.
            headless (bool, optional): Run browser in headless mode. Defaults to True.
            sms_enabled (bool, optional): Enable SMS notifications. Defaults to True.
            update_dashboard (bool, optional): Enable dashboard updates. Defaults to True.
        """
        load_dotenv()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("BrowserUseAgent")
        
        # Set API key if provided, otherwise use from environment
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            
        self.model = model
        self.llm = ChatOpenAI(model=self.model, temperature=0.2)  # Slightly higher temperature for more adaptability
        self.verbose = verbose
        self.headless = headless
        
        # Feature flags
        self.sms_enabled = sms_enabled and SMS_AVAILABLE
        self.update_dashboard = update_dashboard
        
        # Load credentials from environment variables
        self.password = os.getenv("PASSWORD")
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.national_id = os.getenv("NATIONAL_ID")
        
        # Validate environment variables
        if not all([self.password, self.phone_number, self.national_id]):
            raise ValueError("Missing required environment variables. Please check your .env file.")
            
        # Initialize analytics updater if dashboard updates enabled
        self.analytics_updater = AnalyticsUpdater() if self.update_dashboard else None
        
        # Initialize SMS sender if SMS notifications enabled
        self.sms_sender = None
        if self.sms_enabled:
            try:
                config = Config()
                api_key = config.get("messaging", "api_key", "")
                
                # Check if API key is still the placeholder
                if not api_key or api_key in ["your_pindo_api_key_here", "PUT_YOUR_ACTUAL_PINDO_API_KEY_HERE"]:
                    self.logger.warning("Pindo API key not set or contains placeholder value. SMS functionality disabled.")
                    self.sms_enabled = False
                else:
                    self.sms_sender = SMSSender(config)
                    self.logger.info("SMS sender initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize SMS sender: {e}")
                self.sms_enabled = False
                
        self.schema = {}
    
    async def apply_for_birth_certificate(self, for_self=True, processing_office=None, reason=None):
        """
        Apply for a birth certificate on Irembo with enhanced robustness.
        """
        who = "Self" if for_self else "Child"
        self.schema["birth_certificate"] = []
        # Define schema steps
        self.schema["birth_certificate"].append({"login credentials": ["phone number or email", "password"]})
        self.schema["birth_certificate"].append({"Birth services": ["Birth certificate", "Birth record"]})
        
        # Create a dictionary with all values to be formatted in the template
        format_values = {
            'phone_number': self.phone_number,
            'password': self.password,
            'who': who,
            'national_id': self.national_id,
            'reason': reason
        }
        
        # Extract district and sector directly for template
        if isinstance(processing_office, dict):
            format_values['district'] = processing_office.get('District', '')
            format_values['sector'] = processing_office.get('Sector', '')
        else:
            format_values['district'] = ''
            format_values['sector'] = ''
            
        # Use the template from prompts.py with formatted values
        try:
            task = BIRTH_CERTIFICATE_TEMPLATE.format(**format_values)
            self.logger.info("Template formatting successful")
        except Exception as e:
            self.logger.error(f"Error formatting template: {e}")
            raise
        
        # Update schema
        self.schema["birth_certificate"].append({"application type": "self or child"})
        self.schema["birth_certificate"].append("national id")
        self.schema["birth_certificate"].append({"processing details": [{"office": ["District", "Sector"]}, "reason"]})
        self.schema["birth_certificate"].append({"notification": "choose phone number or email or both"})
        
        # Pass the task to the Agent instance
        self.logger.info("Creating Agent for birth certificate application")
        try:
            agent = Agent(
                task=task,
                llm=self.llm
                # The browser_use Agent doesn't accept verbose parameter
            )
            self.logger.info("Agent created successfully")
        except Exception as e:
            self.logger.error(f"Error creating agent: {e}")
            raise
        
        try:
            self.logger.info("Running birth certificate application agent")
            results = await agent.run()
            if self.verbose:
                print(results)
            self.logger.info("Agent completed run")
            
            # Send SMS notification if enabled
            if self.sms_enabled and self.sms_sender:
                try:
                    # Generate transaction ID for the birth certificate application
                    transaction_id = f"BC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Create transaction data for SMS
                    transaction_data = {
                        "transaction_id": transaction_id,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": 5000,  # Example amount for birth certificate
                        "currency": "RWF"
                    }
                    
                    # Send SMS notification
                    self.logger.info(f"Sending SMS notification to {self.phone_number}")
                    sms_result = self.sms_sender.send_task_complete(
                        self.phone_number, 
                        "Birth Certificate",
                        transaction_data
                    )
                    self.logger.info(f"SMS notification sent: {sms_result}")
                    
                    # Update analytics if dashboard updates enabled
                    if self.update_dashboard and self.analytics_updater:
                        # Generate SMS ID
                        sms_id = sms_result.get("id", f"SMS-{uuid.uuid4().hex[:8]}")
                        
                        # Add SMS record to analytics
                        self.analytics_updater.add_sms_record(
                            sms_id=sms_id,
                            recipient=self.phone_number,
                            service="Birth Certificate",
                            status="delivered",
                            sms_type="task_complete",
                            reference=transaction_id
                        )
                        
                        # Add completed call to calls data
                        self.analytics_updater.add_completed_call(
                            phone_number=self.phone_number,
                            service_name="Birth Certificate",
                            success=True,
                            duration_seconds=180
                        )
                except Exception as e:
                    self.logger.error(f"Failed to send SMS notification: {e}")
            
            # Browser-use Agent doesn't have a close method
            # No explicit close needed
            
            # Return results with additional metadata
            return {
                "status": "success",
                "service": "Birth Certificate",
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
        except Exception as e:
            self.logger.error(f"Error during agent run: {e}")
            raise
     
    async def register_driving_license_exam(self, test_type=None, district=None, preferred_date=None):
        """
        Register for driving license written exam on Irembo.
        """
        # Use the template from prompts.py with formatted values
        task = DRIVING_LICENSE_TEMPLATE.format(
            phone_number=self.phone_number,
            password=self.password,
            test_type=test_type,
            district=district
        )
        
        # Pass the task to the Agent instance
        self.logger.info("Creating Agent for driving license exam registration")
        try:
            agent = Agent(
                task=task,
                llm=self.llm
                # The browser_use Agent doesn't accept verbose parameter
            )
            self.logger.info("Agent created successfully")
        except Exception as e:
            self.logger.error(f"Error creating agent: {e}")
            raise
        
        try:
            self.logger.info("Running driving license exam registration agent")
            results = await agent.run()
            if self.verbose:
                print(results)
            self.logger.info("Agent completed run")
            
            # Save schema to file
            with open("schema.json", "w") as json_file:
                json.dump(self.schema, json_file, indent=4)
                
            # Send SMS notification if enabled
            if self.sms_enabled and self.sms_sender:
                try:
                    # Generate transaction ID for the driving license exam
                    transaction_id = f"DL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Create transaction data for SMS
                    transaction_data = {
                        "transaction_id": transaction_id,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": 10000,  # Example amount for driving license exam
                        "currency": "RWF"
                    }
                    
                    # Send SMS notification
                    self.logger.info(f"Sending SMS notification to {self.phone_number}")
                    sms_result = self.sms_sender.send_task_complete(
                        self.phone_number, 
                        "Driving License Exam Registration",
                        transaction_data
                    )
                    self.logger.info(f"SMS notification sent: {sms_result}")
                    
                    # Update analytics if dashboard updates enabled
                    if self.update_dashboard and self.analytics_updater:
                        # Generate SMS ID
                        sms_id = sms_result.get("id", f"SMS-{uuid.uuid4().hex[:8]}")
                        
                        # Add SMS record to analytics
                        self.analytics_updater.add_sms_record(
                            sms_id=sms_id,
                            recipient=self.phone_number,
                            service="Driving License Exam",
                            status="delivered",
                            sms_type="task_complete",
                            reference=transaction_id
                        )
                        
                        # Add completed call to calls data
                        self.analytics_updater.add_completed_call(
                            phone_number=self.phone_number,
                            service_name="Driving License Exam",
                            success=True,
                            duration_seconds=210  # Slightly different duration
                        )
                except Exception as e:
                    self.logger.error(f"Failed to send SMS notification: {e}")
                    
            # Return results with additional metadata
            return {
                "status": "success",
                "service": "Driving License Exam",
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
        except Exception as e:
            self.logger.error(f"Error during agent run: {e}")
            raise

    def run_async(self, coroutine):
        """
        Helper method to run async methods from synchronous code.
        """
        return asyncio.run(coroutine)
    

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Browser agent for government services')
    
    # General arguments
    parser.add_argument('--verbose', type=bool, default=True, help='Verbose output')
    parser.add_argument('--headless', type=bool, default=True, help='Run browser in headless mode')
    parser.add_argument('--sms_enabled', type=bool, default=False, help='Enable SMS notifications')
    parser.add_argument('--update_dashboard', type=bool, default=False, help='Update dashboard analytics')
    
    # Birth certificate arguments
    parser.add_argument('--for_self', type=str, help='Is the certificate for yourself (True/False)')
    parser.add_argument('--district', type=str, help='District for processing office')
    parser.add_argument('--sector', type=str, help='Sector for processing office')
    parser.add_argument('--reason', type=str, help='Reason for certificate request')
    
    # Driving license arguments
    parser.add_argument('--test_type', type=str, help='Type of driving test')
    parser.add_argument('--preferred_date', type=str, help='Preferred date for exam')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create the agent with parsed arguments
    agent = BrowserUseAgent(
        verbose=args.verbose, 
        headless=args.headless,
        sms_enabled=args.sms_enabled,
        update_dashboard=args.update_dashboard
    )
    
    # Determine which service to run based on arguments provided
    if args.for_self is not None and args.district and args.sector and args.reason:
        # Convert string 'True'/'False' to boolean
        for_self = args.for_self.lower() == 'true'
        
        # Apply for birth certificate
        processing_office = {"District": args.district, "Sector": args.sector}
        result = agent.run_async(
            agent.apply_for_birth_certificate(
                for_self=for_self,
                processing_office=processing_office,
                reason=args.reason
            )
        )
        print("Birth Certificate Application completed with result:", result)
        
    elif args.test_type and args.district:
        # Register for driving license exam
        result = agent.run_async(
            agent.register_driving_license_exam(
                test_type=args.test_type,
                district=args.district,
                preferred_date=args.preferred_date
            )
        )
        print("Driving License Exam Registration completed with result:", result)
        
    else:
        print("Error: Insufficient arguments provided. Please provide either:")
        print("  For birth certificate: --for_self, --district, --sector, and --reason")
        print("  For driving license: --test_type and --district")
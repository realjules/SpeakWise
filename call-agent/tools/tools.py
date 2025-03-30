import chainlit as cl
import sys
import os
import logging
from datetime import datetime

# Add the project root to path to allow importing browser_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("call_agent_tools")

# Import BrowserUseAgent class
try:
    from browser_agent.browser_agent import BrowserUseAgent
    BROWSER_AGENT_AVAILABLE = True
    logger.info("Browser agent successfully imported")
except ImportError as e:
    BROWSER_AGENT_AVAILABLE = False
    logger.warning(f"Browser agent not available: {e}")

# No stock-related or chart tools - focusing only on government services

# Define browser agent tools if available
if BROWSER_AGENT_AVAILABLE:
    # Tool for birth certificate application
    birth_certificate_def = {
        "name": "apply_for_birth_certificate",
        "description": "Applies for a birth certificate through the Irembo government portal using browser automation.",
        "parameters": {
            "type": "object",
            "properties": {
                "for_self": {
                    "type": "boolean",
                    "description": "Whether the certificate is for the user themselves (true) or for a child (false)",
                },
                "district": {
                    "type": "string",
                    "description": "The district for processing the certificate (e.g., 'Gasabo', 'Kicukiro')",
                },
                "sector": {
                    "type": "string",
                    "description": "The sector for processing the certificate (e.g., 'Jali', 'Gisozi')",
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for requesting the certificate (e.g., 'Education', 'Employment', 'Travel')",
                },
            },
            "required": ["for_self", "district", "sector", "reason"],
        },
    }

    # Tool for driving license registration
    driving_license_def = {
        "name": "register_driving_license_exam",
        "description": "Registers for a driving license exam through the Irembo government portal using browser automation.",
        "parameters": {
            "type": "object",
            "properties": {
                "test_type": {
                    "type": "string",
                    "description": "The type of driving test (e.g., 'Registration for Driving Test - Provisional, paper-based')",
                },
                "district": {
                    "type": "string",
                    "description": "The district for taking the exam (e.g., 'Gasabo', 'Kicukiro')",
                },
                "preferred_date": {
                    "type": "string",
                    "description": "The preferred date for the exam in YYYY-MM-DD format",
                },
            },
            "required": ["test_type", "district"],
        },
    }

    # Handler for birth certificate application
    async def birth_certificate_handler(for_self, district, sector, reason):
        """
        Handles birth certificate application requests by delegating to the browser agent.
        """
        try:
            # Create browser agent with minimal features (no analytics, no SMS)
            browser_agent = BrowserUseAgent(
                verbose=True, 
                headless=True,
                sms_enabled=False,
                update_dashboard=False
            )
            
            # Format processing_office parameter
            processing_office = {
                "District": district,
                "Sector": sector
            }
            
            # Call the browser agent method
            result = await browser_agent.apply_for_birth_certificate(
                for_self=for_self,
                processing_office=processing_office,
                reason=reason
            )
            
            # Send result to chat UI
            await cl.Message(
                content=f"✅ Birth certificate application submitted successfully!\n\nService: {result['service']}\nTimestamp: {result['timestamp']}"
            ).send()
            
            return {
                "status": "success",
                "service": "Birth Certificate",
                "timestamp": datetime.now().isoformat(),
                "message": "Application submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error in birth certificate application: {e}")
            
            # Send error to chat UI
            await cl.Message(
                content=f"❌ There was an error with your birth certificate application: {str(e)}"
            ).send()
            
            return {
                "status": "error",
                "service": "Birth Certificate",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    # Handler for driving license registration
    async def driving_license_handler(test_type, district, preferred_date=None):
        """
        Handles driving license exam registration requests by delegating to the browser agent.
        """
        try:
            # Create browser agent with minimal features (no analytics, no SMS)
            browser_agent = BrowserUseAgent(
                verbose=True, 
                headless=True,
                sms_enabled=False,
                update_dashboard=False
            )
            
            # Call the browser agent method
            result = await browser_agent.register_driving_license_exam(
                test_type=test_type,
                district=district,
                preferred_date=preferred_date
            )
            
            # Send result to chat UI
            await cl.Message(
                content=f"✅ Driving license exam registration submitted successfully!\n\nService: {result['service']}\nTimestamp: {result['timestamp']}"
            ).send()
            
            return {
                "status": "success",
                "service": "Driving License Exam",
                "timestamp": datetime.now().isoformat(),
                "message": "Registration submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error in driving license registration: {e}")
            
            # Send error to chat UI
            await cl.Message(
                content=f"❌ There was an error with your driving license exam registration: {str(e)}"
            ).send()
            
            return {
                "status": "error",
                "service": "Driving License Exam",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    # Create tool tuples
    birth_certificate = (birth_certificate_def, birth_certificate_handler)
    driving_license = (driving_license_def, driving_license_handler)
    
    # Add browser agent tools to the tools list
    tools = [query_stock_price, draw_plotly_chart, birth_certificate, driving_license]
    
    # Create information tools regardless of browser agent availability

# Tool to list available government services
list_available_services_def = {
    "name": "list_available_services",
    "description": "Lists all currently available government services that can be processed through the voice assistant.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

async def list_available_services_handler():
    """
    Lists all currently available government services.
    """
    services_message = """
# ⚠️ AVAILABLE SERVICES - IMPORTANT

We currently ONLY support these two specific government services:

1. **Birth Certificate Application**
   - Apply for your own birth certificate or for a child
   - Process applications through the Irembo portal

2. **Driving License Exam Registration**
   - Register for driving license written exams
   - Choose your preferred testing location and date

⚠️ NO OTHER SERVICES are available at this time. We cannot process business registrations, marriage certificates, national IDs, passports, or other government services yet.

Would you like help with a birth certificate application or driving license exam registration?
"""
    await cl.Message(content=services_message).send()
    
    return {
        "status": "success",
        "available_services": [
            "Birth Certificate Application",
            "Driving License Exam Registration"
        ]
    }

# Tool to explain birth certificate requirements
birth_certificate_requirements_def = {
    "name": "explain_birth_certificate_requirements",
    "description": "Explains what information is needed to apply for a birth certificate.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

async def birth_certificate_requirements_handler():
    """
    Explains the EXACT requirements for birth certificate applications.
    """
    requirements_message = """
# ⚠️ BIRTH CERTIFICATE APPLICATION - EXACT REQUIREMENTS

We need EXACTLY these items to complete your birth certificate application:

## REQUIRED INFORMATION - NOTHING MORE, NOTHING LESS:
1. **Phone Number**: Your Irembo account phone number
2. **Password**: Your Irembo account password
3. **For Self or Child**: Is this certificate for yourself (yes/no)?
4. **National ID**: Your personal ID number
5. **District**: Processing office district (e.g., Gasabo, Kicukiro)
6. **Sector**: Processing office sector within that district (e.g., Jali, Gisozi)
7. **Reason**: Purpose for certificate request (e.g., Education, Employment, Travel)

We do NOT need any other information such as:
- Guardian name (not required)
- Birth date (not required, already in your National ID)
- Birth place (not required for this application)
- Parent details (not required for this application)
- Email address (optional, phone is sufficient)

Would you like to proceed with a birth certificate application?
"""
    await cl.Message(content=requirements_message).send()
    
    return {
        "status": "success",
        "service": "Birth Certificate",
        "requirements_explained": True
    }

# Tool to explain driving license exam requirements
driving_license_requirements_def = {
    "name": "explain_driving_license_requirements",
    "description": "Explains what information is needed to register for a driving license exam.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

async def driving_license_requirements_handler():
    """
    Explains the EXACT requirements for driving license exam registration.
    """
    requirements_message = """
# ⚠️ DRIVING LICENSE EXAM - EXACT REQUIREMENTS

We need EXACTLY these items to register you for a driving license exam:

## REQUIRED INFORMATION - NOTHING MORE, NOTHING LESS:
1. **Phone Number**: Your Irembo account phone number
2. **Password**: Your Irembo account password
3. **Test Type**: "Registration for Driving Test - Provisional, paper-based"
4. **Test Language**: English or Kinyarwanda
5. **District**: Where you want to take the exam (e.g., Gasabo, Kicukiro)
6. **Date Preference**: Optional - a preferred exam date if you have one

We do NOT need any other information such as:
- Vehicle information (not required for exam registration)
- Previous driving history (not required)
- Medical information (not required at this stage)
- Fingerprint or photo (not needed for registration)
- Home address (not required for this registration)

Would you like to proceed with driving license exam registration?
"""
    await cl.Message(content=requirements_message).send()
    
    return {
        "status": "success",
        "service": "Driving License Exam",
        "requirements_explained": True
    }

# Create information tool tuples
list_available_services = (list_available_services_def, list_available_services_handler)
birth_certificate_requirements = (birth_certificate_requirements_def, birth_certificate_requirements_handler)
driving_license_requirements = (driving_license_requirements_def, driving_license_requirements_handler)

# Add information tools to the main tools list
if BROWSER_AGENT_AVAILABLE:
    # Add both browser agent tools and information tools
    tools = [
        birth_certificate, 
        driving_license,
        list_available_services,
        birth_certificate_requirements,
        driving_license_requirements
    ]
    
    # Log available tools
    logger.info("Browser agent tools and information tools added to voice assistant")
else:
    # Add only information tools if browser agent is not available
    tools = [
        list_available_services,
        birth_certificate_requirements,
        driving_license_requirements
    ]
    
    # Log that browser agent tools are not available
    logger.warning("Browser agent tools not available - continuing with basic and information tools only")

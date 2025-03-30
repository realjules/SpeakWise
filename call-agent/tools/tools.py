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

# Import browser_agent functionality
try:
    # Direct import of the browser_agent module
    import sys
    import os
    # Add browser_agent directory to the path
    browser_agent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../browser_agent'))
    sys.path.insert(0, browser_agent_path)
    
    from browser_agent.browser_agent import BrowserUseAgent
    BROWSER_AGENT_AVAILABLE = True
    logger.info("Browser agent successfully imported from: " + browser_agent_path)
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
        Handles birth certificate application requests by directly running the browser agent script.
        """
        try:
            # Direct execution of the browser_agent instead of creating an instance
            import subprocess
            import sys
            import os
            
            # Get the absolute path to the browser_agent.py file
            browser_agent_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../browser_agent/browser_agent.py'))
            logger.info(f"Running browser agent script at: {browser_agent_script}")
            
            # Create command to run the script with arguments
            command = [
                sys.executable,  # Current Python interpreter
                browser_agent_script,
                "--for_self", str(for_self),
                "--district", district,
                "--sector", sector,
                "--reason", reason,
                "--headless", "True",
                "--update_dashboard", "False"
            ]
            
            # Log the command we're about to run
            logger.info(f"Executing command: {' '.join(command)}")
            
            # Run the browser_agent.py script as a subprocess
            result = subprocess.run(
                command, 
                capture_output=True,
                text=True,
                check=False
            )
            
            # Log the output
            logger.info(f"Browser agent output: {result.stdout}")
            if result.stderr:
                logger.error(f"Browser agent error: {result.stderr}")
                
            # Check if the execution was successful
            if result.returncode != 0:
                raise Exception(f"Browser agent execution failed with code {result.returncode}: {result.stderr}")
                
            # Process result - for now create a result structure similar to what the browser agent would return
            browser_agent_result = {
                "status": "success" if result.returncode == 0 else "error",
                "service": "Birth Certificate",
                "timestamp": datetime.now().isoformat(),
                "output": result.stdout
            }
            
            # Send result to chat UI
            await cl.Message(
                content=f"✅ Birth certificate application submitted successfully!\n\nService: {browser_agent_result['service']}\nTimestamp: {browser_agent_result['timestamp']}\n\nOutput: {browser_agent_result['output'][:500]}..."
            ).send()
            
            return {
                "status": "success",
                "service": "Birth Certificate",
                "timestamp": datetime.now().isoformat(),
                "message": "Application submitted successfully",
                "command_output": result.stdout
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
        Handles driving license exam registration requests by directly running the browser agent script.
        """
        try:
            # Direct execution of the browser_agent instead of creating an instance
            import subprocess
            import sys
            import os
            
            # Get the absolute path to the browser_agent.py file
            browser_agent_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../browser_agent/browser_agent.py'))
            logger.info(f"Running browser agent script at: {browser_agent_script}")
            
            # Create command to run the script with arguments
            command = [
                sys.executable,  # Current Python interpreter
                browser_agent_script,
                "--test_type", test_type,
                "--district", district
            ]
            
            # Add optional preferred date if provided
            if preferred_date:
                command.extend(["--preferred_date", preferred_date])
                
            # Add additional flags
            command.extend([
                "--headless", "True",
                "--update_dashboard", "False"
            ])
            
            # Log the command we're about to run
            logger.info(f"Executing command: {' '.join(command)}")
            
            # Run the browser_agent.py script as a subprocess
            result = subprocess.run(
                command, 
                capture_output=True,
                text=True,
                check=False
            )
            
            # Log the output
            logger.info(f"Browser agent output: {result.stdout}")
            if result.stderr:
                logger.error(f"Browser agent error: {result.stderr}")
                
            # Check if the execution was successful
            if result.returncode != 0:
                raise Exception(f"Browser agent execution failed with code {result.returncode}: {result.stderr}")
                
            # Process result
            browser_agent_result = {
                "status": "success" if result.returncode == 0 else "error",
                "service": "Driving License Exam",
                "timestamp": datetime.now().isoformat(),
                "output": result.stdout
            }
            
            # Send result to chat UI
            await cl.Message(
                content=f"✅ Driving license exam registration submitted successfully!\n\nService: {browser_agent_result['service']}\nTimestamp: {browser_agent_result['timestamp']}\n\nOutput: {browser_agent_result['output'][:500]}..."
            ).send()
            
            return {
                "status": "success",
                "service": "Driving License Exam",
                "timestamp": datetime.now().isoformat(),
                "message": "Registration submitted successfully",
                "command_output": result.stdout
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
   - Our system will AUTOMATICALLY COMPLETE THE APPLICATION by navigating the Irembo website for you
   - You just provide the required information, and our automated system handles the rest

2. **Driving License Exam Registration**
   - Register for driving license written exams
   - Our system will AUTOMATICALLY COMPLETE THE REGISTRATION by navigating the Irembo website for you
   - You just provide the required information, and our automated system handles the rest

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
# ⚠️ CRITICAL CORRECTION - BIRTH CERTIFICATE REQUIREMENTS

## ONLY THESE EXACT ITEMS ARE REQUIRED - DO NOT ASK FOR ANYTHING ELSE:

1. ✅ **Phone Number**: Your Irembo account phone number (no country code)
2. ✅ **Password**: Your Irembo account password
3. ✅ **For Self or Child**: Is this certificate for yourself (yes/no)?
4. ✅ **National ID**: Your personal ID number
5. ✅ **District**: Processing office district (e.g., Gasabo, Kicukiro)
6. ✅ **Sector**: Processing office sector within that district (e.g., Jali, Gisozi)
7. ✅ **Reason**: Purpose for certificate request (e.g., Education, Employment, Travel)

## ❌ DO NOT ASK FOR THESE - THEY ARE NOT NEEDED:
- ❌ NO full name (not needed - extracted from National ID)
- ❌ NO date of birth (not needed - extracted from National ID)
- ❌ NO place of birth (not needed for this application)
- ❌ NO parent names or details (not needed for this application)
- ❌ NO guardian information (not needed for this application)

The system uses ONLY the 7 required items listed above to complete the entire application process automatically.

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
# ⚠️ CRITICAL CORRECTION - DRIVING LICENSE EXAM REQUIREMENTS

## ONLY THESE EXACT ITEMS ARE REQUIRED - DO NOT ASK FOR ANYTHING ELSE:

1. ✅ **Phone Number**: Your Irembo account phone number (no country code)
2. ✅ **Password**: Your Irembo account password
3. ✅ **Test Type**: "Registration for Driving Test - Provisional, paper-based"
4. ✅ **Test Language**: English or Kinyarwanda
5. ✅ **District**: Where you want to take the exam (e.g., Gasabo, Kicukiro)
6. ✅ **Date Preference**: Optional - a preferred exam date if you have one

## ❌ DO NOT ASK FOR THESE - THEY ARE NOT NEEDED:
- ❌ NO full name (not needed - extracted from account)
- ❌ NO vehicle information (not needed for exam registration)
- ❌ NO driving history (not needed for registration)
- ❌ NO medical information (not needed at this stage)
- ❌ NO home address (not needed for registration)

The system uses ONLY the 6 required items listed above to complete the entire registration process automatically.

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
    # Create tool to inform user that automation is not available
    automation_unavailable_def = {
        "name": "inform_automation_unavailable",
        "description": "Informs the user that automated form submission is currently unavailable",
        "parameters": {
            "type": "object",
            "properties": {
                "service_type": {
                    "type": "string",
                    "description": "The type of service being requested (birth_certificate or driving_license)",
                }
            },
            "required": ["service_type"],
        },
    }
    
    async def automation_unavailable_handler(service_type):
        """
        Explains to the user that automated submission is currently unavailable.
        """
        service_name = "Birth Certificate" if service_type == "birth_certificate" else "Driving License Exam"
        
        unavailable_message = f"""
# ⚠️ AUTOMATED SUBMISSION CURRENTLY UNAVAILABLE ⚠️

I apologize, but the automated {service_name} submission system is currently offline due to a technical issue:
```
Browser agent not available: No module named 'browser_use'
```

### What this means:
- The system can explain the requirements for {service_name}
- The system can guide you through preparing the information needed
- However, the system CANNOT automatically submit the application right now

### Your options:
1. I can still provide you with a complete list of requirements
2. You can try again later when the system is fixed
3. You can complete the application yourself on the Irembo website: https://irembo.gov.rw

Would you like me to explain the requirements for {service_name} despite not being able to automatically submit it right now?
"""
        await cl.Message(content=unavailable_message).send()
        
        return {
            "status": "unavailable",
            "service": service_name,
            "timestamp": datetime.now().isoformat(),
            "reason": "Browser automation module not available"
        }
    
    # Create tool tuple
    automation_unavailable = (automation_unavailable_def, automation_unavailable_handler)
    
    # Add only information tools and unavailable notice if browser agent is not available
    tools = [
        list_available_services,
        birth_certificate_requirements,
        driving_license_requirements,
        automation_unavailable
    ]
    
    # Log that browser agent tools are not available
    logger.warning("Browser agent tools not available - continuing with basic and information tools only")

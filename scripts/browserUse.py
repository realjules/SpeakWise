from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
import asyncio
import os
from dotenv import load_dotenv

class BrowserUseAgent:
    def __init__(self, api_key=None, model="gpt-4o", verbose=True):
        """
        Initialize the BrowserUseAgent with API key and model.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None.
            model (str, optional): LLM model to use. Defaults to "gpt-4o".
        """
        load_dotenv()
        
        # Set API key if provided, otherwise use from environment
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            
        self.model = model
        self.llm = ChatOpenAI(model=self.model)
        
        # Safely retrieve environment variables with error handling
        self.password = os.getenv("PASSWORD")
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.national_id = os.getenv("NATIONAL_ID")

        # Configure browser with minimal configuration
        self.browser = Browser(config=BrowserConfig())
        
        # Validate environment variables
        if not all([self.password, self.phone_number, self.national_id]):
            raise ValueError("Missing required environment variables. Please check your .env file.")
    
    async def apply_for_birth_certificate(self, for_self=True, processing_office=None, reason=None):
        """
        Apply for a birth certificate on Irembo with enhanced robustness.
        """
        who = "Self" if for_self else "Child"
        
        # Comprehensive task instructions with enhanced error handling
        task = f"""
        COMPREHENSIVE IREMBO BIRTH CERTIFICATE APPLICATION PROCESS:
        
        0. WEBSITE LOADING AND PREPARATION:
           - Navigate to https://irembo.gov.rw/home/citizen/all_services?lang=en
           - WAIT EXPLICITLY for page to fully load (minimum 10 seconds)
           - IF page doesn't load, REFRESH the browser
           - Check internet connection stability
        
        1. LANGUAGE CONFIGURATION:
           - make sure that the language of the system is set to english 
           - if it is not english change it to english and if set proceed with next steps
        
      2. LOGIN PROCESS:
           - Find and click "Login" or "Sign In" button
           LOGIN CREDENTIALS:
           - Phone Number: {self.phone_number}
           - Password: {self.password}
           
           VERIFICATION STEPS:
           - If prompted for additional verification
           - Be prepared to:
             * Enter SMS code
             * Answer security questions
             * Provide additional identification
        
        3. BIRTH CERTIFICATE APPLICATION:
           - Navigate: Family Services > Birth Services
           - Select "Birth Certificate"
           - Click "Apply"
           
           APPLICATION DETAILS:
           - Applicant Type: "{who}"
           - National ID: {self.national_id}
           
           PROCESSING DETAILS:
           - Office: {processing_office}
           - Reason: {reason}

        4. choose the phone as way of getting notification (check the box: phone number)and use this phone number: {self.phone_number}
        
        5. FINAL SUBMISSION:
           - Carefully review ALL entered information on the rewiew page
           - Verify each field's accuracy
           - MOST IMPORTANT: check the box for certifying that all information provided is true, accurate and up to date
           - click the SUBMIT button 
        
        PERFORMANCE INSTRUCTIONS:
        - Proceed METICULOUSLY and try to be quick please
        - Read EVERY screen thoroughly
        - Anticipate potential website complexities
        """
        
        # Enhanced Agent Configuration
        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser
        )
        
        results = await agent.run()
        print(results)
        await self.browser.close()
        return results

    async def register_driving_license_exam(self, exam_type="B", test_center=None, preferred_date=None):
        """
        Register for driving license written exam on Irembo.
        
        Args:
            exam_type (str, optional): Type of driving license (e.g., "B" for standard car). Defaults to "B".
            test_center (dict, optional): Preferred test center details. Defaults to None.
            preferred_date (str, optional): Preferred exam date. Defaults to None.
        """
        # Comprehensive task instructions for driving license exam registration
        task = f"""
        COMPREHENSIVE DRIVING LICENSE WRITTEN EXAM REGISTRATION PROCESS:
        
        0. WEBSITE LOADING AND PREPARATION:
           - Navigate to https://irembo.gov.rw/home/citizen/all_services?lang=en
           - WAIT EXPLICITLY for page to fully load (minimum 10 seconds)
           - IF page doesn't load, REFRESH the browser
           - Check internet connection stability
        
        1. LANGUAGE CONFIGURATION:
           - IMMEDIATELY locate and change language to ENGLISH
           - Look for language selector (usually top-right corner)
           - If no immediate language option visible, scroll and search carefully
        
        2. INITIAL NAVIGATION:
           - Close any welcome popups or intervention screens
           - Navigate to: Transport Services > Driving License Services
           - Select "Driving License Written Exam Registration"
        
        3. LOGIN PROCESS:
           - Find and click "Login" or "Sign In" button
           
           LOGIN CREDENTIALS:
           - Phone Number: {self.phone_number}
           - Password: {self.password}
           
           VERIFICATION STEPS:
           - If prompted for additional verification
           - Be prepared to:
             * Enter SMS code
             * Answer security questions
             * Provide additional identification
        
        4. EXAM REGISTRATION DETAILS:
           - DRIVING LICENSE DETAILS:
             * License Type: "{exam_type}"
             * National ID: {self.national_id}
           
           - TEST CENTER SELECTION:
             * Location: {test_center or 'Default Nearest Center'}
           
           - PREFERRED EXAM DATE:
             * Date: {preferred_date or 'Next Available'}
        
        5. DOCUMENT PREPARATION:
           - ENSURE FOLLOWING DOCUMENTS ARE READY:
             * National ID (Digital/Physical Copy)
             * Proof of Residence
             * Passport-sized Photo
             * Previous Driving Permit (if applicable)
        
        6. EXAM REGISTRATION STEPS:
           - Fill out all required personal information
           - Upload necessary documents
           - Verify all entered information
           - Pay registration fee
           - Confirm exam slot and details
        
        7. FINAL SUBMISSION:
           - Carefully review ALL entered information
           - Verify each field's accuracy
           - MOST IMPORTANT: check the box for certifying that all information provided is true
           - PREPARE for potential payment
           
        CRITICAL TROUBLESHOOTING:
        - IF ANY STEP FAILS:
          * Stop immediately
          * Screenshot the error
          * Report exact error message
          * DO NOT auto-proceed without human intervention
        
        PERFORMANCE INSTRUCTIONS:
        - Proceed SLOWLY and METICULOUSLY
        - Read EVERY screen thoroughly
        - Anticipate potential website complexities
        PLEASE DON'T OPEN ANY OTHER TAB JUST STAY ON THE WEBSITE UNTIL THE TASK IS DONE
        """
        
        # Enhanced Agent Configuration
        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser
        )
        
        results = await agent.run()
        print(results)
        await self.browser.close()
        return results

    def run_async(self, coroutine):
        """
        Helper method to run async methods from synchronous code."""
        return asyncio.run(coroutine)

if __name__ == "__main__":
    # Create the agent 
    agent = BrowserUseAgent()
    
    # # Option 1: Register for driving license exam
    # result = agent.run_async(
    #     agent.register_driving_license_exam(
    #         exam_type="B",
    #         test_center={"District": "Gasabo", "Sector": "Remera"},
    #         preferred_date="2024-07-15"
    #     )
    # )
    
    # print("Driving License Exam Registration completed with result:", result)
    
    #Option 2: Apply for birth certificate (kept for reference)
    result = agent.run_async(
        agent.apply_for_birth_certificate(
            for_self=True,
            processing_office={"District": "Gasabo", "Sector": "Jali"},
            reason="Education"
        )
    )
    print("Application completed with result:", result)
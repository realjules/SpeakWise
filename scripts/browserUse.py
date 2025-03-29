from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
import asyncio
import os
from dotenv import load_dotenv
import json

class BrowserUseAgent:
    def __init__(self, api_key=None, model="gpt-4o", verbose=True, headless=True):
        """
        Initialize the BrowserUseAgent with API key and model.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None.
            model (str, optional): LLM model to use. Defaults to "gpt-4o".
            verbose (bool, optional): Enable verbose output. Defaults to True.
        """
        load_dotenv()
        
        # Set API key if provided, otherwise use from environment
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            
        self.model = model
        self.llm = ChatOpenAI(model=self.model)
        self.verbose = verbose
        
        self.password = os.getenv("PASSWORD")
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.national_id = os.getenv("NATIONAL_ID")
        
        # Configure browser with improved settings for form elements
        # self.browser_config = BrowserConfig(
        #     viewport_width=1920,
        #     viewport_height=1080,
        #     timeout=60000,  # Longer timeout for slow loading elements
        #     headless=False  # Set to False to see the browser for debugging
        # )
        
        #self.browser = Browser(config=self.browser_config)
        
        # Validate environment variables
        if not all([self.password, self.phone_number, self.national_id]):
            raise ValueError("Missing required environment variables. Please check your .env file.")
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
        
        # Task instructions with explicit element selection for checkboxes and radio buttons
        task = f"""
        COMPREHENSIVE IREMBO BIRTH CERTIFICATE APPLICATION PROCESS:
        
        0. WEBSITE LOADING AND PREPARATION:
           - Go directly to this site https://irembo.gov.rw/home/citizen/all_services?lang=en
           - WAIT explicitly for the page to fully load (minimum 10 seconds).
           - IF the page doesn't load, REFRESH the browser and re-check the connection.
        
        1. LANGUAGE CONFIGURATION:
           - CRITICAL: Look for a language switcher in the top right corner
           - Identify the current language (could be English or Kinyarwanda)
           - If in Kinyarwanda, click on "EN" or "English" option
           - If button shows "ENG", click it to switch to English
           - Verify language change by checking if main text appears in English
        
        2. LOGIN PROCESS:
           - Click the "Login" or "Sign In" button (if in Kinyarwanda, this will show as "Injira").
           - Use credentials:
             * Phone Number: {self.phone_number} (field might be labeled "Telefoni" or "Nomero ya telefoni")
             * Password: {self.password} (field might be labeled "Ijambo ryibanga")
           - Click the login/submit button (labeled "Injira" in Kinyarwanda or "Login/Sign In" in English)
           - Handle any additional verification steps if prompted.
        
        3. BIRTH CERTIFICATE APPLICATION:
           - Navigate via Family Services > Birth Services.
           - IMPORTANT: If interface is in Kinyarwanda, look for "Serivisi z'umuryango" > "Serivisi z'amavuko"
           - Select "Birth Certificate" (or "Icyemezo cy'amavuko") and click "Apply" (or "Saba").
           - For radio buttons selection (Applicant Type):
             * Look for radio buttons or labels containing "{who}"
             * Click directly on the radio button or its label text
             * Verify selection by checking for visual indicators (filled circle or highlight)
           - Provide details:
             * National ID: {self.national_id}
             * Processing Office: {processing_office}
             * Reason: {reason}
        
        4. NOTIFICATION SETUP:
           - For notification method selection (radio buttons):
             * Look for "Phone"/"SMS" option (or "Telefoni"/"Ubutumwa" in Kinyarwanda)
             * Click directly on the radio button or its label text
           - Use this phone number: {self.phone_number}
           - If asked for email (imeyili) or phone (telefoni), select according to instructions
        
        5. SUBMISSION:
           - Review all information carefully.
           - Scroll down the end of the page before you do anything else. 
           - For checkbox confirmation:
             * Look for checkboxes at the bottom of the page
             * Look specifically for text containing "certify"/"confirm" or "Ndemeza"/"Nemeje" in Kinyarwanda
             * Click directly on the checkbox (not just the text)
             * Verify the checkbox is checked (shows checkmark or filled)
           - Click the SUBMIT button (labeled "Ohereza" or "Saba" in Kinyarwanda).
        
        6. PAYMENT:
          - Find and Click "pay" or "Ishyura"
          - Keep MTN Mobile Money as a payment method when {self.phone_number} start with "078" or "079" otherwise use Airtel Money
          - Fill {self.phone_number} to "Or just enter your MTN MoMo phone number to pay"
          - Click "Pay 500 RWF"
          - The system send a payment request to his phone 
          - Wait for someone to pay and close the pop-up window

        ELEMENT SELECTION TIPS:
           - For checkboxes: Target the actual checkbox element or its container
           - For radio buttons: Click on the circle element itself 
           - If direct clicks fail, try clicking on the label text
           - If element is not visible, scroll to make it visible before clicking
           - Wait for elements to be interactable before clicking
        """
        
        # Update schema
        self.schema["birth_certificate"].append({"application type": "self or child"})
        self.schema["birth_certificate"].append("national id")
        self.schema["birth_certificate"].append({"processing details": [{"office": ["District", "Sector"]}, "reason"]})
        self.schema["birth_certificate"].append({"notification": "choose phone number or email or both"})
        
        # Pass the task to the Agent instance
        agent = Agent(
            task=task,
            llm=self.llm
            #browser=self.browser
        )
        
        results = await agent.run()
        if self.verbose:
            print(results)
        # Close the agent properly
        await agent.close()  
        return results
     
    async def register_driving_license_exam(self, test_type=None, district=None, preferred_date=None):
        """
        Register for driving license written exam on Irembo.
        """
        # Task instructions with improved element selection for checkboxes and radio buttons
        task = f"""
        COMPREHENSIVE DRIVING LICENSE WRITTEN EXAM REGISTRATION PROCESS:
        
        0. WEBSITE LOADING AND PREPARATION:
           - Navigate to https://irembo.gov.rw/home/citizen/all_services?lang=en
           - WAIT explicitly for the page to fully load (minimum 10 seconds).
           - IF the page doesn't load, REFRESH the browser and verify connection.
        
        1. LANGUAGE CONFIGURATION:
           - Locate and set the language to English.
        
        2. LOGIN PROCESS:
           - Click the "Login" or "Sign In" button.
           - Use credentials:
             * Phone Number: {self.phone_number}
             * Password: {self.password}
        
        3. INITIAL NAVIGATION:
           - Navigate to: Police > Registration for Driving Test.
           - Look for text or cards containing "{test_type}"
           - Select this option and click "Apply".
        
        4. REGISTRATION DETAILS:
           - For dropdown and radio button selections:
             * Test Language: Click on the dropdown and select "English"
             * District: Click dropdown and select "{district}"
             * For radio buttons for test center, click directly on the radio button itself or its label
             * For date selection, first click on the date field, then select the appropriate date
           - When selecting available slots:
             * Look for radio buttons or selectable cards showing available slots
             * Click directly on the first available option
             * Confirm the selection is highlighted or marked before proceeding
        
        5. SUMMARY AND SUBMISSION:
           - Review the summary details.
           - For notification selection:
             * Look for radio buttons or checkboxes labeled "Phone" or "SMS"
             * Click directly on the option or its label text
           - Enter phone number: {self.phone_number}
           - For certification checkbox:
             * Look for checkbox at bottom containing text about certifying information
             * Click directly on the checkbox element itself (not just the text)
             * Verify the checkbox is checked (shows checkmark or filled)
           - Click the SUBMIT button.
        
        HANDLING DIFFICULT ELEMENTS:
           - If unable to click a checkbox or radio button directly, try:
             * Clicking the element's label or text
             * Using JavaScript to check the element
             * Clicking slightly above or to the side of the visible checkbox
           - For hidden or dynamically loaded elements:
             * Wait for elements to be fully loaded and visible
             * Scroll to make sure the element is in view
             * Try clicking multiple times with short pauses between attempts
        """
        
        # Pass the task to the Agent instance
        agent = Agent(
            task=task,
            llm=self.llm
            # browser=self.browser
        )
        
        results = await agent.run()
        if self.verbose:
            print(results)
        # Save schema without closing browser (since we don't initialize it)
        with open("schema.json", "w") as json_file:
            json.dump(self.schema, json_file, indent=4)
        return results

    def run_async(self, coroutine):
        """
        Helper method to run async methods from synchronous code.
        """
        return asyncio.run(coroutine)
    

if __name__ == "__main__":
    # Create the agent 
    agent = BrowserUseAgent(verbose=True, headless=False)  # Set headless=False to see the browser
    
    # Option 2: Apply for birth certificate
    result = agent.run_async(
        agent.apply_for_birth_certificate(
            for_self=True,
            processing_office={"District": "Gasabo", "Sector": "Jali"},
            reason="Education"
        )
    )
    print("Birth Certificate Application completed with result:", result)
    
    # Option 1: Register for driving license exam (commented out)
    # result = agent.run_async(
    #     agent.register_driving_license_exam(
    #         test_type="Registration for Driving Test - Provisional, paper-based",
    #         district="Gasabo",
    #         preferred_date="2025-07-15"
    #     )
    # )
    # print("Driving License Exam Registration completed with result:", result)
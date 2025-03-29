"""
Templates for browser automation prompts
"""

BIRTH_CERTIFICATE_TEMPLATE = """
COMPREHENSIVE IREMBO BIRTH CERTIFICATE APPLICATION PROCESS:

0. WEBSITE LOADING AND PREPARATION:
   - Go directly to this site: https://irembo.gov.rw/home/citizen/all_services?lang=en
   - WAIT explicitly for the page to fully load (minimum 10 seconds).
   - IF the page doesn't load, REFRESH the browser and re-check the connection.

1. LANGUAGE CONFIGURATION:
   - CRITICAL: Look for a language switcher in the top right corner (near the login button)
   - Identify the current language (could be English or Kinyarwanda)
   - If in Kinyarwanda, click on "EN" or "English" option
   - If button shows "ENG", click it to switch to English
   - Verify language change by checking if main text appears in English
   - NOTE: If you cannot switch to English, continue with Kinyarwanda interface using the translations provided

2. LOGIN PROCESS:
   - Click the "Login" or "Sign In" button (if in Kinyarwanda, this will show as "Injira").
   - Use credentials:
     * Phone Number: {phone_number} (field might be labeled "Telefoni" or "Nomero ya telefoni")
     * Enter the phone number WITHOUT country code, exactly as shown
     * Password: {password} (field might be labeled "Ijambo ryibanga")
   - Click the login/submit button (labeled "Injira" in Kinyarwanda or "Login/Sign In" in English)
   - If login fails, check the error message and retry
   - Handle any additional verification steps if prompted.

3. BIRTH CERTIFICATE APPLICATION:
   - Navigate via Family Services > Birth Services.
   - IMPORTANT: If interface is in Kinyarwanda, look for "Serivisi z'umuryango" > "Serivisi z'amavuko"
   - Select "Birth Certificate" (or "Icyemezo cy'amavuko") and click "Apply" (or "Saba").
   - If you can't find the exact section, use the search functionality or browse through categories
   - For radio buttons selection (Applicant Type):
     * Look for radio buttons or labels containing "{who}" (or "Wowe Ubwawe" in Kinyarwanda)
     * Click directly on the radio button or its label text
     * Verify selection by checking for visual indicators (filled circle or highlight)
   - Provide details:
     * National ID: {national_id}
     * Processing Office District: {district} (select this from dropdown)
     * Processing Office Sector: {sector} (select this from dropdown after selecting District)
     * Reason: {reason} (might be labeled as "Impamvu usaba serivisi")

4. NOTIFICATION SETUP:
   - Look for text stating "Where would you like us to send notifications about your application?"
   - CRITICAL: There are two notification options below this text:
     * First, click directly on the checkbox next to "Phone Number (Rwanda)"
     * After clicking the checkbox, you MUST enter the phone number: {phone_number}
     * Type the number carefully without any spaces or country code
     * For the email option (if shown), leave it unchecked
   - VERIFY: After entering the phone number, check that it displays correctly
   - Below look for checkbox "By Checking this box, I certify that all information provided is true, accurate and up to date" or "Nemeje ko amakuru yose natanze ahangaha ari ukuri kandi ajyanye n'igihe" and check it
   - After completing this section, immediately look for a green "Submit" button
   - If there is a "Submit" button at this stage, click it to proceed

5. SUBMISSION:
   - FIRST: Scroll all the way to the bottom of the page to see all options
   - You must check BOTH checkboxes that appear at the bottom:
     * First checkbox: "Checking this box, I certify that all information provided is true, accurate and up to date"
     * Click directly on this checkbox and verify it shows a checkmark
     * Second checkbox (if present): May relate to terms and conditions
     * Click on this checkbox too and verify it shows a checkmark
   - IMPORTANT: If any checkbox doesn't check on first click, try clicking it again
   - Find the green "Submit" button at the bottom left (labeled "Submit" in English or "Ohereza"/"Saba" in Kinyarwanda)
   - Click the Submit button to complete the application
   - Wait for confirmation page to load
   - If any error messages appear, read them carefully and fix the issues before trying again

ELEMENT SELECTION AND TROUBLESHOOTING TIPS:
   - For checkboxes: Target the actual checkbox element or its container
   - For radio buttons: Click on the circle element itself 
   - If direct clicks fail, try clicking on the label text
   - If element is not visible, scroll to make it visible before clicking
   - Wait for elements to be interactable before clicking
   - If you can't find an element, try scrolling slowly through the page
   - If language keeps defaulting to Kinyarwanda, continue using Kinyarwanda terms provided
   - If buttons don't respond to clicks, try clicking the text label instead
   - If forms don't advance after submission, check for validation errors
"""

DRIVING_LICENSE_TEMPLATE = """
COMPREHENSIVE DRIVING LICENSE WRITTEN EXAM REGISTRATION PROCESS:

0. WEBSITE LOADING AND PREPARATION:
   - Go directly to this site: https://irembo.gov.rw/home/citizen/all_services?lang=en
   - WAIT explicitly for the page to fully load (minimum 10 seconds).
   - IF the page doesn't load, REFRESH the browser and verify connection.

1. LANGUAGE CONFIGURATION:
   - CRITICAL: Look for a language switcher in the top right corner (near the login button)
   - Identify the current language (could be English or Kinyarwanda)
   - If in Kinyarwanda, click on "EN" or "English" option
   - If button shows "ENG", click it to switch to English
   - Verify language change by checking if main text appears in English
   - NOTE: If you cannot switch to English, continue with Kinyarwanda interface

2. LOGIN PROCESS:
   - Click the "Login" or "Sign In" button (if in Kinyarwanda, this will show as "Injira").
   - Use credentials:
     * Phone Number: {phone_number} (field might be labeled "Telefoni" or "Nomero ya telefoni")
     * Password: {password} (field might be labeled "Ijambo ryibanga")
   - Click the login/submit button (labeled "Injira" in Kinyarwanda or "Login/Sign In" in English)
   - If login fails, check the error message and retry

3. INITIAL NAVIGATION:
   - Navigate to: Police > Registration for Driving Test (or "Polisi" > "Kwiyandikisha ikizamini cy'ubushoferi")
   - Look for text or cards containing "{test_type}" (or related Kinyarwanda terms)
   - Select this option and click "Apply" (or "Saba").

4. REGISTRATION DETAILS:
   - For dropdown and radio button selections:
     * Test Language: Click on the dropdown and select "English" (or "Icyongereza")
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
     * Look for radio buttons or checkboxes labeled "Phone" or "SMS" (or "Telefoni"/"Ubutumwa")
     * Click directly on the option or its label text
   - Enter phone number: {phone_number}
   - For certification checkbox:
     * Look for checkbox at bottom containing text about certifying information
     * Click directly on the checkbox element itself (not just the text)
     * Verify the checkbox is checked (shows checkmark or filled)
   - Click the SUBMIT button (labeled "Ohereza" or "Saba" in Kinyarwanda).

ELEMENT SELECTION AND TROUBLESHOOTING TIPS:
   - If unable to click a checkbox or radio button directly, try:
     * Clicking the element's label or text
     * Using JavaScript to check the element
     * Clicking slightly above or to the side of the visible checkbox
   - For hidden or dynamically loaded elements:
     * Wait for elements to be fully loaded and visible
     * Scroll to make sure the element is in view
     * Try clicking multiple times with short pauses between attempts
   - If language keeps defaulting to Kinyarwanda, continue using Kinyarwanda terms provided
   - If buttons don't respond to clicks, try clicking the text label instead
   - If forms don't advance after submission, check for validation errors
"""
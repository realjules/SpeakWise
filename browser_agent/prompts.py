"""
Templates for browser automation prompts
"""

BIRTH_CERTIFICATE_TEMPLATE = """
IREMBO BIRTH CERTIFICATE APPLICATION:

1. Go to: https://irembo.gov.rw/home/citizen/all_services?lang=en
   - If needed, switch to English using the language button in top right

2. Login:
   - Phone Number: {phone_number}
   - Password: {password}

3. Navigate to Birth Certificate:
   - Find Family Services > Birth Services
   - Select Birth Certificate and Apply
   - Select applicant type: {who}
   - Enter National ID: {national_id}
   - Select District: {district}
   - Select Sector: {sector}
   - Enter Reason: {reason}

4. Notification:
   - Select Phone Number checkbox
   - Enter phone: {phone_number}

5. Submit:
   - Check certification checkboxes at bottom
   - Click Submit button
   - Confirm successful submission

Tips:
- If language is in Kinyarwanda, look for equivalent terms
- If elements don't respond, try clicking labels or containers
- Ensure checkboxes are visibly checked before proceeding
"""

DRIVING_LICENSE_TEMPLATE = """
DRIVING LICENSE EXAM REGISTRATION:

1. Go to: https://irembo.gov.rw/home/citizen/all_services?lang=en
   - Switch to English if needed using top-right language button

2. Login:
   - Phone Number: {phone_number}
   - Password: {password}

3. Navigate to Driving Test:
   - Find Police > Registration for Driving Test
   - Select test type: {test_type}
   - Click Apply

4. Complete Registration:
   - Select Test Language: English
   - Select District: {district}
   - Select first available test center
   - Choose first available date/slot

5. Notification and Submit:
   - Select Phone notification option
   - Enter phone: {phone_number}
   - Check certification checkbox at bottom
   - Click Submit

6. Payment:
   - Use phone number {phone_number} for payment
   - Complete payment by clicking Pay 500

Tips:
- If elements don't respond, try clicking labels
- Ensure checkboxes show checkmarks before proceeding
- If using Kinyarwanda interface, use equivalent terms
"""
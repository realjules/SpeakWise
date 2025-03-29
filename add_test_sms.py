#!/usr/bin/env python3
"""
Script to directly add a test SMS record to the analytics.json file.
This bypasses any file locking or error handling to ensure the record is added.
"""

import os
import json
from datetime import datetime

# Path to analytics.json
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'frontend', 'data'))
analytics_file = os.path.join(data_dir, 'analytics.json')

print(f"Adding test SMS to: {analytics_file}")

# Load the current analytics data
with open(analytics_file, 'r') as f:
    analytics_data = json.load(f)

# Create a test SMS record
test_sms = {
    "id": "TEST-SMS-"+datetime.now().strftime("%H%M%S"),
    "recipient": "+250787641302",
    "timestamp": datetime.now().isoformat(),
    "type": "test_message",
    "status": "delivered",
    "service": "SpeakWise Test",
    "reference": "REF-TEST-" + datetime.now().strftime("%H%M%S")
}

print(f"Created test SMS record: {test_sms}")

# Add the record to the SMS records list
sms_records = analytics_data.get("sms_records", [])
sms_records.append(test_sms)
analytics_data["sms_records"] = sms_records

# Save the updated data
with open(analytics_file, 'w') as f:
    json.dump(analytics_data, f, indent=2)

print(f"Successfully added test SMS record with ID: {test_sms['id']}")
print("Please check the SMS Tracking page to see if this record appears.")
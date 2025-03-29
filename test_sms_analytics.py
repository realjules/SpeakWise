#!/usr/bin/env python3
"""
Test script to simulate sending an SMS and update analytics.json.
This script doesn't actually send an SMS but simulates the process
and updates the analytics database to show how it would work.
"""

import os
import json
import sys
import platform
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Get recipient from command line
    recipient = sys.argv[1] if len(sys.argv) > 1 else "+250787641302"
    
    # Define path to JSON file
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'frontend', 'data'))
    analytics_file = os.path.join(data_dir, 'analytics.json')
    
    logger.info(f"Analytics file path: {analytics_file}")
    logger.info(f"Simulating SMS to: {recipient}")
    
    # Load current data with platform-specific locking
    try:
        if platform.system() == 'Windows':
            # Windows implementation - no file locking
            with open(analytics_file, 'r') as f:
                analytics_data = json.load(f)
        else:
            # Unix implementation with fcntl
            import fcntl
            with open(analytics_file, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    analytics_data = json.load(f)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error loading analytics data: {str(e)}")
        return False
    
    # Generate a test SMS record
    sms_id = f"SMS-TEST-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().isoformat() + "Z"
    message = f"Test message sent at {datetime.now().strftime('%H:%M:%S')} on {datetime.now().strftime('%Y-%m-%d')}"
    
    logger.info(f"Message: {message}")
    logger.info(f"Generated SMS ID: {sms_id}")
    
    new_record = {
        "id": sms_id,
        "recipient": recipient,
        "timestamp": timestamp,
        "type": "test_message",
        "status": "delivered",
        "service": "Test Service",
        "reference": f"REF-{uuid.uuid4().hex[:6]}"
    }
    
    # Add record to SMS records
    sms_records = analytics_data.get("sms_records", [])
    sms_records.append(new_record)
    analytics_data["sms_records"] = sms_records
    
    # Update SMS stats
    total_sent = len(sms_records)
    delivered = sum(1 for record in sms_records if record.get("status") == "delivered")
    failed = total_sent - delivered
    delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0
    
    analytics_data["sms_stats"] = {
        "total_sent": total_sent,
        "delivery_success": delivered,
        "delivery_failed": failed,
        "delivery_rate": round(delivery_rate, 1)
    }
    
    # Update daily SMS data
    today = datetime.now().strftime("%Y-%m-%d")
    daily_sms = analytics_data.get("daily_sms", [])
    
    # Find today's entry or create a new one
    today_data = next((day for day in daily_sms if day["date"] == today), None)
    
    if today_data:
        today_data["sent"] += 1
        today_data["delivered"] += 1
    else:
        daily_sms.append({
            "date": today,
            "sent": 1,
            "delivered": 1,
            "failed": 0
        })
    
    analytics_data["daily_sms"] = daily_sms
    
    # Save updated data with platform-specific locking
    try:
        if platform.system() == 'Windows':
            # Windows implementation - no file locking
            with open(analytics_file, 'w') as f:
                json.dump(analytics_data, f, indent=2)
            
            logger.info(f"Successfully added SMS record with ID: {sms_id}")
            
            # Print the before and after statistics
            logger.info(f"Updated SMS statistics:")
            logger.info(f"- Total SMS: {total_sent}")
            logger.info(f"- Delivered: {delivered}")
            logger.info(f"- Failed: {failed}")
            logger.info(f"- Delivery Rate: {round(delivery_rate, 1)}%")
            
            # Print message about checking the dashboard
            logger.info("")
            logger.info("===========================================================")
            logger.info("SMS record added to analytics database!")
            logger.info("This simulates what happens when a real SMS is sent.")
            logger.info("The Home page will now show updated statistics on refresh.")
            logger.info("===========================================================")
            
            return True
        else:
            # Unix implementation with fcntl
            import fcntl
            with open(analytics_file, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(analytics_data, f, indent=2)
                    
                    logger.info(f"Successfully added SMS record with ID: {sms_id}")
                    
                    # Print the before and after statistics
                    logger.info(f"Updated SMS statistics:")
                    logger.info(f"- Total SMS: {total_sent}")
                    logger.info(f"- Delivered: {delivered}")
                    logger.info(f"- Failed: {failed}")
                    logger.info(f"- Delivery Rate: {round(delivery_rate, 1)}%")
                    
                    # Print message about checking the dashboard
                    logger.info("")
                    logger.info("===========================================================")
                    logger.info("SMS record added to analytics database!")
                    logger.info("This simulates what happens when a real SMS is sent.")
                    logger.info("The Home page will now show updated statistics on refresh.")
                    logger.info("===========================================================")
                    
                    return True
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error saving analytics data: {str(e)}")
        return False

if __name__ == "__main__":
    main()
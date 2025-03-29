#!/usr/bin/env python3
"""
Update the analytics database with a real SMS that was sent.
Cross-platform version that works on both Windows and Unix.
"""

import os
import json
import platform
from datetime import datetime
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Get parameters from command line or use defaults
    recipient = sys.argv[1] if len(sys.argv) > 1 else "+250787641302"
    sms_id = sys.argv[2] if len(sys.argv) > 2 else "out_sms_01JQFPYQBFXAMGT9JB98VW00YQ"
    
    # Define path to JSON file
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'frontend', 'data'))
    analytics_file = os.path.join(data_dir, 'analytics.json')
    
    logger.info(f"Analytics file path: {analytics_file}")
    logger.info(f"Updating analytics for SMS to: {recipient} with ID: {sms_id}")
    
    # Load current data with platform-specific handling
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
    
    # Create a new SMS record
    timestamp = datetime.now().isoformat() + "Z"
    
    new_record = {
        "id": sms_id,
        "recipient": recipient,
        "timestamp": timestamp,
        "type": "real_message",
        "status": "delivered",
        "service": "SpeakWise Demo",
        "reference": f"REF-REAL-{datetime.now().strftime('%H%M%S')}"
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
    
    # Save updated data with platform-specific handling
    try:
        if platform.system() == 'Windows':
            # Windows implementation - no file locking
            with open(analytics_file, 'w') as f:
                json.dump(analytics_data, f, indent=2)
            
            logger.info(f"Successfully added SMS record to analytics")
            
            # Print the before and after statistics
            logger.info(f"Updated SMS statistics:")
            logger.info(f"- Total SMS: {total_sent}")
            logger.info(f"- Delivered: {delivered}")
            logger.info(f"- Failed: {failed}")
            logger.info(f"- Delivery Rate: {round(delivery_rate, 1)}%")
            
            # Print message about checking the SMS Tracking page
            logger.info("")
            logger.info("==============================================================")
            logger.info("REAL SMS record added to analytics database!")
            logger.info("You should now be able to see this message in the SMS Tracking")
            logger.info("page with ID: " + sms_id)
            logger.info("==============================================================")
            
            return True
        else:
            # Unix implementation with fcntl
            import fcntl
            with open(analytics_file, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(analytics_data, f, indent=2)
                    logger.info(f"Successfully added SMS record to analytics")
                    
                    # Print the before and after statistics
                    logger.info(f"Updated SMS statistics:")
                    logger.info(f"- Total SMS: {total_sent}")
                    logger.info(f"- Delivered: {delivered}")
                    logger.info(f"- Failed: {failed}")
                    logger.info(f"- Delivery Rate: {round(delivery_rate, 1)}%")
                    
                    # Print message about checking the SMS Tracking page
                    logger.info("")
                    logger.info("==============================================================")
                    logger.info("REAL SMS record added to analytics database!")
                    logger.info("You should now be able to see this message in the SMS Tracking")
                    logger.info("page with ID: " + sms_id)
                    logger.info("==============================================================")
                    
                    return True
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error saving analytics data: {str(e)}")
        return False

if __name__ == "__main__":
    main()
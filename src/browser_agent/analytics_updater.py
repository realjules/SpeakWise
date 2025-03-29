"""
Analytics updater for browser agent integration.

Handles updating the frontend JSON files with browser agent activity
and SMS notification data.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Define paths to JSON files
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'data'))
ANALYTICS_FILE = os.path.join(DATA_DIR, 'analytics.json')
CALLS_FILE = os.path.join(DATA_DIR, 'calls.json')

class AnalyticsUpdater:
    """
    Updates frontend analytics files with browser agent data.
    Handles SMS records and transaction data for the dashboard.
    """
    
    def __init__(self):
        """Initialize the analytics updater."""
        self.analytics_data = self._load_analytics_data()
        self.calls_data = self._load_calls_data()
        
    def _load_analytics_data(self) -> Dict[str, Any]:
        """Load analytics data from JSON file."""
        try:
            with open(ANALYTICS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading analytics data: {e}")
            return {
                "call_stats": {"total_calls": 0, "active_calls": 0, "completed_calls": 0, "failed_calls": 0},
                "sms_stats": {"total_sent": 0, "delivery_success": 0, "delivery_failed": 0, "delivery_rate": 0},
                "daily_calls": [],
                "daily_sms": [],
                "service_distribution": [],
                "hourly_distribution": [],
                "sms_records": []
            }
            
    def _load_calls_data(self) -> Dict[str, Any]:
        """Load calls data from JSON file."""
        try:
            with open(CALLS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading calls data: {e}")
            return {"active_calls": [], "recent_calls": []}
            
    def _save_analytics_data(self):
        """Save analytics data to JSON file."""
        try:
            os.makedirs(os.path.dirname(ANALYTICS_FILE), exist_ok=True)
            with open(ANALYTICS_FILE, 'w') as f:
                json.dump(self.analytics_data, f, indent=2)
            logger.info(f"Analytics data saved to {ANALYTICS_FILE}")
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
            
    def _save_calls_data(self):
        """Save calls data to JSON file."""
        try:
            os.makedirs(os.path.dirname(CALLS_FILE), exist_ok=True)
            with open(CALLS_FILE, 'w') as f:
                json.dump(self.calls_data, f, indent=2)
            logger.info(f"Calls data saved to {CALLS_FILE}")
        except Exception as e:
            logger.error(f"Error saving calls data: {e}")
            
    def add_sms_record(self, 
                      sms_id: str, 
                      recipient: str, 
                      service: str, 
                      status: str = "delivered",
                      sms_type: str = "task_complete",
                      reference: Optional[str] = None):
        """
        Add a new SMS record to analytics.
        
        Args:
            sms_id: The SMS ID
            recipient: The recipient phone number
            service: The service name (e.g., "Birth Certificate")
            status: Delivery status (delivered or failed)
            sms_type: Type of SMS (task_complete or document_ready)
            reference: Reference number or transaction ID
        """
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Create SMS record
        sms_record = {
            "id": sms_id,
            "recipient": recipient,
            "timestamp": timestamp,
            "type": sms_type,
            "status": status,
            "service": service
        }
        
        if reference:
            sms_record["reference"] = reference
            
        # Add to SMS records
        self.analytics_data["sms_records"].insert(0, sms_record)
        
        # Update SMS stats
        self.analytics_data["sms_stats"]["total_sent"] += 1
        if status == "delivered":
            self.analytics_data["sms_stats"]["delivery_success"] += 1
        else:
            self.analytics_data["sms_stats"]["delivery_failed"] += 1
            
        # Calculate delivery rate
        total = self.analytics_data["sms_stats"]["total_sent"]
        success = self.analytics_data["sms_stats"]["delivery_success"]
        self.analytics_data["sms_stats"]["delivery_rate"] = round((success / total) * 100, 1) if total > 0 else 0
        
        # Update daily SMS stats
        today = datetime.now().strftime("%Y-%m-%d")
        daily_sms = next((day for day in self.analytics_data["daily_sms"] if day["date"] == today), None)
        
        if daily_sms:
            daily_sms["sent"] += 1
            if status == "delivered":
                daily_sms["delivered"] += 1
            else:
                daily_sms["failed"] += 1
        else:
            # Create new daily entry
            self.analytics_data["daily_sms"].append({
                "date": today,
                "sent": 1,
                "delivered": 1 if status == "delivered" else 0,
                "failed": 0 if status == "delivered" else 1
            })
            
        # Save updated analytics data
        self._save_analytics_data()
        
        return sms_record
        
    def update_service_stats(self, service_name: str, success: bool = True):
        """
        Update service statistics.
        
        Args:
            service_name: The service name
            success: Whether the service request was successful
        """
        # Update service distribution
        service_entry = next((s for s in self.analytics_data["service_distribution"] 
                            if s["service"] == service_name), None)
        
        if service_entry:
            service_entry["count"] += 1
        else:
            # Create new service entry
            self.analytics_data["service_distribution"].append({
                "service": service_name,
                "count": 1,
                "percentage": 0  # Will be calculated below
            })
            
        # Recalculate percentages
        total_count = sum(s["count"] for s in self.analytics_data["service_distribution"])
        for service in self.analytics_data["service_distribution"]:
            service["percentage"] = round((service["count"] / total_count) * 100, 1) if total_count > 0 else 0
            
        # Update call stats
        self.analytics_data["call_stats"]["total_calls"] += 1
        if success:
            self.analytics_data["call_stats"]["completed_calls"] += 1
        else:
            self.analytics_data["call_stats"]["failed_calls"] += 1
            
        # Calculate success rate
        total = self.analytics_data["call_stats"]["completed_calls"] + self.analytics_data["call_stats"]["failed_calls"]
        success_count = self.analytics_data["call_stats"]["completed_calls"]
        self.analytics_data["call_stats"]["success_rate"] = round((success_count / total) * 100, 1) if total > 0 else 0
        
        # Update daily call stats
        today = datetime.now().strftime("%Y-%m-%d")
        daily_call = next((day for day in self.analytics_data["daily_calls"] if day["date"] == today), None)
        
        if daily_call:
            daily_call["count"] += 1
            if success:
                daily_call["completed"] += 1
            else:
                daily_call["failed"] += 1
        else:
            # Create new daily entry
            self.analytics_data["daily_calls"].append({
                "date": today,
                "count": 1,
                "completed": 1 if success else 0,
                "failed": 0 if success else 1
            })
            
        # Update hourly distribution
        hour = datetime.now().hour
        hour_entry = next((h for h in self.analytics_data["hourly_distribution"] 
                          if h["hour"] == hour), None)
        
        if hour_entry:
            hour_entry["count"] += 1
        else:
            # Create new hour entry
            self.analytics_data["hourly_distribution"].append({
                "hour": hour,
                "count": 1
            })
            
        # Save updated analytics data
        self._save_analytics_data()
        
    def add_completed_call(self, 
                         phone_number: str, 
                         service_name: str, 
                         success: bool = True, 
                         duration_seconds: int = 180,
                         transcript: Optional[list] = None):
        """
        Add a completed call to the calls data.
        
        Args:
            phone_number: The phone number
            service_name: The service name
            success: Whether the call was successful
            duration_seconds: Call duration in seconds
            transcript: Call transcript (list of messages)
        """
        # Create a unique call ID
        import random
        import string
        call_id = f"CALL-{''.join(random.choices(string.hexdigits.lower(), k=4))}"
        
        # Get timestamps
        start_time = datetime.now() - datetime.timedelta(seconds=duration_seconds)
        end_time = datetime.now()
        
        # Create default transcript if none provided
        if not transcript:
            transcript = [
                {
                    "role": "system",
                    "content": f"Hello, welcome to SpeakWise. How can I help you with {service_name} today?",
                    "timestamp": start_time.isoformat()
                },
                {
                    "role": "user",
                    "content": f"I need help with {service_name}",
                    "timestamp": (start_time + datetime.timedelta(seconds=10)).isoformat()
                },
                {
                    "role": "system",
                    "content": f"Processing your {service_name} request...",
                    "timestamp": (start_time + datetime.timedelta(seconds=20)).isoformat()
                }
            ]
            
        # Create call data
        call_data = {
            "id": call_id,
            "phone": phone_number,
            "service": service_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration_seconds,
            "status": "Completed" if success else "Failed",
            "current_step": 5,  # Final step
            "total_steps": 5,
            "agent_id": f"AGT-{''.join(random.choices(string.hexdigits.lower(), k=3))}",
            "ai_actions": [],
            "success_rate": 100.0 if success else 0.0,
            "transcript": transcript
        }
        
        # Add to recent calls
        self.calls_data["recent_calls"].insert(0, call_data)
        
        # Trim recent calls if too many
        if len(self.calls_data["recent_calls"]) > 25:
            self.calls_data["recent_calls"] = self.calls_data["recent_calls"][:25]
            
        # Save updated calls data
        self._save_calls_data()
        
        # Update service stats
        self.update_service_stats(service_name, success)
        
        return call_data
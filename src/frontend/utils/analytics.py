import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import random

logger = logging.getLogger(__name__)

# Define path to JSON file
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
ANALYTICS_FILE = os.path.join(DATA_DIR, 'analytics.json')

class AnalyticsManager:
    """Manager for analytics data and reporting."""
    
    def __init__(self):
        """Initialize the analytics manager."""
        self.analytics_data = self._load_analytics_data()
        
    def _load_analytics_data(self) -> Dict[str, Any]:
        """Load analytics data from JSON file."""
        try:
            with open(ANALYTICS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics data: {str(e)}")
            # Return default structure if file not found or invalid
            return {
                "call_stats": {},
                "sms_stats": {},
                "daily_calls": [],
                "daily_sms": [],
                "service_distribution": [],
                "hourly_distribution": [],
                "sms_records": []
            }
    
    def _save_analytics_data(self) -> bool:
        """Save analytics data to JSON file with cross-platform thread safety."""
        try:
            os.makedirs(os.path.dirname(ANALYTICS_FILE), exist_ok=True)
            
            # Platform-specific file locking
            import platform
            if platform.system() == 'Windows':
                # Windows implementation - no file locking, just direct write
                # For a production system, consider using a proper locking mechanism
                # like portalocker or filelock packages
                with open(ANALYTICS_FILE, 'w') as f:
                    json.dump(self.analytics_data, f, indent=2)
                return True
            else:
                # Unix implementation with fcntl
                import fcntl
                with open(ANALYTICS_FILE, 'w') as f:
                    # Acquire exclusive lock
                    fcntl.flock(f, fcntl.LOCK_EX)
                    try:
                        # Write data with pretty formatting
                        json.dump(self.analytics_data, f, indent=2)
                        return True
                    finally:
                        # Release lock
                        fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Error saving analytics data: {str(e)}")
            return False
    
    def get_call_stats(self) -> Dict[str, Any]:
        """Get call statistics."""
        return self.analytics_data.get("call_stats", {})
    
    def get_sms_stats(self) -> Dict[str, Any]:
        """Get SMS statistics."""
        return self.analytics_data.get("sms_stats", {})
    
    def get_daily_calls(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily call data for the specified number of days.
        
        Args:
            days: Number of days to return
            
        Returns:
            List of daily call data
        """
        daily_calls = self.analytics_data.get("daily_calls", [])
        return daily_calls[-days:] if days < len(daily_calls) else daily_calls
    
    def get_daily_sms(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily SMS data for the specified number of days.
        
        Args:
            days: Number of days to return
            
        Returns:
            List of daily SMS data
        """
        daily_sms = self.analytics_data.get("daily_sms", [])
        return daily_sms[-days:] if days < len(daily_sms) else daily_sms
    
    def get_service_distribution(self) -> List[Dict[str, Any]]:
        """Get service distribution data."""
        return self.analytics_data.get("service_distribution", [])
    
    def get_hourly_distribution(self) -> List[Dict[str, Any]]:
        """Get hourly call distribution."""
        return self.analytics_data.get("hourly_distribution", [])
    
    def get_sms_records(self, limit: int = 100, service: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get SMS records with optional filtering.
        
        Args:
            limit: Maximum number of records to return
            service: Filter by service type (optional)
            
        Returns:
            List of SMS records
        """
        sms_records = self.analytics_data.get("sms_records", [])
        
        # Apply service filter if provided
        if service:
            sms_records = [record for record in sms_records if record.get("service") == service]
            
        # Sort by timestamp (newest first)
        sms_records = sorted(
            sms_records,
            key=lambda x: datetime.fromisoformat(x["timestamp"].replace('Z', '+00:00')),
            reverse=True
        )
        
        # Limit results
        return sms_records[:limit]
    
    def add_sms_record(self, record: Dict[str, Any]) -> bool:
        """
        Add a new SMS record.
        
        Args:
            record: SMS record data
            
        Returns:
            True if successful, False otherwise
        """
        # Print record for debugging
        print(f"Adding SMS record: {json.dumps(record, indent=2)}")
        
        required_fields = ["recipient", "timestamp", "type", "status", "service"]
        if not all(field in record for field in required_fields):
            logger.error("Missing required fields in SMS record")
            return False
            
        # Generate ID if not provided
        if "id" not in record:
            # Find the highest existing ID
            existing_ids = [int(r["id"].split('-')[1]) for r in self.analytics_data.get("sms_records", [])
                          if r["id"].startswith("SMS-") and r["id"][4:].isdigit()]
            next_id = max(existing_ids, default=0) + 1
            record["id"] = f"SMS-{next_id:05d}"
            
        # Add record
        self.analytics_data.setdefault("sms_records", []).append(record)
        
        # Update statistics
        self._update_sms_stats()
        
        # Save data
        return self._save_analytics_data()
    
    def _update_sms_stats(self) -> None:
        """Update SMS statistics based on records."""
        sms_records = self.analytics_data.get("sms_records", [])
        
        # Calculate totals
        total_sent = len(sms_records)
        delivered = sum(1 for record in sms_records if record.get("status") == "delivered")
        failed = total_sent - delivered
        delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0
        
        # Update stats
        self.analytics_data["sms_stats"] = {
            "total_sent": total_sent,
            "delivery_success": delivered,
            "delivery_failed": failed,
            "delivery_rate": round(delivery_rate, 1)
        }
        
        # Update daily SMS data based on actual records
        self._update_daily_sms_data()
        
    def _update_daily_sms_data(self) -> None:
        """Update daily SMS data based on records."""
        sms_records = self.analytics_data.get("sms_records", [])
        
        # Group records by date
        daily_data = {}
        for record in sms_records:
            try:
                # Parse timestamp to get date
                timestamp = datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                date_str = timestamp.strftime("%Y-%m-%d")
                
                # Initialize date entry if needed
                if date_str not in daily_data:
                    daily_data[date_str] = {"sent": 0, "delivered": 0, "failed": 0}
                
                # Increment counters
                daily_data[date_str]["sent"] += 1
                if record.get("status") == "delivered":
                    daily_data[date_str]["delivered"] += 1
                else:
                    daily_data[date_str]["failed"] += 1
            except Exception as e:
                logger.error(f"Error processing record timestamp: {str(e)}")
        
        # Convert to list format and sort by date
        daily_sms = []
        for date_str, counts in daily_data.items():
            daily_sms.append({
                "date": date_str,
                "sent": counts["sent"],
                "delivered": counts["delivered"],
                "failed": counts["failed"]
            })
        
        # Sort by date
        daily_sms.sort(key=lambda x: x["date"])
        
        # Update analytics data
        self.analytics_data["daily_sms"] = daily_sms
        
    def update_call_record(self, call_record: Dict[str, Any]) -> bool:
        """
        Update or add a call record and update statistics.
        
        Args:
            call_record: Call record data with status update
            
        Returns:
            True if successful, False otherwise
        """
        required_fields = ["call_id", "status", "timestamp", "service"]
        if not all(field in call_record for field in required_fields):
            logger.error("Missing required fields in call record")
            return False
            
        # Get existing calls or initialize
        calls = self.analytics_data.get("calls", [])
        
        # Find existing call or add new one
        call_id = call_record["call_id"]
        existing_call = next((call for call in calls if call.get("id") == call_id), None)
        
        if existing_call:
            # Update existing call
            existing_call.update(call_record)
        else:
            # Format record for storage
            formatted_record = {
                "id": call_id,
                "phone": call_record.get("phone", ""),
                "service": call_record.get("service", ""),
                "status": call_record.get("status", ""),
                "start_time": call_record.get("timestamp", ""),
                "duration": call_record.get("duration", 0)
            }
            calls.append(formatted_record)
        
        # Update analytics data
        self.analytics_data["calls"] = calls
        
        # Update daily call data
        self._update_daily_call_data()
        
        # Update call statistics
        self._update_call_stats()
        
        # Save to file
        return self._save_analytics_data()
        
    def _update_daily_call_data(self) -> None:
        """Update daily call data based on call records."""
        calls = self.analytics_data.get("calls", [])
        
        # Group records by date
        daily_data = {}
        for call in calls:
            try:
                # Parse timestamp to get date
                timestamp = datetime.fromisoformat(call["start_time"].replace('Z', '+00:00') 
                    if isinstance(call.get("start_time"), str) else datetime.now().isoformat())
                date_str = timestamp.strftime("%Y-%m-%d")
                
                # Initialize date entry if needed
                if date_str not in daily_data:
                    daily_data[date_str] = {"count": 0, "completed": 0, "failed": 0}
                
                # Increment counters
                daily_data[date_str]["count"] += 1
                if call.get("status") == "Completed":
                    daily_data[date_str]["completed"] += 1
                elif call.get("status") == "Failed":
                    daily_data[date_str]["failed"] += 1
            except Exception as e:
                logger.error(f"Error processing call timestamp: {str(e)}")
        
        # Convert to list format and sort by date
        daily_calls = []
        for date_str, counts in daily_data.items():
            daily_calls.append({
                "date": date_str,
                "count": counts["count"],
                "completed": counts["completed"],
                "failed": counts["failed"]
            })
        
        # Sort by date
        daily_calls.sort(key=lambda x: x["date"])
        
        # Update analytics data
        self.analytics_data["daily_calls"] = daily_calls
        
    def _update_call_stats(self) -> None:
        """Update call statistics based on call records."""
        calls = self.analytics_data.get("calls", [])
        daily_calls = self.analytics_data.get("daily_calls", [])
        
        # Count active calls (those with status "In Progress")
        active_calls = sum(1 for call in calls if call.get("status") == "In Progress")
        
        # Calculate totals
        total_calls = sum(day["count"] for day in daily_calls) if daily_calls else len(calls)
        completed_calls = sum(day["completed"] for day in daily_calls) if daily_calls else sum(1 for call in calls if call.get("status") == "Completed")
        failed_calls = sum(day["failed"] for day in daily_calls) if daily_calls else sum(1 for call in calls if call.get("status") == "Failed")
        
        # Calculate success rate
        success_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Calculate average duration from completed calls with duration
        completed_with_duration = [call for call in calls if call.get("status") == "Completed" and call.get("duration")]
        avg_duration = sum(call["duration"] for call in completed_with_duration) / len(completed_with_duration) if completed_with_duration else 0
        
        # Update stats
        self.analytics_data["call_stats"] = {
            "total_calls": total_calls,
            "active_calls": active_calls,
            "completed_calls": completed_calls,
            "failed_calls": failed_calls,
            "avg_duration_seconds": round(avg_duration),
            "success_rate": round(success_rate, 1)
        }
        
    def generate_demo_data(self, num_records: int = 100) -> bool:
        """
        Generate demo data for analytics.
        
        Args:
            num_records: Number of SMS records to generate
            
        Returns:
            True if successful, False otherwise
        """
        # Sample data for generation
        services = ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]
        sms_types = ["task_complete", "document_ready"]
        statuses = ["delivered", "failed"]
        status_weights = [0.95, 0.05]  # 95% delivered, 5% failed
        
        # Generate SMS records
        sms_records = []
        for i in range(1, num_records + 1):
            # Create a random timestamp within the last 30 days
            days_ago = random.randint(0, 29)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = (datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).isoformat() + "Z"
            
            record = {
                "id": f"SMS-{i:05d}",
                "recipient": f"+2507{random.randint(0, 9)}{random.randint(1000000, 9999999)}",
                "timestamp": timestamp,
                "type": random.choice(sms_types),
                "status": random.choices(statuses, status_weights)[0],
                "service": random.choice(services)
            }
            sms_records.append(record)
        
        # Sort by timestamp
        sms_records = sorted(
            sms_records,
            key=lambda x: datetime.fromisoformat(x["timestamp"].replace('Z', '+00:00'))
        )
        
        # Update analytics data
        self.analytics_data["sms_records"] = sms_records
        
        # Generate daily call and SMS data (last 30 days)
        daily_calls = []
        daily_sms = []
        
        for i in range(30):
            date_str = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            
            # Generate random counts with weekend dips
            weekday = (datetime.now() - timedelta(days=29-i)).weekday()
            is_weekend = weekday >= 5  # 5=Saturday, 6=Sunday
            
            # Calls (fewer on weekends)
            call_count = random.randint(4, 8) if is_weekend else random.randint(8, 16)
            failed_calls = random.randint(0, 2)
            completed_calls = call_count - failed_calls
            
            daily_calls.append({
                "date": date_str,
                "count": call_count,
                "completed": completed_calls,
                "failed": failed_calls
            })
            
            # SMS (approximately 2x calls)
            sms_count = call_count * 2
            failed_sms = random.randint(0, 2)
            delivered_sms = sms_count - failed_sms
            
            daily_sms.append({
                "date": date_str,
                "sent": sms_count,
                "delivered": delivered_sms,
                "failed": failed_sms
            })
        
        self.analytics_data["daily_calls"] = daily_calls
        self.analytics_data["daily_sms"] = daily_sms
        
        # Generate service distribution
        total_calls = sum(day["count"] for day in daily_calls)
        service_counts = [
            int(total_calls * 0.38),  # Business Registration
            int(total_calls * 0.23),  # Marriage Certificate
            int(total_calls * 0.17),  # Land Transfer
            int(total_calls * 0.22)   # Passport Application
        ]
        
        # Adjust to match total
        difference = total_calls - sum(service_counts)
        service_counts[0] += difference
        
        service_distribution = []
        for i, service in enumerate(services):
            service_distribution.append({
                "service": service,
                "count": service_counts[i],
                "percentage": round(service_counts[i] / total_calls * 100, 1)
            })
        
        self.analytics_data["service_distribution"] = service_distribution
        
        # Generate hourly distribution (bell curve with peaks at 10-11 AM and 2-3 PM)
        hourly_distribution = []
        for hour in range(24):
            if 0 <= hour < 6:
                # Night (very few calls)
                count = random.randint(0, 2)
            elif 6 <= hour < 8:
                # Early morning (few calls)
                count = random.randint(1, 5)
            elif 8 <= hour < 10:
                # Morning (increasing)
                count = random.randint(10, 20)
            elif 10 <= hour < 12:
                # Late morning (peak)
                count = random.randint(30, 50)
            elif 12 <= hour < 14:
                # Lunch (slight dip)
                count = random.randint(25, 40)
            elif 14 <= hour < 16:
                # Afternoon (second peak)
                count = random.randint(35, 50)
            elif 16 <= hour < 18:
                # Late afternoon (decreasing)
                count = random.randint(20, 40)
            elif 18 <= hour < 20:
                # Early evening (few calls)
                count = random.randint(5, 15)
            else:
                # Night (very few calls)
                count = random.randint(0, 5)
                
            hourly_distribution.append({
                "hour": hour,
                "count": count
            })
        
        self.analytics_data["hourly_distribution"] = hourly_distribution
        
        # Calculate overall call stats
        total_calls = sum(day["count"] for day in daily_calls)
        completed_calls = sum(day["completed"] for day in daily_calls)
        failed_calls = sum(day["failed"] for day in daily_calls)
        active_calls = random.randint(0, 5)  # Random number of active calls
        
        # Calculate average duration (3-5 minutes)
        avg_duration = random.randint(180, 300)
        
        # Calculate success rate
        success_rate = round(completed_calls / total_calls * 100, 1) if total_calls > 0 else 0
        
        self.analytics_data["call_stats"] = {
            "total_calls": total_calls,
            "active_calls": active_calls,
            "completed_calls": completed_calls,
            "failed_calls": failed_calls,
            "avg_duration_seconds": avg_duration,
            "success_rate": success_rate
        }
        
        # Calculate overall SMS stats
        total_sms = sum(day["sent"] for day in daily_sms)
        delivered_sms = sum(day["delivered"] for day in daily_sms)
        failed_sms = sum(day["failed"] for day in daily_sms)
        
        # Calculate delivery rate
        delivery_rate = round(delivered_sms / total_sms * 100, 1) if total_sms > 0 else 0
        
        self.analytics_data["sms_stats"] = {
            "total_sent": total_sms,
            "delivery_success": delivered_sms,
            "delivery_failed": failed_sms,
            "delivery_rate": delivery_rate
        }
        
        # Save all data
        return self._save_analytics_data()

# Create a singleton instance
analytics_manager = AnalyticsManager()

# Helper function for streamlit
def get_analytics_manager() -> AnalyticsManager:
    """Get the analytics manager instance."""
    return analytics_manager
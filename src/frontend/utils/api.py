import json
import os
import logging
import requests
import time
import uuid
import websocket
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths to JSON files
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
CALLS_FILE = os.path.join(DATA_DIR, 'calls.json')
AUTH_FILE = os.path.join(DATA_DIR, 'auth.json')

class APIClient:
    """Client for interacting with the SpeakWise API."""
    
    def __init__(self, use_real_api=False):
        """
        Initialize API client.
        
        Args:
            use_real_api: If True, use real API endpoints. If False, use local JSON files.
        """
        self.use_real_api = use_real_api
        self.config = self._load_config()
        self.base_url = self.config.get("api", {}).get("base_url", "http://localhost:5000")
        self.endpoints = self.config.get("api", {}).get("endpoints", {})
        self.token = None
        self.ws = None
        self.ws_queue = queue.Queue()
        self.ws_callbacks = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            return False
    
    def _load_calls(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load call data from JSON file."""
        try:
            with open(CALLS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading calls: {str(e)}")
            return {"active_calls": [], "recent_calls": []}
    
    def _save_calls(self, calls: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save call data to JSON file."""
        try:
            os.makedirs(os.path.dirname(CALLS_FILE), exist_ok=True)
            with open(CALLS_FILE, 'w') as f:
                json.dump(calls, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving calls: {str(e)}")
            return False
    
    def _load_auth(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load authentication data from JSON file."""
        try:
            with open(AUTH_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading auth data: {str(e)}")
            return {"users": [], "sessions": [], "login_attempts": []}
    
    def _save_auth(self, auth_data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save authentication data to JSON file."""
        try:
            os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
            with open(AUTH_FILE, 'w') as f:
                json.dump(auth_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving auth data: {str(e)}")
            return False
    
    def _make_api_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request to the SpeakWise API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response
        """
        if not self.use_real_api:
            # Simulate API request using local data
            return self._simulate_api_request(method, endpoint, data)
        
        # Make real API request
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return {"error": str(e)}
    
    def _simulate_api_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate an API request using local data.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Simulated API response
        """
        # Simulate API latency (0.2-0.5 seconds)
        time.sleep(0.2 + (0.3 * (time.time() % 1)))
        
        # Handle different endpoints
        if endpoint == self.endpoints.get("health", "/telephony/health"):
            return {"status": "healthy", "version": "1.0.0"}
        
        elif endpoint == self.endpoints.get("calls", "/telephony/calls"):
            calls_data = self._load_calls()
            return {"calls": calls_data["active_calls"]}
        
        elif endpoint.startswith(self.endpoints.get("call", "/telephony/call")):
            calls_data = self._load_calls()
            
            # Handle call details
            if "/" in endpoint[len(self.endpoints.get("call", "/telephony/call")):]:
                call_id = endpoint.split("/")[-1]
                
                # Find call in active or recent calls
                call = next((c for c in calls_data["active_calls"] if c["id"] == call_id), None)
                if not call:
                    call = next((c for c in calls_data["recent_calls"] if c["id"] == call_id), None)
                
                if call:
                    if method.upper() == "GET":
                        return call
                    elif method.upper() == "DELETE":
                        # Move from active to recent
                        if call in calls_data["active_calls"]:
                            calls_data["active_calls"].remove(call)
                            call["status"] = "Completed"
                            call["end_time"] = datetime.now().isoformat()
                            calls_data["recent_calls"].append(call)
                            self._save_calls(calls_data)
                        return {"status": "success", "message": "Call ended"}
                else:
                    return {"error": "Call not found"}
            
            # Handle call creation
            elif method.upper() == "POST" and data:
                new_call = {
                    "id": f"CALL-{uuid.uuid4().hex[:4]}",
                    "phone": data.get("phone_number", "+250789999999"),
                    "service": data.get("service", "General Inquiry"),
                    "start_time": datetime.now().isoformat(),
                    "duration": 0,
                    "status": "Active",
                    "current_step": 1,
                    "total_steps": 5,
                    "agent_id": f"AGT-{uuid.uuid4().hex[:3]}",
                    "ai_actions": [],
                    "success_rate": 100.0,
                    "transcript": [
                        {
                            "role": "system",
                            "content": "Hello, welcome to SpeakWise. How can I help you today?",
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                }
                calls_data["active_calls"].append(new_call)
                self._save_calls(calls_data)
                return new_call
        
        elif endpoint == self.endpoints.get("config", "/system/config"):
            config = self._load_config()
            
            if method.upper() == "GET":
                return config
            elif method.upper() == "PUT" and data:
                # Update config with new data
                for section, values in data.items():
                    if section in config:
                        if isinstance(config[section], dict) and isinstance(values, dict):
                            config[section].update(values)
                        else:
                            config[section] = values
                    else:
                        config[section] = values
                
                self._save_config(config)
                return {"status": "success", "message": "Configuration updated"}
        
        # Handle authentication
        elif endpoint == "/auth/login":
            if method.upper() == "POST" and data:
                username = data.get("username")
                password = data.get("password")
                
                auth_data = self._load_auth()
                user = next((u for u in auth_data["users"] if u["username"] == username), None)
                
                # In a real system, we would verify the password hash here
                # For demo purposes, we'll just check for valid username
                if user:
                    # Update login time and session
                    user["last_login"] = datetime.now().isoformat()
                    self.token = user["token"]
                    
                    # Record successful login attempt
                    auth_data["login_attempts"].append({
                        "username": username,
                        "timestamp": datetime.now().isoformat(),
                        "success": True,
                        "ip_address": "127.0.0.1"
                    })
                    
                    # Add session
                    session = {
                        "user_id": user["id"],
                        "token": user["token"],
                        "created_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(days=1)).isoformat(),
                        "last_activity": datetime.now().isoformat(),
                        "ip_address": "127.0.0.1",
                        "user_agent": "Streamlit"
                    }
                    auth_data["sessions"].append(session)
                    
                    self._save_auth(auth_data)
                    return {
                        "status": "success",
                        "token": user["token"],
                        "user": {
                            "id": user["id"],
                            "username": user["username"],
                            "role": user["role"],
                            "email": user["email"]
                        }
                    }
                else:
                    # Record failed login attempt
                    auth_data["login_attempts"].append({
                        "username": username if username else "unknown",
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "ip_address": "127.0.0.1"
                    })
                    self._save_auth(auth_data)
                    return {"error": "Invalid username or password"}
        
        # Default response for unknown endpoints
        return {"error": "Unknown endpoint"}
    
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """Get list of active calls."""
        if self.use_real_api:
            result = self._make_api_request("GET", self.endpoints.get("calls", "/telephony/calls"))
            return result.get("calls", [])
        else:
            calls_data = self._load_calls()
            return calls_data["active_calls"]
    
    def get_recent_calls(self) -> List[Dict[str, Any]]:
        """Get list of recent calls."""
        if self.use_real_api:
            # Assume there's an endpoint for recent calls
            result = self._make_api_request("GET", "/telephony/calls/recent")
            return result.get("calls", [])
        else:
            calls_data = self._load_calls()
            return calls_data["recent_calls"]
    
    def get_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific call."""
        endpoint = f"{self.endpoints.get('call', '/telephony/call')}/{call_id}"
        result = self._make_api_request("GET", endpoint)
        
        if "error" in result:
            return None
        return result
    
    def end_call(self, call_id: str) -> bool:
        """End an active call."""
        endpoint = f"{self.endpoints.get('call', '/telephony/call')}/{call_id}"
        result = self._make_api_request("DELETE", endpoint)
        
        return "error" not in result
    
    def initiate_call(self, phone_number: str, service: str = None) -> Optional[Dict[str, Any]]:
        """Initiate a new call."""
        data = {"phone_number": phone_number}
        if service:
            data["service"] = service
        
        result = self._make_api_request("POST", self.endpoints.get("call", "/telephony/call"), data)
        
        if "error" in result:
            return None
        return result
    
    def get_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        if self.use_real_api:
            result = self._make_api_request("GET", self.endpoints.get("config", "/system/config"))
            return result
        else:
            return self._load_config()
    
    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """Update system configuration."""
        result = self._make_api_request(
            "PUT", self.endpoints.get("config", "/system/config"), config_updates
        )
        
        return "error" not in result
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Log in to the system."""
        result = self._make_api_request("POST", "/auth/login", {
            "username": username,
            "password": password
        })
        
        if "token" in result:
            self.token = result["token"]
        
        return result
    
    def logout(self) -> bool:
        """Log out from the system."""
        if not self.token:
            return True
        
        result = self._make_api_request("POST", "/auth/logout")
        
        if "error" not in result:
            self.token = None
            return True
        return False
    
    def check_auth(self) -> bool:
        """Check if user is authenticated."""
        if not self.token:
            return False
        
        if self.use_real_api:
            result = self._make_api_request("GET", "/auth/check")
            return "error" not in result
        else:
            # In simulation mode, just check if token exists
            auth_data = self._load_auth()
            session = next((s for s in auth_data["sessions"] if s["token"] == self.token), None)
            return session is not None
    
    def connect_websocket(self, on_message: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Connect to the WebSocket for real-time updates.
        
        Args:
            on_message: Callback function for received messages
            
        Returns:
            True if connection successful, False otherwise
        """
        if not self.use_real_api:
            # Start simulation thread for WebSocket in demo mode
            self._start_ws_simulation(on_message)
            return True
        
        try:
            ws_url = self.config.get("api", {}).get("websocket_url", "ws://localhost:5000/ws")
            
            def on_ws_message(ws, message):
                try:
                    data = json.loads(message)
                    on_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid WebSocket message format: {message}")
            
            def on_ws_error(ws, error):
                logger.error(f"WebSocket error: {error}")
            
            def on_ws_close(ws, close_status_code, close_msg):
                logger.info(f"WebSocket closed: {close_status_code}, {close_msg}")
            
            def on_ws_open(ws):
                logger.info("WebSocket connection established")
                if self.token:
                    ws.send(json.dumps({"type": "auth", "token": self.token}))
            
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                
            self.ws = websocket.WebSocketApp(
                ws_url,
                header=headers,
                on_message=on_ws_message,
                on_error=on_ws_error,
                on_close=on_ws_close,
                on_open=on_ws_open
            )
            
            # Start WebSocket connection in a separate thread
            threading.Thread(target=self.ws.run_forever, daemon=True).start()
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            return False
    
    def disconnect_websocket(self) -> None:
        """Disconnect from the WebSocket."""
        if self.ws:
            self.ws.close()
            self.ws = None
    
    def _start_ws_simulation(self, on_message: Callable[[Dict[str, Any]], None]) -> None:
        """
        Start a thread to simulate WebSocket events.
        
        Args:
            on_message: Callback function for received messages
        """
        def simulate_ws_events():
            # Simulated event types
            event_types = ["call.new", "call.update", "call.end", "system.status"]
            
            while True:
                try:
                    # Check if there's a message in the queue
                    try:
                        message = self.ws_queue.get(block=False)
                        on_message(message)
                        self.ws_queue.task_done()
                        continue
                    except queue.Empty:
                        pass
                    
                    # Randomly generate events (with low probability)
                    if time.time() % 30 < 0.5:  # Generate event roughly every 30 seconds
                        event_type = event_types[int(time.time()) % len(event_types)]
                        
                        if event_type == "call.new":
                            # Simulate new call event
                            calls_data = self._load_calls()
                            if len(calls_data["active_calls"]) < 5:  # Limit to 5 active calls
                                new_call = {
                                    "id": f"CALL-{uuid.uuid4().hex[:4]}",
                                    "phone": f"+25078{uuid.uuid4().hex[:7]}",
                                    "service": ["Business Registration", "Marriage Certificate", 
                                               "Land Transfer", "Passport Application"][
                                                int(time.time()) % 4],
                                    "start_time": datetime.now().isoformat(),
                                    "duration": 0,
                                    "status": "Active",
                                    "current_step": 1,
                                    "total_steps": 5,
                                    "agent_id": f"AGT-{uuid.uuid4().hex[:3]}",
                                    "ai_actions": [],
                                    "success_rate": 100.0,
                                    "transcript": [
                                        {
                                            "role": "system",
                                            "content": "Hello, welcome to SpeakWise. How can I help you today?",
                                            "timestamp": datetime.now().isoformat()
                                        }
                                    ]
                                }
                                calls_data["active_calls"].append(new_call)
                                self._save_calls(calls_data)
                                
                                on_message({
                                    "type": "call.new",
                                    "call": new_call
                                })
                        
                        elif event_type == "call.update":
                            # Simulate call update event
                            calls_data = self._load_calls()
                            if calls_data["active_calls"]:
                                call = calls_data["active_calls"][int(time.time()) % len(calls_data["active_calls"])]
                                
                                # Update call duration and add transcript entry
                                call["duration"] += 30
                                
                                # Add to transcript based on step
                                if call["current_step"] < call["total_steps"]:
                                    if len(call["transcript"]) % 2 == 0:
                                        # Add system message
                                        call["transcript"].append({
                                            "role": "system",
                                            "content": f"I need some more information for your {call['service']} request. Can you please provide your next detail?",
                                            "timestamp": datetime.now().isoformat()
                                        })
                                    else:
                                        # Add user message
                                        call["transcript"].append({
                                            "role": "user",
                                            "content": "Here is the information you requested.",
                                            "timestamp": datetime.now().isoformat()
                                        })
                                        
                                        # Update current step
                                        call["current_step"] = min(call["current_step"] + 1, call["total_steps"])
                                
                                # Add AI action if appropriate
                                if len(call["ai_actions"]) < call["current_step"]:
                                    call["ai_actions"].append({
                                        "timestamp": datetime.now().isoformat(),
                                        "action": f"Process Step {call['current_step']}",
                                        "details": f"Processing data for {call['service']}",
                                        "success": True,
                                        "duration": 3
                                    })
                                
                                self._save_calls(calls_data)
                                
                                on_message({
                                    "type": "call.update",
                                    "call": call
                                })
                        
                        elif event_type == "call.end":
                            # Simulate call end event
                            calls_data = self._load_calls()
                            if calls_data["active_calls"]:
                                # Randomly end a call
                                call_idx = int(time.time()) % len(calls_data["active_calls"])
                                call = calls_data["active_calls"][call_idx]
                                
                                # Move to recent calls
                                calls_data["active_calls"].pop(call_idx)
                                call["status"] = "Completed"
                                call["end_time"] = datetime.now().isoformat()
                                calls_data["recent_calls"].insert(0, call)
                                
                                # Trim recent calls if too many
                                if len(calls_data["recent_calls"]) > 20:
                                    calls_data["recent_calls"] = calls_data["recent_calls"][:20]
                                
                                self._save_calls(calls_data)
                                
                                on_message({
                                    "type": "call.end",
                                    "call": call
                                })
                        
                        elif event_type == "system.status":
                            # Simulate system status update
                            on_message({
                                "type": "system.status",
                                "status": {
                                    "active_calls": len(self._load_calls()["active_calls"]),
                                    "recent_calls": len(self._load_calls()["recent_calls"]),
                                    "cpu_usage": 25 + (int(time.time()) % 20),
                                    "memory_usage": 40 + (int(time.time()) % 15),
                                    "uptime": int(time.time() % 86400)
                                }
                            })
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    logger.error(f"WebSocket simulation error: {str(e)}")
                    time.sleep(5)  # Pause before retrying
        
        # Start simulation thread
        threading.Thread(target=simulate_ws_events, daemon=True).start()
    
    def queue_ws_message(self, message: Dict[str, Any]) -> None:
        """
        Queue a message to be sent via simulated WebSocket.
        
        Args:
            message: Message data
        """
        self.ws_queue.put(message)
    
    def register_ws_callback(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback for a specific WebSocket event type.
        
        Args:
            event_type: Event type to listen for
            callback: Function to call when event is received
        """
        self.ws_callbacks[event_type] = callback
    
    def unregister_ws_callback(self, event_type: str) -> None:
        """
        Unregister a callback for a WebSocket event type.
        
        Args:
            event_type: Event type to stop listening for
        """
        if event_type in self.ws_callbacks:
            del self.ws_callbacks[event_type]
    
    def simulate_incoming_call(self, phone_number: str, service_type: str) -> Dict[str, Any]:
        """
        Simulate an incoming call (for demo purposes).
        
        Args:
            phone_number: Phone number of the caller
            service_type: Type of service requested
            
        Returns:
            New call data
        """
        new_call = {
            "id": f"CALL-{uuid.uuid4().hex[:4]}",
            "phone": phone_number,
            "service": service_type,
            "start_time": datetime.now().isoformat(),
            "duration": 0,
            "status": "Active",
            "current_step": 1,
            "total_steps": 5,
            "agent_id": f"AGT-{uuid.uuid4().hex[:3]}",
            "ai_actions": [],
            "success_rate": 100.0,
            "transcript": [
                {
                    "role": "system",
                    "content": "Hello, welcome to SpeakWise. How can I help you today?",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        calls_data = self._load_calls()
        calls_data["active_calls"].append(new_call)
        self._save_calls(calls_data)
        
        # Queue WebSocket event
        self.queue_ws_message({
            "type": "call.new",
            "call": new_call
        })
        
        return new_call
    
    def simulate_call_progress(self, call_id: str, message: str = None) -> Optional[Dict[str, Any]]:
        """
        Simulate progress on a call (for demo purposes).
        
        Args:
            call_id: ID of the call to update
            message: Optional user message to add
            
        Returns:
            Updated call data or None if call not found
        """
        calls_data = self._load_calls()
        
        # Find call
        call = next((c for c in calls_data["active_calls"] if c["id"] == call_id), None)
        if not call:
            return None
        
        # Update call
        call["duration"] += 30
        
        # Add user message if provided
        if message:
            call["transcript"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
        
        # Generate system response
        if call["current_step"] < call["total_steps"]:
            # Add system message based on service type and step
            service_responses = {
                "Business Registration": [
                    "What type of business is this?",
                    "Please provide your business address.",
                    "What's your full name as the business owner?",
                    "Please provide your national ID number.",
                    "I'll now process your business registration. This will take a moment."
                ],
                "Marriage Certificate": [
                    "What is your partner's full name?",
                    "When do you plan to have the ceremony?",
                    "Please provide your national ID number.",
                    "Please provide your partner's national ID number.",
                    "I'll now process your marriage certificate application."
                ],
                "Land Transfer": [
                    "Who are you transferring the land to?",
                    "Please provide your national ID number.",
                    "Please provide the recipient's national ID number.",
                    "What is the land title number?",
                    "I'll now process your land transfer request."
                ],
                "Passport Application": [
                    "Please provide your date of birth.",
                    "What is your current address?",
                    "Is this your first passport or a renewal?",
                    "We'll need your photo. Have you prepared a digital passport photo?",
                    "I'll now process your passport application."
                ]
            }
            
            # Get appropriate response for this service and step
            responses = service_responses.get(call["service"], 
                ["I need some more information.", "Please provide additional details.", 
                 "Thank you. Just a few more questions.", "Almost done. One last question.",
                 "I'll now process your request."])
            
            response_idx = min(call["current_step"] - 1, len(responses) - 1)
            
            call["transcript"].append({
                "role": "system",
                "content": responses[response_idx],
                "timestamp": datetime.now().isoformat()
            })
            
            # Add AI action
            call["ai_actions"].append({
                "timestamp": datetime.now().isoformat(),
                "action": f"Process Step {call['current_step']}",
                "details": f"Processing data for {call['service']}, step {call['current_step']}",
                "success": True,
                "duration": random.randint(2, 5)
            })
            
            # Update step
            call["current_step"] += 1
        
        # Save updated data
        self._save_calls(calls_data)
        
        # Queue WebSocket event
        self.queue_ws_message({
            "type": "call.update",
            "call": call
        })
        
        return call
    
    def simulate_end_call(self, call_id: str, success: bool = True) -> bool:
        """
        Simulate ending a call (for demo purposes).
        
        Args:
            call_id: ID of the call to end
            success: Whether the call was successful
            
        Returns:
            True if call was found and ended, False otherwise
        """
        calls_data = self._load_calls()
        
        # Find call
        call_idx = next((i for i, c in enumerate(calls_data["active_calls"]) 
                         if c["id"] == call_id), None)
        if call_idx is None:
            return False
        
        # Remove call from active calls
        call = calls_data["active_calls"].pop(call_idx)
        
        # Update call status
        call["status"] = "Completed" if success else "Failed"
        call["end_time"] = datetime.now().isoformat()
        
        # Add final transcript entries
        if success:
            # Add completion message
            service_completions = {
                "Business Registration": "I've successfully submitted your business registration. Your reference number is BR-" + uuid.uuid4().hex[:8].upper() + ". You'll receive confirmation via SMS within 3 business days.",
                "Marriage Certificate": "I've submitted your marriage certificate application. Your reference number is MC-" + uuid.uuid4().hex[:8].upper() + ". You'll need to visit the sector office to finalize the process.",
                "Land Transfer": "I've submitted your land transfer request. Your reference number is LT-" + uuid.uuid4().hex[:8].upper() + ". Both parties will need to visit the land office within 14 days.",
                "Passport Application": "I've submitted your passport application. Your reference number is PP-" + uuid.uuid4().hex[:8].upper() + ". You'll need to visit the immigration office for biometric data collection."
            }
            
            completion_message = service_completions.get(
                call["service"], 
                "Your request has been successfully processed. You'll receive a confirmation soon."
            )
            
            call["transcript"].append({
                "role": "system",
                "content": completion_message,
                "timestamp": datetime.now().isoformat()
            })
            
            call["transcript"].append({
                "role": "user",
                "content": "Thank you for your help!",
                "timestamp": datetime.now().isoformat()
            })
            
            call["transcript"].append({
                "role": "system",
                "content": "You're welcome! Thank you for using SpeakWise. Have a great day!",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Add failure message
            call["transcript"].append({
                "role": "system",
                "content": "I'm sorry, but we're experiencing technical difficulties. Please try again later or contact support for assistance.",
                "timestamp": datetime.now().isoformat()
            })
        
        # Add to recent calls
        calls_data["recent_calls"].insert(0, call)
        
        # Trim recent calls if too many
        if len(calls_data["recent_calls"]) > 20:
            calls_data["recent_calls"] = calls_data["recent_calls"][:20]
        
        # Save updated data
        self._save_calls(calls_data)
        
        # Queue WebSocket event
        self.queue_ws_message({
            "type": "call.end",
            "call": call
        })
        
        return True

# Create a singleton instance
api_client = APIClient(use_real_api=False)

# Helper functions for streamlit
def get_api_client() -> APIClient:
    """Get the API client instance."""
    return api_client
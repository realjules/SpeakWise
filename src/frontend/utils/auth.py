import os
import json
import logging
import hashlib
import secrets
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths to JSON files
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
AUTH_FILE = os.path.join(DATA_DIR, 'auth.json')

class AuthManager:
    """Manager for authentication and user sessions."""
    
    def __init__(self):
        """Initialize the authentication manager."""
        self.current_user = None
        self.session_token = None
    
    def _load_auth_data(self) -> Dict[str, Any]:
        """Load authentication data from JSON file."""
        try:
            with open(AUTH_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading auth data: {str(e)}")
            return {"users": [], "sessions": [], "login_attempts": []}
    
    def _save_auth_data(self, auth_data: Dict[str, Any]) -> bool:
        """Save authentication data to JSON file."""
        try:
            os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
            with open(AUTH_FILE, 'w') as f:
                json.dump(auth_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving auth data: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """
        Create a simple password hash for demo purposes.
        
        In a real system, use bcrypt or another secure hashing algorithm.
        """
        # This is a simplistic hash for demo only - not secure for production!
        salt = "speakwise_salt"
        hash_object = hashlib.sha256((password + salt).encode())
        return hash_object.hexdigest()
    
    def _generate_token(self) -> str:
        """Generate a random token for authentication."""
        # Generate random bytes and encode as URL-safe base64
        token_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(token_bytes).decode('utf-8')
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Attempt to log in a user.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Tuple of (success, user_data)
        """
        auth_data = self._load_auth_data()
        
        # Record login attempt
        auth_data["login_attempts"].append({
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "success": False,  # Default to failure, update if successful
            "ip_address": "127.0.0.1"  # Demo IP
        })
        
        # Find user
        user = next((u for u in auth_data["users"] if u["username"] == username), None)
        if not user:
            self._save_auth_data(auth_data)
            return False, None
        
        # Check password (in a real system, verify against stored hash)
        # For demo, we'll just check if user exists
        # password_hash = self._hash_password(password)
        # if user["password_hash"] != password_hash:
        #    return False, None
        
        # Update login attempt to success
        auth_data["login_attempts"][-1]["success"] = True
        
        # Generate session token
        token = self._generate_token()
        
        # Update user's last login
        user["last_login"] = datetime.now().isoformat()
        
        # Add session
        session = {
            "user_id": user["id"],
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "last_activity": datetime.now().isoformat(),
            "ip_address": "127.0.0.1",
            "user_agent": "Streamlit"
        }
        auth_data["sessions"].append(session)
        
        # Save changes
        self._save_auth_data(auth_data)
        
        # Set current user and token
        self.current_user = user
        self.session_token = token
        
        # Return user data (without sensitive info)
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "permissions": user.get("permissions", [])
        }
        
        return True, user_data
    
    def logout(self) -> bool:
        """
        Log out the current user.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.session_token:
            return True
            
        auth_data = self._load_auth_data()
        
        # Remove session
        auth_data["sessions"] = [s for s in auth_data["sessions"] 
                               if s["token"] != self.session_token]
        
        # Save changes
        success = self._save_auth_data(auth_data)
        
        # Clear current user and token
        self.current_user = None
        self.session_token = None
        
        return success
    
    def check_auth(self, token: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a token is valid and return the associated user.
        
        Args:
            token: Session token to verify (uses current token if None)
            
        Returns:
            Tuple of (is_valid, user_data)
        """
        token = token or self.session_token
        
        if not token:
            return False, None
            
        auth_data = self._load_auth_data()
        
        # Find session
        session = next((s for s in auth_data["sessions"] if s["token"] == token), None)
        if not session:
            return False, None
            
        # Check if session is expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            # Remove expired session
            auth_data["sessions"] = [s for s in auth_data["sessions"] if s["token"] != token]
            self._save_auth_data(auth_data)
            return False, None
            
        # Update last activity
        session["last_activity"] = datetime.now().isoformat()
        
        # Find user
        user = next((u for u in auth_data["users"] if u["id"] == session["user_id"]), None)
        if not user:
            return False, None
            
        # Save changes
        self._save_auth_data(auth_data)
        
        # Return user data (without sensitive info)
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "permissions": user.get("permissions", [])
        }
        
        return True, user_data
    
    def create_user(self, username: str, password: str, email: str, role: str = "Viewer") -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Create a new user.
        
        Args:
            username: User's username
            password: User's password
            email: User's email
            role: User's role (Admin, Operator, Viewer)
            
        Returns:
            Tuple of (success, user_data)
        """
        auth_data = self._load_auth_data()
        
        # Check if username or email already exists
        if any(u["username"] == username for u in auth_data["users"]):
            return False, {"error": "Username already exists"}
            
        if any(u["email"] == email for u in auth_data["users"]):
            return False, {"error": "Email already exists"}
            
        # Set permissions based on role
        permissions = []
        if role == "Admin":
            permissions = ["view", "edit", "manage_users", "system_config"]
        elif role == "Operator":
            permissions = ["view", "edit"]
        elif role == "Viewer":
            permissions = ["view"]
            
        # Create user
        user_id = max([u["id"] for u in auth_data["users"]], default=0) + 1
        
        user = {
            "id": user_id,
            "username": username,
            "password_hash": self._hash_password(password),
            "email": email,
            "role": role,
            "permissions": permissions,
            "last_login": None
        }
        
        auth_data["users"].append(user)
        
        # Save changes
        success = self._save_auth_data(auth_data)
        
        if not success:
            return False, {"error": "Failed to save user data"}
            
        # Return user data (without sensitive info)
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "permissions": user["permissions"]
        }
        
        return True, user_data
    
    def get_users(self) -> list:
        """
        Get list of all users (without sensitive info).
        
        Returns:
            List of user data
        """
        auth_data = self._load_auth_data()
        
        # Return users without sensitive info
        users = []
        for user in auth_data["users"]:
            users.append({
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "permissions": user.get("permissions", []),
                "last_login": user.get("last_login")
            })
            
        return users
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if successful, False otherwise
        """
        auth_data = self._load_auth_data()
        
        # Remove user
        auth_data["users"] = [u for u in auth_data["users"] if u["id"] != user_id]
        
        # Remove user's sessions
        auth_data["sessions"] = [s for s in auth_data["sessions"] if s["user_id"] != user_id]
        
        # Save changes
        return self._save_auth_data(auth_data)
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Update a user's information.
        
        Args:
            user_id: ID of the user to update
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (success, user_data)
        """
        auth_data = self._load_auth_data()
        
        # Find user
        user = next((u for u in auth_data["users"] if u["id"] == user_id), None)
        if not user:
            return False, {"error": "User not found"}
            
        # Update fields
        for field, value in updates.items():
            if field == "password":
                # Handle password separately
                user["password_hash"] = self._hash_password(value)
            elif field != "id" and field != "password_hash":
                # Don't allow changing ID or direct hash changes
                user[field] = value
                
        # Save changes
        success = self._save_auth_data(auth_data)
        
        if not success:
            return False, {"error": "Failed to save user data"}
            
        # Return updated user data (without sensitive info)
        user_data = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "permissions": user.get("permissions", []),
            "last_login": user.get("last_login")
        }
        
        return True, user_data
    
    def has_permission(self, permission: str, user_id: Optional[int] = None) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            permission: Permission to check
            user_id: User ID to check (uses current user if None)
            
        Returns:
            True if user has permission, False otherwise
        """
        # If no current user and no user_id, no permission
        if not self.current_user and user_id is None:
            return False
            
        auth_data = self._load_auth_data()
        
        # Find user
        if user_id:
            user = next((u for u in auth_data["users"] if u["id"] == user_id), None)
        else:
            user = next((u for u in auth_data["users"] if u["id"] == self.current_user["id"]), None)
            
        if not user:
            return False
            
        # Check permission
        return permission in user.get("permissions", [])

# Create a singleton instance
auth_manager = AuthManager()

# Helper functions for streamlit
def get_auth_manager() -> AuthManager:
    """Get the authentication manager instance."""
    return auth_manager
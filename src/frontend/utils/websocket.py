import streamlit as st
import threading
import time
import json
import logging
from typing import Dict, Any, Callable, Optional

from .api import get_api_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manager for WebSocket connections and event handling."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.callbacks = {}
        self.connected = False
        self.update_thread = None
        self.stop_event = threading.Event()
    
    def on_message(self, message: Dict[str, Any]) -> None:
        """
        Handle incoming WebSocket messages.
        
        Args:
            message: Message data
        """
        message_type = message.get("type")
        
        if message_type and message_type in self.callbacks:
            # Call registered callbacks for this message type
            for callback in self.callbacks.get(message_type, []):
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in WebSocket callback: {str(e)}")
        
        # Store the message in session state for access by components
        if "ws_messages" not in st.session_state:
            st.session_state.ws_messages = []
        
        st.session_state.ws_messages.append(message)
        
        # Keep only the last 100 messages
        if len(st.session_state.ws_messages) > 100:
            st.session_state.ws_messages = st.session_state.ws_messages[-100:]
    
    def connect(self) -> bool:
        """
        Connect to the WebSocket.
        
        Returns:
            True if connection successful or already connected, False otherwise
        """
        if self.connected:
            return True
        
        try:
            api_client = get_api_client()
            success = api_client.connect_websocket(self.on_message)
            
            if success:
                self.connected = True
                
                # Start the update thread
                self.stop_event.clear()
                self.update_thread = threading.Thread(target=self._trigger_updates)
                self.update_thread.daemon = True
                self.update_thread.start()
                
                logger.info("WebSocket connected")
                return True
            else:
                logger.error("Failed to connect WebSocket")
                return False
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the WebSocket."""
        if not self.connected:
            return
        
        try:
            # Stop the update thread
            if self.update_thread:
                self.stop_event.set()
                self.update_thread.join(timeout=2.0)
                self.update_thread = None
            
            api_client = get_api_client()
            api_client.disconnect_websocket()
            
            self.connected = False
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {str(e)}")
    
    def register_callback(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Event type to listen for
            callback: Function to call when event is received
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        
        self.callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: str, callback: Optional[Callable] = None) -> None:
        """
        Unregister a callback for an event type.
        
        Args:
            event_type: Event type to stop listening for
            callback: Specific callback to remove (removes all if None)
        """
        if event_type in self.callbacks:
            if callback:
                self.callbacks[event_type] = [cb for cb in self.callbacks[event_type] if cb != callback]
            else:
                self.callbacks[event_type] = []
    
    def _trigger_updates(self) -> None:
        """Trigger Streamlit to update when new messages arrive."""
        while not self.stop_event.is_set():
            # Check if there are any new messages
            if hasattr(st.session_state, 'ws_messages') and st.session_state.ws_messages:
                # Set a flag to indicate new messages
                st.session_state.ws_new_messages = True
                
                # Force Streamlit to rerun if possible
                if hasattr(st, 'rerun'):
                    try:
                        st.rerun()
                    except Exception:
                        pass
            
            # Sleep for a short time
            time.sleep(0.1)
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message through the WebSocket.
        
        Args:
            message: Message data
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            if not self.connected:
                return False
                
            api_client = get_api_client()
            api_client.queue_ws_message(message)
            return True
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {str(e)}")
            return False

# Create a singleton instance
ws_manager = WebSocketManager()

# Helper functions for streamlit
def get_ws_manager() -> WebSocketManager:
    """Get the WebSocket manager instance."""
    return ws_manager

def initialize_ws_connection() -> None:
    """Initialize WebSocket connection in Streamlit session."""
    if not hasattr(st.session_state, 'ws_initialized'):
        ws_manager = get_ws_manager()
        ws_manager.connect()
        st.session_state.ws_initialized = True
        
        # Initialize messages list if needed
        if "ws_messages" not in st.session_state:
            st.session_state.ws_messages = []

def get_latest_ws_messages(event_type: Optional[str] = None, limit: int = 10) -> list:
    """
    Get the latest WebSocket messages.
    
    Args:
        event_type: Filter by event type (all if None)
        limit: Maximum number of messages to return
        
    Returns:
        List of messages
    """
    if "ws_messages" not in st.session_state:
        return []
        
    if event_type:
        messages = [m for m in st.session_state.ws_messages if m.get("type") == event_type]
    else:
        messages = st.session_state.ws_messages.copy()
        
    return messages[-limit:]
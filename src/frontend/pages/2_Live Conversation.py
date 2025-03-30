import streamlit as st
st.set_page_config(
    page_title="Live Conversation | SpeakWise",
    page_icon="🗣️",
    layout="wide"
)

import time
from datetime import datetime, timedelta
import random
import json
import threading
import queue

# Import utility functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_api_client, get_ws_manager, initialize_ws_connection, get_latest_ws_messages

# Import OpenAI helper - use current directory path
try:
    # Get the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)  # Add current directory to path
    
    # Try to import directly first
    try:
        from openai_helper import generate_ai_response, is_openai_available
        OPENAI_AVAILABLE = is_openai_available()
    except ImportError:
        # If that fails, try with the full path
        openai_helper_path = os.path.join(current_dir, "openai_helper.py")
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_helper", openai_helper_path)
        openai_helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openai_helper)
        
        # Get the functions
        generate_ai_response = openai_helper.generate_ai_response
        is_openai_available = openai_helper.is_openai_available
        OPENAI_AVAILABLE = is_openai_available()
except Exception as e:
    st.warning(f"OpenAI helper not available: {str(e)}")
    OPENAI_AVAILABLE = False
    
    # Fallback function if the import fails
    def generate_ai_response(user_message, service_type):
        """Fallback generate_ai_response function"""
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
        
        responses = service_responses.get(service_type, 
            ["I need some more information.", "Please provide additional details.", 
             "Thank you. Just a few more questions.", "Almost done. One last question.",
             "I'll now process your request."])
        
        # Pick a response based on the step or random
        return random.choice(responses)

st.markdown("""
<style>
    /* Sidebar styling */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        width: 100%;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
        padding-left: 0.4rem;
    }
    /* Style Home item */
    section[data-testid="stSidebarNav"] div[data-testid="stSidebarNavItems"] > div:first-child {
        font-weight: bold;
    }
    /* Style Live Conversation item (highlighted when active) */
    section[data-testid="stSidebarNav"] div[data-testid="stSidebarNavItems"] > div:nth-child(4) {
        background-color: rgba(141, 198, 191, 0.2);
        border-right: 4px solid #8DC6BF;
        font-weight: bold;
    }

    /* Custom styling for the conversation visualization */
    .conversation-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .system-message {
        background-color: #e3f2fd;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
        color: #0d47a1;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .user-message {
        background-color: #e8f5e9;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0 8px auto;
        max-width: 80%;
        float: right;
        clear: both;
        color: #1b5e20;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .processing-indicator {
        background-color: #f3e5f5;
        border-radius: 18px;
        padding: 8px 16px;
        margin: 8px 0;
        max-width: 60%;
        float: left;
        clear: both;
        color: #4a148c;
        font-style: italic;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .timestamp {
        font-size: 0.7em;
        color: #757575;
        margin-top: 4px;
        display: block;
    }
    
    .typing-indicator {
        display: inline-block;
        width: 50px;
        text-align: left;
    }
    
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #888;
        margin-right: 3px;
        animation: wave 1.3s linear infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: -1.1s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: -0.9s;
    }
    
    @keyframes wave {
        0%, 60%, 100% {
            transform: initial;
            background-color: #888;
        }
        30% {
            transform: translateY(-5px);
            background-color: #666;
        }
    }
    
    .message-row {
        margin-bottom: 16px;
        overflow: hidden;
    }
    
    .system-avatar, .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        overflow: hidden;
        float: left;
        margin-right: 10px;
    }
    
    .user-avatar {
        float: right;
        margin-right: 0;
        margin-left: 10px;
    }
    
    .system-avatar img, .user-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .message-content {
        display: inline-block;
        max-width: calc(100% - 50px);
    }
    
    /* Microphone and Waveform visualization */
    .microphone-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 20px 0;
    }
    
    .microphone {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: #8DC6BF;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        border: 3px solid #f9f9f9;
    }
    
    .microphone.listening {
        animation: pulse 1.5s infinite;
        background-color: #F97B4F;
    }
    
    .microphone i {
        font-size: 40px;
        color: white;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
    }
    
    .waveform {
        height: 120px;
        width: 100%;
        position: relative;
        margin: 10px 0;
        background-color: #f9f9f9;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .waveform-bars {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 100%;
        padding: 0 10px;
    }
    
    .waveform-bar {
        width: 3px;
        background-color: #584053;
        border-radius: 3px;
        transition: height 0.2s ease;
    }
    
    .waveform-bar.user {
        background-color: #FCBC66;
    }
    
    .waveform-bar.ai {
        background-color: #8DC6BF;
    }
    
    .waveform-label {
        position: absolute;
        top: 5px;
        color: #584053;
        font-size: 12px;
        font-weight: bold;
    }
    
    .waveform-label.user {
        right: 10px;
    }
    
    .waveform-label.ai {
        left: 10px;
    }
    
    /* Button styling */
    .demo-button {
        background-color: #8DC6BF;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s;
        margin: 5px;
    }
    
    .demo-button:hover {
        background-color: #6BA5A0;
    }
    
    .reset-button {
        background-color: #FF5252;
    }
    
    .reset-button:hover {
        background-color: #D32F2F;
    }
    
    /* Voice levels indicator */
    .voice-levels {
        display: flex;
        align-items: center;
        height: 40px;
        position: relative;
        margin: 10px 0;
    }
    
    .voice-level-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #ccc;
        margin: 0 3px;
        transition: all 0.1s ease;
    }
    
    .voice-level-dot.active {
        background-color: #4CAF50;
        box-shadow: 0 0 5px #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API client and WebSocket connection
api_client = get_api_client()
initialize_ws_connection()

# Get WebSocket manager
ws_manager = get_ws_manager()

# Header
st.markdown("# 🗣️ Live Conversation")
st.markdown("Real-time visualization of caller conversations with SpeakWise AI")

# Function to simulate waveform visualization
def generate_waveform_heights(active=False, user_active=False, ai_active=False, num_bars=100):
    heights = []
    
    # Generate heights for user and AI
    for i in range(num_bars):
        if i < num_bars / 2:  # First half (AI)
            if ai_active:
                # Active AI waveform (left side)
                height = random.randint(10, 80) if random.random() > 0.2 else random.randint(5, 15)
            else:
                # Inactive AI waveform
                height = random.randint(2, 8)
        else:  # Second half (User)
            if user_active:
                # Active user waveform (right side)
                height = random.randint(10, 80) if random.random() > 0.2 else random.randint(5, 15)
            else:
                # Inactive user waveform
                height = random.randint(2, 8)
        heights.append(height)
    
    return heights

# Function to create an enhanced waveform visualization
def render_waveform(call_data=None):
    num_bars = 100
    
    # Determine active states based on call data
    user_active = False
    ai_active = False
    
    if call_data and call_data.get("status") == "Active":
        # Check the latest message to determine who's speaking
        if "transcript" in call_data and call_data["transcript"]:
            latest_message = call_data["transcript"][-1]
            if latest_message["role"] == "user":
                user_active = True
            elif latest_message["role"] == "system":
                ai_active = True
    
    heights = generate_waveform_heights(active=True, user_active=user_active, ai_active=ai_active, num_bars=num_bars)
    
    html = """
    <div class="waveform">
        <span class="waveform-label ai">SpeakWise AI</span>
        <span class="waveform-label user">User</span>
        <div class="waveform-bars">
    """
    
    for i, height in enumerate(heights):
        # Set the class based on position (left half is AI, right half is user)
        bar_class = "waveform-bar ai" if i < num_bars / 2 else "waveform-bar user"
        html += f'<div class="{bar_class}" style="height: {height}px;"></div>'
    
    html += """
        </div>
    </div>
    """
    
    return html

# Function to render the microphone visualization
def render_microphone(is_listening=False):
    listening_class = "listening" if is_listening else ""
    
    html = f"""
    <div class="microphone-container">
        <div class="microphone {listening_class}">
            <i>🎤</i>
        </div>
        <div style="text-align: center; font-weight: bold; margin-bottom: 10px;">
            {("LISTENING..." if is_listening else "CALL ACTIVE")}
        </div>
    </div>
    """
    
    return html

# Function to create voice level indicators
def render_voice_levels(active=False, num_dots=20):
    if active:
        # More dots active when speaking
        active_dots = random.randint(5, num_dots)
    else:
        # Fewer dots active when quiet
        active_dots = random.randint(0, 3)
    
    html = """
    <div class="voice-levels">
    """
    
    for i in range(num_dots):
        if i < active_dots:
            html += '<div class="voice-level-dot active"></div>'
        else:
            html += '<div class="voice-level-dot"></div>'
    
    html += """
    </div>
    """
    
    return html

# Function to render conversation messages with timestamps
def render_conversation_messages(call_data):
    if not call_data or "transcript" not in call_data:
        return "<p>No conversation data available.</p>"
    
    transcript = call_data["transcript"]
    messages_html = ""
    
    for message in transcript:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        
        # Format timestamp
        if isinstance(message.get("timestamp"), str):
            message_time = datetime.fromisoformat(message["timestamp"].replace('Z', '+00:00'))
            timestamp = message_time.strftime("%H:%M:%S")
        else:
            timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M:%S")
        
        if role == "system":
            messages_html += f"""
            <div class="message-row">
                <div class="system-avatar">
                    <img src="https://via.placeholder.com/36/e3f2fd/0d47a1?text=AI" alt="AI">
                </div>
                <div class="message-content">
                    <div class="system-message">
                        {content}
                        <span class="timestamp">{timestamp}</span>
                    </div>
                </div>
            </div>
            """
        elif role == "user":
            messages_html += f"""
            <div class="message-row">
                <div class="user-avatar">
                    <img src="https://via.placeholder.com/36/e8f5e9/1b5e20?text=U" alt="User">
                </div>
                <div class="message-content" style="float: right;">
                    <div class="user-message">
                        {content}
                        <span class="timestamp">{timestamp}</span>
                    </div>
                </div>
            </div>
            """
        elif role == "processing":
            messages_html += f"""
            <div class="message-row">
                <div class="processing-indicator">
                    {content}
                    <div class="typing-indicator">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                    </div>
                    <span class="timestamp">{timestamp}</span>
                </div>
            </div>
            """
    
    # Add voice level visualization for latest message
    if transcript and transcript[-1]["role"] in ["user", "system"]:
        is_active = call_data.get("status") == "Active"
        is_user = transcript[-1]["role"] == "user"
        
        if is_user:
            messages_html += f"""
            <div style="clear: both; margin: 10px 0; text-align: right;">
                <div style="display: inline-block; width: 80%; text-align: right;">
                    {render_voice_levels(is_active)}
                </div>
            </div>
            """
        else:
            messages_html += f"""
            <div style="clear: both; margin: 10px 0;">
                <div style="display: inline-block; width: 80%;">
                    {render_voice_levels(is_active)}
                </div>
            </div>
            """
    
    return f"""
    <div class="conversation-container">
        {messages_html}
    </div>
    """

# Register for WebSocket updates
if "ws_call_callbacks_registered" not in st.session_state:
    def on_call_update(message):
        # Update call data if it's the selected call
        if "selected_live_call_id" in st.session_state and message["call"]["id"] == st.session_state.selected_live_call_id:
            st.session_state.live_call_data = message["call"]
    
    # Register for call updates
    ws_manager.register_callback("call.update", on_call_update)
    ws_manager.register_callback("call.end", on_call_update)
    
    st.session_state.ws_call_callbacks_registered = True

# Layout - two columns
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("Active Calls")
    
    # Get active calls
    active_calls = api_client.get_active_calls()
    
    if not active_calls:
        st.info("No active calls at the moment.")
        st.markdown("### Demo Controls")
        
        # Demo form
        with st.form("new_call_form"):
            demo_phone = st.text_input("Phone Number", value="+250783456789")
            demo_service = st.selectbox("Service Type", 
                ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"])
            
            # Add OpenAI toggle
            use_openai = st.checkbox("Use OpenAI for responses", value=OPENAI_AVAILABLE, disabled=not OPENAI_AVAILABLE)
            if not OPENAI_AVAILABLE:
                st.caption("OpenAI integration not available. Check your API key configuration.")
            
            # Submit button
            submitted = st.form_submit_button("Simulate New Call")
            if submitted:
                new_call = api_client.simulate_incoming_call(demo_phone, demo_service)
                
                # Store OpenAI preference in session state
                st.session_state.use_openai = use_openai and OPENAI_AVAILABLE
                
                st.success(f"New call simulated: {new_call['id']}")
                
                # Select the new call
                st.session_state.selected_live_call_id = new_call['id']
                st.session_state.live_call_data = new_call
                st.rerun()
    else:
        # List active calls
        for call in active_calls:
            # Format duration
            duration_mins = call["duration"] // 60
            duration_secs = call["duration"] % 60
            
            # Create a card for each call
            with st.container():
                st.markdown(f"**Call ID**: {call['id']}")
                st.markdown(f"**Phone**: {call['phone']}")
                st.markdown(f"**Service**: {call['service']}")
                st.markdown(f"**Duration**: {duration_mins}m {duration_secs}s")
                st.progress(value=call["current_step"]/call["total_steps"], 
                           text=f"Step {call['current_step']}/{call['total_steps']}")
                
                # View button
                if st.button("View Conversation", key=f"view_call_{call['id']}"):
                    st.session_state.selected_live_call_id = call["id"]
                    st.session_state.live_call_data = call
                    st.rerun()
                
                st.markdown("---")
        
        # Add demo button to simulate new call
        if st.button("+ Simulate New Call"):
            # Phone number format +250XXXXXXXX
            phone = f"+250{random.randint(700000000, 799999999)}"
            service = random.choice([
                "Business Registration", "Marriage Certificate", 
                "Land Transfer", "Passport Application"
            ])
            new_call = api_client.simulate_incoming_call(phone, service)
            st.success(f"New call simulated: {new_call['id']}")
            st.session_state.selected_live_call_id = new_call['id']
            st.session_state.live_call_data = new_call
            st.rerun()

with right_col:
    # Get selected call data
    if "selected_live_call_id" in st.session_state and st.session_state.selected_live_call_id:
        if "live_call_data" not in st.session_state:
            # Find call data
            call_data = next((call for call in active_calls if call["id"] == st.session_state.selected_live_call_id), None)
            if call_data:
                st.session_state.live_call_data = call_data
        
        call_data = st.session_state.live_call_data
        
        if call_data:
            # Call info header
            st.subheader(f"Live Conversation: {call_data['id']}")
            
            # Call metadata
            info_col1, info_col2, info_col3, info_col4 = st.columns([1, 1, 1, 1])
            
            with info_col1:
                st.markdown(f"**Phone**: {call_data['phone']}")
            
            with info_col2:
                st.markdown(f"**Service**: {call_data['service']}")
            
            with info_col3:
                # Format duration
                duration_mins = call_data["duration"] // 60
                duration_secs = call_data["duration"] % 60
                st.markdown(f"**Duration**: {duration_mins}m {duration_secs}s")
            
            with info_col4:
                status_color = "#4CAF50" if call_data["status"] == "Active" else "#2196F3" if call_data["status"] == "Completed" else "#F44336"
                st.markdown(f"**Status**: <span style='color:{status_color};'>{call_data['status']}</span>", unsafe_allow_html=True)
            
            # Progress bar
            st.markdown(f"**Progress**: Step {call_data['current_step']} of {call_data['total_steps']}")
            st.progress(value=call_data["current_step"]/call_data["total_steps"])
            
            # Live conversation visualization with microphone and waveform
            st.markdown("### Live Conversation Stream")
            
            # Create containers for our visualizations
            mic_container = st.empty()
            waveform_container = st.empty()
            
            # Determine if someone is speaking (for mic animation)
            is_speaking = False
            is_user_speaking = False
            if call_data["status"] == "Active" and "transcript" in call_data and call_data["transcript"]:
                latest_message = call_data["transcript"][-1]
                # Consider it active speaking if the message is very recent (within 5 seconds)
                if "timestamp" in latest_message:
                    try:
                        message_time = datetime.fromisoformat(latest_message["timestamp"].replace('Z', '+00:00'))
                        is_speaking = (datetime.now().replace(tzinfo=None) - message_time.replace(tzinfo=None)).total_seconds() < 5
                        is_user_speaking = is_speaking and latest_message["role"] == "user"
                    except:
                        pass
            
            # Render microphone and waveform visualizations
            mic_container.markdown(render_microphone(is_speaking), unsafe_allow_html=True)
            waveform_container.markdown(render_waveform(call_data), unsafe_allow_html=True)
            
            # Conversation transcript display
            st.markdown("### Conversation Transcript")
            conversation_placeholder = st.empty()
            conversation_placeholder.markdown(render_conversation_messages(call_data), unsafe_allow_html=True)
            
            # Control buttons
            if call_data["status"] == "Active":
                st.markdown("### Demo Controls")
                control_col1, control_col2, control_col3 = st.columns([1, 1, 1])
                
                with control_col1:
                    # Advance call
                    if st.button("⏩ Advance Call", key="live_advance"):
                        updated_call = api_client.simulate_call_progress(call_data["id"])
                        if updated_call:
                            st.session_state.live_call_data = updated_call
                            st.rerun()
                
                with control_col2:
                    # End call successfully
                    if st.button("✅ Complete Call", key="live_complete"):
                        success = api_client.simulate_end_call(call_data["id"], True)
                        if success:
                            st.success("Call completed successfully")
                            st.session_state.live_call_data["status"] = "Completed"
                            st.rerun()
                
                with control_col3:
                    # End call with failure
                    if st.button("❌ Fail Call", key="live_fail"):
                        success = api_client.simulate_end_call(call_data["id"], False)
                        if success:
                            st.error("Call ended with failure")
                            st.session_state.live_call_data["status"] = "Failed"
                            st.rerun()
                
                # Custom message input
                st.markdown("### Add Custom User Message")
                custom_message = st.text_input("Enter user message:", key="live_custom_message")
                
                # Check if OpenAI is enabled in session state
                use_openai = st.session_state.get("use_openai", False) and OPENAI_AVAILABLE
                
                if st.button("Send Message", key="live_send_message"):
                    if custom_message:
                        if use_openai:
                            # Generate AI response using OpenAI
                            with st.spinner("Generating AI response..."):
                                ai_response = generate_ai_response(
                                    custom_message, 
                                    call_data["service"]
                                )
                                # Use the API client's method to update with both message and response
                                updated_call = api_client.simulate_call_progress_with_response(
                                    call_data["id"], 
                                    custom_message,
                                    ai_response
                                )
                        else:
                            # Use the original simulation
                            updated_call = api_client.simulate_call_progress(call_data["id"], custom_message)
                            
                        if updated_call:
                            st.session_state.live_call_data = updated_call
                            st.rerun()
            
            # Refresh button
            if st.button("🔄 Refresh", key="refresh_convo"):
                # Get updated call data
                if call_data["status"] == "Active":
                    updated_call = api_client.get_call_details(call_data["id"])
                    if updated_call:
                        st.session_state.live_call_data = updated_call
                st.rerun()
                
            # Auto-refresh
            auto_refresh = st.checkbox("Auto-refresh (every 3s)", value=False, key="auto_refresh")
            if auto_refresh and call_data["status"] == "Active":
                time.sleep(3)  # Wait 3 seconds
                st.rerun()
                
            # Add OpenAI Voice Interface if available
            if OPENAI_AVAILABLE and call_data["status"] == "Active":
                st.markdown("---")
                st.markdown("### Voice Integration")
                
                # Add this to src/frontend/pages/2_Live Conversation.py

                # Replace the simulated recording with real microphone access
                if "recording" not in st.session_state:
                    st.session_state.recording = False
                    st.session_state.audio_bytes = None

                # Create a container for the voice interface
                voice_container = st.container()

                with voice_container:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Real audio recording button
                        if not st.session_state.recording:
                            if st.button("🎤 Start Recording", key="start_recording"):
                                st.session_state.recording = True
                                st.rerun()
                        else:
                            st.button("⏹️ Stop Recording", key="stop_recording", 
                                    help="Click to stop recording and process audio")
                            st.markdown("**Recording... Speak now**")
                            
                            # Use streamlit-webrtc for real audio capture
                            try:
                                import streamlit_webrtc
                                
                                # Define audio processor
                                def audio_processor(frame):
                                    # Save the audio data
                                    st.session_state.audio_bytes = frame.to_ndarray().tobytes()
                                    return frame
                                
                                # Handle different versions of streamlit-webrtc
                                try:
                                    # Try newer API first
                                    ctx = streamlit_webrtc.webrtc_streamer(
                                        key="speech-to-text",
                                        audio_processor_factory=lambda: audio_processor,
                                        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                                        media_stream_constraints={"audio": True, "video": False},
                                    )
                                except Exception as api_error:
                                    st.warning(f"Using alternative streamlit-webrtc configuration: {str(api_error)}")
                                    # Try older API as fallback
                                    try:
                                        # Try legacy API without using WebRtcMode enum
                                        ctx = streamlit_webrtc.webrtc_streamer(
                                            key="speech-to-text-fallback",
                                            audio_processor_factory=audio_processor,
                                            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                                            media_stream_constraints={"audio": True, "video": False},
                                        )
                                    except Exception as e:
                                        st.error(f"Audio recording requires an updated streamlit-webrtc package: {str(e)}")
                                        ctx = None
                                
                                # When recording is stopped
                                if ctx and hasattr(ctx, 'state') and hasattr(ctx.state, 'playing') and not ctx.state.playing and st.session_state.recording:
                                    st.session_state.recording = False
                                    
                                    # Process the captured audio
                                    if st.session_state.audio_bytes:
                                        with st.spinner("Processing audio..."):
                                            # Connect to OpenAI for transcription
                                            if OPENAI_AVAILABLE:
                                                # Create a temporary file with the audio bytes
                                                import tempfile
                                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                                                    f.write(st.session_state.audio_bytes)
                                                    temp_file = f.name
                                                
                                                # Initialize the speech processor
                                                api_key = os.getenv("OPENAI_API_KEY")
                                                processor = SpeechProcessor(api_key=api_key)
                                                
                                                # Transcribe the audio
                                                transcribed_text = processor.transcribe(temp_file)
                                                os.unlink(temp_file)  # Clean up temp file
                                                
                                                # Show transcribed text and enable sending to AI
                                                if transcribed_text:
                                                    st.session_state.transcribed_text = transcribed_text
                                                    st.rerun()
                                            else:
                                                st.error("OpenAI is not available. Please check your API key.")
                            except ImportError:
                                st.error("Please install streamlit-webrtc: pip install streamlit-webrtc")
                    
                    # Show transcribed text if available
                    if "transcribed_text" in st.session_state:
                        st.markdown(f"**You said:** {st.session_state.transcribed_text}")
                        
                        # Process button to send to AI
                        if st.button("Send to AI", key="send_to_ai"):
                            # Generate AI response
                            with st.spinner("Generating AI response..."):
                                call_id = st.session_state.selected_live_call_id
                                service_type = call_data["service"] if "call_data" in locals() else "General Inquiry"
                                
                                ai_response = generate_ai_response(
                                    st.session_state.transcribed_text, 
                                    service_type
                                )
                                
                                # Update call with transcribed text and AI response
                                updated_call = api_client.simulate_call_progress_with_response(
                                    call_id,
                                    st.session_state.transcribed_text,
                                    ai_response
                                )
                                
                                if updated_call:
                                    st.session_state.live_call_data = updated_call
                                    # Text-to-speech the response
                                    try:
                                        api_key = os.getenv("OPENAI_API_KEY")
                                        processor = SpeechProcessor(api_key=api_key)
                                        audio_response = processor.synthesize(ai_response)
                                        
                                        # Play the audio response
                                        import base64
                                        audio_bytes = base64.b64encode(audio_response).decode()
                                        st.markdown(f"""
                                        <audio autoplay>
                                            <source src="data:audio/mp3;base64,{audio_bytes}" type="audio/mp3">
                                        </audio>
                                        """, unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Error generating speech: {e}")
                                    
                                    # Clear transcribed text
                                    del st.session_state.transcribed_text
                                    st.rerun()
# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
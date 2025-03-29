import streamlit as st
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

st.set_page_config(
    page_title="Live Conversation | SpeakWise",
    page_icon="🗣️",
    layout="wide"
)

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
            
            # Submit button
            submitted = st.form_submit_button("Simulate New Call")
            if submitted:
                new_call = api_client.simulate_incoming_call(demo_phone, demo_service)
                st.success(f"New call simulated: {new_call['id']}")
                
                # Select the new call
                st.session_state.selected_live_call_id = new_call['id']
                st.session_state.live_call_data = new_call
                st.experimental_rerun()
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
                    st.experimental_rerun()
                
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
            st.experimental_rerun()

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
                            st.experimental_rerun()
                
                with control_col2:
                    # End call successfully
                    if st.button("✅ Complete Call", key="live_complete"):
                        success = api_client.simulate_end_call(call_data["id"], True)
                        if success:
                            st.success("Call completed successfully")
                            st.session_state.live_call_data["status"] = "Completed"
                            st.experimental_rerun()
                
                with control_col3:
                    # End call with failure
                    if st.button("❌ Fail Call", key="live_fail"):
                        success = api_client.simulate_end_call(call_data["id"], False)
                        if success:
                            st.error("Call ended with failure")
                            st.session_state.live_call_data["status"] = "Failed"
                            st.experimental_rerun()
                
                # Custom message input
                st.markdown("### Add Custom User Message")
                custom_message = st.text_input("Enter user message:", key="live_custom_message")
                if st.button("Send Message", key="live_send_message"):
                    if custom_message:
                        updated_call = api_client.simulate_call_progress(call_data["id"], custom_message)
                        if updated_call:
                            st.session_state.live_call_data = updated_call
                            st.experimental_rerun()
            
            # Refresh button
            if st.button("🔄 Refresh", key="refresh_convo"):
                # Get updated call data
                if call_data["status"] == "Active":
                    updated_call = api_client.get_call_details(call_data["id"])
                    if updated_call:
                        st.session_state.live_call_data = updated_call
                st.experimental_rerun()
                
            # Auto-refresh
            auto_refresh = st.checkbox("Auto-refresh (every 3s)", value=False, key="auto_refresh")
            if auto_refresh and call_data["status"] == "Active":
                time.sleep(3)  # Wait 3 seconds
                st.experimental_rerun()
        else:
            st.warning(f"Call {st.session_state.selected_live_call_id} not found.")
            if st.button("Clear Selection"):
                if "selected_live_call_id" in st.session_state:
                    del st.session_state.selected_live_call_id
                if "live_call_data" in st.session_state:
                    del st.session_state.live_call_data
                st.experimental_rerun()
    else:
        # No call selected
        st.image("https://via.placeholder.com/800x500?text=Select+a+call+to+view+conversation", width=800)
        st.info("Select an active call from the left panel to view the conversation in real-time.")
        
        if not active_calls:
            if st.button("Create Demo Call"):
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
                st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
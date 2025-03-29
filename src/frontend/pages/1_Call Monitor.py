import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
import json
import time

# Import utility functions
import sys
import os
# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_api_client, get_ws_manager, initialize_ws_connection, get_latest_ws_messages

st.set_page_config(
    page_title="Call Monitor | SpeakWise",
    page_icon="📞",
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
    /* Style Call Monitor item (highlighted when active) */
    section[data-testid="stSidebarNav"] div[data-testid="stSidebarNavItems"] > div:nth-child(2) {
        background-color: rgba(141, 198, 191, 0.2);
        border-right: 4px solid #8DC6BF;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .call-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .active-call {
        border-left: 5px solid #4CAF50;
    }
    .completed-call {
        border-left: 5px solid #2196F3;
    }
    .failed-call {
        border-left: 5px solid #F44336;
    }
    .call-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .call-info {
        font-size: 0.9rem;
        color: #546E7A;
    }
    .call-status {
        font-weight: bold;
    }
    .status-active {
        color: #4CAF50;
    }
    .status-completed {
        color: #2196F3;
    }
    .status-failed {
        color: #F44336;
    }
    .ai-action-card {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #1976D2;
    }
    .ai-action-success {
        border-left-color: #4CAF50;
    }
    .ai-action-fail {
        border-left-color: #F44336;
    }
    .ai-action-title {
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    .ai-action-details {
        font-size: 0.9rem;
        color: #616161;
    }
    .screenshot-container {
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 5px;
        margin-top: 0.5rem;
    }
    .clickable-row {
        cursor: pointer;
    }
    .clickable-row:hover {
        background-color: rgba(25, 118, 210, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize API client and WebSocket connection
api_client = get_api_client()
initialize_ws_connection()

# Get WebSocket manager
ws_manager = get_ws_manager()

# Register callback for WebSocket events
if "ws_callbacks_registered" not in st.session_state:
    def on_call_new(message):
        # Add new call to active calls
        if "active_calls" in st.session_state:
            st.session_state.active_calls.append(message["call"])
    
    def on_call_update(message):
        # Update call in active calls
        if "active_calls" in st.session_state:
            call_id = message["call"]["id"]
            for i, call in enumerate(st.session_state.active_calls):
                if call["id"] == call_id:
                    st.session_state.active_calls[i] = message["call"]
                    break
    
    def on_call_end(message):
        # Remove call from active calls and add to recent calls
        if "active_calls" in st.session_state and "recent_calls" in st.session_state:
            call_id = message["call"]["id"]
            # Remove from active calls
            st.session_state.active_calls = [c for c in st.session_state.active_calls if c["id"] != call_id]
            # Add to recent calls at the beginning
            st.session_state.recent_calls.insert(0, message["call"])
            # Limit recent calls to 20
            if len(st.session_state.recent_calls) > 20:
                st.session_state.recent_calls = st.session_state.recent_calls[:20]
    
    ws_manager.register_callback("call.new", on_call_new)
    ws_manager.register_callback("call.update", on_call_update)
    ws_manager.register_callback("call.end", on_call_end)
    
    st.session_state.ws_callbacks_registered = True

# Header
st.markdown("# 📞 Call Monitor")
st.markdown("Real-time monitoring and management of active and recent calls")

# Load call data from API
@st.cache_data(ttl=5)  # Cache for 5 seconds
def load_call_data():
    active_calls = api_client.get_active_calls()
    recent_calls = api_client.get_recent_calls()
    return active_calls, recent_calls

# Check if we need to reload data
if "active_calls" not in st.session_state or "recent_calls" not in st.session_state:
    active_calls, recent_calls = load_call_data()
    st.session_state.active_calls = active_calls
    st.session_state.recent_calls = recent_calls

# Function to set selected call and trigger a rerun
def select_call(call_id):
    st.session_state.selected_call_id = call_id
    st.experimental_rerun()

# Initialize selected call ID if not present
if "selected_call_id" not in st.session_state:
    st.session_state.selected_call_id = None

# Tabs for different views
call_tab, history_tab = st.tabs(["Active Calls", "Call History"])

# Active Calls Tab
with call_tab:
    # Controls row
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### Active Calls ({len(st.session_state.active_calls)})")
    
    with col2:
        service_filter = st.selectbox(
            "Filter by service",
            ["All Services"] + list(set([call["service"] for call in st.session_state.active_calls]) or ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]),
            key="active_service_filter"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Duration (Longest)", "Duration (Shortest)"],
            key="active_sort"
        )
    
    # Apply filters
    filtered_active_calls = st.session_state.active_calls
    if service_filter != "All Services":
        filtered_active_calls = [call for call in st.session_state.active_calls if call["service"] == service_filter]
    
    # Apply sorting
    if sort_by == "Newest First":
        filtered_active_calls = sorted(filtered_active_calls, 
                                       key=lambda x: datetime.fromisoformat(x["start_time"]) if isinstance(x["start_time"], str) else x["start_time"], 
                                       reverse=True)
    elif sort_by == "Oldest First":
        filtered_active_calls = sorted(filtered_active_calls, 
                                       key=lambda x: datetime.fromisoformat(x["start_time"]) if isinstance(x["start_time"], str) else x["start_time"])
    elif sort_by == "Duration (Longest)":
        filtered_active_calls = sorted(filtered_active_calls, key=lambda x: x["duration"], reverse=True)
    elif sort_by == "Duration (Shortest)":
        filtered_active_calls = sorted(filtered_active_calls, key=lambda x: x["duration"])
    
    # Display active calls
    if not filtered_active_calls:
        st.info("No active calls match your filters")
        
        # Demo buttons
        st.markdown("### Demo Controls")
        demo_col1, demo_col2 = st.columns(2)
        
        with demo_col1:
            demo_phone = st.text_input("Phone Number", value="+250783456789", key="demo_phone")
            demo_service = st.selectbox("Service Type", 
                ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"],
                key="demo_service")
        
        with demo_col2:
            if st.button("Simulate New Call", key="simulate_call"):
                new_call = api_client.simulate_incoming_call(demo_phone, demo_service)
                st.success(f"New call simulated: {new_call['id']}")
                st.session_state.selected_call_id = new_call['id']
                st.experimental_rerun()
    else:
        for i, call in enumerate(filtered_active_calls):
            col1, col2 = st.columns([3, 1])
            
            # Format timestamp
            if isinstance(call["start_time"], str):
                start_time = datetime.fromisoformat(call["start_time"].replace('Z', '+00:00'))
                start_time_str = start_time.strftime("%H:%M:%S")
            else:
                start_time_str = call["start_time"].strftime("%H:%M:%S")
            
            with col1:
                st.markdown(f"""
                <div class="call-card active-call">
                    <div class="call-header">
                        {call["id"]} - {call["phone"]} <span class="call-status status-active">● ACTIVE</span>
                    </div>
                    <div class="call-info">
                        <strong>Service:</strong> {call["service"]}<br>
                        <strong>Started:</strong> {start_time_str}<br>
                        <strong>Duration:</strong> {call["duration"] // 60}m {call["duration"] % 60}s<br>
                        <strong>Agent:</strong> {call["agent_id"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**Current Step:** {call['current_step']} of {call['total_steps']}")
                progress = call["current_step"] / call["total_steps"]
                st.progress(progress)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("View Details", key=f"view_active_{i}"):
                        st.session_state.selected_call_id = call["id"]
                
                with col_b:
                    if st.button("Advance Call", key=f"advance_{i}"):
                        api_client.simulate_call_progress(call["id"])
                        st.experimental_rerun()
    
    # Refresh controls
    refresh_col1, refresh_col2, refresh_col3 = st.columns([2, 1, 1])
    with refresh_col2:
        if st.button("Refresh Data", key="refresh_active"):
            active_calls, recent_calls = load_call_data()
            st.session_state.active_calls = active_calls
            st.session_state.recent_calls = recent_calls
            st.experimental_rerun()
    
    with refresh_col3:
        if st.button("Simulate New Call", key="new_call"):
            # Phone number format +250XXXXXXXX
            phone = f"+250{random.randint(700000000, 799999999)}"
            service = random.choice([
                "Business Registration", "Marriage Certificate", 
                "Land Transfer", "Passport Application"
            ])
            new_call = api_client.simulate_incoming_call(phone, service)
            st.success(f"New call simulated: {new_call['id']}")
            st.session_state.selected_call_id = new_call['id']
            st.experimental_rerun()

# Call History Tab
with history_tab:
    # Controls row
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("### Call History")
    
    with col2:
        history_service_filter = st.selectbox(
            "Filter by service",
            ["All Services"] + list(set([call["service"] for call in st.session_state.recent_calls]) or ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]),
            key="history_service_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Filter by status",
            ["All Statuses", "Completed", "Failed"],
            key="status_filter"
        )
    
    with col4:
        history_sort_by = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Duration (Longest)", "Duration (Shortest)"],
            key="history_sort"
        )
    
    # Apply filters
    filtered_recent_calls = st.session_state.recent_calls
    if history_service_filter != "All Services":
        filtered_recent_calls = [call for call in filtered_recent_calls if call["service"] == history_service_filter]
    
    if status_filter != "All Statuses":
        filtered_recent_calls = [call for call in filtered_recent_calls if call["status"] == status_filter]
    
    # Apply sorting
    if history_sort_by == "Newest First":
        filtered_recent_calls = sorted(filtered_recent_calls, 
                                      key=lambda x: datetime.fromisoformat(x["start_time"]) if isinstance(x["start_time"], str) else x["start_time"], 
                                      reverse=True)
    elif history_sort_by == "Oldest First":
        filtered_recent_calls = sorted(filtered_recent_calls, 
                                     key=lambda x: datetime.fromisoformat(x["start_time"]) if isinstance(x["start_time"], str) else x["start_time"])
    elif history_sort_by == "Duration (Longest)":
        filtered_recent_calls = sorted(filtered_recent_calls, key=lambda x: x["duration"], reverse=True)
    elif history_sort_by == "Duration (Shortest)":
        filtered_recent_calls = sorted(filtered_recent_calls, key=lambda x: x["duration"])
    
    # Create dataframe for display
    if filtered_recent_calls:
        # Convert to DataFrame
        df = pd.DataFrame(filtered_recent_calls)
        
        # Create a copy without the AI actions to display
        display_df = df.copy()
        
        # Convert timestamps to strings
        if "start_time" in display_df.columns:
            display_df["start_time"] = display_df["start_time"].apply(
                lambda x: datetime.fromisoformat(x.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, str) else x.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        if "end_time" in display_df.columns:
            display_df["end_time"] = display_df["end_time"].apply(
                lambda x: datetime.fromisoformat(x.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, str) and x else ''
            )
        
        # Format duration
        display_df["duration"] = display_df["duration"].apply(lambda x: f"{x // 60}m {x % 60}s")
        
        # Drop complex columns before display
        display_cols = ["id", "phone", "service", "start_time", "duration", "status"]
        
        # Call ID Search 
        search_id = st.text_input(
            "Call ID Search",
            placeholder="Type a call ID or leave empty to browse all calls",
            key="call_id_search"
        )
        
        if search_id:
            # Filter displayed calls based on search
            matching_calls = display_df[display_df["id"].str.contains(search_id, case=False)]
            if not matching_calls.empty:
                # Highlight the first matching call
                st.session_state.selected_call_id = matching_calls.iloc[0]["id"]
                display_df = matching_calls
            else:
                st.warning(f"No calls matching '{search_id}' found")
        
        # Display the table
        st.dataframe(
            display_df[display_cols],
            column_config={
                "id": st.column_config.Column(
                    "Call ID",
                    help="Click on a row to view call details"
                ),
                "phone": "Phone Number",
                "service": "Service",
                "start_time": "Start Time",
                "duration": "Duration",
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Completed", "Failed", "Active"],
                    disabled=True
                )
            },
            use_container_width=True
        )
        
        # Add manual call selectors
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            call_options = [call["id"] for call in filtered_recent_calls]
            if call_options:
                selected_call = st.selectbox("Select Call", call_options, key="manual_call_select")
                if st.button("View Details", key="view_selected"):
                    st.session_state.selected_call_id = selected_call
                    st.experimental_rerun()
                    
        with col6:
            # Random call button for demo purposes
            if st.button("Random Call", help="View a random call for demonstration"):
                if filtered_recent_calls:
                    random_idx = random.randint(0, len(filtered_recent_calls) - 1)
                    st.session_state.selected_call_id = filtered_recent_calls[random_idx]["id"]
                    st.experimental_rerun()
        
        st.info("Enter a Call ID in the search box or use the selector to view details")
    else:
        st.info("No calls match your filters")

# Call details section - shown if a call is selected
if st.session_state.selected_call_id:
    st.markdown("---")
    st.markdown("### Call Details")
    
    # Find the selected call from both active and recent calls
    selected_call = next((call for call in st.session_state.active_calls if call["id"] == st.session_state.selected_call_id), None)
    if not selected_call:
        selected_call = next((call for call in st.session_state.recent_calls if call["id"] == st.session_state.selected_call_id), None)
    
    if selected_call:
        # Display call details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            status_class = "status-active" if selected_call["status"] == "Active" else "status-completed" if selected_call["status"] == "Completed" else "status-failed"
            card_class = "active-call" if selected_call["status"] == "Active" else "completed-call" if selected_call["status"] == "Completed" else "failed-call"
            
            # Format timestamps
            if isinstance(selected_call["start_time"], str):
                start_time = datetime.fromisoformat(selected_call["start_time"].replace('Z', '+00:00'))
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                start_time_str = selected_call["start_time"].strftime("%Y-%m-%d %H:%M:%S")
            
            st.markdown(f"""
            <div class="call-card {card_class}">
                <div class="call-header">
                    {selected_call["id"]} <span class="call-status {status_class}">● {selected_call["status"].upper()}</span>
                </div>
                <div class="call-info">
                    <strong>Phone:</strong> {selected_call["phone"]}<br>
                    <strong>Service:</strong> {selected_call["service"]}<br>
                    <strong>Started:</strong> {start_time_str}<br>
                    <strong>Duration:</strong> {selected_call["duration"] // 60}m {selected_call["duration"] % 60}s<br>
                    <strong>Agent ID:</strong> {selected_call["agent_id"]}<br>
                    <strong>Success Rate:</strong> {selected_call.get("success_rate", 0):.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add control buttons if call is active
            if selected_call["status"] == "Active":
                if st.button("Advance Call", key="detail_advance"):
                    api_client.simulate_call_progress(selected_call["id"])
                    st.experimental_rerun()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("End Call (Success)", key="end_success"):
                        api_client.simulate_end_call(selected_call["id"], True)
                        st.experimental_rerun()
                
                with col_b:
                    if st.button("End Call (Fail)", key="end_fail"):
                        api_client.simulate_end_call(selected_call["id"], False)
                        st.experimental_rerun()
        
        with col2:
            # Basic call information
            st.markdown("#### Call Summary")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Duration", f"{selected_call['duration'] // 60}m {selected_call['duration'] % 60}s")
            with col_b:
                st.metric("Success Rate", f"{selected_call.get('success_rate', 0):.1f}%")
            with col_c:
                st.metric("AI Actions", len(selected_call.get('ai_actions', [])))
        
        # Tabs for call details
        action_tab, transcript_tab = st.tabs(["AI Actions", "Call Transcript"])
        
        with action_tab:
            st.markdown("#### Browser Automation Steps")
            st.markdown("Powered by **browser-use** - [github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)")
            
            # Display all actions
            ai_actions = selected_call.get('ai_actions', [])
            if not ai_actions:
                st.info("No AI actions recorded for this call yet.")
            else:
                for i, action in enumerate(ai_actions):
                    success_class = "ai-action-success" if action.get("success", True) else "ai-action-fail"
                    success_text = "✅ Success" if action.get("success", True) else "❌ Failed"
                    
                    # Format timestamp
                    if isinstance(action.get("timestamp"), str):
                        action_time = datetime.fromisoformat(action["timestamp"].replace('Z', '+00:00'))
                        action_time_str = action_time.strftime("%H:%M:%S")
                    else:
                        action_time_str = action.get("timestamp", datetime.now()).strftime("%H:%M:%S")
                    
                    st.markdown(f"""
                    <div class="ai-action-card {success_class}">
                        <div class="ai-action-title">
                            {i+1}. {action.get("action", "Unknown Action")} - {success_text} ({action.get("duration", 0)}s)
                        </div>
                        <div class="ai-action-details">
                            {action_time_str} - {action.get("details", "No details available")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show screenshot if available - use placeholder for demo
                    with st.expander("Show screenshot"):
                        screenshot = action.get("screenshot", "https://via.placeholder.com/600x400?text=Screenshot+Placeholder")
                        st.image(screenshot, use_column_width=True)
        
        with transcript_tab:
            st.markdown("#### Call Transcript")
            
            # Display transcript
            transcript = selected_call.get('transcript', [])
            if not transcript:
                st.info("No transcript available for this call yet.")
            else:
                for entry in transcript:
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    
                    # Format timestamp
                    if isinstance(entry.get("timestamp"), str):
                        entry_time = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
                        entry_time_str = entry_time.strftime("%H:%M:%S")
                    else:
                        entry_time_str = entry.get("timestamp", datetime.now()).strftime("%H:%M:%S")
                    
                    if role == "system":
                        st.markdown(f"**System** ({entry_time_str}): {content}")
                    elif role == "user":
                        st.markdown(f"**User** ({entry_time_str}): {content}", help="User spoke this")
                    elif role == "processing":
                        st.info(f"**Processing**: {content}")
            
            # Add custom message if call is active
            if selected_call["status"] == "Active":
                custom_message = st.text_input("Add user message:", key="custom_transcript_message")
                if st.button("Send Message"):
                    if custom_message:
                        api_client.simulate_call_progress(selected_call["id"], custom_message)
                        st.experimental_rerun()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Download Transcript"):
                st.info("Transcript download functionality will be implemented in production")
        
        with col2:
            if st.button("Download AI Action Log"):
                st.info("Action log download functionality will be implemented in production")
        
        with col3:
            if st.button("Close Details"):
                st.session_state.selected_call_id = None
                st.experimental_rerun()
    else:
        st.error(f"Call {st.session_state.selected_call_id} not found. It may have been removed.")
        if st.button("Clear Selection"):
            st.session_state.selected_call_id = None
            st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
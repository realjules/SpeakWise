import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
import json

st.set_page_config(
    page_title="Call Monitor | SpeakWise",
    page_icon="📞",
    layout="wide"
)

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

# Header
st.markdown("# 📞 Call Monitor")
st.markdown("Real-time monitoring and management of active and recent calls")

# Function to generate sample AI actions for a call
def generate_ai_actions(service_type, num_actions=8):
    actions = []
    
    # Common initial actions
    actions.append({
        "timestamp": datetime.now() - timedelta(minutes=random.randint(10, 30)),
        "action": "Initialize Session",
        "details": "Started new browser session for service automation",
        "success": True,
        "duration": random.randint(1, 3),
        "screenshot": "https://via.placeholder.com/600x400?text=Browser+Initialized"
    })
    
    actions.append({
        "timestamp": datetime.now() - timedelta(minutes=random.randint(8, 28)),
        "action": "Navigate to Main Page",
        "details": "Navigated to https://services.gov.rw/",
        "success": True,
        "duration": random.randint(2, 4),
        "screenshot": "https://via.placeholder.com/600x400?text=Main+Page+Navigation"
    })
    
    # Service-specific actions
    if service_type == "Business Registration":
        service_actions = [
            {
                "action": "Search Service",
                "details": "Searched for 'business registration' in the service catalog",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Search+Service"
            },
            {
                "action": "Select Business Type",
                "details": "Selected 'Limited Liability Company' from the available options",
                "success": True,
                "duration": random.randint(1, 2),
                "screenshot": "https://via.placeholder.com/600x400?text=Select+Business+Type"
            },
            {
                "action": "Fill Business Details",
                "details": "Entered business name, address, and contact information",
                "success": True,
                "duration": random.randint(3, 6),
                "screenshot": "https://via.placeholder.com/600x400?text=Business+Details+Form"
            },
            {
                "action": "Upload Documents",
                "details": "Uploaded identification and business plan documents",
                "success": random.choice([True, True, False]),
                "duration": random.randint(5, 10),
                "screenshot": "https://via.placeholder.com/600x400?text=Document+Upload"
            },
            {
                "action": "Retry Document Upload",
                "details": "Retried document upload with optimized file size",
                "success": True,
                "duration": random.randint(3, 7),
                "screenshot": "https://via.placeholder.com/600x400?text=Document+Upload+Retry"
            },
            {
                "action": "Payment Processing",
                "details": "Processed payment of 15,000 RWF via mobile money",
                "success": True,
                "duration": random.randint(5, 12),
                "screenshot": "https://via.placeholder.com/600x400?text=Payment+Processing"
            },
            {
                "action": "Generate Receipt",
                "details": "Generated and saved payment receipt",
                "success": True,
                "duration": random.randint(2, 4),
                "screenshot": "https://via.placeholder.com/600x400?text=Receipt+Generation"
            },
            {
                "action": "Confirmation",
                "details": "Received confirmation of successful registration submission",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Confirmation+Page"
            }
        ]
    elif service_type == "Marriage Certificate":
        service_actions = [
            {
                "action": "Search Service",
                "details": "Searched for 'marriage certificate' in the service catalog",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Search+Marriage+Service"
            },
            {
                "action": "Enter Applicant Details",
                "details": "Entered names and identification for both partners",
                "success": True,
                "duration": random.randint(4, 8),
                "screenshot": "https://via.placeholder.com/600x400?text=Applicant+Details"
            },
            {
                "action": "Select Ceremony Date",
                "details": "Selected preferred date for ceremony from calendar",
                "success": True,
                "duration": random.randint(1, 2),
                "screenshot": "https://via.placeholder.com/600x400?text=Date+Selection"
            },
            {
                "action": "Add Witness Information",
                "details": "Added details for required witnesses",
                "success": True,
                "duration": random.randint(3, 6),
                "screenshot": "https://via.placeholder.com/600x400?text=Witness+Information"
            },
            {
                "action": "Upload Identification",
                "details": "Uploaded ID cards for both applicants",
                "success": True,
                "duration": random.randint(4, 8),
                "screenshot": "https://via.placeholder.com/600x400?text=ID+Upload"
            },
            {
                "action": "Payment Processing",
                "details": "Processed payment of 7,500 RWF via mobile money",
                "success": random.choice([True, False]),
                "duration": random.randint(5, 12),
                "screenshot": "https://via.placeholder.com/600x400?text=Payment+Processing"
            },
            {
                "action": "Retry Payment",
                "details": "Retried payment after initial failure",
                "success": True,
                "duration": random.randint(3, 8),
                "screenshot": "https://via.placeholder.com/600x400?text=Payment+Retry"
            },
            {
                "action": "Confirmation",
                "details": "Received confirmation and appointment details",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Confirmation+Page"
            }
        ]
    else:
        # Generic actions for other services
        service_actions = [
            {
                "action": "Search Service",
                "details": f"Searched for '{service_type}' in the service catalog",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Search+Service"
            },
            {
                "action": "Enter User Information",
                "details": "Entered personal details and identification",
                "success": True,
                "duration": random.randint(3, 6),
                "screenshot": "https://via.placeholder.com/600x400?text=User+Information"
            },
            {
                "action": "Form Completion",
                "details": "Completed all required service-specific fields",
                "success": True,
                "duration": random.randint(4, 10),
                "screenshot": "https://via.placeholder.com/600x400?text=Form+Completion"
            },
            {
                "action": "Service Option Selection",
                "details": "Selected appropriate service options and preferences",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Option+Selection"
            },
            {
                "action": "Upload Required Documents",
                "details": "Uploaded all required supporting documents",
                "success": random.choice([True, True, False]),
                "duration": random.randint(5, 10),
                "screenshot": "https://via.placeholder.com/600x400?text=Document+Upload"
            },
            {
                "action": "Fix Document Format",
                "details": "Converted and reuploaded documents in correct format",
                "success": True,
                "duration": random.randint(3, 8),
                "screenshot": "https://via.placeholder.com/600x400?text=Document+Fix"
            },
            {
                "action": "Payment Processing",
                "details": f"Processed payment for {service_type} service fee",
                "success": True,
                "duration": random.randint(5, 12),
                "screenshot": "https://via.placeholder.com/600x400?text=Payment+Processing"
            },
            {
                "action": "Service Confirmation",
                "details": "Received confirmation and reference number",
                "success": True,
                "duration": random.randint(1, 3),
                "screenshot": "https://via.placeholder.com/600x400?text=Service+Confirmation"
            }
        ]
    
    # Select a random subset of service-specific actions
    selected_actions = random.sample(service_actions, min(len(service_actions), num_actions - 2))
    
    # Add timestamps to service-specific actions
    for i, action in enumerate(selected_actions):
        action["timestamp"] = actions[-1]["timestamp"] + timedelta(minutes=random.randint(1, 3))
        actions.append(action)
    
    # Ensure actions are in chronological order
    actions.sort(key=lambda x: x["timestamp"])
    
    # Calculate success rate
    success_count = sum(1 for action in actions if action["success"])
    success_rate = success_count / len(actions) * 100
    
    # Calculate total duration
    total_duration = sum(action["duration"] for action in actions)
    
    return actions, success_rate, total_duration

# Generate sample transaction data
def generate_call_data(num_active=5, num_recent=20):
    services = ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]
    statuses = ["Active", "Completed", "Failed"]
    status_weights = [0.2, 0.7, 0.1]
    
    # Active calls
    active_calls = []
    for i in range(random.randint(0, num_active)):
        service = random.choice(services)
        duration = random.randint(30, 900)
        start_time = datetime.now() - timedelta(seconds=duration)
        step = random.randint(1, 5)
        total_steps = random.randint(5, 8)
        
        # Generate AI actions for this call
        ai_actions, success_rate, action_duration = generate_ai_actions(service, random.randint(3, 8))
        
        active_calls.append({
            "id": f"CALL-{random.randint(1000, 9999)}",
            "phone": f"+25078{random.randint(1000000, 9999999)}",
            "service": service,
            "start_time": start_time,
            "duration": duration,
            "status": "Active",
            "current_step": step,
            "total_steps": total_steps,
            "agent_id": f"AGT-{random.randint(100, 999)}",
            "ai_actions": ai_actions,
            "success_rate": success_rate,
            "action_duration": action_duration
        })
    
    # Recent calls
    recent_calls = []
    for i in range(num_recent):
        service = random.choice(services)
        status = random.choices(statuses, status_weights)[0]
        duration = random.randint(30, 900) if status != "Failed" else random.randint(10, 120)
        end_time = datetime.now() - timedelta(minutes=random.randint(5, 120))
        start_time = end_time - timedelta(seconds=duration)
        
        if status == "Active":
            completion = None
        elif status == "Failed":
            completion = "Error"
        else:
            completion = "Success"
        
        # Generate AI actions for this call
        ai_actions, success_rate, action_duration = generate_ai_actions(service, random.randint(5, 10))
        
        recent_calls.append({
            "id": f"CALL-{random.randint(1000, 9999)}",
            "phone": f"+25078{random.randint(1000000, 9999999)}",
            "service": service,
            "start_time": start_time,
            "end_time": end_time if status != "Active" else None,
            "duration": duration,
            "status": status,
            "completion": completion,
            "agent_id": f"AGT-{random.randint(100, 999)}",
            "ai_actions": ai_actions,
            "success_rate": success_rate,
            "action_duration": action_duration
        })
    
    return active_calls, recent_calls

active_calls, recent_calls = generate_call_data()

# Store in session state for persistence
if 'active_calls' not in st.session_state:
    st.session_state.active_calls = active_calls

if 'recent_calls' not in st.session_state:
    st.session_state.recent_calls = recent_calls

if 'selected_call_id' not in st.session_state:
    st.session_state.selected_call_id = None

# Function to set selected call and trigger a rerun
def select_call(call_id):
    st.session_state.selected_call_id = call_id
    st.rerun()

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
            ["All Services"] + list(set([call["service"] for call in st.session_state.active_calls])),
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
        filtered_active_calls = sorted(filtered_active_calls, key=lambda x: x["start_time"], reverse=True)
    elif sort_by == "Oldest First":
        filtered_active_calls = sorted(filtered_active_calls, key=lambda x: x["start_time"])
    elif sort_by == "Duration (Longest)":
        filtered_active_calls = sorted(filtered_active_calls, key=lambda x: x["duration"], reverse=True)
    elif sort_by == "Duration (Shortest)":
        filtered_active_calls = sorted(filtered_active_calls, key=lambda x: x["duration"])
    
    # Display active calls
    if not filtered_active_calls:
        st.info("No active calls match your filters")
    else:
        for i, call in enumerate(filtered_active_calls):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="call-card active-call">
                    <div class="call-header">
                        {call["id"]} - {call["phone"]} <span class="call-status status-active">● ACTIVE</span>
                    </div>
                    <div class="call-info">
                        <strong>Service:</strong> {call["service"]}<br>
                        <strong>Started:</strong> {call["start_time"].strftime("%H:%M:%S")}<br>
                        <strong>Duration:</strong> {call["duration"] // 60}m {call["duration"] % 60}s<br>
                        <strong>Agent:</strong> {call["agent_id"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**Current Step:** {call['current_step']} of {call['total_steps']}")
                progress = call["current_step"] / call["total_steps"]
                st.progress(progress)
                
                if st.button("View Details", key=f"view_active_{i}"):
                    st.session_state.selected_call_id = call["id"]
                    st.session_state.active_tab = "details"
    
    # Refresh controls
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Refresh Data", key="refresh_active"):
            st.session_state.active_calls, _ = generate_call_data()
            st.rerun()

# Call History Tab
with history_tab:
    # Controls row
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("### Call History")
    
    with col2:
        history_service_filter = st.selectbox(
            "Filter by service",
            ["All Services"] + list(set([call["service"] for call in st.session_state.recent_calls])),
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
        filtered_recent_calls = sorted(filtered_recent_calls, key=lambda x: x["start_time"], reverse=True)
    elif history_sort_by == "Oldest First":
        filtered_recent_calls = sorted(filtered_recent_calls, key=lambda x: x["start_time"])
    elif history_sort_by == "Duration (Longest)":
        filtered_recent_calls = sorted(filtered_recent_calls, key=lambda x: x["duration"], reverse=True)
    elif history_sort_by == "Duration (Shortest)":
        filtered_recent_calls = sorted(filtered_recent_calls, key=lambda x: x["duration"])
    
    # Create dataframe for display
    if filtered_recent_calls:
        df = pd.DataFrame(filtered_recent_calls)
        
        # Create a copy without the AI actions to display
        display_df = df.copy()
        display_df["start_time"] = display_df["start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        if "end_time" in display_df.columns:
            display_df["end_time"] = display_df["end_time"].astype(str).replace('NaT', '')
        display_df["duration"] = display_df["duration"].apply(lambda x: f"{x // 60}m {x % 60}s")
        
        # Drop the AI actions column before display
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
        
        # Create dataframe with clickable Call IDs
        def handle_row_click(row):
            st.session_state.selected_call_id = row["id"]
            st.experimental_rerun()
        
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
                    st.rerun()
                    
        with col6:
            # Random call button for demo purposes
            if st.button("Random Call", help="View a random call for demonstration"):
                if filtered_recent_calls:
                    random_idx = random.randint(0, len(filtered_recent_calls) - 1)
                    st.session_state.selected_call_id = filtered_recent_calls[random_idx]["id"]
                    st.rerun()
        
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
            
            st.markdown(f"""
            <div class="call-card {card_class}">
                <div class="call-header">
                    {selected_call["id"]} <span class="call-status {status_class}">● {selected_call["status"].upper()}</span>
                </div>
                <div class="call-info">
                    <strong>Phone:</strong> {selected_call["phone"]}<br>
                    <strong>Service:</strong> {selected_call["service"]}<br>
                    <strong>Started:</strong> {selected_call["start_time"].strftime("%Y-%m-%d %H:%M:%S")}<br>
                    <strong>Duration:</strong> {selected_call["duration"] // 60}m {selected_call["duration"] % 60}s<br>
                    <strong>Agent ID:</strong> {selected_call["agent_id"]}<br>
                    <strong>Success Rate:</strong> {selected_call["success_rate"]:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Basic call information
            st.markdown("#### Call Summary")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Duration", f"{selected_call['duration'] // 60}m {selected_call['duration'] % 60}s")
            with col_b:
                st.metric("Success Rate", f"{selected_call['success_rate']:.1f}%")
            with col_c:
                st.metric("AI Actions", len(selected_call['ai_actions']))
        
        # Tabs for call details
        action_tab, transcript_tab = st.tabs(["AI Actions", "Call Transcript"])
        
        with action_tab:
            st.markdown("#### Browser Automation Steps")
            st.markdown("Powered by **browser-use** - [github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)")
            
            # Display all actions
            for i, action in enumerate(selected_call['ai_actions']):
                success_class = "ai-action-success" if action["success"] else "ai-action-fail"
                success_text = "✅ Success" if action["success"] else "❌ Failed"
                
                st.markdown(f"""
                <div class="ai-action-card {success_class}">
                    <div class="ai-action-title">
                        {i+1}. {action["action"]} - {success_text} ({action["duration"]}s)
                    </div>
                    <div class="ai-action-details">
                        {action["timestamp"].strftime("%H:%M:%S")} - {action["details"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show screenshot - use expander to save space
                with st.expander("Show screenshot"):
                    st.image(action["screenshot"], use_column_width=True)
        
        with transcript_tab:
            st.markdown("#### Call Transcript")
            # Generate a sample transcript based on the service
            st.markdown("""
            **System**: Hello, welcome to SpeakWise. How can I help you today?  
            **User**: I need help with getting a business registration certificate.  
            **System**: I'd be happy to help you apply for a business registration certificate. Can you tell me the name of your business?  
            **User**: Yes, it's called 'Akagera Tours and Travel'.  
            **System**: Thank you. And what type of business is Akagera Tours and Travel?  
            **User**: It's a tour company.  
            **System**: Great. I'll need a few more details to complete your application. What's your full name as the business owner?
            **User**: My name is Jean-Claude Mutabazi.
            **System**: Thank you, Jean-Claude. Could you provide your national ID number?
            **User**: Yes, it's 1198780012345678.
            **System**: Perfect. Now I need your business address.
            **User**: It's KN 5 Ave, Kigali, Rwanda.
            **System**: Thank you. I'm now going to process this information and complete your business registration application. This will take a few minutes.
            [Processing...]
            **System**: I've successfully completed your business registration. Your application reference number is BR-2023-78901. You'll receive the official certificate via SMS within 3 business days. Is there anything else you need help with?
            **User**: No, that's all. Thank you!
            **System**: You're welcome! Thank you for using SpeakWise. Have a great day!
            """)
        
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
                st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
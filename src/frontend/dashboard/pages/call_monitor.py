import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 📞 Call Monitor")
st.markdown("Real-time monitoring and management of active and recent calls")

# Generate sample data for active and recent calls
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
        
        active_calls.append({
            "id": f"CALL-{random.randint(1000, 9999)}",
            "phone": f"+25078{random.randint(1000000, 9999999)}",
            "service": service,
            "start_time": start_time,
            "duration": duration,
            "status": "Active",
            "current_step": step,
            "total_steps": total_steps,
            "agent_id": f"AGT-{random.randint(100, 999)}"
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
        
        recent_calls.append({
            "id": f"CALL-{random.randint(1000, 9999)}",
            "phone": f"+25078{random.randint(1000000, 9999999)}",
            "service": service,
            "start_time": start_time,
            "end_time": end_time if status != "Active" else None,
            "duration": duration,
            "status": status,
            "completion": completion,
            "agent_id": f"AGT-{random.randint(100, 999)}"
        })
    
    return active_calls, recent_calls

active_calls, recent_calls = generate_call_data()

# Tabs for different views
tab1, tab2 = st.tabs(["Active Calls", "Call History"])

# Active Calls Tab
with tab1:
    # Controls row
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### Active Calls ({len(active_calls)})")
    
    with col2:
        service_filter = st.selectbox(
            "Filter by service",
            ["All Services"] + list(set([call["service"] for call in active_calls])),
            key="active_service_filter"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Duration (Longest)", "Duration (Shortest)"],
            key="active_sort"
        )
    
    # Apply filters
    filtered_active_calls = active_calls
    if service_filter != "All Services":
        filtered_active_calls = [call for call in active_calls if call["service"] == service_filter]
    
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
                    st.session_state.selected_call = call["id"]
    
    # Refresh controls
    col1, col2 = st.columns([3, 1])
    with col2:
        st.button("Refresh Data", key="refresh_active")

# Call History Tab
with tab2:
    # Controls row
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("### Call History")
    
    with col2:
        history_service_filter = st.selectbox(
            "Filter by service",
            ["All Services"] + list(set([call["service"] for call in recent_calls])),
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
    filtered_recent_calls = recent_calls
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
        df["start_time"] = df["start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        if "end_time" in df.columns:
            # Handle NaT values properly
            df["end_time"] = df["end_time"].astype(str).replace('NaT', '')
        df["duration"] = df["duration"].apply(lambda x: f"{x // 60}m {x % 60}s")
        
        # Format for display
        display_cols = ["id", "phone", "service", "start_time", "duration", "status"]
        st.dataframe(
            df[display_cols],
            column_config={
                "id": "Call ID",
                "phone": "Phone Number",
                "service": "Service",
                "start_time": "Start Time",
                "duration": "Duration",
                "status": "Status"
            },
            use_container_width=True
        )
    else:
        st.info("No calls match your filters")
    
    # Call details section
    st.markdown("### Call Details")
    
    selected_call_id = st.selectbox(
        "Select a call to view details",
        [call["id"] for call in recent_calls],
        index=0 if recent_calls else None
    )
    
    if selected_call_id:
        # Find the selected call
        selected_call = next((call for call in recent_calls if call["id"] == selected_call_id), None)
        
        if selected_call:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                status_class = "status-completed" if selected_call["status"] == "Completed" else "status-failed" if selected_call["status"] == "Failed" else "status-active"
                card_class = "completed-call" if selected_call["status"] == "Completed" else "failed-call" if selected_call["status"] == "Failed" else "active-call"
                
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
                        <strong>Agent:</strong> {selected_call["agent_id"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Timeline visualization
                st.markdown("#### Call Timeline")
                
                # Generate random timeline data for the selected call
                timeline_data = []
                
                # Start of call
                timeline_data.append({
                    "time": selected_call["start_time"],
                    "event": "Call Started",
                    "details": f"Incoming call from {selected_call['phone']}"
                })
                
                # Service selection
                service_time = selected_call["start_time"] + timedelta(seconds=random.randint(5, 20))
                timeline_data.append({
                    "time": service_time,
                    "event": "Service Selected",
                    "details": f"User selected {selected_call['service']}"
                })
                
                # Form filling steps
                num_steps = random.randint(3, 5)
                last_time = service_time
                
                for i in range(num_steps):
                    step_time = last_time + timedelta(seconds=random.randint(30, 90))
                    last_time = step_time
                    
                    if step_time < selected_call["start_time"] + timedelta(seconds=selected_call["duration"]):
                        timeline_data.append({
                            "time": step_time,
                            "event": f"Step {i+1} Completed",
                            "details": random.choice([
                                "User information collected",
                                "Form section completed",
                                "Document verification completed",
                                "Payment information collected",
                                "Service options selected"
                            ])
                        })
                
                # End of call (if applicable)
                if selected_call["status"] != "Active" and "end_time" in selected_call:
                    timeline_data.append({
                        "time": selected_call["end_time"],
                        "event": "Call Ended",
                        "details": "Success" if selected_call["status"] == "Completed" else "Failed due to error"
                    })
                
                # Sort by time
                timeline_data = sorted(timeline_data, key=lambda x: x["time"])
                
                # Display timeline
                for i, event in enumerate(timeline_data):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown(f"**{event['time'].strftime('%H:%M:%S')}**")
                    
                    with col2:
                        st.markdown(f"**{event['event']}**  \n{event['details']}")
                    
                    if i < len(timeline_data) - 1:
                        st.markdown("---")
                
                # Call transcript (placeholder)
                st.markdown("#### Transcript Sample")
                st.markdown("""
                **System**: Hello, welcome to SpeakWise. How can I help you today?  
                **User**: I need help with getting a business registration certificate.  
                **System**: I'd be happy to help you apply for a business registration certificate. Can you tell me the name of your business?  
                **User**: Yes, it's called 'Akagera Tours and Travel'.  
                **System**: Thank you. And what type of business is Akagera Tours and Travel?  
                **User**: It's a tour company.  
                **System**: Great. I'll need a few more details to complete your application...
                """)

# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="SpeakWise Dashboard",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #546E7A;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #546E7A;
    }
    .success-metric {
        color: #4CAF50;
    }
    .warning-metric {
        color: #FF9800;
    }
    .error-metric {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=SpeakWise", width=200)
    st.markdown("### System Controls")
    
    # Date filter
    st.subheader("Date Range")
    date_option = st.selectbox(
        "Select period",
        ["Today", "Last 7 days", "Last 30 days", "Custom"]
    )
    
    if date_option == "Custom":
        start_date = st.date_input("Start date", datetime.now() - timedelta(days=7))
        end_date = st.date_input("End date", datetime.now())
    
    # Service filter
    st.subheader("Services")
    services = ["All Services", "Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]
    selected_services = st.multiselect("Select services", services, default="All Services")
    
    # Status filter
    st.subheader("Call Status")
    statuses = ["All", "Completed", "In Progress", "Failed"]
    selected_status = st.multiselect("Select status", statuses, default="All")
    
    # Refresh rate
    st.subheader("Dashboard Settings")
    refresh_rate = st.slider("Refresh rate (seconds)", 5, 60, 30)
    
    # Control buttons
    st.button("Refresh Data")
    
    st.markdown("---")
    st.markdown("### Admin Actions")
    if st.button("View System Logs"):
        st.session_state.show_logs = True

# Header
st.markdown('<p class="main-header">SpeakWise Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time monitoring and analytics of the voice assistant system</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Call Analytics", "Service Performance", "System Status"])

# Generate sample data
def generate_sample_data(days=30, calls_per_day=50):
    data = []
    services = ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]
    statuses = ["Completed", "In Progress", "Failed"]
    status_weights = [0.7, 0.2, 0.1]
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        n_calls = random.randint(calls_per_day - 20, calls_per_day + 20)
        
        for j in range(n_calls):
            service = random.choice(services)
            status = random.choices(statuses, status_weights)[0]
            duration = random.randint(60, 900) if status != "Failed" else random.randint(10, 120)
            steps_completed = random.randint(0, 5)
            
            # Generate a random time during business hours
            hour = random.randint(8, 17)
            minute = random.randint(0, 59)
            timestamp = date.replace(hour=hour, minute=minute)
            
            data.append({
                "timestamp": timestamp,
                "service": service,
                "status": status,
                "duration": duration,
                "steps_completed": steps_completed,
                "user_satisfaction": random.randint(1, 5) if status == "Completed" else None
            })
    
    return pd.DataFrame(data)

df = generate_sample_data()

# Overview tab
with tab1:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{len(df[df["timestamp"].dt.date == datetime.now().date()])}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Calls Today</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        completion_rate = len(df[df["status"] == "Completed"]) / len(df) * 100
        color_class = "success-metric" if completion_rate > 75 else "warning-metric" if completion_rate > 50 else "error-metric"
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value {color_class}">{completion_rate:.1f}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Completion Rate</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        active_calls = len(df[df["status"] == "In Progress"])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{active_calls}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Active Calls</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        avg_duration = df[df["status"] == "Completed"]["duration"].mean() / 60
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{avg_duration:.1f} min</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Avg. Call Duration</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Call Volume Trend")
    # Prepare data for chart
    daily_counts = df.groupby(df["timestamp"].dt.date).size().reset_index(name="count")
    daily_counts.columns = ["date", "count"]
    
    # Create line chart
    fig = px.line(
        daily_counts, 
        x="date", 
        y="count",
        labels={"count": "Number of Calls", "date": "Date"},
        markers=True
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Active calls
    st.markdown("### Active Calls")
    if active_calls > 0:
        # In a real implementation, this would pull actual active call data
        active_df = df[df["status"] == "In Progress"].sample(min(active_calls, 5))
        
        for i, row in active_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Service:** {row['service']}")
                st.markdown(f"**Started:** {row['timestamp'].strftime('%H:%M:%S')}")
                st.markdown(f"**Current step:** {row['steps_completed']} of 5")
                st.progress(row['steps_completed'] / 5)
            with col2:
                st.markdown(f"**Duration:** {row['duration'] // 60}m {row['duration'] % 60}s")
                if st.button("View Details", key=f"view_{i}"):
                    st.session_state.view_call = i
    else:
        st.info("No active calls at the moment.")

# Call Analytics tab
with tab2:
    st.markdown("### Call Distribution by Status")
    
    # Prepare data
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    
    # Create pie chart
    fig = px.pie(
        status_counts, 
        values="count", 
        names="status",
        color="status",
        color_discrete_map={
            "Completed": "#4CAF50",
            "In Progress": "#2196F3",
            "Failed": "#F44336"
        },
        hole=0.4
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Hourly Distribution")
        hourly_counts = df.groupby(df["timestamp"].dt.hour).size().reset_index(name="count")
        hourly_counts.columns = ["hour", "count"]
        
        fig = px.bar(
            hourly_counts,
            x="hour",
            y="count",
            labels={"count": "Number of Calls", "hour": "Hour of Day"},
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### Duration Distribution")
        
        # Create histogram for call duration
        fig = px.histogram(
            df[df["status"] == "Completed"],
            x="duration",
            nbins=20,
            labels={"duration": "Call Duration (seconds)"},
            color_discrete_sequence=["#1E88E5"]
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recent calls table
    st.markdown("### Recent Calls")
    recent_calls = df.sort_values("timestamp", ascending=False).head(10)
    # Format for display
    display_df = recent_calls.copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["duration"] = display_df["duration"].apply(lambda x: f"{x//60}m {x%60}s")
    
    # Use a custom formatter to color the status column
    def highlight_status(val):
        if val == "Completed":
            return "background-color: #E8F5E9; color: #2E7D32"
        elif val == "In Progress":
            return "background-color: #E3F2FD; color: #1565C0"
        else:
            return "background-color: #FFEBEE; color: #C62828"
    
    st.dataframe(
        display_df[["timestamp", "service", "status", "duration", "steps_completed"]],
        column_config={
            "timestamp": "Time",
            "service": "Service",
            "status": "Status",
            "duration": "Duration",
            "steps_completed": "Steps"
        },
        use_container_width=True
    )

# Service Performance tab
with tab3:
    st.markdown("### Service Comparison")
    
    # Service counts
    service_counts = df.groupby("service")["status"].value_counts().unstack().fillna(0)
    service_counts["total"] = service_counts.sum(axis=1)
    service_counts["completion_rate"] = service_counts["Completed"] / service_counts["total"] * 100
    
    # Sort by most used
    service_counts = service_counts.sort_values("total", ascending=False)
    
    # Create bar chart
    fig = go.Figure()
    
    for status in ["Completed", "In Progress", "Failed"]:
        if status in service_counts.columns:
            fig.add_trace(go.Bar(
                x=service_counts.index,
                y=service_counts[status],
                name=status,
                marker_color="#4CAF50" if status == "Completed" else "#2196F3" if status == "In Progress" else "#F44336"
            ))
    
    fig.update_layout(
        barmode="stack",
        xaxis={"title": "Service"},
        yaxis={"title": "Number of Calls"},
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Service completion rates
    st.markdown("### Service Completion Rates")
    
    fig = px.bar(
        service_counts.reset_index(),
        x="service",
        y="completion_rate",
        labels={"completion_rate": "Completion Rate (%)", "service": "Service"},
        color="completion_rate",
        color_continuous_scale=["#F44336", "#FFEB3B", "#4CAF50"],
        range_color=[0, 100]
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Service details
    st.markdown("### Service Details")
    selected_service = st.selectbox("Select service for detailed view", df["service"].unique())
    
    service_df = df[df["service"] == selected_service]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        success_rate = len(service_df[service_df["status"] == "Completed"]) / len(service_df) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col2:
        avg_duration = service_df[service_df["status"] == "Completed"]["duration"].mean() / 60
        st.metric("Avg. Duration", f"{avg_duration:.1f} min")
    
    with col3:
        if "user_satisfaction" in service_df:
            avg_satisfaction = service_df["user_satisfaction"].mean()
            st.metric("User Satisfaction", f"{avg_satisfaction:.1f}/5")
    
    # Daily trend for the selected service
    daily_service = service_df.groupby(service_df["timestamp"].dt.date).size().reset_index(name="count")
    daily_service.columns = ["date", "count"]
    
    fig = px.line(
        daily_service,
        x="date",
        y="count",
        labels={"count": "Number of Calls", "date": "Date"},
        markers=True
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# System Status tab
with tab4:
    st.markdown("### System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        system_uptime = random.randint(95, 100)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        color_class = "success-metric" if system_uptime > 98 else "warning-metric" if system_uptime > 95 else "error-metric"
        st.markdown(f'<p class="metric-value {color_class}">{system_uptime}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">System Uptime</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        speech_accuracy = random.randint(80, 95)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        color_class = "success-metric" if speech_accuracy > 90 else "warning-metric" if speech_accuracy > 80 else "error-metric"
        st.markdown(f'<p class="metric-value {color_class}">{speech_accuracy}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Speech Recognition Accuracy</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        browser_success = random.randint(85, 98)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        color_class = "success-metric" if browser_success > 95 else "warning-metric" if browser_success > 85 else "error-metric"
        st.markdown(f'<p class="metric-value {color_class}">{browser_success}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Browser Agent Success Rate</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Service status
    st.markdown("### Service Status")
    
    service_status = pd.DataFrame({
        "service": ["Speech-to-Text", "LLM Service", "Text-to-Speech", "Browser Agent", "WhatsApp Delivery", "Database"],
        "status": ["Online", "Online", "Online", "Online", "Online", "Online"],
        "latency": [120, 350, 90, 180, 220, 30]
    })
    
    # Randomly introduce some degraded performance
    degraded_idx = random.randint(0, len(service_status) - 1)
    service_status.at[degraded_idx, "status"] = "Degraded"
    service_status.at[degraded_idx, "latency"] = service_status.at[degraded_idx, "latency"] * 2
    
    # Create a visualization
    fig = px.bar(
        service_status,
        x="service",
        y="latency",
        color="status",
        labels={"latency": "Latency (ms)", "service": "Service Component"},
        color_discrete_map={
            "Online": "#4CAF50", 
            "Degraded": "#FF9800",
            "Offline": "#F44336"
        }
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Error logs
    st.markdown("### Recent Error Logs")
    
    if random.random() < 0.7:  # 70% chance to show some errors
        log_entries = [
            {"timestamp": "2023-10-29 15:43:22", "level": "ERROR", "component": "Browser Agent", "message": "Timeout waiting for form element to appear"},
            {"timestamp": "2023-10-29 14:12:05", "level": "WARNING", "component": "Speech Processor", "message": "Low confidence in speech recognition result"},
            {"timestamp": "2023-10-29 10:37:18", "level": "ERROR", "component": "LLM Service", "message": "API rate limit reached, retrying after backoff"},
            {"timestamp": "2023-10-28 18:22:41", "level": "WARNING", "component": "WhatsApp Sender", "message": "Message delivery delayed due to network issues"}
        ]
        log_df = pd.DataFrame(log_entries)
        
        # Use a custom formatter for the level column
        st.dataframe(
            log_df,
            column_config={
                "timestamp": "Time",
                "level": "Level",
                "component": "Component",
                "message": "Message"
            },
            use_container_width=True
        )
    else:
        st.success("No errors recorded in the last 24 hours")
    
    # System resources
    st.markdown("### System Resources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cpu_usage = random.randint(30, 80)
        st.markdown("#### CPU Usage")
        st.progress(cpu_usage / 100)
        st.text(f"{cpu_usage}%")
        
    with col2:
        memory_usage = random.randint(40, 90)
        st.markdown("#### Memory Usage")
        st.progress(memory_usage / 100)
        st.text(f"{memory_usage}%")

# Footer
st.markdown("---")
st.markdown("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.markdown("© 2023 SpeakWise")
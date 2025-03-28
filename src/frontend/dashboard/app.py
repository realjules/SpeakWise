import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="Home | SpeakWise",  # Changed to Home
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
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1rem;
        color: #546E7A;
        font-weight: 500;
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

# Sidebar - Simplified
with st.sidebar:
    # Use a custom SVG logo
    logo_path = "static/images/logo.svg"
    
    try:
        # Try to load the logo
        st.image(logo_path, width=200)
    except Exception:
        # Fallback to text if image loading fails
        st.markdown(f'<h1 style="color: #584053;">SpeakWise</h1>', unsafe_allow_html=True)
        
    st.markdown('<h3 style="color: #584053; margin-top: 2rem;">Date Filter</h3>', unsafe_allow_html=True)
    
    # Date filter
    date_option = st.selectbox(
        "Select period",
        ["Today", "Last 7 days", "Last 30 days", "Custom"]
    )
    
    if date_option == "Custom":
        start_date = st.date_input("Start date", datetime.now() - timedelta(days=7))
        end_date = st.date_input("End date", datetime.now())
    
    # Status filter
    st.markdown('<h3 style="color: #584053; margin-top: 2rem;">Call Status</h3>', unsafe_allow_html=True)
    statuses = ["All", "Completed", "In Progress", "Failed"]
    selected_status = st.multiselect("Select status", statuses, default="All")
    
    # Simple refresh button
    st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    st.button("Refresh Data")

# Header
st.markdown('<p class="main-header">SpeakWise Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time monitoring and analytics of the voice assistant system</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["Overview", "Call Analytics"])

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
        calls_today = len(df[df["timestamp"].dt.date == datetime.now().date()])
        st.metric("Calls Today", calls_today)
    
    with col2:
        completion_rate = len(df[df["status"] == "Completed"]) / len(df) * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        active_calls = len(df[df["status"] == "In Progress"])
        st.metric("Active Calls", active_calls)
    
    with col4:
        avg_duration = df[df["status"] == "Completed"]["duration"].mean() / 60
        st.metric("Avg. Call Duration", f"{avg_duration:.1f} min")
    
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
    

# Call Analytics tab
with tab2:
    st.markdown("### Call Analytics")
    
    # Calculate summary metrics
    total_calls = len(df)
    completed_calls = len(df[df["status"] == "Completed"])
    failed_calls = len(df[df["status"] == "Failed"])
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Calls", f"{total_calls}")
    with col2:
        st.metric("Completed Calls", f"{completed_calls}", 
                 delta=f"{completed_calls/total_calls*100:.1f}%" if total_calls > 0 else "0%")
    with col3:
        st.metric("Failed Calls", f"{failed_calls}",
                 delta=f"{failed_calls/total_calls*100:.1f}%" if total_calls > 0 else "0%")
    
    # Create two larger charts side by side
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
            color_discrete_sequence=["#1E88E5"]
        )
        fig.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=2
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### Duration Distribution")
        
        # Create histogram for call duration
        fig = px.histogram(
            df[df["status"] == "Completed"],
            x="duration",
            nbins=20,
            labels={"duration": "Call Duration (seconds)", "count": "Number of Calls"},
            color_discrete_sequence=["#1E88E5"]
        )
        fig.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis_title="Number of Calls"
        )
        st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown("---")
st.markdown("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.markdown("© 2025 SpeakWise")
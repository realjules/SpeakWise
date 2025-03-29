import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json

# Import websocket utility only
from utils import get_ws_manager, initialize_ws_connection

st.set_page_config(
    page_title="Dashboard | SpeakWise",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
    /* Color scheme based on COLORS.jpg */
    :root {
        --deep-purple: #584053;
        --teal: #8DC6BF;
        --yellow-orange: #FCBC66;
        --coral: #F97B4F;
    }
    
    /* Main heading styling */
    h1 {
        color: var(--deep-purple);
    }
    
    h2 {
        color: var(--deep-purple);
        border-bottom: 2px solid var(--teal);
        padding-bottom: 8px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        width: 100%;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
        padding-left: 0.4rem;
    }
    /* Style Home item (highlighted when active) */
    section[data-testid="stSidebarNav"] div[data-testid="stSidebarNavItems"] > div:first-child {
        background-color: rgba(141, 198, 191, 0.2);
        border-right: 4px solid var(--teal);
        font-weight: bold;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
        border-top: 4px solid var(--teal);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
        color: var(--deep-purple);
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
    }
    
    .metric-trend {
        font-size: 12px;
        margin-top: 5px;
    }
    
    .metric-trend-up {
        color: var(--teal);
    }
    
    .metric-trend-down {
        color: var(--coral);
    }
    
    /* Status pill */
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .status-active {
        background-color: rgba(141, 198, 191, 0.2);
        color: var(--teal);
    }
    
    .status-completed {
        background-color: rgba(252, 188, 102, 0.2);
        color: var(--yellow-orange);
    }
    
    .status-failed {
        background-color: rgba(249, 123, 79, 0.2);
        color: var(--coral);
    }
    
    /* Footer styling */
    footer {
        color: var(--deep-purple);
    }
</style>
""", unsafe_allow_html=True)

# Direct reading from JSON database files
import os
import json

# Define path to JSON files
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
ANALYTICS_FILE = os.path.join(DATA_DIR, 'analytics.json')
CALLS_FILE = os.path.join(DATA_DIR, 'calls.json')

# Load data directly from JSON files
def load_json_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading data from {file_path}: {str(e)}")
        return {}

# Load analytics data
analytics_data = load_json_data(ANALYTICS_FILE)

# Initialize connection for WebSocket (for active calls)
initialize_ws_connection()

# Register for WebSocket updates
if "ws_dashboard_callbacks_registered" not in st.session_state:
    def on_system_status(message):
        # Update system status data
        st.session_state.system_status = message.get("status", {})
    
    # Get WebSocket manager
    ws_manager = get_ws_manager()
    ws_manager.register_callback("system.status", on_system_status)
    
    st.session_state.ws_dashboard_callbacks_registered = True

# Header
st.markdown("# SpeakWise Dashboard")
st.markdown("Welcome to the SpeakWise control center. Monitor call performance and track service usage.")

# Call Operations Statistics
st.markdown("## Call Operations Statistics")

# Get call and SMS stats directly from loaded data
call_stats = analytics_data.get("call_stats", {})
sms_stats = analytics_data.get("sms_stats", {})

# System status from WebSocket (or default values if not available)
if "system_status" not in st.session_state:
    st.session_state.system_status = {
        "active_calls": call_stats.get("active_calls", 0),
        "uptime": random.randint(86400, 604800)  # 1-7 days in seconds
    }

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Active calls metric
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Active Calls</div>
        <div class="metric-value">{}</div>
        <div class="metric-trend">
            <span class="status-pill status-active">● ACTIVE</span>
        </div>
    </div>
    """.format(st.session_state.system_status.get("active_calls", 0)), unsafe_allow_html=True)

with col2:
    # Call success rate
    success_rate = call_stats.get("success_rate", 0)
    trend_class = "metric-trend-up" if success_rate >= 95 else "metric-trend-down"
    
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Call Success Rate</div>
        <div class="metric-value">{:.1f}%</div>
        <div class="metric-trend {}">
            {} Target: 95%
        </div>
    </div>
    """.format(
        success_rate, 
        trend_class,
        "✓" if success_rate >= 95 else "✗"
    ), unsafe_allow_html=True)

with col3:
    # Average call duration
    avg_duration = call_stats.get("avg_duration_seconds", 0)
    minutes = avg_duration // 60
    seconds = avg_duration % 60
    
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Avg Call Duration</div>
        <div class="metric-value">{:d}m {:02d}s</div>
        <div class="metric-trend">
            Last 30 days
        </div>
    </div>
    """.format(minutes, seconds), unsafe_allow_html=True)

with col4:
    # Total calls metric
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Total Calls</div>
        <div class="metric-value">{:,}</div>
        <div class="metric-trend">
            All time
        </div>
    </div>
    """.format(call_stats.get("total_calls", 0)), unsafe_allow_html=True)

# Call volume trends
st.markdown("## Call & SMS Volume Trends")

# Get daily call and SMS data directly from loaded data
daily_calls = analytics_data.get("daily_calls", [])[-30:] # Last 30 days
daily_sms = analytics_data.get("daily_sms", [])[-30:] # Last 30 days

# Create DataFrames
df_calls = pd.DataFrame(daily_calls)
df_calls["date"] = pd.to_datetime(df_calls["date"])

df_sms = pd.DataFrame(daily_sms)
df_sms["date"] = pd.to_datetime(df_sms["date"])

# Plotting
fig = go.Figure()

# Call volume trace
fig.add_trace(go.Scatter(
    x=df_calls["date"],
    y=df_calls["count"],
    name="Calls",
    mode="lines",
    line=dict(width=3, color="#584053")  # Deep purple from COLORS.jpg
))

# SMS volume trace
fig.add_trace(go.Scatter(
    x=df_sms["date"],
    y=df_sms["sent"],
    name="SMS",
    mode="lines",
    line=dict(width=3, color="#8DC6BF")  # Teal from COLORS.jpg
))

# Update layout
fig.update_layout(
    title={
        "text": "Daily Volume (Last 30 Days)",
        "font": {"color": "#584053"}  # Deep purple from COLORS.jpg
    },
    xaxis_title="Date",
    yaxis_title="Count",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=20, r=20, t=60, b=20),
    height=400,
    paper_bgcolor="white",
    plot_bgcolor="rgba(141, 198, 191, 0.05)",  # Very light teal background
    font=dict(
        color="#584053"  # Deep purple for all text
    )
)

st.plotly_chart(fig, use_container_width=True)


# Footer
st.markdown('<hr style="border-top: 2px solid #8DC6BF;">', unsafe_allow_html=True)
st.markdown('<p style="color: #584053; text-align: center;">© 2023 SpeakWise | Dashboard v1.0 | Last updated: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</p>', unsafe_allow_html=True)
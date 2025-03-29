import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import time
import requests
import sys
import os

# Import utility functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_api_client, get_analytics_manager
from twilio.rest import Client

st.set_page_config(
    page_title="SMS Tracking | SpeakWise",
    page_icon="📱",
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
    /* Style SMS Tracking item (highlighted when active) */
    section[data-testid="stSidebarNav"] div[data-testid="stSidebarNavItems"] > div:nth-child(5) {
        background-color: rgba(141, 198, 191, 0.2);
        border-right: 4px solid #8DC6BF;
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
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        margin: 10px 0;
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
        color: #4CAF50;
    }
    
    .metric-trend-down {
        color: #F44336;
    }
    
    /* Table styling */
    .highlight-row {
        background-color: #f0f9ff;
    }
    
    /* Status pill */
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .status-delivered {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    
    .status-failed {
        background-color: #FFEBEE;
        color: #C62828;
    }
    
    .status-pending {
        background-color: #FFF8E1;
        color: #F57F17;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API client and analytics manager
api_client = get_api_client()
analytics_manager = get_analytics_manager()

# Header
st.markdown("# 📱 SMS Tracking")
st.markdown("Track and manage SMS notifications sent through the SpeakWise platform")

# Get SMS statistics and data (still needed for filters)
sms_stats = analytics_manager.get_sms_stats()
daily_sms = analytics_manager.get_daily_sms(30)

# SMS Records section
st.markdown("## SMS Records")

# Get SMS records first
sms_records = analytics_manager.get_sms_records(100)

# Display test record information
test_records = [r for r in sms_records if "TEST-SMS" in str(r.get('id', ''))]
if test_records:
    st.success(f"Found {len(test_records)} test SMS records in the system!")
    for r in test_records:
        st.info(f"Test SMS ID: {r.get('id')} to {r.get('recipient')} - Status: {r.get('status')}")

# Filters
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1, 1, 1, 1])

with filter_col1:
    # Get all unique services from SMS records to ensure we include all possible services
    all_services = set()
    for record in sms_records:
        if "service" in record and record["service"]:
            all_services.add(record["service"])
    
    service_filter = st.selectbox(
        "Filter by Service",
        ["All Services"] + sorted(list(all_services))
    )

with filter_col2:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All Statuses", "Delivered", "Failed"]
    )

with filter_col3:
    # Get all unique SMS types from records
    all_types = set()
    for record in sms_records:
        if "type" in record and record["type"]:
            # Format types for display (convert snake_case to Title Case)
            display_type = " ".join(word.capitalize() for word in record["type"].split("_"))
            all_types.add(display_type)
    
    type_filter = st.selectbox(
        "Filter by Type",
        ["All Types"] + sorted(list(all_types))
    )

with filter_col4:
    date_range = st.date_input(
        "Date Range",
        value=[datetime.now() - timedelta(days=30), datetime.now()],
        max_value=datetime.now()
    )

# Apply filters
filtered_records = sms_records

# Service filter
if service_filter != "All Services":
    filtered_records = [r for r in filtered_records if r["service"] == service_filter]

# Status filter
if status_filter != "All Statuses":
    status_value = status_filter.lower()
    filtered_records = [r for r in filtered_records if r["status"] == status_value]

# Type filter
if type_filter != "All Types":
    # Convert selected type to both formats for flexible matching
    type_value_snake = type_filter.lower().replace(" ", "_")
    type_value_display = type_filter
    
    # Match against either format
    filtered_records = [r for r in filtered_records if 
                       r.get("type") == type_value_snake or
                       # Also check if it matches the display format directly
                       " ".join(word.capitalize() for word in r.get("type", "").split("_")) == type_value_display]

# Date range filter
if len(date_range) == 2:
    start_date, end_date = date_range
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())
    
    date_filtered_records = []
    for r in filtered_records:
        try:
            timestamp = r.get("timestamp", "")
            if not timestamp:
                # If no timestamp, include the record
                date_filtered_records.append(r)
                continue
                
            # Handle different timestamp formats
            if isinstance(timestamp, str):
                # Strip microseconds if they cause issues
                if '.' in timestamp and not timestamp[-1].isdigit():
                    parts = timestamp.split('.')
                    timestamp = parts[0] + '.' + parts[1].rstrip('Z') + ('Z' if timestamp.endswith('Z') else '')
                
                # Remove timezone indicator for comparison
                if 'Z' in timestamp:
                    record_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).replace(tzinfo=None)
                elif '+' in timestamp:
                    record_time = datetime.fromisoformat(timestamp).replace(tzinfo=None)
                else:
                    record_time = datetime.fromisoformat(timestamp)
                
                if start_date <= record_time <= end_date:
                    date_filtered_records.append(r)
            else:
                # If timestamp is not a string, include the record
                date_filtered_records.append(r)
                
        except Exception as e:
            # If there's an error parsing the date, include the record
            st.warning(f"Error parsing date for record {r.get('id', '')}: {str(e)}")
            date_filtered_records.append(r)
    
    filtered_records = date_filtered_records

# Convert to DataFrame for display
if filtered_records:
    df_records = pd.DataFrame(filtered_records)
    
    # Format timestamp safely
    def format_timestamp(timestamp):
        try:
            if isinstance(timestamp, str):
                if 'Z' in timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif '+' in timestamp:
                    dt = datetime.fromisoformat(timestamp)
                else:
                    dt = datetime.fromisoformat(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return str(timestamp)
        except Exception as e:
            st.warning(f"Error formatting timestamp: {timestamp} - {str(e)}")
            return str(timestamp)

    df_records["formatted_time"] = df_records["timestamp"].apply(format_timestamp)
    
    # Format type safely
    def format_type(type_value):
        try:
            if isinstance(type_value, str):
                return " ".join(word.capitalize() for word in type_value.split("_"))
            return str(type_value)
        except Exception:
            return str(type_value)
            
    # Only format the type if the column exists
    if "type" in df_records.columns:
        df_records["formatted_type"] = df_records["type"].apply(format_type)
    else:
        df_records["formatted_type"] = "Unknown"
    
    # Format status with color pill safely
    def format_status(status):
        try:
            if isinstance(status, str):
                return f'<span class="status-pill status-{status.lower()}">{status.capitalize()}</span>'
            return f'<span class="status-pill status-unknown">{str(status)}</span>'
        except Exception:
            return f'<span class="status-pill status-unknown">Unknown</span>'
            
    # Only format the status if the column exists
    if "status" in df_records.columns:
        df_records["formatted_status"] = df_records["status"].apply(format_status)
    else:
        df_records["formatted_status"] = '<span class="status-pill status-unknown">Unknown</span>'
    
    # Make sure all required columns exist
    for col in ["id", "service", "recipient"]:
        if col not in df_records.columns:
            df_records[col] = "Unknown"
            
    # Select columns for display, handling missing columns
    display_cols = []
    col_order = ["id", "formatted_time", "service", "recipient", "formatted_type", "formatted_status"]
    for col in col_order:
        if col in df_records.columns:
            display_cols.append(col)
    
    # Display the records
    st.dataframe(
        df_records[display_cols],
        column_config={
            "id": "SMS ID",
            "formatted_time": "Timestamp",
            "service": "Service",
            "recipient": "Phone Number",
            "formatted_type": "SMS Type",
            "formatted_status": st.column_config.Column(
                "Status",
                help="Delivery status of the SMS message",
                width="medium"
            )
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Export options
    export_col1, export_col2 = st.columns([1, 5])
    
    with export_col1:
        if st.button("Export Data"):
            st.info("Data export functionality will be implemented in production")
else:
    st.info("No SMS records match the selected filters")

# Add new SMS section
st.markdown("## Send Real SMS")
st.markdown("Use this form to send a real SMS using the Pindo API")

# Form for sending a real SMS
with st.form("send_sms_form"):
    form_col1, form_col2 = st.columns(2)
    
    with form_col1:
        recipient = st.text_input("Recipient Phone Number", value="+250787641302")
        from_number = st.text_input("From Phone Number", 
                                    help="Your Twilio phone number. Leave blank to use the first number from your account.")
        
        # Inputs for Twilio credentials with sensitive flag
        account_sid = st.text_input("Twilio Account SID", type="password", 
                                  help="Your Twilio Account SID. This is required to send real SMS.")
        
        auth_token = st.text_input("Twilio Auth Token", type="password", 
                                 help="Your Twilio Auth Token. This is required to send real SMS.")
        
    with form_col2:
        # Get all available services dynamically
        all_services = set()
        for record in sms_records:
            if "service" in record and record["service"]:
                all_services.add(record["service"])
                
        service = st.selectbox(
            "Service Type",
            ["SpeakWise Test"] + sorted(list(all_services))
        )
        
        # Message text
        message = st.text_area("Message", value=f"Test message from SpeakWise at {datetime.now().strftime('%H:%M:%S')}")
        
        # Message type
        sms_type = st.selectbox(
            "SMS Type",
            ["Test Message", "Task Complete", "Document Ready"]
        )
    
    # Submit button
    submitted = st.form_submit_button("Send Real SMS")
    
    if submitted:
        if not account_sid or not auth_token:
            st.error("Twilio Account SID and Auth Token are required to send real SMS")
        else:
            try:
                # Convert message type to snake_case for database
                db_type = sms_type.lower().replace(" ", "_")
                
                # Log the request for debugging (mask credentials)
                masked_sid = account_sid[:4] + "..." + account_sid[-4:] if len(account_sid) > 8 else "****"
                masked_token = auth_token[:4] + "..." + auth_token[-4:] if len(auth_token) > 8 else "****"
                
                st.info(f"Sending SMS to {recipient} via Twilio" + (f" from {from_number}" if from_number else ""))
                st.code(f"Account SID: {masked_sid}\nAuth Token: {masked_token}", language="text")
                
                # Send the SMS directly using Twilio API
                with st.spinner(f"Sending SMS to {recipient}..."):
                    # Initialize Twilio client
                    client = Client(account_sid, auth_token)
                    
                    # Create message
                    twilio_message = client.messages.create(
                        body=message,
                        from_=from_number if from_number else None,  # Twilio will use first number if None
                        to=recipient
                    )
                    
                    # Prepare result
                    result = {
                        "sid": twilio_message.sid,
                        "status": twilio_message.status,
                        "from": twilio_message.from_,
                        "to": twilio_message.to,
                        "body": twilio_message.body,
                        "date_created": str(twilio_message.date_created)
                    }
                
                # Generate a unique SMS ID based on Twilio's SID
                sms_id = f"SMS-{twilio_message.sid}"
                
                # Show the success message with SMS ID
                st.success(f"✅ SMS sent successfully to {recipient}!")
                st.info(f"SMS ID: {sms_id} | Status: {twilio_message.status}")
                
                # Create and add the SMS record to analytics
                timestamp = datetime.now().isoformat() + "Z"
                new_record = {
                    "id": sms_id,
                    "recipient": recipient,
                    "timestamp": timestamp,
                    "type": db_type,
                    "status": "delivered",
                    "service": service,
                    "reference": twilio_message.sid
                }
                
                # Add the record to analytics
                if analytics_manager.add_sms_record(new_record):
                    st.info("The SMS record has been successfully added to the analytics database.")
                else:
                    st.warning("SMS was sent but could not be added to analytics database.")
                
            except Exception as e:
                st.error(f"Failed to send SMS: {str(e)}")
                
                # Try to add a record anyway to track the attempt
                timestamp = datetime.now().isoformat() + "Z"
                sms_id = f"SMS-FAILED-{int(time.time())}"
                
                new_record = {
                    "id": sms_id,
                    "recipient": recipient,
                    "timestamp": timestamp,
                    "type": sms_type.lower().replace(" ", "_"),
                    "status": "failed",
                    "service": service,
                    "reference": f"ERROR: {str(e)[:50]}"
                }
                
                analytics_manager.add_sms_record(new_record)
                st.warning("A failure record has been added to analytics for tracking.")


# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
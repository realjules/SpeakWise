import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Transaction Log | SpeakWise",
    page_icon="💰",
    layout="wide"
)

# Header
st.markdown("# 💰 Transaction Log")
st.markdown("Track all payment transactions processed through the system")

# Generate sample transaction data
def generate_transactions(n=100):
    services = ["Business Registration", "Marriage Certificate", "Land Transfer", "Passport Application"]
    payment_methods = ["Mobile Money", "Credit Card", "Bank Transfer"]
    statuses = ["Completed", "Failed", "Pending"]
    status_weights = [0.85, 0.1, 0.05]
    
    transactions = []
    for i in range(n):
        service = random.choice(services)
        status = random.choices(statuses, status_weights)[0]
        
        # Determine amount based on service
        if service == "Business Registration":
            amount = random.randint(15000, 25000)
        elif service == "Marriage Certificate":
            amount = random.randint(5000, 10000)
        elif service == "Land Transfer":
            amount = random.randint(50000, 100000)
        else:  # Passport
            amount = random.randint(20000, 30000)
        
        # Generate date within the last 30 days
        days_ago = random.randint(0, 30)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        payment_method = random.choice(payment_methods)
        payment_id = f"PAY-{random.randint(100000, 999999)}"
        user_id = f"+25078{random.randint(1000000, 9999999)}"
        
        transactions.append({
            "transaction_id": f"TXN-{random.randint(10000, 99999)}",
            "service": service,
            "amount": amount,
            "currency": "RWF",
            "status": status,
            "payment_method": payment_method,
            "payment_id": payment_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "call_id": f"CALL-{random.randint(1000, 9999)}"
        })
    
    # Sort by timestamp
    transactions = sorted(transactions, key=lambda x: x["timestamp"], reverse=True)
    return pd.DataFrame(transactions)

# Load data
transactions_df = generate_transactions(150)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    
    # Date range filter
    st.subheader("Date Range")
    date_option = st.selectbox(
        "Select period",
        ["All Time", "Today", "Last 7 days", "Last 30 days", "Custom"]
    )
    
    if date_option == "Custom":
        start_date = st.date_input("Start date", datetime.now() - timedelta(days=7))
        end_date = st.date_input("End date", datetime.now())
    
    # Service filter
    st.subheader("Service")
    service_options = ["All"] + list(transactions_df["service"].unique())
    selected_service = st.selectbox("Select service", service_options)
    
    # Status filter
    st.subheader("Transaction Status")
    status_options = ["All"] + list(transactions_df["status"].unique())
    selected_status = st.selectbox("Select status", status_options)
    
    # Payment method filter
    st.subheader("Payment Method")
    payment_options = ["All"] + list(transactions_df["payment_method"].unique())
    selected_payment = st.selectbox("Select payment method", payment_options)

# Apply filters
filtered_df = transactions_df.copy()

# Date filter
if date_option == "Today":
    filtered_df = filtered_df[filtered_df["timestamp"].dt.date == datetime.now().date()]
elif date_option == "Last 7 days":
    filtered_df = filtered_df[filtered_df["timestamp"] >= datetime.now() - timedelta(days=7)]
elif date_option == "Last 30 days":
    filtered_df = filtered_df[filtered_df["timestamp"] >= datetime.now() - timedelta(days=30)]
elif date_option == "Custom":
    filtered_df = filtered_df[
        (filtered_df["timestamp"].dt.date >= start_date) & 
        (filtered_df["timestamp"].dt.date <= end_date)
    ]

# Service filter
if selected_service != "All":
    filtered_df = filtered_df[filtered_df["service"] == selected_service]

# Status filter
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]

# Payment method filter
if selected_payment != "All":
    filtered_df = filtered_df[filtered_df["payment_method"] == selected_payment]

# Transaction summary metrics
st.subheader("Transaction Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transactions = len(filtered_df)
    st.metric("Total Transactions", total_transactions)

with col2:
    total_amount = filtered_df["amount"].sum()
    st.metric("Total Amount", f"{total_amount:,} RWF")

with col3:
    success_rate = len(filtered_df[filtered_df["status"] == "Completed"]) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    st.metric("Success Rate", f"{success_rate:.1f}%")

with col4:
    avg_amount = filtered_df["amount"].mean() if len(filtered_df) > 0 else 0
    st.metric("Average Amount", f"{avg_amount:,.0f} RWF")

# Transaction visualization
st.subheader("Transaction Trends")

# Prepare data for charts
filtered_df["date"] = filtered_df["timestamp"].dt.date
daily_totals = filtered_df.groupby("date").agg(
    transaction_count=("transaction_id", "count"),
    total_amount=("amount", "sum")
).reset_index()

# Tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Daily Volume", "Service Breakdown", "Payment Methods"])

with tab1:
    # Daily transaction volume and amount
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            daily_totals,
            x="date",
            y="transaction_count",
            title="Daily Transaction Count",
            labels={"date": "Date", "transaction_count": "Number of Transactions"},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            daily_totals,
            x="date",
            y="total_amount",
            title="Daily Transaction Amount",
            labels={"date": "Date", "total_amount": "Total Amount (RWF)"},
            markers=True
        )
        fig.update_layout(yaxis_title="Amount (RWF)")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Service breakdown
    service_breakdown = filtered_df.groupby("service").agg(
        transaction_count=("transaction_id", "count"),
        total_amount=("amount", "sum")
    ).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            service_breakdown,
            values="transaction_count",
            names="service",
            title="Transactions by Service",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            service_breakdown,
            x="service",
            y="total_amount",
            title="Revenue by Service",
            labels={"service": "Service", "total_amount": "Total Amount (RWF)"},
            color="service"
        )
        fig.update_layout(yaxis_title="Amount (RWF)")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Payment method breakdown
    payment_breakdown = filtered_df.groupby(["payment_method", "status"]).agg(
        transaction_count=("transaction_id", "count")
    ).reset_index()
    
    # Status breakdown by payment method
    fig = px.bar(
        payment_breakdown,
        x="payment_method",
        y="transaction_count",
        color="status",
        title="Payment Methods and Success Rates",
        labels={"payment_method": "Payment Method", "transaction_count": "Number of Transactions", "status": "Status"},
        color_discrete_map={
            "Completed": "#4CAF50",
            "Failed": "#F44336",
            "Pending": "#FFC107"
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Average transaction amount by payment method
    payment_avg = filtered_df.groupby("payment_method").agg(
        avg_amount=("amount", "mean")
    ).reset_index()
    
    fig = px.bar(
        payment_avg,
        x="payment_method",
        y="avg_amount",
        title="Average Transaction Amount by Payment Method",
        labels={"payment_method": "Payment Method", "avg_amount": "Average Amount (RWF)"},
        color="payment_method"
    )
    fig.update_layout(yaxis_title="Amount (RWF)")
    st.plotly_chart(fig, use_container_width=True)

# Transaction list
st.subheader("Transaction List")

# Format data for display
display_df = filtered_df.copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
display_df["amount"] = display_df["amount"].apply(lambda x: f"{x:,} {display_df['currency'].iloc[0]}")

# Define sort column and order
sort_options = ["Newest First", "Oldest First", "Amount (High to Low)", "Amount (Low to High)"]
sort_selection = st.selectbox("Sort by", sort_options)

if sort_selection == "Newest First":
    display_df = display_df.sort_values("timestamp", ascending=False)
elif sort_selection == "Oldest First":
    display_df = display_df.sort_values("timestamp", ascending=True)
elif sort_selection == "Amount (High to Low)":
    display_df["amount_numeric"] = filtered_df["amount"]
    display_df = display_df.sort_values("amount_numeric", ascending=False)
    display_df = display_df.drop(columns=["amount_numeric"])
elif sort_selection == "Amount (Low to High)":
    display_df["amount_numeric"] = filtered_df["amount"]
    display_df = display_df.sort_values("amount_numeric", ascending=True)
    display_df = display_df.drop(columns=["amount_numeric"])

# Display table
st.dataframe(
    display_df[[
        "transaction_id", "service", "amount", "status", 
        "payment_method", "payment_id", "user_id", "timestamp"
    ]],
    column_config={
        "transaction_id": "Transaction ID",
        "service": "Service",
        "amount": "Amount",
        "status": "Status",
        "payment_method": "Payment Method",
        "payment_id": "Payment ID",
        "user_id": "User ID",
        "timestamp": "Timestamp"
    },
    use_container_width=True
)

# Transaction details
st.subheader("Transaction Details")

selected_transaction = st.selectbox(
    "Select a transaction to view details",
    options=filtered_df["transaction_id"],
    index=0 if not filtered_df.empty else None
)

if selected_transaction:
    # Find the selected transaction
    transaction = filtered_df[filtered_df["transaction_id"] == selected_transaction].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        st.write(f"**Transaction ID:** {transaction['transaction_id']}")
        st.write(f"**Service:** {transaction['service']}")
        st.write(f"**Amount:** {transaction['amount']:,} {transaction['currency']}")
        st.write(f"**Status:** {transaction['status']}")
        st.write(f"**Timestamp:** {transaction['timestamp']}")
    
    with col2:
        st.markdown("#### Payment Details")
        st.write(f"**Payment Method:** {transaction['payment_method']}")
        st.write(f"**Payment ID:** {transaction['payment_id']}")
        st.write(f"**User ID:** {transaction['user_id']}")
        st.write(f"**Call ID:** {transaction['call_id']}")
    
    # Timeline for the transaction
    st.markdown("#### Transaction Timeline")
    
    # Generate a fake timeline for the demo
    timeline_events = []
    
    # Initial event
    start_time = transaction["timestamp"]
    timeline_events.append({
        "time": start_time,
        "event": "Transaction Initiated",
        "details": f"User {transaction['user_id']} initiated payment for {transaction['service']}"
    })
    
    # Payment processing
    processing_time = start_time + timedelta(seconds=random.randint(5, 15))
    timeline_events.append({
        "time": processing_time,
        "event": "Payment Processing",
        "details": f"Payment request sent to {transaction['payment_method']} gateway"
    })
    
    # Result event
    if transaction["status"] == "Completed":
        completion_time = processing_time + timedelta(seconds=random.randint(5, 20))
        timeline_events.append({
            "time": completion_time,
            "event": "Payment Successful",
            "details": f"Payment of {transaction['amount']:,} {transaction['currency']} confirmed with ID {transaction['payment_id']}"
        })
        
        # Receipt event
        receipt_time = completion_time + timedelta(seconds=random.randint(3, 10))
        timeline_events.append({
            "time": receipt_time,
            "event": "Receipt Generated",
            "details": "Payment receipt and confirmation sent to user"
        })
    
    elif transaction["status"] == "Failed":
        failure_time = processing_time + timedelta(seconds=random.randint(5, 15))
        timeline_events.append({
            "time": failure_time,
            "event": "Payment Failed",
            "details": "Payment gateway returned an error: Insufficient funds"
        })
        
        # Retry suggestion
        retry_time = failure_time + timedelta(seconds=random.randint(3, 8))
        timeline_events.append({
            "time": retry_time,
            "event": "Retry Suggested",
            "details": "User was advised to try an alternative payment method"
        })
    
    elif transaction["status"] == "Pending":
        pending_time = processing_time + timedelta(seconds=random.randint(5, 15))
        timeline_events.append({
            "time": pending_time,
            "event": "Payment Pending",
            "details": "Waiting for confirmation from payment provider"
        })
    
    # Display timeline
    for i, event in enumerate(timeline_events):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"**{event['time'].strftime('%H:%M:%S')}**")
        
        with col2:
            st.markdown(f"**{event['event']}**")
            st.markdown(f"{event['details']}")
        
        if i < len(timeline_events) - 1:
            st.markdown("---")
    
    # Action buttons for the transaction
    st.markdown("#### Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("View Receipt", disabled=transaction["status"] != "Completed")
    
    with col2:
        st.button("Resend Confirmation", disabled=transaction["status"] != "Completed")
    
    with col3:
        st.button("Retry Payment", disabled=transaction["status"] != "Failed")

# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
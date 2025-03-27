import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="System Configuration | SpeakWise",
    page_icon="⚙️",
    layout="wide"
)

# Header
st.markdown("# ⚙️ System Configuration")
st.markdown("Configure and manage system settings, workflows, and integrations")

# Sidebar with navigation
st.sidebar.markdown("## Configuration Areas")
config_section = st.sidebar.radio(
    "Select area to configure:",
    ["General Settings", "Service Workflows", "Telephony Integration", "LLM Settings", "Browser Agent", "User Management"]
)

# Mock configuration data
def load_mock_config():
    return {
        "general": {
            "system_name": "SpeakWise",
            "language": "Kinyarwanda",
            "secondary_language": "English",
            "call_timeout": 1800,
            "max_retries": 3,
            "recording_enabled": True,
            "analytics_level": "Full"
        },
        "services": [
            {
                "id": "bus_reg",
                "name": "Business Registration",
                "enabled": True,
                "url_path": "/services/business-registration",
                "requires_payment": True,
                "steps": 7,
                "required_fields": ["business_name", "type", "address", "owner_id", "contact"]
            },
            {
                "id": "marriage_cert",
                "name": "Marriage Certificate",
                "enabled": True,
                "url_path": "/services/marriage-certificate",
                "requires_payment": True,
                "steps": 5,
                "required_fields": ["bride_id", "groom_id", "date", "location", "witnesses"]
            },
            {
                "id": "land_transfer",
                "name": "Land Transfer",
                "enabled": False,
                "url_path": "/services/land-transfer",
                "requires_payment": True,
                "steps": 9,
                "required_fields": ["current_owner_id", "new_owner_id", "land_title", "location", "payment_info"]
            },
            {
                "id": "passport",
                "name": "Passport Application",
                "enabled": True,
                "url_path": "/services/passport",
                "requires_payment": True,
                "steps": 6,
                "required_fields": ["applicant_id", "photo", "address", "contact", "payment_info"]
            }
        ],
        "telephony": {
            "provider": "Twilio",
            "phone_number": "+250780123456",
            "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "auth_token": "************************",
            "webhook_url": "https://api.irembovai.rw/calls/webhook",
            "recording_enabled": True,
            "call_timeout": 1800,
            "greeting_message": "Welcome to SpeakWise. How can I assist you today?"
        },
        "llm": {
            "provider": "OpenAI",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500,
            "system_prompt": "You are an assistant that helps citizens access government services through SpeakWise.",
            "fallback_message": "I'm sorry, I didn't understand that. Could you please repeat?"
        },
        "browser_agent": {
            "browser": "Chrome",
            "headless": True,
            "timeout": 30,
            "screenshots_enabled": True,
            "screenshot_path": "/var/log/irembovai/screenshots",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "default_viewport": {"width": 1280, "height": 720}
        },
        "users": [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@speakwise.com",
                "role": "Admin",
                "last_login": "2023-10-28T09:15:43Z"
            },
            {
                "id": 2,
                "username": "operator",
                "email": "operator@speakwise.com",
                "role": "Operator",
                "last_login": "2023-10-29T08:30:22Z"
            },
            {
                "id": 3,
                "username": "viewer",
                "email": "viewer@speakwise.com",
                "role": "Viewer",
                "last_login": "2023-10-27T15:45:19Z"
            }
        ]
    }

# Load configuration
config = load_mock_config()

# Helper function to save configuration
def save_config(config):
    # In a real application, this would save to a database or file
    st.success("Configuration saved successfully!")
    st.session_state.config = config

# General Settings
if config_section == "General Settings":
    st.header("General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Information")
        config["general"]["system_name"] = st.text_input("System Name", config["general"]["system_name"])
        
        languages = ["English", "Kinyarwanda", "French", "Swahili"]
        config["general"]["language"] = st.selectbox("Primary Language", languages, languages.index(config["general"]["language"]))
        config["general"]["secondary_language"] = st.selectbox("Secondary Language", ["None"] + languages, 0 if config["general"]["secondary_language"] not in languages else languages.index(config["general"]["secondary_language"])+1)
        
        st.subheader("Call Settings")
        config["general"]["call_timeout"] = st.number_input("Call Timeout (seconds)", min_value=60, max_value=3600, value=config["general"]["call_timeout"])
        config["general"]["max_retries"] = st.number_input("Max Retries", min_value=0, max_value=10, value=config["general"]["max_retries"])
    
    with col2:
        st.subheader("System Behavior")
        config["general"]["recording_enabled"] = st.toggle("Enable Call Recording", config["general"]["recording_enabled"])
        
        analytics_options = ["Minimal", "Basic", "Full", "Debug"]
        config["general"]["analytics_level"] = st.selectbox("Analytics Level", analytics_options, analytics_options.index(config["general"]["analytics_level"]))
        
        st.subheader("System Status")
        st.metric("System Uptime", "23 days 4 hours")
        st.metric("Last Deployment", "2023-10-25 09:12:45")
        
        # Display environment
        st.subheader("Environment")
        st.code("Production", language=None)
    
    if st.button("Save General Settings"):
        save_config(config)

# Service Workflows
elif config_section == "Service Workflows":
    st.header("Service Workflows")
    
    # Create tabs for service configuration
    services_tab, fields_tab, steps_tab = st.tabs(["Available Services", "Field Mapping", "Workflow Steps"])
    
    with services_tab:
        st.subheader("Available Services")
        
        # Convert services to DataFrame for easier editing
        services_df = pd.DataFrame(config["services"])
        
        # Edit the services table
        edited_services = st.data_editor(
            services_df,
            column_config={
                "id": st.column_config.TextColumn("Service ID", disabled=True),
                "name": st.column_config.TextColumn("Service Name"),
                "enabled": st.column_config.CheckboxColumn("Enabled"),
                "url_path": st.column_config.TextColumn("URL Path"),
                "requires_payment": st.column_config.CheckboxColumn("Requires Payment"),
                "steps": st.column_config.NumberColumn("Steps"),
                "required_fields": None  # Hide this column in the editor
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Option to add a new service
        st.subheader("Add New Service")
        col1, col2 = st.columns(2)
        with col1:
            new_service_id = st.text_input("Service ID (internal)")
            new_service_name = st.text_input("Service Name")
            new_service_url = st.text_input("URL Path")
        with col2:
            new_service_enabled = st.checkbox("Enabled", value=True)
            new_service_payment = st.checkbox("Requires Payment", value=True)
            new_service_steps = st.number_input("Steps", min_value=1, max_value=20, value=5)
        
        if st.button("Add Service"):
            if new_service_id and new_service_name:
                # In a real app, validation would be more thorough
                edited_services = pd.concat([
                    edited_services, 
                    pd.DataFrame([{
                        "id": new_service_id,
                        "name": new_service_name,
                        "enabled": new_service_enabled,
                        "url_path": new_service_url,
                        "requires_payment": new_service_payment,
                        "steps": new_service_steps,
                        "required_fields": []
                    }])
                ], ignore_index=True)
                st.success(f"Added new service: {new_service_name}")
            else:
                st.error("Service ID and Name are required")
        
        # Save changes to services
        if st.button("Save Services Configuration"):
            # Update the config with the edited services
            config["services"] = edited_services.to_dict('records')
            save_config(config)
    
    with fields_tab:
        st.subheader("Field Mapping Configuration")
        
        # Select a service to configure fields
        service_id = st.selectbox(
            "Select Service to Configure Fields",
            options=[s["id"] for s in config["services"]],
            format_func=lambda x: next((s["name"] for s in config["services"] if s["id"] == x), "")
        )
        
        selected_service = next((s for s in config["services"] if s["id"] == service_id), None)
        
        if selected_service:
            st.write(f"Configuring fields for: **{selected_service['name']}**")
            
            # Display existing required fields
            st.write("Current required fields:")
            required_fields = selected_service.get("required_fields", [])
            
            # Field mapping editor
            field_mapping = []
            for field in required_fields:
                field_mapping.append({
                    "field_name": field,
                    "display_name": field.replace("_", " ").title(),
                    "required": True,
                    "field_type": "text"
                })
            
            # Convert to DataFrame for editing
            if field_mapping:
                field_df = pd.DataFrame(field_mapping)
                
                edited_fields = st.data_editor(
                    field_df,
                    column_config={
                        "field_name": st.column_config.TextColumn("Field Name"),
                        "display_name": st.column_config.TextColumn("Display Name"),
                        "required": st.column_config.CheckboxColumn("Required"),
                        "field_type": st.column_config.SelectboxColumn(
                            "Field Type",
                            options=["text", "number", "date", "select", "file", "phone", "email"]
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Add a new field
                st.subheader("Add New Field")
                col1, col2 = st.columns(2)
                with col1:
                    new_field_name = st.text_input("Field Name")
                    new_field_display = st.text_input("Display Name")
                with col2:
                    new_field_required = st.checkbox("Required Field", value=True)
                    new_field_type = st.selectbox("Field Type", ["text", "number", "date", "select", "file", "phone", "email"])
                
                if st.button("Add Field"):
                    if new_field_name:
                        edited_fields = pd.concat([
                            edited_fields,
                            pd.DataFrame([{
                                "field_name": new_field_name,
                                "display_name": new_field_display or new_field_name.replace("_", " ").title(),
                                "required": new_field_required,
                                "field_type": new_field_type
                            }])
                        ], ignore_index=True)
                        st.success(f"Added new field: {new_field_name}")
                    else:
                        st.error("Field Name is required")
                
                # Save field configuration
                if st.button("Save Field Configuration"):
                    # Update the required_fields list for this service
                    for i, service in enumerate(config["services"]):
                        if service["id"] == service_id:
                            config["services"][i]["required_fields"] = edited_fields["field_name"].tolist()
                            break
                    
                    save_config(config)
            else:
                st.info("No fields defined for this service yet. Add fields below.")
                
                # Add first field
                col1, col2 = st.columns(2)
                with col1:
                    first_field_name = st.text_input("First Field Name")
                    first_field_display = st.text_input("Display Name")
                with col2:
                    first_field_required = st.checkbox("Required", value=True)
                    first_field_type = st.selectbox("Field Type", ["text", "number", "date", "select", "file", "phone", "email"])
                
                if st.button("Add First Field"):
                    if first_field_name:
                        for i, service in enumerate(config["services"]):
                            if service["id"] == service_id:
                                config["services"][i]["required_fields"] = [first_field_name]
                                break
                        save_config(config)
                        st.success(f"Added first field: {first_field_name}")
                        st.rerun()
                    else:
                        st.error("Field Name is required")
    
    with steps_tab:
        st.subheader("Workflow Steps Configuration")
        
        # Select a service to configure workflow
        workflow_service_id = st.selectbox(
            "Select Service to Configure Workflow",
            options=[s["id"] for s in config["services"]],
            format_func=lambda x: next((s["name"] for s in config["services"] if s["id"] == x), ""),
            key="workflow_service_selector"
        )
        
        selected_workflow_service = next((s for s in config["services"] if s["id"] == workflow_service_id), None)
        
        if selected_workflow_service:
            st.write(f"Configuring workflow for: **{selected_workflow_service['name']}**")
            
            # Mock workflow steps data
            steps = []
            for i in range(1, selected_workflow_service['steps'] + 1):
                step_name = ""
                if i == 1:
                    step_name = "Initial Information Collection"
                elif i == selected_workflow_service['steps']:
                    step_name = "Confirmation and Receipt"
                elif selected_workflow_service['requires_payment'] and i == selected_workflow_service['steps'] - 1:
                    step_name = "Payment Processing"
                else:
                    step_name = f"Form Section {i-1}"
                
                steps.append({
                    "step_number": i,
                    "name": step_name,
                    "description": f"Step {i} of the {selected_workflow_service['name']} process",
                    "fields": [],
                    "requires_user_input": True,
                    "has_validation": i > 1
                })
            
            # Convert to DataFrame for editing
            steps_df = pd.DataFrame(steps)
            
            edited_steps = st.data_editor(
                steps_df,
                column_config={
                    "step_number": st.column_config.NumberColumn("Step #", disabled=True),
                    "name": st.column_config.TextColumn("Step Name"),
                    "description": st.column_config.TextColumn("Description"),
                    "fields": None,  # Hide this column
                    "requires_user_input": st.column_config.CheckboxColumn("Requires Input"),
                    "has_validation": st.column_config.CheckboxColumn("Has Validation")
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Step details editor
            st.subheader("Step Details")
            selected_step = st.number_input(
                "Select Step to Edit",
                min_value=1,
                max_value=selected_workflow_service['steps'],
                value=1
            )
            
            step_data = edited_steps[edited_steps["step_number"] == selected_step].iloc[0]
            
            st.write(f"Editing: **{step_data['name']}**")
            
            prompt_text = st.text_area(
                "AI Prompt for this step",
                value=f"I'll help you with {step_data['name']}. Please provide the following information:"
            )
            
            retry_text = st.text_input(
                "Retry prompt",
                value="I'm sorry, I didn't get that. Could you please try again?"
            )
            
            # Example code to add fields to a step
            st.subheader("Fields in this step")
            
            all_fields = selected_workflow_service.get("required_fields", [])
            
            if all_fields:
                selected_fields = st.multiselect(
                    "Select fields to include in this step",
                    options=all_fields,
                    default=[]
                )
                
                if st.button(f"Save Step {selected_step} Configuration"):
                    st.success(f"Step {selected_step} configuration saved")
            else:
                st.info("No fields defined for this service yet. Please add fields in the Field Mapping tab first.")

# Telephony Integration
elif config_section == "Telephony Integration":
    st.header("Telephony Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Telephony Provider")
        
        provider_options = ["Twilio", "Africa's Talking", "Vonage", "Custom"]
        selected_provider = st.selectbox(
            "Select Provider",
            provider_options,
            provider_options.index(config["telephony"]["provider"])
        )
        
        st.subheader("Phone Configuration")
        phone_number = st.text_input("Phone Number", config["telephony"]["phone_number"])
        
        # Provider-specific fields
        if selected_provider == "Twilio":
            account_sid = st.text_input("Account SID", config["telephony"]["account_sid"])
            auth_token = st.text_input("Auth Token", config["telephony"]["auth_token"], type="password")
        elif selected_provider == "Africa's Talking":
            api_key = st.text_input("API Key", "af67d939c7639f989e7834a092d5" if selected_provider != config["telephony"]["provider"] else "", type="password")
            username = st.text_input("Username", "irembovai" if selected_provider != config["telephony"]["provider"] else "")
    
    with col2:
        st.subheader("Call Handling")
        webhook_url = st.text_input("Webhook URL", config["telephony"]["webhook_url"])
        recording_enabled = st.checkbox("Enable Call Recording", config["telephony"]["recording_enabled"])
        call_timeout = st.number_input("Call Timeout (seconds)", min_value=60, max_value=3600, value=config["telephony"]["call_timeout"])
        
        st.subheader("Messages")
        greeting_message = st.text_area("Greeting Message", config["telephony"]["greeting_message"])
        
        # Test connection
        st.subheader("Test Connection")
        if st.button("Test Telephony Integration"):
            st.success("Connection successful! Phone system is operational.")
    
    # Save changes
    if st.button("Save Telephony Configuration"):
        # Update config
        config["telephony"]["provider"] = selected_provider
        config["telephony"]["phone_number"] = phone_number
        config["telephony"]["webhook_url"] = webhook_url
        config["telephony"]["recording_enabled"] = recording_enabled
        config["telephony"]["call_timeout"] = call_timeout
        config["telephony"]["greeting_message"] = greeting_message
        
        if selected_provider == "Twilio":
            config["telephony"]["account_sid"] = account_sid
            config["telephony"]["auth_token"] = auth_token
        
        save_config(config)

# LLM Settings
elif config_section == "LLM Settings":
    st.header("Language Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Selection")
        
        provider_options = ["OpenAI", "Anthropic", "Google", "Self-hosted"]
        selected_provider = st.selectbox(
            "LLM Provider",
            provider_options,
            provider_options.index(config["llm"]["provider"])
        )
        
        model_options = {
            "OpenAI": ["gpt-4", "gpt-4-32k", "gpt-3.5-turbo"],
            "Anthropic": ["claude-2", "claude-instant"],
            "Google": ["palm-2", "gemini"],
            "Self-hosted": ["llama-2-13b", "llama-2-70b", "falcon-40b"]
        }
        
        selected_model = st.selectbox(
            "Model",
            model_options[selected_provider],
            0 if config["llm"]["model"] not in model_options[selected_provider] else model_options[selected_provider].index(config["llm"]["model"])
        )
        
        st.subheader("Model Parameters")
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=config["llm"]["temperature"], step=0.1)
        max_tokens = st.number_input("Max Tokens", min_value=100, max_value=8000, value=config["llm"]["max_tokens"])
    
    with col2:
        st.subheader("Prompts and Messages")
        system_prompt = st.text_area("System Prompt", config["llm"]["system_prompt"], height=150)
        fallback_message = st.text_area("Fallback Message", config["llm"]["fallback_message"])
        
        # API settings
        st.subheader("API Settings")
        api_key = st.text_input("API Key", "sk-********************************", type="password")
        
        # Test model
        st.subheader("Test LLM")
        test_input = st.text_input("Test prompt", "Hello, can you help me with a business registration?")
        if st.button("Test Model Response"):
            st.info("Testing connection to LLM...")
            st.success("Connection successful!")
            st.write("**Sample response:**")
            st.write("Hello! I'd be happy to help you with business registration. To get started, I'll need some information about your business. First, could you tell me the name of your business and what type of business it is?")
    
    # Save changes
    if st.button("Save LLM Configuration"):
        # Update config
        config["llm"]["provider"] = selected_provider
        config["llm"]["model"] = selected_model
        config["llm"]["temperature"] = temperature
        config["llm"]["max_tokens"] = max_tokens
        config["llm"]["system_prompt"] = system_prompt
        config["llm"]["fallback_message"] = fallback_message
        
        save_config(config)

# Browser Agent
elif config_section == "Browser Agent":
    st.header("Browser Agent Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Browser Settings")
        
        browser_options = ["Chrome", "Firefox", "Edge", "WebKit"]
        selected_browser = st.selectbox(
            "Browser",
            browser_options,
            browser_options.index(config["browser_agent"]["browser"])
        )
        
        headless = st.checkbox("Headless Mode", config["browser_agent"]["headless"])
        
        st.subheader("Timeout and Performance")
        timeout = st.number_input("Timeout (seconds)", min_value=5, max_value=120, value=config["browser_agent"]["timeout"])
        
        st.subheader("Browser Identity")
        user_agent = st.text_area("User Agent", config["browser_agent"]["user_agent"])
    
    with col2:
        st.subheader("Viewport and Display")
        col_a, col_b = st.columns(2)
        with col_a:
            viewport_width = st.number_input("Viewport Width", min_value=800, max_value=1920, value=config["browser_agent"]["default_viewport"]["width"])
        with col_b:
            viewport_height = st.number_input("Viewport Height", min_value=600, max_value=1080, value=config["browser_agent"]["default_viewport"]["height"])
        
        st.subheader("Debugging and Logging")
        screenshots_enabled = st.checkbox("Enable Screenshots", config["browser_agent"]["screenshots_enabled"])
        screenshot_path = st.text_input("Screenshot Path", config["browser_agent"]["screenshot_path"])
        
        # Test browser
        st.subheader("Test Browser Agent")
        if st.button("Test Browser Connection"):
            st.info("Testing browser agent...")
            st.success("Browser agent is functioning correctly!")
    
    # Save changes
    if st.button("Save Browser Agent Configuration"):
        # Update config
        config["browser_agent"]["browser"] = selected_browser
        config["browser_agent"]["headless"] = headless
        config["browser_agent"]["timeout"] = timeout
        config["browser_agent"]["user_agent"] = user_agent
        config["browser_agent"]["default_viewport"]["width"] = viewport_width
        config["browser_agent"]["default_viewport"]["height"] = viewport_height
        config["browser_agent"]["screenshots_enabled"] = screenshots_enabled
        config["browser_agent"]["screenshot_path"] = screenshot_path
        
        save_config(config)

# User Management
elif config_section == "User Management":
    st.header("User Management")
    
    # Tabs
    user_tab, roles_tab, activity_tab = st.tabs(["Users", "Roles and Permissions", "Activity Log"])
    
    with user_tab:
        st.subheader("System Users")
        
        # Convert users to DataFrame
        users_df = pd.DataFrame(config["users"])
        
        # Format the last login time
        users_df["last_login"] = pd.to_datetime(users_df["last_login"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Display users table
        edited_users = st.data_editor(
            users_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "username": st.column_config.TextColumn("Username"),
                "email": st.column_config.TextColumn("Email"),
                "role": st.column_config.SelectboxColumn("Role", options=["Admin", "Operator", "Viewer"]),
                "last_login": st.column_config.TextColumn("Last Login", disabled=True)
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Add new user
        st.subheader("Add New User")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
        with col2:
            new_role = st.selectbox("Role", ["Admin", "Operator", "Viewer"])
            new_password = st.text_input("Password", type="password")
        
        if st.button("Add User"):
            if new_username and new_email and new_password:
                next_id = max(edited_users["id"]) + 1 if not edited_users.empty else 1
                edited_users = pd.concat([
                    edited_users,
                    pd.DataFrame([{
                        "id": next_id,
                        "username": new_username,
                        "email": new_email,
                        "role": new_role,
                        "last_login": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    }])
                ], ignore_index=True)
                st.success(f"Added new user: {new_username}")
            else:
                st.error("Username, email, and password are required")
        
        # Save user changes
        if st.button("Save User Configuration"):
            # Update the config with the edited users
            config["users"] = edited_users.to_dict('records')
            save_config(config)
    
    with roles_tab:
        st.subheader("Roles and Permissions")
        
        # Role descriptions
        st.markdown("""
        ### Role Descriptions
        
        - **Admin**: Full access to all system features including user management and configuration
        - **Operator**: Can monitor calls, view analytics, and manage specific services
        - **Viewer**: Read-only access to dashboards and call monitoring
        """)
        
        # Permission matrix
        st.subheader("Permission Matrix")
        
        permissions = {
            "View Dashboard": {"Admin": True, "Operator": True, "Viewer": True},
            "Monitor Calls": {"Admin": True, "Operator": True, "Viewer": True},
            "View Analytics": {"Admin": True, "Operator": True, "Viewer": True},
            "Edit Service Config": {"Admin": True, "Operator": False, "Viewer": False},
            "Manage Users": {"Admin": True, "Operator": False, "Viewer": False},
            "System Configuration": {"Admin": True, "Operator": False, "Viewer": False},
            "Download Reports": {"Admin": True, "Operator": True, "Viewer": False}
        }
        
        # Convert to DataFrame
        permissions_df = pd.DataFrame.from_dict(permissions, orient='index').reset_index()
        permissions_df.columns = ["Permission", "Admin", "Operator", "Viewer"]
        
        # Display permission matrix
        st.dataframe(
            permissions_df,
            column_config={
                "Permission": st.column_config.TextColumn("Permission"),
                "Admin": st.column_config.CheckboxColumn("Admin"),
                "Operator": st.column_config.CheckboxColumn("Operator"),
                "Viewer": st.column_config.CheckboxColumn("Viewer")
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.info("Note: Permission changes require a separate security role configuration, which is managed by system administrators.")
    
    with activity_tab:
        st.subheader("User Activity Log")
        
        # Generate mock activity data
        activities = []
        for i in range(20):
            user = random.choice(config["users"])
            action_types = ["Login", "Logout", "View Dashboard", "Edit Configuration", "Update User", "Monitor Call"]
            action = random.choice(action_types)
            timestamp = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            activities.append({
                "timestamp": timestamp,
                "user": user["username"],
                "action": action,
                "ip_address": f"192.168.1.{random.randint(2, 254)}"
            })
        
        # Sort by timestamp
        activities = sorted(activities, key=lambda x: x["timestamp"], reverse=True)
        
        # Convert to DataFrame
        activity_df = pd.DataFrame(activities)
        activity_df["timestamp"] = pd.to_datetime(activity_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Date filter
        date_range = st.date_input(
            "Filter by date range",
            value=(datetime.now().date() - timedelta(days=7), datetime.now().date())
        )
        
        # User filter
        user_filter = st.multiselect(
            "Filter by user",
            options=[user["username"] for user in config["users"]],
            default=[]
        )
        
        # Display activity log
        st.dataframe(
            activity_df,
            column_config={
                "timestamp": st.column_config.TextColumn("Timestamp"),
                "user": st.column_config.TextColumn("User"),
                "action": st.column_config.TextColumn("Action"),
                "ip_address": st.column_config.TextColumn("IP Address")
            },
            use_container_width=True,
            hide_index=True
        )

# Display the current configuration (debug view)
with st.expander("View Current Configuration (JSON)"):
    st.json(config)

# Footer
st.markdown("---")
st.markdown("© 2023 SpeakWise | Configuration Portal")
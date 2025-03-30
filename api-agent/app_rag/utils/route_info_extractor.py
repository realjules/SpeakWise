import json
import requests
from typing import Dict, Any

def extract_schema_info(schema_ref, schemas):
    schema_name = schema_ref.split("/")[-1]
    schema = schemas.get(schema_name, {})
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])

    return {
        "schema_name": schema_name,
        "fields": list(properties.keys()),
        "required_fields": required_fields
    }

def extract_paths_info(openapi_spec):
    paths_info = []
    paths = openapi_spec.get("paths", {})
    schemas = openapi_spec.get("components", {}).get("schemas", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            description = details.get("description", "No description provided")
            request_body = details.get("requestBody", {})
            schema_ref = request_body.get("content", {}).get("application/json", {}).get("schema", {}).get("$ref", "")

            if schema_ref:
                schema_info = extract_schema_info(schema_ref, schemas)
            else:
                schema_info = {"schema_name": "None", "fields": [], "required_fields": []}

            paths_info.append({
                "path": path,
                "method": method,
                "description": description,
                "schema_name": schema_info["schema_name"],
                "fields": schema_info["fields"],
                "required_fields": schema_info["required_fields"]
            })
    return paths_info

def load_forms_fields() -> Dict[str, Any]:
    form_api_url = f"http://localhost:8000/openapi.json"
    response = requests.get(form_api_url)

    if response.status_code == 200:
        # Extract the form information
        form_data = extract_paths_info(response.json())
        
        # Save extracted data to a local JSON file
        with open("./data/forms_fields.json", "w") as json_file:
            json.dump(form_data, json_file, indent=4)
        
        return form_data
    else:
        return {"error": "Form not found"}
    
# Function to load form fields from local JSON file
def load_local_form_fields() -> Dict[str, Any]:
    try:
        with open("./data/forms_fields.json", "r") as json_file:
            form_data = json.load(json_file)
        return form_data
    except FileNotFoundError:
        return {"error": "Local form fields file not found"}
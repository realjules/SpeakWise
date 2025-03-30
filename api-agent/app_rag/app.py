from fastapi import FastAPI, Request, Depends, Response, Cookie

import uuid  # For generating session IDs
import requests  # For making external API calls

from utils.route_info_extractor import load_forms_fields, load_local_form_fields
from utils.llm import groq, call_groq_llm, get_answer_from_chroma, classify_intent, classify_form, extract_fields, generate_field_request, generate_fields_request, generate_report
from utils.chroma_utils import setup_chroma_with_sample_data
from utils.schemas import ConversationData
from utils.db import get_db, SessionLocal, Conversation

from sms.sms_sender import SMSSender
from sms.config import Config

from pydantic import BaseModel

# Initialize the FastAPI app
app = FastAPI()
setup_chroma_with_sample_data()
sms_sender = SMSSender(Config())

api_url = "http://localhost:8000/"

sessions_data = {}

from enum import Enum

class ConversationState(Enum):
    IDLE = "idle"
    FORM_STATE = "form_state"


def submit_form(api_url, form_data):
    try:
        response = requests.post(api_url, json=form_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.post("/chat/")
async def chat_with_bot(
    data: ConversationData, 
    request: Request, 
    response: Response,
    session_id: str = Cookie(None),  # Use cookie-based session tracking
    db: SessionLocal = Depends(get_db)
):
    # Generate or get session_id
    # if session_id is None:
    #     # session_id = str(uuid.uuid4())
    #     # response.set_cookie(key="session_id", value=session_id)
    #     session
    session_id = request.client.host

    # Extract user agent
    user_agent = request.headers.get("user-agent")

    # Classify the user's intent
    intent = classify_intent(data.message)

    if session_id not in sessions_data:
        sessions_data[session_id] = {
            "state": ConversationState.IDLE,
            "fields": {},
            "description": "",
            "form": ""
        }

    current_state = sessions_data[session_id]["state"]

    print(current_state)
    print(intent)
    print(request.client.host)

    if intent == "stop_form":
        # Stop the form filling process
        bot_response = "Form filling process stopped."
        sessions_data[session_id]["state"] = ConversationState.IDLE  # Reset state
        entities = {"intent": "stop_form"}
    
    elif current_state == ConversationState.FORM_STATE:
        # Extract information based on expected fields
        extracted_information = extract_fields(data.message, sessions_data[session_id]["fields"])
        print("Extracted information", extracted_information)

        # Update only unfilled fields (those that are None)
        for field, value in extracted_information.items():
            if value is not None and sessions_data[session_id]["fields"][field] is None:
                sessions_data[session_id]["fields"][field] = value  # Only update unfilled fields

        # Check if there are still unfilled fields
        unfilled_fields = [key for key, value in sessions_data[session_id]["fields"].items() if value is None]

        if unfilled_fields:
            # Ask for the next unfilled field
            next_field = unfilled_fields[0]
            bot_response = generate_field_request(sessions_data[session_id]["description"], next_field)
        else:
            # All fields are filled, proceed with submission or further processing
            bot_response = "Form completed successfully. Here are the collected information:\n" + generate_report(sessions_data[session_id])

            form_data = sessions_data[session_id]["fields"]
            url_path = sessions_data[session_id]["form"]
            api_response = submit_form(api_url+url_path, form_data)
            # sms_sender.send_message("0780465060", bot_response)
            # sms_sender.send_message("0780465060","HELLO THERE")
            sessions_data[session_id]["state"] = ConversationState.IDLE  # Reset state

        entities = {"intent": "fill_form", "information": extracted_information}
    elif intent == "ask_question":
        # Retrieve answers from Chroma vector database
        bot_response = get_answer_from_chroma(data.message)
        entities = {"intent": "ask_question"}

    elif intent == "fill_form":
        api_details = load_local_form_fields()
        form, fields, description = classify_form(data.message, api_details)
        sessions_data[session_id]["state"] = ConversationState.FORM_STATE
        sessions_data[session_id]["fields"] = {item: None for item in fields["required_fields"]}
        sessions_data[session_id]["form"] = form
        sessions_data[session_id]["description"] = description
        bot_response = generate_field_request(description, fields["required_fields"][0])
        entities = {"intent": "fill_form", "form_name": form, "fields": fields}

    else:
        # Use the Groq LLM for a generic response
        bot_response = call_groq_llm(data.message).content
        entities = {"intent": "unknown"}

    print(sessions_data)

    # Save the conversation to the SQLite database
    new_conversation = Conversation(
        session_id=session_id,
        user_agent=user_agent,
        user_message=data.message,
        bot_response=bot_response,
        extracted_entities=str(entities)  # Save extracted entities as a string
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return {
        "message": "Conversation recorded successfully",
        "bot_response": bot_response,
        "entities": entities
    }


# Optional: Endpoint to retrieve all conversations
@app.get("/conversations/")
async def get_conversations(db: SessionLocal = Depends(get_db)):
    conversations = db.query(Conversation).all()
    return conversations

@app.on_event("startup")
async def startup_event():
    load_forms_fields()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

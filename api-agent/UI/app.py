import streamlit as st
import requests

# Change this to the URL of your FastAPI endpoint.
API_URL = "http://localhost:8001/chat/"

st.title("Form Filling Assistant")

# Initialize session state for messages if not already defined.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get the user prompt.
if prompt := st.chat_input("What is up?"):
    # Add the user's message to session state and display it.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Call the FastAPI endpoint.
    try:
        response = requests.post(API_URL, json={"message": prompt})
        response.raise_for_status()  # Raise an error for bad status codes.
        data = response.json()
        answer = data.get("bot_response", "No answer received from the API.")
    except Exception as e:
        answer = f"Error calling the API: {e}"
    
    # Display the assistant's reply.
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    # Save the assistant's reply.
    st.session_state.messages.append({"role": "assistant", "content": answer})


# import streamlit as st
# import requests
# import speech_recognition as sr
# import pyttsx3
# import tempfile
# import os

# # Change this to the URL of your FastAPI endpoint.
# API_URL = "http://localhost:8001/chat/"

# st.title("Form Filling Assistant with Voice")

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "listening" not in st.session_state:
#     st.session_state.listening = False

# # Function to convert text to speech
# def text_to_speech(text):
#     engine = pyttsx3.init()
#     # Save to a temporary file
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
#         temp_filename = tmp_file.name
    
#     # Configure and save to the temporary file    
#     engine.save_to_file(text, temp_filename)
#     engine.runAndWait()
    
#     # Read the file back in
#     with open(temp_filename, 'rb') as f:
#         audio_bytes = f.read()
    
#     # Clean up
#     os.unlink(temp_filename)
    
#     return audio_bytes

# # Function to recognize speech with better error handling
# def speech_to_text():
#     st.session_state.listening = True
#     st.toast("Listening... Speak now.")
    
#     try:
#         recognizer = sr.Recognizer()
#         with sr.Microphone() as source:
#             # Adjust for ambient noise
#             recognizer.adjust_for_ambient_noise(source)
#             # Set a reasonable timeout
#             audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
#             # Convert to text
#             result = recognizer.recognize_google(audio)
#             return result
#     except sr.UnknownValueError:
#         return "Sorry, I couldn't understand what you said."
#     except sr.RequestError:
#         return "Sorry, there was an issue connecting to the speech recognition service."
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         # Always reset the listening state no matter what happens
#         st.session_state.listening = False

# # Display the conversation history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#         # Add audio playback for assistant messages
#         if message["role"] == "assistant" and "audio" in message:
#             st.audio(message["audio"], format="audio/mp3")

# # Status indicator for listening mode
# if st.session_state.listening:
#     st.markdown("🎤 **Listening...**")

# # Voice record button
# col1, col2 = st.columns([1, 6])

# with col1:
#     # Disable the button when already listening
#     if st.button("🎤", disabled=st.session_state.listening, help="Click to speak"):
#         prompt = speech_to_text()
        
#         # Only process valid responses
#         if prompt and not prompt.startswith("Sorry") and not prompt.startswith("Error"):
#             # Add the user's message to session state
#             st.session_state.messages.append({"role": "user", "content": prompt})
            
#             # Call the FastAPI endpoint
#             try:
#                 response = requests.post(API_URL, json={"message": prompt})
#                 response.raise_for_status()
#                 data = response.json()
#                 answer = data.get("bot_response", "No answer received from the API.")
#             except Exception as e:
#                 answer = f"Error calling the API: {e}"
            
#             # Convert answer to speech
#             audio_bytes = text_to_speech(answer)
            
#             # Save the assistant's reply with audio
#             st.session_state.messages.append({
#                 "role": "assistant", 
#                 "content": answer,
#                 "audio": audio_bytes
#             })
#         else:
#             # Show error message to user
#             st.error(prompt)
            
#         st.rerun()

# # Text input as alternative
# with col2:
#     if prompt := st.chat_input("Type your question...", disabled=st.session_state.listening):
#         # Add the user's message to session state
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         # Call the FastAPI endpoint
#         try:
#             response = requests.post(API_URL, json={"message": prompt})
#             response.raise_for_status()
#             data = response.json()
#             answer = data.get("bot_response", "No answer received from the API.")
#         except Exception as e:
#             answer = f"Error calling the API: {e}"
        
#         # Convert answer to speech
#         audio_bytes = text_to_speech(answer)
        
#         # Save the assistant's reply with audio
#         st.session_state.messages.append({
#             "role": "assistant", 
#             "content": answer,
#             "audio": audio_bytes
#         })
        
#         st.rerun()
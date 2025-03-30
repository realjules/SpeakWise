#!/usr/bin/env python3
"""
SpeakWise Voice Assistant using Gradio
"""

import os
import sys
import io
import tempfile
import base64
from pathlib import Path
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# Add the project root to the Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default settings
DEFAULT_MODEL = "gpt-4"
DEFAULT_VOICE = "nova"
VOICE_OPTIONS = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

class SpeakWiseAssistant:
    def __init__(self):
        """Initialize the SpeakWise assistant"""
        self.messages = []
        self.system_message = (
            "You are a helpful, concise voice assistant called SpeakWise. "
            "Respond clearly and naturally as if speaking to the user. "
            "Keep responses relatively brief and conversational."
        )
        self.reset_conversation()
        
    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = [{"role": "system", "content": self.system_message}]
        return "Conversation has been reset."
    
    def process_message(self, message, model=DEFAULT_MODEL, voice=DEFAULT_VOICE, temperature=0.7):
        """Process a user message and generate a response with audio"""
        if not message.strip():
            return "Please enter a message.", None
        
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": message})
        
        try:
            # Generate text response
            response = client.chat.completions.create(
                model=model,
                messages=self.messages,
                temperature=temperature
            )
            
            response_text = response.choices[0].message.content
            
            # Save assistant response to history
            self.messages.append({"role": "assistant", "content": response_text})
            
            # Generate audio response
            audio_file = None
            
            if response_text.strip():
                speech_response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=response_text
                )
                
                # Create a temporary audio file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    f.write(speech_response.content)
                    audio_file = f.name
            
            return response_text, audio_file
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)
            return error_message, None

def create_demo():
    """Create and configure the Gradio interface"""
    assistant = SpeakWiseAssistant()
    
    with gr.Blocks(title="SpeakWise Voice Assistant", theme=gr.themes.Soft(primary_hue="blue")) as demo:
        gr.Markdown("# SpeakWise Voice Assistant")
        gr.Markdown("Welcome to SpeakWise! Chat with the AI using text and hear spoken responses.")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    height=500,
                    show_copy_button=True,
                    show_label=False,
                    elem_id="chatbot",
                )
                
                with gr.Group():
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Type your message here...",
                            scale=9,
                            show_label=False,
                            container=False,
                        )
                        submit = gr.Button("Send", scale=1, variant="primary")
                
                with gr.Row():
                    audio_output = gr.Audio(label="AI Voice Response", autoplay=True, elem_id="audio-output")
                    clear = gr.Button("Reset Conversation")
                    
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### Settings")
                    model = gr.Dropdown(
                        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
                        value=DEFAULT_MODEL,
                        label="Model"
                    )
                    voice = gr.Dropdown(
                        choices=VOICE_OPTIONS,
                        value=DEFAULT_VOICE,
                        label="Voice"
                    )
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="Temperature"
                    )
                
                gr.Markdown("### About")
                gr.Markdown("""
                SpeakWise combines powerful language models with text-to-speech 
                technology to provide a natural conversational experience.
                
                **Features:**
                - Text chat with AI
                - Voice responses
                - Adjustable model settings
                """)
        
        # Define event handlers
        def user_message(message, history):
            return "", history + [[message, None]]
        
        def bot_message(history, model_value, voice_value, temp_value):
            user_message = history[-1][0]
            response, audio = assistant.process_message(
                user_message, 
                model=model_value,
                voice=voice_value,
                temperature=temp_value
            )
            history[-1][1] = response
            return history, audio if audio else None
        
        def reset_chat():
            assistant.reset_conversation()
            return [], None
        
        # Connect event handlers
        msg.submit(
            user_message,
            [msg, chatbot],
            [msg, chatbot],
            queue=False
        ).then(
            bot_message,
            [chatbot, model, voice, temperature],
            [chatbot, audio_output]
        )
        
        submit.click(
            user_message,
            [msg, chatbot],
            [msg, chatbot],
            queue=False
        ).then(
            bot_message,
            [chatbot, model, voice, temperature],
            [chatbot, audio_output]
        )
        
        clear.click(
            reset_chat,
            None,
            [chatbot, audio_output],
            queue=False
        )
    
    return demo

def main():
    """Run the SpeakWise Voice Assistant"""
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please add your OpenAI API key to a .env file or set it in your environment.")
        print("Example .env file content: OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Create and launch the demo
    demo = create_demo()
    demo.launch(share=False, inbrowser=True)

if __name__ == "__main__":
    main()
import os
import asyncio
from openai import AsyncOpenAI

import chainlit as cl
from uuid import uuid4
from chainlit.logger import logger

from tools import RealtimeClient
from tools.tools import tools
from assistant_personality import get_introduction, format_system_prompt

client = AsyncOpenAI()


async def setup_openai_realtime():
    """Instantiate and configure the OpenAI Realtime Client"""
    openai_realtime = RealtimeClient(api_key=os.getenv("OPENAI_API_KEY"))
    cl.user_session.set("track_id", str(uuid4()))
    
    # Update session with our personality and improved settings for complete sentences
    system_prompt = format_system_prompt()
    await openai_realtime.update_session(
        instructions=system_prompt,
        turn_detection={
            "type": "server_vad", 
            "silence_duration_ms": 1000
        },
        voice="alloy"
    )

    async def handle_conversation_updated(event):
        item = event.get("item")
        delta = event.get("delta")
        """Currently used to stream audio back to the client."""
        if delta:
            # Only one of the following will be populated for any given event
            if "audio" in delta:
                audio = delta["audio"]  # Int16Array, audio added
                await cl.context.emitter.send_audio_chunk(
                    cl.OutputAudioChunk(
                        mimeType="pcm16",
                        data=audio,
                        track=cl.user_session.get("track_id"),
                    )
                )
            if "transcript" in delta:
                transcript = delta["transcript"]  # string, transcript added
                # Display transcript in the chat interface
                if item and item.get("role") == "user":
                    logger.info(f"User transcript: {transcript}")
                elif item and item.get("role") == "assistant":
                    logger.info(f"Assistant transcript: {transcript}")
            if "arguments" in delta:
                arguments = delta["arguments"]  # string, function arguments added
                pass

    async def handle_item_completed(item):
        """Used to populate the chat context with transcription once an item is completed."""
        if not item:
            return
            
        # Display completed items in the chat for text tracking
        try:
            role = item.get("role")
            formatted = item.get("formatted", {})
            text = formatted.get("text", "")
            transcript = formatted.get("transcript", "")
            
            # Only display if we have text or transcript content
            if text or transcript:
                content = text or transcript
                
                # For user messages, display what was said
                if role == "user" and content:
                    # Add "You said: " prefix to distinguish user messages
                    await cl.Message(
                        content=f"💬 **You said**: {content}",
                        author="User",
                        disable_feedback=True
                    ).send()
                
                # For assistant messages, only display if no explicit message was sent
                elif role == "assistant" and content:
                    # Check if this is a new message that should be displayed
                    if cl.user_session.get("last_assistant_text") != content:
                        cl.user_session.set("last_assistant_text", content)
                        
                        # Use assistant author to distinguish system responses
                        await cl.Message(
                            content=content,
                            author="Assistant",
                            disable_feedback=True
                        ).send()
        except Exception as e:
            logger.error(f"Error displaying completed item: {e}")

    async def handle_conversation_interrupt(event):
        """Used to cancel the client previous audio playback."""
        cl.user_session.set("track_id", str(uuid4()))
        await cl.context.emitter.send_audio_interrupt()

    async def handle_error(event):
        logger.error(event)

    openai_realtime.on("conversation.updated", handle_conversation_updated)
    openai_realtime.on("conversation.item.completed", handle_item_completed)
    openai_realtime.on("conversation.interrupted", handle_conversation_interrupt)
    openai_realtime.on("error", handle_error)

    cl.user_session.set("openai_realtime", openai_realtime)
    coros = [
        openai_realtime.add_tool(tool_def, tool_handler)
        for tool_def, tool_handler in tools
    ]
    await asyncio.gather(*coros)


@cl.on_chat_start
async def start():
    # Initialize session variables for tracking conversation
    cl.user_session.set("last_assistant_text", "")
    
    # Use our personality-driven introduction
    welcome_message = get_introduction()
    await cl.Message(
        content=welcome_message,
        author="Assistant"
    ).send()
    await setup_openai_realtime()


@cl.on_message
async def on_message(message: cl.Message):
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime and openai_realtime.is_connected():
        # TODO: Try image processing with message.elements
        await openai_realtime.send_user_message_content(
            [{"type": "input_text", "text": message.content}]
        )
    else:
        await cl.Message(
            content="Please activate voice mode before sending messages!"
        ).send()


@cl.on_audio_start
async def on_audio_start():
    try:
        openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
        await openai_realtime.connect()
        logger.info("Connected to OpenAI realtime")
        # TODO: might want to recreate items to restore context
        # openai_realtime.create_conversation_item(item)
        return True
    except Exception as e:
        await cl.ErrorMessage(
            content=f"Failed to connect to OpenAI realtime: {e}"
        ).send()
        return False


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    
    # Set audio mode indicator in session to help with UI feedback
    cl.user_session.set("audio_mode_active", True)
    
    if openai_realtime and openai_realtime.is_connected():
        await openai_realtime.append_input_audio(chunk.data)
    else:
        logger.info("RealtimeClient is not connected")


@cl.on_audio_end
@cl.on_chat_end
@cl.on_stop
async def on_end():
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime and openai_realtime.is_connected():
        await openai_realtime.disconnect()
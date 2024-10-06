import os
import requests
import logging

from dns.e164 import query

import config

from markdown_it.rules_inline import image
from requests import Response
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional

from mongodb import *

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get MongoDB collection
conversation_collection = get_collection("telegram_conversations")

# Telegram bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_HARDCODED_TOKEN_HERE"
print(f"Loaded TOKEN: {TOKEN}")

# Conversation states
NAME, PHONE, ADMIN = range(3)
RAG_MODEL_URL = config.RAG_MODEL_URL

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Message]] = []

async def rag_mode_endpoint(request: QueryRequest) -> Response:
    # Convert the request data into the correct format
    payload = {
        "query": request.query,
        "conversation_history": [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
    }

    try:
        # Send the payload to the RAG_MODEL_URL
        response = requests.post(RAG_MODEL_URL, json=payload)
        response.raise_for_status()  # Raise an error for bad responses

        return response  # Return the actual response object from the RAG model
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to RAG model failed: {e}")
        raise HTTPException(status_code=500, detail="RAG model request failed.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Hello! I'm your AI assistant. How can I help you today?")
    return NAME  # Move to the next state if needed

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I'm here to help! Just ask me any question.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message_text = update.message.text

    # Retrieve conversation history
    conversation = conversation_collection.find_one({"user_id": user_id})
    history = conversation.get("history", []) if conversation else []

    # Prepare the request for the RAG query
    request = QueryRequest(
        query=message_text,
        conversation_history=[Message(**msg) for msg in history]
    )

    try:
        # Call the RAG model endpoint
        rag_response = await rag_mode_endpoint(request)
        response_text = rag_response.json().get('response')  # Assuming the response contains a 'response' field
    except HTTPException as e:
        logger.error(f"Error handling query: {e}")
        response_text = "I'm sorry, I couldn't process your question. Please try again later."

    # Update conversation history
    history.append({"role": "user", "content": message_text})
    history.append({"role": "assistant", "content": response_text})

    # Trim history if it's too long (keep last 20 messages)
    if len(history) > 20:
        history = history[-20:]

    # Update or insert conversation in MongoDB
    conversation_collection.update_one(
        {"user_id": user_id},
        {"$set": {"history": history}},
        upsert=True
    )

    # Send the response to the user
    await update.message.reply_text(response_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')

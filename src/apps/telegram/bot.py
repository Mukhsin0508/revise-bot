import json
import logging
from telegram import Update
from telegram.ext import ContextTypes
import os
import re

from src.apps.amocrm.amocrm_integration import handle_customer_info
from src.apps.mongodb.connection import get_collection

from src.apps.rag.rag_model_endpoint import rag_model_endpoint, QueryRequest, Message


# ======== Logging configuration ========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== Get MongoDB collection ========
conversation_collection = get_collection("telegram_conversations")

# ======== Telegram bot token ========
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_HARDCODED_TOKEN_HERE"
COMPANY_NAME = os.getenv("COMPANY_NAME", "SpineUP")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles messages sent by the bot from Telegram.
    :param update:
    :param context:
    :return:
    """
    user_id = update.effective_user.name
    user_message_text = update.message.text

    # ======== Retrieve only the last 10 conversation messages from MongoDB ========
    conversation = conversation_collection.find_one({"user_id":user_id})
    history = conversation.get("history", [])[-10:] if conversation else []
    # ====== Print Full Retrieved conversation history for debug (can be deleted) ======
    # print(f"Retrieved conversation history: {json.dumps(history, indent=2)}")

    # ==== Format the history into the role: user, role: assistant, content=content format for the rag_model input ====
    conversation_history = [Message(content=msg['content'], role=msg['role']) for msg in history]

    # ======== Prepare the request for the RAG query (important) ========
    request = QueryRequest(
        query=user_message_text,
        conversation_history=conversation_history,
        company_name=COMPANY_NAME
        )

    try:
        # ======== Call the RAG model endpoint ========
        rag_response = await rag_model_endpoint(request)

        # ======== Extract the response text ========
        response_text = rag_response['response']

        # ======== Remove any occurrence of "LEAD_CAPTURED" or "LEAD_CAPTURED: ..." from the response ========
        # ======== (needed to send clean response to User) ========
        response_text = re.sub(r'LEAD_CAPTURED(:.*?(\[.*?\])?)?$', '', response_text).strip()

        # ==== Handle customer info if it's part of the response (Required to send the client data to amocrm) ====
        await handle_customer_info(rag_response)
        customer_info =rag_response.get("additional_data", {}).get("customer_info", {})

        # ==== Combine response_text and customer_info into a single string for saving it in History MongoDB ====
        if customer_info:
            customer_info_str = json.dumps(customer_info, indent=2)
            content = f"{response_text}\n\n{customer_info_str}"
        else:
            content = response_text

        # ======== Update conversation history for "role": "user" ========
        history.append({
            "role":"user",
            "content":user_message_text
            })
        # ======== Update conversation history for "role": "assistant" ========
        history.append({
            "role":"assistant",
            "content":content,
            })

        # ======== Update or insert conversation in MongoDB ========
        conversation_collection.update_one(
            {"user_id":user_id},
            {"$set":{"history":history}},
            upsert=True
            )

        # ======== Send the response to the user ========
        await update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        await update.message.reply_text("Hozir javob yozvoraman, ozgina kutib turing, hop!?)")
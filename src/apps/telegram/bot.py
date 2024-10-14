import re
import json
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.config import settings
from src.apps.mongodb.connection import get_collection
from src.apps.telegram.utils.save_admin_message import save_message_to_history

from src.apps.rag.rag_model_endpoint import rag_model_endpoint, QueryRequest, Message


# ======== Logging configuration ========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== Get MongoDB collection ========
conversation_collection = get_collection("telegram_conversations")

# ======== Telegram bot token ========
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
COMPANY_NAME = settings.COMPANY_NAME
BUSINESS_USERNAME = settings.BUSINESS_USERNAME

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles messages sent by the bot from Telegram.
    :param update: Telegram update object containing the message data.
    :param context: Context object that contains useful bot data.
    """
    # incoming_full_update = update.to_dict()
    # print("Incoming update: ", json.dumps(incoming_full_update, indent=4))

    # ======= Username of the message sender ========
    business_username = update.business_message.from_user.name # admin or the client usernames

    # The username of the client, always comes intact in any update from telegram as chat username ========
    client_username = update.business_message.chat.username
    print("Client username: {}".format(client_username))


    # ========= Prevent bot from responding to its own business account messages ========
    if str(business_username) == BUSINESS_USERNAME:
        print(f"Message from our own business account {business_username} detected."
              f"Saving in conversation_history but not responding.")
        await save_message_to_history(update, client_username)
        return

    try:
        # ======== Handle both user messages and business messages dynamically ========
        user_message_text = None
        if update.message and update.message.text:
            user_message_text = update.message.text
        elif hasattr(update, 'business_message') and update.business_message and update.business_message.text:
            user_message_text = update.business_message.text
        else:
            logger.error("No valid message received")
            await update.message.reply_text("No valid message received.")
            return

    except AttributeError as e:
        logger.error(f"Error while handling message: {e}")
        return

    # ======== Retrieve only the last 10 conversation messages from MongoDB ========
    conversation = conversation_collection.find_one({"username": client_username})
    history = conversation.get("history", [])[-10:] if conversation else []

    # ==== Format the history into the role: user, role: assistant, content=content format for the rag_model input ====
    conversation_history = [Message(content=msg['content'], role=msg['role']) for msg in history]

    # ======== Prepare the request for the RAG query ========
    if user_message_text:
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
            response_text = re.sub(r'LEAD_CAPTURED(:.*?(\[.*?\])?)?$', '', response_text).strip()

            # ==== Handle customer info if it's part of the response ====
            # await handle_customer_info(rag_response)
            customer_info = rag_response.get("additional_data", {}).get("customer_info", {})

            # ==== Combine response_text and customer_info into a single string for saving it in History MongoDB ====
            if customer_info:
                customer_info_str = json.dumps(customer_info, indent=2)
                content = f"{response_text}\n\n{customer_info_str}"
            else:
                content = response_text

            # ======== Update conversation history for "role": "user" ========
            history.append({"role": "user", "content": user_message_text})

            # ======== Update conversation history for "role": "assistant" ========
            history.append({"role": "assistant", "content": content})

            # ======== Update or insert conversation in MongoDB ========
            conversation_collection.update_one(
                {"username": client_username},
                {"$set": {"history": history}},
                upsert=True
            )

            # ======== Send the response to the user in bot or in the PM ========
            if update.message:
                await update.message.reply_text(response_text)
            elif hasattr(update, 'business_message') and update.business_message:
                await update.business_message.reply_text(response_text)
            else:
                logger.error("No valid message type found for response.")


        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            if update.message:
                await update.message.reply_text("Hozir javob yozvoraman, ozgina kutib turing, hop!?)")
            elif hasattr(update, 'business_message') and update.business_message:
                await update.business_message.reply_text("Hozir javob yozvoraman, ozgina kutib turing, hop?)")
    else:
        logger.error("Received a message with no text.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


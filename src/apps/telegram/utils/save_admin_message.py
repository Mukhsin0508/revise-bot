from src.apps.telegram.bot import Update
from src.apps.mongodb.connection import get_collection


# ======== Get MongoDB collection ========
conversation_collection = get_collection("telegram_conversations")


async def save_message_to_history(update: Update, client_username):
    """
    Save the admin_message to MongoDB conversation history.
    This function is used to save the admin_message to MongoDB conversation history.

    :reason: In the Personal Telegram Business account, the bot is connected to for I/O and when the admin responds
    to the client, it was being progressed through the RAG_MODEL endpoint as well, so this resulted in generating a
    response_text and sending it to the current Telegram Chat. To avoid this, I am preventing the admin_messages from
    sent to the rag_model_endpoint, but save it in the conversation_history collection in MongoDB for future
    rag_model_endpoint requests. This way the rag_model knows what the admin and the client talked in the event of
    stopping the bot in Telegram.

    :param update: Telegram update object
    :param client_username: Username of the CHAT between the client and the Telegram Business Account
    :return: None
    :admin_message: admin_message is being taken from the update object.
    :save_message_to_history: save_message_to_history only gets triggered if the
        update.business_message.from_user.username is the business_username given in env file.
    """

    # ======== Get the admin_message ========
    admin_message = update.business_message.text

    # ======== Append the message to conversation_history ========
    conversation = conversation_collection.find_one({"username": client_username})
    history = conversation.get("history", []) if conversation else []
    history.append({"role": "admin", "content": admin_message})

    # ======== Update or insert the conversation in MongoDB ========
    conversation_collection.update_one(
        {"username":client_username},  # Query to find the document by username (business_username)
        {"$set":{"history":history}},  # Set the 'history' field to the current history value
        upsert=True  # If no document is found with the username, insert a new one (update + insert)
    )



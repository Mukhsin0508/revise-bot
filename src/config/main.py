import os
import sys
from telegram.ext import (Application, MessageHandler, Updater, filters, )

# ======== Add the project root directory to the Python path ========
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.apps.telegram.bot import handle_message, error_handler

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main() -> None:
    print("Starting bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ======== Add other handlers ========
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)

    # ======== Start the bot ========
    print("Starting Telegram bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()

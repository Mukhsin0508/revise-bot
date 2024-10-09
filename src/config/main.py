import os
import sys
import dotenv
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.telegram.bot import handle_message

# Load environment variables
dotenv.load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_HARDCODED_TOKEN_HERE"  # Update to match your variable

def main() -> None:
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()

    # Add other handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Starting Telegram bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()

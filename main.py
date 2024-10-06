import os
import dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from bot import start, help_command, handle_message, error_handler, NAME, PHONE, ADMIN

# Load environment variables
dotenv.load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_HARDCODED_TOKEN_HERE"  # Update to match your variable

def main() -> None:
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(conv_handler)

    # Add other handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    print("Starting Telegram bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()

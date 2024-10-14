import os
from dotenv import load_dotenv

load_dotenv()

# ======= ENV ========
ENV = os.getenv("ENV")

# =============== Development Telegram Configurations ====================
TELEGRAM_DEV_BOT_TOKEN= os.getenv('TELEGRAM_DEV_BOT_TOKEN')
DEV_BOT_USERNAME= os.getenv('DEV_BOT_USERNAME')
DEV_BUSINESS_USERNAME= os.getenv('DEV_BUSINESS_USERNAME')
DEV_COMPANY_NAME = os.getenv('DEV_COMPANY_NAME')

# =============== Production Telegram Bot Configurations ====================
TELEGRAM_REVITE_BOT_TOKEN=os.getenv('TELEGRAM_REVITE_BOT_TOKEN')
REVITE_BOT_USERNAME= os.getenv('REVITE_BOT_USERNAME')
BUSINESS_USERNAME=os.getenv('BUSINESS_USERNAME')
COMPANY_NAME = os.getenv('COMPANY_NAME')

TELEGRAM_BOT_TOKEN = TELEGRAM_DEV_BOT_TOKEN if ENV == 'development' else TELEGRAM_REVITE_BOT_TOKEN
TELEGRAM_BOT_USERNAME = DEV_BOT_USERNAME if ENV == 'development' else REVITE_BOT_USERNAME
BUSINESS_USERNAME = DEV_BUSINESS_USERNAME if ENV == 'development' else BUSINESS_USERNAME
COMPANY_NAME = DEV_COMPANY_NAME if ENV == 'development' else COMPANY_NAME

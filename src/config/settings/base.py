import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Development URL (localhost)
DEV_URL = os.getenv("DEV_URL")

# Production URL (your actual production server)
PROD_URL = os.getenv("PROD_URL")

# Set the environment variable (development by default)
ENV = os.getenv('ENV')
RAG_MODEL_URL = DEV_URL if ENV == 'development' else PROD_URL
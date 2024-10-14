import os
from amocrm.v2 import Lead, tokens
from typing import Dict
import logging
from dotenv import load_dotenv
import asyncio

load_dotenv()

# ===== Logging configuration =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SUBDOMAIN = os.getenv("SUBDOMAIN")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_CODE = os.getenv("AUTH_CODE")

# print("CLIENT_ID:", CLIENT_ID)
# print("CLIENT_SECRET:", CLIENT_SECRET)
# print("SUBDOMAIN:", SUBDOMAIN)
# print("REDIRECT_URI:", REDIRECT_URI)
# print("AUTH_CODE:", AUTH_CODE)


async def handle_customer_info(rag_response):
    customer_info = rag_response.get("additional_data", {}).get("customer_info", {})
    logger.info(f"Received Customer info: {customer_info}")
    if customer_info:
        await send_data_to_amocrm(customer_info)
    else:
        logger.warning("No customer information found in the RAG response.")


async def send_data_to_amocrm(customer_info):
    """
    :does: This method send data to Amocrm
    :param customer_info:
    :return:
    """

    try:
        tokens.default_token_manager(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            subdomain='muxsinmuxtorov01',  # your amoCRM account subdomain (e.g. company.amocrm.com)
            redirect_url=REDIRECT_URI,
            storage=tokens.FileTokensStorage()  # storage to persist tokens
        )
        tokens.default_token_manager.init(
            code=AUTH_CODE, skip_error=True
        )
        logger.info("Token initialization successful.")
    except Exception as e:
        logger.error(f"Error during token initialization: {str(e)}")
        return {"Error":"Token initialization failed."}

    lead_data = (f"Имя:{customer_info.get('name')} \n"
                 f"Номер_телефона:{customer_info.get('phone')} \n"
                 f"Услуга:{customer_info.get('service') or 'Hizmat aniqlanmadi'} \n"
                 f"Платформа: Telegram Bot")

    lead_ = Lead.objects.create(name=lead_data)

    # Return success response
    leads = Lead.objects.all()

    for lead in leads:
        print(f'Lead ID: {lead.id}, Lead Name: {lead.name}')

    return {"Success": True}  # Optionally return a success message

#
# if __name__ == "__main__":
#     data = {
#         'additional_data':{
#             'customer_info':{
#                 'name':'Shaxzod',
#                 'phone':'+998993233532',
#                 'service':"bel og'rig'ini davolash dasturi"
#                 }
#             }
#         }
#     asyncio.run(handle_customer_info(data))
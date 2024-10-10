import os
from amocrm.v2 import Lead, tokens
from typing import Dict
import logging
import asyncio

# ===== Logging configuration =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SUBDOMAIN = os.getenv("SUBDOMAIN")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_CODE = os.getenv("AUTH_CODE")


def send_data_to_amocrm(customer_info) -> Dict[str, str]:
    """
    :does: This method sends data to Amocrm
    :param customer_info:
    :return:
    """

    try:
        tokens.default_token_manager(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            subdomain=SUBDOMAIN,
            redirect_url=REDIRECT_URI,
            storage=tokens.FileTokensStorage()
            )
        # Uncomment the next line if you need to initialize with AUTH_CODE
        # tokens.default_token_manager.init(code=AUTH_CODE, skip_error=True)
        logger.info("Token initialization successful.")
    except Exception as e:
        logger.error(f"Error during token initialization: {str(e)}")
        return {"Error":"Token initialization failed."}

    lead_data = (f"Имя: {customer_info.get('name')} \n"
                 f"Номер_телефона: {customer_info.get('phone')} \n"
                 f"Услуга: {customer_info.get('service', 'Hizmat aniqlanmadi')} \n"
                 f"Платформа: Telegram Bot")

    try:
        lead = Lead.objects.create(name=lead_data)
        return {"Lead created successfully":lead_data}
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        return {"Error":str(e)}


async def handle_customer_info(rag_response):
    """
    Extracts name and phone from the rag response
    Required to send the client data to send_data_to_amocrm.
    :param rag_response:
    :return:
    """
    customer_info = rag_response.get("additional_data", {}).get("customer_info", {})
    logger.info(f"Received Customer info: {customer_info}")
    if customer_info and customer_info.get('name') and customer_info.get('phone'):
        amocrm_response = send_data_to_amocrm(customer_info)
        logger.info(f"Amocrm response: {amocrm_response}")
    else:
        logger.warning("Customer info is missing name or phone.")


if __name__ == "__main__":
    # Correctly define customer_info as a dictionary
    data = {
        'additional_data':{
            'customer_info':{
                'name':'Shaxzod',
                'phone':'+998993233532',
                'service':"bel og'rig'ini davolash dasturi"
                }
            }
        }

    # Run the async function in an event loop
    asyncio.run(handle_customer_info(data))

# ===== Imports =====
import json
import requests
import logging
from pydantic import BaseModel
from typing import List, Optional
from fastapi import HTTPException
from src.config import settings

# ===== Logging configuration =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== RAG Model URL =====
RAG_MODEL_URL = settings.RAG_MODEL_URL


# ===== Pydantic models =====
class Message(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Message]] = ""
    company_name: str = 'SpineUP'


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    service: Optional[str] = None


# ===== RAG Model Endpoint function =====
async def rag_model_endpoint(request: QueryRequest):
    """
    Endpoint for rag model
    :role: rag model
    :purpose: Rag model endpoint for sending query request and conversation history and company name
    :param request:
    :return: Returns response from rag model for the telegram user message
    """
    payload = {
        "query": request.query,
        "conversation_history": [{"role": msg.role, "content": msg.content} for msg in request.conversation_history],
        "company_name": request.company_name
    }

    try:
        formatted_payload = json.dumps(payload, indent=4)
        # ====== Print Full payload for debug (can be deleted) ======
        print(f"Payload being sent to RAG model: {formatted_payload}")

        # ======== Print the exact payload structure being sent (can be deleted) ========
        print(f"Exact payload being sent to RAG model: {payload}")

        # ========= Send the payload to the RAG_MODEL_URL =========
        response = requests.post(RAG_MODEL_URL, json=payload)
        response.raise_for_status()  # ========= Raise an error for bad responses =========

        # ========= Print the full response from Rag Model (can be deleted) =======
        print("Full Response from RAG model: ", json.dumps(response.json(), indent=4))
        # ========= Print the full seconds waited for Rag Model's response (can be deleted) =======
        print("Total Seconds waited for Response: ", response.elapsed.total_seconds())

        # ========= Parse the response into json format =========
        response_data = response.json()

        return response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to RAG model failed: {e}")
        raise HTTPException(status_code=500, detail="RAG model request failed.")

from fastapi import APIRouter
import uuid, os
from dotenv import load_dotenv
import httpx

router = APIRouter(
    prefix="/payments",
    tags=['payments']
)

load_dotenv()

client_id = os.getenv("CASHFREE_CILENT_ID")
secret_key = os.getenv("CASHFREE_CLIENT_SECRET_KEY")

@router.get("/payment_link")
async def execute_cashfree_script():
    url = "https://sandbox.cashfree.com/pg/links"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-version": "2022-09-01",
        "x-client-id": client_id,
        "x-client-secret": secret_key,
        "x-idempotency-key": str(uuid.uuid4()),
        "x-request-id": str(uuid.uuid4()),
    }

    data = {
        "customer_details": {
            "customer_phone": "6378639230",
            "customer_email": "utkarsharma12311@gmail.com",
            "customer_name": "Utkarsh Sharma"
        },
        "link_notify": {
            "send_sms": True,
            "send_email": True
        },
        "link_id": str(uuid.uuid4()),
        "link_amount": 20,
        "link_currency": "INR",
        "link_purpose": "testing worker employment"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

        if response.status_code // 100 != 2:
            return {"error": f"Failed to execute Cashfree script. Status code: {response.status_code}", "response_data": response.text}

    return {"status_code": response.status_code, "response_data": response.json()}

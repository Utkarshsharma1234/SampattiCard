import uuid
import httpx


async def execute_cashfree_script():
    url = "https://sandbox.cashfree.com/pg/links"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-version": "2022-09-01",
        "x-client-id": "1994686bae5c30d3e4be55a6a9864991",
        "x-client-secret": "6ed2dd114b39ca3c84dd2429a1b64e55b5904c69",
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
        "link_amount": 1500,
        "link_currency": "INR",
        "link_purpose": "testing worker employment"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

        if response.status_code // 100 != 2:
            return {"error": f"Failed to execute Cashfree script. Status code: {response.status_code}", "response_data": response.text}

    return {"status_code": response.status_code, "response_data": response.json()}
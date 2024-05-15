import requests

def send_whatsapp_message(api_key, namespace, cust_name, dw_name, month_year, session_id, receiver_number):
    url = "https://orailap.azurewebsites.net/api/cloud/Dialog"
    headers = {
        "API-KEY": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "template": {
            "namespace": namespace,
            "name": "salary_payment_link_for_employer",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": cust_name
                        },
                        {
                            "type": "text",
                            "text": dw_name
                        },
                        {
                            "type": "text",
                            "text": month_year
                        }
                    ]
                },
                {
                    "index": 0,
                    "parameters": [
                        {
                            "type": "text",
                            "text": session_id
                        }
                    ],
                    "sub_type": "url",
                    "type": "button"
                }
            ],
            "language": {
                "code": "en",
                "policy": "deterministic"
            }
        },
        "messaging_product": "whatsapp",
        "to": receiver_number,
        "type": "template"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
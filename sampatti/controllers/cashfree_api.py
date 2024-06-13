from datetime import datetime
from queue import Full
from fastapi import HTTPException
import json, uuid, requests, os
from cashfree_pg.api_client import Cashfree
from cashfree_verification.api_client import Cashfree as Cashfree_Verification
from cashfree_verification.models.upi_mobile_request_schema import UpiMobileRequestSchema
from cashfree_verification.models.pan_advance_request_schema import PanAdvanceRequestSchema
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from .. import models
from .whatsapp_message import send_whatsapp_message
from sqlalchemy.orm import Session
from sqlalchemy import update
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import update

load_dotenv()
verification_id= os.environ.get('CASHFREE_VERIFICATION_ID')
verification_secret = os.environ.get('CASHFREE_VERIFICATION_SECRET')

pg_id = os.environ.get('CASHFREE_PG_ID')
pg_secret = os.environ.get('CASHFREE_PG_SECRET')

orai_api_key = os.environ.get('ORAI_API_KEY')
orai_namespace = os.environ.get('ORAI_NAMESPACE')



def fetch_vpa(workerNumber : int):
    Cashfree_Verification.XClientId = verification_id
    Cashfree_Verification.XClientSecret = verification_secret
    Cashfree_Verification.XEnvironment = Cashfree_Verification.XProduction
    uuid_value = uuid.uuid4().hex
    
    user_info = UpiMobileRequestSchema(mobile_number= f"{workerNumber}", verification_id = uuid_value)

    api_response = None
    try:
        api_response = Cashfree_Verification().vrs_upi_mobile_verification(user_info, None)
        if not api_response or not api_response.data:
            raise HTTPException(status_code=400, detail="Bad request: No response from API")
        
    except Exception as e:
        # Log the exception and raise a 400 HTTP exception with the error message
        print(e)
        raise HTTPException(status_code=400, detail=f"Bad request: No response from API")
    
    response = dict(api_response.data)
    return response

# adding a vendor to the cashfree dashboard.

def add_a_vendor(vpa : str, workerNumber : int, name : str, pan : str, db : Session, employerNumber : int):

    uuid_value = uuid.uuid4().hex
    payload = {
    "vendor_id": uuid_value,
    "status": "ACTIVE",
    "name": name,
    "email": "johndoe@gmail.com",
    "phone": f"{workerNumber}",
    "verify_account": True,
    "dashboard_access": False,
    "schedule_option": 1,
    "upi": {
      "vpa": vpa,
  	  "account_holder": name
    },
    "kyc_details": {
        "account_type": "INDIVIDUAL",
        "business_type": "Education",
        "pan": pan
    }
}

    headers = {
        "X-Client-Id" : pg_id,
        "X-Client-Secret" : pg_secret,
        "Content-Type" : "application/json",
        "x-api-version" : "2023-08-01"
    }


    url = "https://api.cashfree.com/pg/easy-split/vendors"

    response = requests.post(url, json=payload, headers=headers)

    response_data = json.loads(response.text)
    vendor_id = response_data.get('vendor_id')
    update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employerNumber).values(vendor_id= vendor_id)

    db.execute(update_statement)
    db.commit()
    print(response.text)
    
    return uuid_value

# checking the order status

def check_order_status(order_id):

    url = f"https://api.cashfree.com/pg/orders/{order_id}"


    headers = {
        "x-client-id": pg_id,
        "x-client-secret": pg_secret,
        "x-api-version" : "2023-08-01"
    }

    response = requests.get(url, headers=headers)

    print(response.text)
    response_data = json.loads(response.text)
    order_status = response_data.get('order_status')
    return order_status
    

def pan_verification(pan : str, name : str):
    Cashfree_Verification.XClientId = verification_id
    Cashfree_Verification.XClientSecret = verification_secret
    Cashfree_Verification.XEnvironment = Cashfree_Verification.XProduction
    uuid_val = uuid.uuid4().hex

    pan_schema = PanAdvanceRequestSchema(pan=pan, verification_id=uuid_val, name=name)

    api_response = None
    try:
        api_response = Cashfree_Verification().vrs_pan_advance_verification(pan_schema, None)
        # print(api_response.data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Bad request: No response from API")
    
    response = dict(api_response.data)
    return response



def payment_link_generation(db : Session):
    Cashfree.XClientId = pg_id
    Cashfree.XClientSecret = pg_secret
    Cashfree.XEnvironment = Cashfree.XProduction
    x_api_version = "2023-08-01"

    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year

    payment_ids = []
    total_workers = db.query(models.worker_employer).all()
    
    for item in total_workers:

        customerDetails = CustomerDetails(customer_id= f"{item.worker_number}", customer_phone= f"{item.employer_number}")
        createOrderRequest = CreateOrderRequest(order_amount = item.salary_amount, order_currency="INR", customer_details=customerDetails)
        try:
            api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
            # print(api_response.data)
        except Exception as e:
            print(e)

        response = dict(api_response.data)
        payment_session_id = response["payment_session_id"]

        send_whatsapp_message(api_key=orai_api_key,namespace=orai_namespace,cust_name=item.employer_number,dw_name=item.worker_number, month_year= f"{current_month} {current_year}",session_id=payment_session_id,receiver_number=f"91{item.employer_number}")

        update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == item.worker_number).where(models.worker_employer.c.employer_number == item.employer_number).values(order_id= response["order_id"])


        db.execute(update_statement)
        db.commit()
        payment_ids.append(payment_session_id)

    return payment_ids


def custom_json_encoder(obj):
    if obj is None:
        return "null"
    else:
        raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")


def unsettled_balance(db : Session):

    
    headers = {
        'x-client-id': pg_id,
        'x-client-secret': pg_secret,
        'Content-Type': 'application/json'
    }

    total_workers = db.query(models.worker_employer).all()
    for worker in total_workers:
        
        status = check_order_status(order_id=worker.order_id)
        if(status == "PAID"):

            url = f'https://api.cashfree.com/api/v2/easy-split/orders/{worker.order_id}/split'

            data = {
                "split": [
                    {
                        "vendorId": worker.vendor_id,
                        "amount" : worker.salary_amount,
                        "percentage" : None
                    }
                ],
                "splitType" : "ORDER_AMOUNT"
            }

            json_data = json.dumps(data)
            response = requests.post(url, headers=headers, data=json_data)

            print(response.text)

        else:
            continue

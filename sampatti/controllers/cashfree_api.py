import json, uuid, requests, os
from cashfree_verification.api_client import Cashfree as Cashfree_Verification
from cashfree_verification.models.upi_mobile_request_schema import UpiMobileRequestSchema
from cashfree_verification.models.pan_advance_request_schema import PanAdvanceRequestSchema
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import update
from sampatti.env import config
from dotenv import load_dotenv

load_dotenv()
verification_id= os.environ.get('CASHFREE_VERIFICATION_ID')
verification_secret = os.environ.get('CASHFREE_VERIFICATION_SECRET')

pg_id = os.environ.get('CASHFREE_PG_ID')
pg_secret = os.environ.get('CASHFREE_PG_SECRET')

# fetching the vpa

def fetch_vpa(workerNumber : int):
    Cashfree_Verification.XClientId = verification_id
    Cashfree_Verification.XClientSecret = verification_secret
    Cashfree_Verification.XEnvironment = Cashfree_Verification.XProduction
    uuid_value = uuid.uuid4().hex
    
    user_info = UpiMobileRequestSchema(mobile_number= f"{workerNumber}", verification_id = uuid_value)

    api_response = None
    try:
        api_response = Cashfree_Verification().vrs_upi_mobile_verification(user_info, None)
        # print(api_response.data)
    except Exception as e:
        print(e)
    
    response = dict(api_response.data)
    return response


# generating the payment link

def payment_link_generation(workerNumber : int, employerNumber : int, db : Session):
    Cashfree.XClientId = pg_id
    Cashfree.XClientSecret = pg_secret
    Cashfree.XEnvironment = Cashfree.XProduction
    x_api_version = "2023-08-01"

    item = db.query(models.worker_employer).filter((models.worker_employer.c.worker_number == workerNumber) & (models.worker_employer.c.employer_number == employerNumber)).first()

    customerDetails = CustomerDetails(customer_id= f"{workerNumber}", customer_phone= f"{employerNumber}")

    createOrderRequest = CreateOrderRequest(order_amount = item.salary_amount, order_currency="INR", customer_details=customerDetails)

    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        # print(api_response.data)
    except Exception as e:
        print(e)
    
    
    response = dict(api_response.data)
    update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employerNumber).values(order_id= response["order_id"])

    db.execute(update_statement)
    db.commit()

    payment_session_id = response["payment_session_id"]
    return {"payment_session_id" : f"https://sampatticard.in/payment/{payment_session_id}"}


# adding a vendor to the cashfree dashboard.

def add_a_vendor(vpa : str, workerNumber : int, name : str, pan : str):

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

    return uuid_value
    print(response.text)

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
    version = "2023-08-01"

    pan_schema = PanAdvanceRequestSchema(pan=pan, verification_id="randomvalue", name=name)

    api_response = None
    try:
        api_response = Cashfree_Verification().vrs_pan_advance_verification(pan_schema, None)
        # print(api_response.data)
    except Exception as e:
        print(e)
    
    response = dict(api_response.data)
    return response


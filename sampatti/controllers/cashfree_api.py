import json, uuid, requests
from cashfree_verification.api_client import Cashfree
from cashfree_verification.models.upi_mobile_request_schema import UpiMobileRequestSchema
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import update


verification_id="CF247908CNU1BNNCGJPB1I184JQ0"
verification_secret="cfsk_ma_prod_bb3c4a5baf101049ea7ee3a6bc46810e_3cfe1b33"

pg_id="2479085b6888e2c6f308be5f99809742"
pg_secret="cfsk_ma_prod_621ba66b6ae1480acf735eec2769d625_25e34a9c"


# fetching the vpa

def fetch_vpa(workerNumber : int):
    Cashfree.XClientId = verification_id
    Cashfree.XClientSecret = verification_secret
    Cashfree.XEnvironment = Cashfree.XProduction
    uuid_value = uuid.uuid4().hex

    user_info = UpiMobileRequestSchema(mobile_number= f"{workerNumber}", verification_id = uuid_value)
    api_response = None
    try:
        api_response = Cashfree().vrs_upi_mobile_verification(user_info, None)
        print(api_response.data)
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
    return f"https://sampatticard.in/payment/{payment_session_id}"


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
    




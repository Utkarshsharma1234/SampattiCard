from datetime import datetime
from queue import Full
import random
import string
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
from .. import schemas

load_dotenv()
verification_id= os.environ.get('CASHFREE_VERIFICATION_ID')
verification_secret = os.environ.get('CASHFREE_VERIFICATION_SECRET')

pg_id = os.environ.get('CASHFREE_PG_ID')
pg_secret = os.environ.get('CASHFREE_PG_SECRET')

orai_api_key = os.environ.get('ORAI_API_KEY')
orai_namespace = os.environ.get('ORAI_NAMESPACE')



def generate_unique_id(length=8):

    unique_id = uuid.uuid4().hex
    letters_only = ''.join([char for char in unique_id if char.isalpha()])[:length]
    if len(letters_only) < length:
        letters_only += ''.join(random.choices(string.ascii_letters, k=length - len(letters_only)))
    return letters_only


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


def fetch_multiple_vpa(workerNumber : int):
    
    uuid_val = generate_unique_id()
    url = "https://api.cashfree.com/verification/upi/mobile"

    payload = {
        "verification_id": uuid_val,
        "mobile_number": f"{workerNumber}",
        "additional_vpas": True
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-client-id": verification_id,
        "x-client-secret": verification_secret
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    response_data = json.loads(response.text)
    vpa = response_data.get('vpa')
    additional_vpas = response_data.get('additional_vpas')
    name_at_bank = response_data.get('name_at_bank')
    if name_at_bank is None:
        name_at_bank = "INVALID"
    if len(additional_vpas) == 0:
        additional_vpas = []
    additional_vpas.append(vpa)

    multiple_vpa = []
    for vpa in additional_vpas:
        record = {
            "text": vpa,
            "postback": f"data_vpa_upi_id={vpa}"
        }
        multiple_vpa.append(record)
    
    return {
        "name_at_bank" : name_at_bank,
        "vpa_array" : multiple_vpa
    }


# adding a vendor to the cashfree dashboard.

def add_a_vendor(request : schemas.Vendor, db: Session):

    if request.vpa == "None":
        request.vpa = None

    elif request.accountNumber == "None":
        request.accountNumber = None

    uuid_value = uuid.uuid4().hex
    payload = {
    "vendor_id": uuid_value,
    "status": "ACTIVE",
    "name": request.name,
    "email": "johndoe@gmail.com",
    "phone": f"{request.workerNumber}",
    "verify_account": True,
    "dashboard_access": False,
    "schedule_option": 1,
    "kyc_details": {
        "account_type": "INDIVIDUAL",
        "business_type": "Education",
        "pan": request.pan
    }
}
    
    if request.vpa:
        payload["upi"] = {
            "vpa": request.vpa,
            "account_holder": request.name
        }


    elif request.accountNumber:
        payload["bank"] = {
            "account_number": request.accountNumber,
            "account_holder": request.name,
            "ifsc": request.ifsc
        }

    print(payload)
    headers = {
        "X-Client-Id" : pg_id,
        "X-Client-Secret" : pg_secret,
        "Content-Type" : "application/json",
        "x-api-version" : "2023-08-01"
    }

    existing_worker_list = db.query(models.worker_employer).filter(models.worker_employer.c.worker_number == request.workerNumber).all()

    existing_vendor_id = None
    for existing_worker in existing_worker_list:
        if existing_worker.vendor_id:
            existing_vendor_id = existing_worker.vendor_id
            break

    if not existing_vendor_id :
        url = "https://api.cashfree.com/pg/easy-split/vendors"

        response = requests.post(url, json=payload, headers=headers)

        response_data = json.loads(response.text)
        vendor_id = response_data.get('vendor_id')
        update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == request.workerNumber).where(models.worker_employer.c.employer_number == request.employerNumber).values(vendor_id= vendor_id)

        db.execute(update_statement)
        db.commit()
        print(response.text)
        print(f"The vendor has been added successfully. Vendor Id : {vendor_id}")
        
        return uuid_value
    
    else:
        vendor_id = existing_vendor_id
        print(vendor_id)
        update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == request.workerNumber).where(models.worker_employer.c.employer_number == request.employerNumber).values(vendor_id= vendor_id)
        print(f"This vendor already exists.")
        db.execute(update_statement)
        db.commit()

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
    
# pan verification

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


# payment link generation

def payment_link_generation(db : Session):
    Cashfree.XClientId = pg_id
    Cashfree.XClientSecret = pg_secret
    Cashfree.XEnvironment = Cashfree.XProduction
    x_api_version = "2023-08-01"

    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year

    payment_ids = []
    total_workers = db.query(models.worker_employer).all()
    total_domestic = db.query(models.Domestic_Worker).all()
    
    for item in total_workers:
        dummy_number = item.employer_number
        actual_number = int(str(dummy_number)[2:])
        
        customerDetails = CustomerDetails(customer_id= f"{item.worker_number}", customer_phone= f"{actual_number}")
        createOrderRequest = CreateOrderRequest(order_amount = item.salary_amount, order_currency="INR", customer_details=customerDetails)
        try:
            api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
            # print(api_response.data)
        except Exception as e:
            print(e)

        response = dict(api_response.data)
        payment_session_id = response["payment_session_id"]

        worker_name = ""
        for worker in total_domestic:
            if worker.workerNumber == item.worker_number:
                worker_name = worker.name
                break

        send_whatsapp_message(api_key=orai_api_key,namespace=orai_namespace,cust_name=item.employer_number,dw_name=worker_name, month_year= f"{current_month} {current_year}",session_id=payment_session_id,receiver_number=f"{dummy_number}")

        update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == item.worker_number).where(models.worker_employer.c.employer_number == item.employer_number).values(order_id= response["order_id"])

        db.execute(update_statement)
        db.commit()
        payment_ids.append(payment_session_id)

    return payment_ids

# unsettled balance

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

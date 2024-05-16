import os
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from .. import models
from .whatsapp_message import send_whatsapp_message
from sqlalchemy.orm import Session
from sqlalchemy import update
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

pg_id = os.environ.get('CASHFREE_PG_ID')
pg_secret = os.environ.get('CASHFREE_PG_SECRET')

orai_api_key = os.environ.get('ORAI_API_KEY')
orai_namespace = os.environ.get('ORAI_NAMESPACE')

current_month = datetime.now().strftime("%B")
current_year = datetime.now().year

def payment_link_generation(db : Session):
    Cashfree.XClientId = pg_id
    Cashfree.XClientSecret = pg_secret
    Cashfree.XEnvironment = Cashfree.XProduction
    x_api_version = "2023-08-01"

    payment_ids = []
    total_workers = db.query(models.worker_employer).all()
    for item in total_workers:
        
    # item = db.query(models.worker_employer).filter((models.worker_employer.c.worker_number == workerNumber) & (models.worker_employer.c.employer_number == employerNumber)).first()
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
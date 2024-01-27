import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import httpx
from .. import schemas
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import userControllers
from ..payments import cashfree
from ..controllers import salary_slip_generation
import uuid

router = APIRouter(
    prefix="/user",
    tags=['users']
)


@router.post("/employer/create")
def create_employer(request : schemas.Employer, db : Session = Depends(get_db)):
    return userControllers.create_employer(request, db)


@router.get("/employer/{employerNumber}", response_model = schemas.Employer_Schema)
def get_employer(employerNumber : int, db :Session = Depends(get_db)):
    return userControllers.get_employer(employerNumber,db)

@router.get("/domestic_worker/{workerNumber}", response_model = schemas.Domestic_Worker_Schema)
def get_domestic_worker(workerNumber,db:Session = Depends(get_db)):
    return userControllers.get_domestic_worker(workerNumber,db)

@router.post('/domestic_worker/create')
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session = Depends(get_db)):
    return userControllers.create_domestic_worker(request, db)

@router.get("/generate_salary_slip", response_class=FileResponse, name="Generate Salary Slip")
async def generate_salary_slip_endpoint():

    salary_slip_generation.generate_salary_slip()

    static_pdf_path = os.path.join(os.getcwd(), 'static', 'salary_slip.pdf')

    return FileResponse(static_pdf_path, media_type='application/pdf', filename="salary_slip.pdf")

@router.get("/payment_link")
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

@router.post("/contract")
def contract_generation(request : schemas.Contract, db : Session = Depends(get_db)):
    return userControllers.create_contract(request,db)

    
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import userControllers, salary_slip_generation
from ..controllers import employment_contract_gen
from datetime import datetime
import requests


router = APIRouter(
    prefix="/user",
    tags=['users']
)


@router.post("/employer/create")
def create_employer(request : schemas.Employer, db : Session = Depends(get_db)):
    return userControllers.create_employer(request, db)

@router.post('/domestic_worker/create')
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session = Depends(get_db)):
    return userControllers.create_domestic_worker(request, db)


@router.post('/talk_to_agent/create')
def create_talk_to_agent_employer(employerNumber : int, db : Session = Depends(get_db)):
    return userControllers.create_talk_to_agent_employer(employerNumber, db)

@router.put('/domestic_worker/update')
def update_worker(oldNumber : int, newNumber: int, db : Session = Depends(get_db)):
    return userControllers.update_worker(oldNumber,newNumber, db)


@router.post("/salary")
def insert_salary(request : schemas.Salary, db : Session = Depends(get_db)):
    return userControllers.insert_salary(request, db)


@router.get("/generate_salary_slip/{workerNumber}", response_class=FileResponse, name="Generate Salary Slip")
def generate_salary_slip_endpoint(workerNumber : int, db: Session = Depends(get_db)):

    salary_slip_generation.generate_salary_slip(workerNumber, db)
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year

    worker = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.workerNumber == workerNumber).first()

    static_pdf_path = os.path.join(os.getcwd(), 'static', f"{worker.id}_SS_{current_month}_{current_year}.pdf")

    return FileResponse(static_pdf_path, media_type='application/pdf', filename=f"{worker.id}_SS_{current_month}_{current_year}.pdf")


@router.post("/contract")
def contract_generation(request : schemas.Contract, db : Session = Depends(get_db)):

    employment_contract_gen.create_employment_record_pdf(request, db)

    static_pdf_path = os.path.join(os.getcwd(), 'contracts', f"{request.workerNumber}_ER_{request.employerNumber}.pdf")

    return FileResponse(static_pdf_path, media_type='application/pdf', filename=f"{request.workerNumber}_ER_{request.employerNumber}.pdf")
    
    
@router.post("/generate_contract")
def generate(workerNumber: int, employerNumber: int):

    url = "https://waba-v2.360dialog.io/media"
    static_pdf_path = os.path.join(os.getcwd(), 'contracts', f"{workerNumber}_ER_{employerNumber}.pdf")

    if os.path.exists(static_pdf_path):
        headers = {
            "D360-API-KEY": "DFrBXp0qYnJIOvtWrFUPc4TkAK"
        }
        data = {
            "messaging_product": "whatsapp"
        }
        files = {
            "file": (f"{workerNumber}_ER_{employerNumber}.pdf", open(static_pdf_path, "rb"), "application/pdf")
        }

        try:
            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            return response.json()
        except Exception as e:

            print(f"Exception occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    else:
        raise HTTPException(status_code=404, detail="PDF file not found")
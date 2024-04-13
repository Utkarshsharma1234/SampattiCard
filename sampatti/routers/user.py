import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from .. import schemas
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import userControllers, salary_slip_generation
from ..controllers import employment_contract_gen
from datetime import datetime


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


@router.post("/salary")
def insert_salary(request : schemas.Salary, db : Session = Depends(get_db)):
    return userControllers.insert_salary(request, db)


@router.get("/generate_salary_slip/{workerNumber}", response_class=FileResponse, name="Generate Salary Slip")
def generate_salary_slip_endpoint(workerNumber : int, db: Session = Depends(get_db)):

    salary_slip_generation.generate_salary_slip(workerNumber, db)
    current_month = datetime.now().strftime("%B")

    static_pdf_path = os.path.join(os.getcwd(), 'static', f"{workerNumber}_salary_slip_{current_month}.pdf")

    return FileResponse(static_pdf_path, media_type='application/pdf', filename=f"{workerNumber}_salary_slip_{current_month}.pdf")


@router.post("/contract")
def contract_generation(request : schemas.Contract, db : Session = Depends(get_db)):

    employment_contract_gen.create_employment_record_pdf(request, db)
    current_month = datetime.now().strftime("%B")

    static_pdf_path = os.path.join(os.getcwd(), 'contracts', f"{request.workerNumber}_contract_{current_month}.pdf")

    return FileResponse(static_pdf_path, media_type='application/pdf', filename=f"{request.workerNumber}_contract_{current_month}.pdf")
    
import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from .. import schemas
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import userControllers
from ..controllers import salary_slip_generation

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


@router.post("/contract")
def contract_generation(request : schemas.Contract, db : Session = Depends(get_db)):
    return userControllers.create_contract(request,db)


# @router.post("/domestic_worker/exist/{phoneNumber}")
# def check_existing_worker(phoneNumber, db: Session = Depends(get_db)):
#     return userControllers.check_existing_worker(phoneNumber, db)


# @router.post("/login/employer")
# def login_employer(request : schemas.Login_Employer, db : Session = Depends(get_db)):
#     return userControllers.login_employer(request,db)
    
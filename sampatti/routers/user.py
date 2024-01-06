from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import userControllers

router = APIRouter(
    prefix="/user",
    tags=['users']
)


@router.post("/employer/create")
def create_employer(request : schemas.Employer, db : Session = Depends(get_db)):
    return userControllers.create_employer(request, db)


@router.get("/employer/{id}", response_model = schemas.Employer_Schema)
def get_employer(id, db :Session = Depends(get_db)):
    return userControllers.get_employer(id,db)

@router.get("/domestic_worker/{id}", response_model = schemas.Domestic_Worker_Schema)
def get_domestic_worker(id,db:Session = Depends(get_db)):
    return userControllers.get_domestic_worker(id,db)

@router.post('/domestic_worker/create')
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session = Depends(get_db)):
    return userControllers.create_domestic_worker(request, db)


@router.post("/domestic_worker/exist/{phoneNumber}")
def check_existing_worker(phoneNumber, db: Session = Depends(get_db)):
    return userControllers.check_existing_worker(phoneNumber, db)


@router.post("/login/employer")
def login_employer(request : schemas.Login_Employer, db : Session = Depends(get_db)):
    return userControllers.login_employer(request,db)
    
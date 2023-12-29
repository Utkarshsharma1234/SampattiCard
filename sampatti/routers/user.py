from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import userControllers

router = APIRouter(
    prefix="/user",
    tags=['users']
)

@router.post('/employer')
def create_employer(request : schemas.Employer, db: Session = Depends(get_db)):
    return userControllers.create_employer(request, db)

@router.post('/domestic_worker')
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session = Depends(get_db)):
    return userControllers.create_domestic_worker(request,db)
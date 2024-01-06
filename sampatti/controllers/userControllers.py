import ctypes
from fastapi import Depends, HTTPException, status
from ..import schemas, models
from ..hashing import Hash
from sqlalchemy.orm import Session, joinedload

# creating the employer
def create_employer(request : schemas.Employer, db: Session):
    worker_name = request.name
    worker_email = request.email
    worker_password = request.password

    new_user = models.Employer(name = worker_name, email = worker_email, password = Hash.bcrypt(worker_password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# creating a domestic worker
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session):
    worker_name = request.name
    worker_email = request.email
    worker_phoneNumber = request.phoneNumber

    new_worker = models.Domestic_Worker(name = worker_name, email = worker_email, phoneNumber = worker_phoneNumber)
    employer = db.query(models.Employer).filter(models.Employer.id == 1).first()

    new_worker.employers.append(employer)
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return new_worker
   

# getting a employer
def get_employer(id, db :Session):
    employer = db.query(models.Employer).options(joinedload(models.Employer.workers)).filter(models.Employer.id == id).first()
    if not employer:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")
    return employer


# getting domestic worker
def get_domestic_worker(id,db:Session):
    domestic_worker = db.query(models.Domestic_Worker).options(joinedload(models.Domestic_Worker.employers)).filter(models.Domestic_Worker.id == id).first()
    if not domestic_worker:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domestic Worker not Found.")
    return domestic_worker


# checking for the domestic worker using phone number
def check_existing_worker(phoneNumber, db: Session):
    user = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.phoneNumber == phoneNumber).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The domestic worker is not registered. Please egister the worker.")
    else:
        return user


# logging in the employer
def login_employer(request : schemas.Login_Employer, db):
    employer = db.query(models.Employer).filter(models.Employer.email == request.email).first()
    if not employer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="The employer is not registered.")
    
    if not Hash.verify(employer.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password")

    return {
        "Employer_Name" : employer.name,
        "Employer_Email" : employer.email
    }
import ctypes
from fastapi import Depends, HTTPException, status
from ..import schemas, models
from ..hashing import Hash
from sqlalchemy.orm import Session, joinedload
import hashlib
import json

# creating the employer
def create_employer(request : schemas.Employer, db: Session):
    employer_name = request.name
    employer_email = request.email
    employer_number = request.employerNumber

    new_user = models.Employer(name = employer_name, email = employer_email, employerNumber = employer_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# creating a domestic worker
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session):
    worker_name = request.name
    worker_email = request.email
    worker_phoneNumber = request.workerNumber
    employer_phoneNumber = request.employerNumber

    existing_worker = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.workerNumber == worker_phoneNumber).first()
    
    if not existing_worker:
        new_worker = models.Domestic_Worker(name = worker_name, email = worker_email, workerNumber = worker_phoneNumber, employerNumber = employer_phoneNumber)
        employer = db.query(models.Employer).filter(models.Employer.employerNumber == employer_phoneNumber).first()

        new_worker.employers.append(employer)
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)
        return new_worker
    
    else:
        employer = db.query(models.Employer).filter(models.Employer.employerNumber == employer_phoneNumber).first()

        existing_worker.employers.append(employer)
        db.commit()
        db.refresh(existing_worker)
        return existing_worker
    
   

# getting a employer
def get_employer(employerNumber, db :Session):
    employer = db.query(models.Employer).options(joinedload(models.Employer.workers)).filter(models.Employer.employerNumber == employerNumber).first()
    if not employer:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")
    return employer


# getting domestic worker
def get_domestic_worker(workerNumber,db:Session):
    domestic_worker = db.query(models.Domestic_Worker).options(joinedload(models.Domestic_Worker.employers)).filter(models.Domestic_Worker.workerNumber == workerNumber).first()
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

def create_contract(request : schemas.Contract, db):

    my_object = {
        "employer_number" : request.employer_number,
        "worker_number" : request.worker_number,
        "message" : request.message,
        "timestamp" : request.timestamp,
    }

    json_string = json.dumps(my_object, sort_keys=True)

    hash_object = hashlib.sha256()

    hash_object.update(json_string.encode('utf-8'))

    hashed_result = hash_object.hexdigest()

    contract = models.Contract(employer_number = request.employer_number, worker_number = request.worker_number, message = request.message, timestamp = request.timestamp, hashedMessage = hashed_result)

    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract
from fastapi import HTTPException, status
from sqlalchemy import update

from .. import models
from ..import schemas
from ..hashing import Hash
from sqlalchemy.orm import Session, joinedload
import hashlib
import json
from fastapi.responses import JSONResponse

# creating the employer
def create_employer(request : schemas.Employer, db: Session):

    employerNumber = request.employerNumber

    employer = db.query(models.Employer).filter(models.Employer.employerNumber == employerNumber).first()

    if not employer :
        new_user = models.Employer(employerNumber = employerNumber)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    else:
        {"message" : "Employer already Exists."}


# creating a domestic worker
def create_domestic_worker(request : schemas.Domestic_Worker, db: Session):
    worker_name = request.name
    worker_email = request.email
    workerNumber = request.workerNumber
    employerNumber = request.employerNumber
    worker_pan = request.panNumber
    worker_upi = request.upi_id

    employer = db.query(models.Employer).filter(models.Employer.employerNumber == employerNumber).first()

    if not employer:
        raise HTTPException(status_code=404, detail="The employer is not registered. You must register the employer first.")

    existing_worker = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.workerNumber == workerNumber).first()
    
    if not existing_worker:
        new_worker = models.Domestic_Worker(name = worker_name, email = worker_email, workerNumber = workerNumber, panNumber = worker_pan, upi_id = worker_upi)

        new_worker.employers.append(employer)
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)
        return new_worker
    
    else:
        existing_worker.employers.append(employer)
        db.commit()
        db.refresh(existing_worker)
        return existing_worker
    
   

# # getting a employer
# def get_employer(employerNumber, db :Session):
#     employer = db.query(models.Employer).options(joinedload(models.Employer.workers)).filter(models.Employer.employerNumber == employerNumber).first()
#     if not employer:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found. Please register yourself first.")
#     return employer


# # getting domestic worker
# def get_domestic_worker(workerNumber,db:Session):
#     domestic_worker = db.query(models.Domestic_Worker).options(joinedload(models.Domestic_Worker.employers)).filter(models.Domestic_Worker.workerNumber == workerNumber).first()
#     if not domestic_worker:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not Found.")
#     return domestic_worker


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

def insert_salary(request : schemas.Salary, db : Session):

    workerNumber = request.workerNumber
    employerNumber = request.employerNumber
    salary = request.salary_amount

    update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employerNumber).values(salary_amount=salary)

    db.execute(update_statement)
    db.commit()

    return {"salary credited successfully."}
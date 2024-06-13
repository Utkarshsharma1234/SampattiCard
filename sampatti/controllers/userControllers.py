from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import update
import uuid, random, string
from .. import models
from ..import schemas
from ..hashing import Hash
from sqlalchemy.orm import Session, joinedload
import hashlib
import json
from fastapi.responses import JSONResponse


def generate_unique_id(length=8):

    unique_id = uuid.uuid4().hex
    letters_only = ''.join([char for char in unique_id if char.isalpha()])[:length]
    if len(letters_only) < length:
        letters_only += ''.join(random.choices(string.ascii_letters, k=length - len(letters_only)))
    return letters_only

# creating the employer
def create_employer(request : schemas.Employer, db: Session):

    employerNumber = request.employerNumber

    employer = db.query(models.Employer).filter(models.Employer.employerNumber == employerNumber).first()

    if not employer :
        unique_id = generate_unique_id()
        new_user = models.Employer(id= unique_id, employerNumber = employerNumber)
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
        raise HTTPException(status_code=400, detail="The employer is not registered. You must register the employer first.")

    existing_worker = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.workerNumber == workerNumber).first()
    
    if not existing_worker:
        unique_id = generate_unique_id()
        new_worker = models.Domestic_Worker(id=unique_id, name = worker_name, email = worker_email, workerNumber = workerNumber, panNumber = worker_pan, upi_id = worker_upi)
        new_worker.employers.append(employer)
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)

        unique_id2 = generate_unique_id()
        update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employer.employerNumber).values(id=unique_id2)
        db.execute(update_statement)
        db.commit()
        return new_worker
    
    else:
        existing_worker.employers.append(employer)
        db.commit()
        db.refresh(existing_worker)

        unique_id2 = generate_unique_id()
        update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employer.employerNumber).values(id=unique_id2)
        db.execute(update_statement)
        db.commit()
        return existing_worker
    

def update_worker(oldNumber : int, newNumber : int, db : Session):

        update_statement = update(models.Domestic_Worker).where(models.Domestic_Worker.workerNumber == oldNumber).values(workerNumber=newNumber)

        db.execute(update_statement)
        db.commit()


def insert_salary(request : schemas.Salary, db : Session):

    workerNumber = request.workerNumber
    employerNumber = request.employerNumber
    salary = request.salary_amount

    update_statement = update(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employerNumber).values(salary_amount=salary)

    db.execute(update_statement)
    db.commit()

    return {"salary credited successfully."}



def create_talk_to_agent_employer(employerNumber : int, db:Session):

    current_date = datetime.now().date()

    unique_id = generate_unique_id()
    new_user = models.TalkToAgentEmployer(id = unique_id, employerNumber = employerNumber, date=f"{current_date}")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

    
def check_existence(employerNumber : int, workerNumber : int, db : Session):

    field = db.query(models.worker_employer).where(models.worker_employer.c.worker_number == workerNumber).where(models.worker_employer.c.employer_number == employerNumber).first()

    if not field:
        return {"message" : "VALID"}
    else : 
        return {"message" : "INVALID"}


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

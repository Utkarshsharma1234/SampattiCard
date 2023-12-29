from ..import schemas, models
from sqlalchemy.orm import Session


def create_employer(request : schemas.Employer, db: Session):
    employer_name = request.name
    employer_email = request.email
    # hashed_user_password = pwd_cxt.hash()
    employer_password = request.password

    new_user = models.Employer(name=employer_name, email=employer_email, password=employer_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_domestic_worker(request : schemas.Employer, db: Session):
    worker_name = request.name
    worker_email = request.email
    # hashed_user_password = pwd_cxt.hash()
    worker_password = request.password

    new_user = models.Domestic_Worker(name=worker_name, email=worker_email, password=worker_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
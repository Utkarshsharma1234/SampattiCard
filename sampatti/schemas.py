from pydantic import BaseModel
from typing import List

class Domestic_Worker(BaseModel):
    name: str
    email : str
    workerNumber:int
    employerNumber : int
    panNumber : str
    upi_id : str
    class Config:
        from_attributes = True

class Employer(BaseModel):
    # name: str
    # email : str
    employerNumber:int
    class Config:
        from_attributes = True

class Salary(BaseModel):
    workerNumber : int
    employerNumber : int
    salary_amount : int
    class Config:
        from_attributes = True

class Dummy_worker(BaseModel):
    name: str
    email : str
    workerNumber:int

class Domestic_Worker_Schema(Dummy_worker):
    employers : List[Employer] = []

class Employer_Schema(Employer):
    workers : List[Dummy_worker] = []

class ShowEmployer(BaseModel):
    name:str
    email:str
    domestic_workers: List[Domestic_Worker] = []
    class Config():
        from_attributes = True


class ShowDomesticWorker(BaseModel):
    name : str
    email: str
    employers : List[Employer] = []
    class Config():
        from_attributes = True

class Login_Employer(BaseModel):
    email: str
    password:str    

class Contract(BaseModel):
    employerNumber: int
    workerNumber : int
    message : str
    upi : str
    name : str
    salary : int

class Vendor(BaseModel):
    vpa : str
    workerNumber : int
    name : str
    pan : str
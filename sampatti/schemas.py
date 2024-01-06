from pydantic import BaseModel
from typing import List, Optional

# class EmployerBase(BaseModel):
#     id: int
#     name: str

#     class Config:
#         orm_mode = True

# class WorkerBase(BaseModel):
#     name: int
#     email: str

#     class Config:
#         orm_mode = True

# class WorkerSchema(WorkerBase):
#     employers : List[EmployerBase]

# class EmployerSchema(EmployerBase):
#     workers: List[WorkerBase]

class Domestic_Worker(BaseModel):
    name: str
    email : str
    phoneNumber:int
    class Config:
        from_attributes = True

class Employer(BaseModel):
    name: str
    email : str
    password:str
    class Config:
        from_attributes = True

class Domestic_Worker_Schema(Domestic_Worker):
    employers : List[Employer] = []

class Employer_Schema(Employer):
    workers : List[Domestic_Worker] = []


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

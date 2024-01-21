from pydantic import BaseModel
from fastapi import Body
from typing import List, Annotated
from datetime import datetime

class Domestic_Worker(BaseModel):
    name: str
    email : str
    workerNumber:int
    employerNumber : int
    class Config:
        from_attributes = True

class Employer(BaseModel):
    name: str
    email : str
    employerNumber:int
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

class Contract(BaseModel):
    employer_number: int
    worker_number : int
    message : str
    timestamp : str
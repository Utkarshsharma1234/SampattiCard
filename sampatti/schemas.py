from pydantic import BaseModel
from typing import List, Optional

class Employer(BaseModel):
    name: str
    email : str
    password:str

class Domestic_Worker(BaseModel):
    name: str
    email : str
    password:str

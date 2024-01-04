from sqlalchemy import Column, Integer, String
from .database import Base

class Employer(Base):
    __tablename__ = "Employers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

class Domestic_Worker(Base):

    __tablename__ = "Domestic_Workers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phoneNumber = Column(Integer)


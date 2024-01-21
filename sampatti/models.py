from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

worker_employer = Table('worker_employer', Base.metadata,
    Column('worker_id', ForeignKey('Domestic_Worker.id'), primary_key=True),
    Column('employer_id', ForeignKey('Employer.id'), primary_key=True)
)

class Domestic_Worker(Base):

    __tablename__ = "Domestic_Worker"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    workerNumber = Column(Integer)
    employerNumber = Column(Integer)
    employers = relationship("Employer", secondary="worker_employer", back_populates='workers')


class Employer(Base):
    __tablename__ = "Employer"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    employerNumber = Column(Integer)
    workers = relationship("Domestic_Worker", secondary="worker_employer",back_populates='employers')


class Contract(Base) :

    __tablename__ = "Contracts"
    id = Column(Integer, primary_key=True, index=True)
    employer_number = Column(Integer)
    worker_number = Column(Integer)
    message = Column(String)
    timestamp = Column(String)
    hashedMessage = Column(String)

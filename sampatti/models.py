from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

worker_employer = Table('worker_employer', Base.metadata,
    Column('id', String),
    Column('worker_number', ForeignKey('Domestic_Worker.workerNumber'), primary_key=True),
    Column('employer_number', ForeignKey('Employer.employerNumber'), primary_key=True),
    Column('salary_amount', Integer, default=0),
    Column('order_id', String, default=''),
    Column('status', String, default=''),
    Column('vendor_id', String, default='')
)


class Domestic_Worker(Base):

    __tablename__ = "Domestic_Worker"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=True)
    workerNumber = Column(Integer)
    panNumber = Column(String)
    upi_id = Column(String, nullable=True)
    accountNumber = Column(String, nullable=True)
    ifsc = Column(String, nullable=True)
    employers = relationship("Employer", secondary="worker_employer", back_populates='workers') 


class Employer(Base):
    __tablename__ = "Employer"
    id = Column(String, primary_key=True)
    employerNumber = Column(Integer)
    workers = relationship("Domestic_Worker", secondary="worker_employer",back_populates='employers')

class TalkToAgentEmployer(Base):
    __tablename__ = "Talk_To_Agent"
    id = Column(String, primary_key=True)   
    date = Column(String)
    employerNumber = Column(Integer)
    category = Column(String)


class ExplainDomesticWorker(Base):
    __tablename__ = "ExplainDomesticWorker"
    id = Column(String, primary_key=True)   
    date = Column(String)
    employerNumber = Column(Integer)
    workerNumber = Column(Integer)
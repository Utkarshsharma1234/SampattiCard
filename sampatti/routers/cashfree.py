import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from .. import schemas
from ..database import get_db
from sqlalchemy.orm import Session
from ..controllers import cashfree_api

router = APIRouter(
    prefix="/cashfree",
    tags=['Cashfree']
)


@router.get("/fetch_vpa/{workerNumber}")
def fetch_vpa(workerNumber : int):
    return cashfree_api.fetch_vpa(workerNumber=workerNumber)

@router.get("/payment_link")
def payment_link_generation(db : Session = Depends(get_db)):
    return cashfree_api.payment_link_generation(db)

@router.get("order_status")
def check_order_status(orderId : str):
    return cashfree_api.check_order_status(orderId)

@router.post("/add_a_vendor")
def add_a_vendor(request : schemas.Vendor, db : Session = Depends(get_db)):
    return cashfree_api.add_a_vendor(request.vpa, request.workerNumber, request.name, request.pan, db, request.employerNumber)

@router.get("/pan_verification")
def pan_verification(pan : str, name : str):
    return cashfree_api.pan_verification(pan, name)


@router.get("/unsettled_balance")
def unsettled_balance(db : Session = Depends(get_db)):
    return cashfree_api.unsettled_balance(db)
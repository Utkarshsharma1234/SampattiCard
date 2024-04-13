import os
from fastapi import HTTPException, status
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from textwrap import wrap
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models
from .cashfree_api import check_order_status
from ..controllers import amount_to_words


def generate_salary_slip(workerNumber, db:Session) :

    worker = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.workerNumber == workerNumber).first()
    
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    if not worker :
        raise HTTPException(status_code=404, detail="The domestic worker is not registered. You must register the worker first.")
    
    static_dir = os.path.join(os.getcwd(), 'static')
    pdf_path = os.path.join(static_dir, f"{workerNumber}_salary_slip_{current_month}.pdf")

    if not os.path.exists('static'):
        os.makedirs('static')
    w, h = A4
    c = canvas.Canvas(pdf_path, pagesize=A4)
    
    flat_logo = os.path.join(os.getcwd(), 'logos/flat_logo.png')
    circular_logo = os.path.join(os.getcwd(), 'logos/circular_logo.png')

    c.setFont("Helvetica-Bold", 18)

    c.setFillColorRGB(0.078, 0.33, 0.45)
    c.drawImage(flat_logo, w-120, h-55, width=100, height=45)
    text = "Propublica Finance and Investment Services Pvt. Ltd."
    size = len(text)
    c.drawString(w/2 - size*4, h-80, text=text)

    x = 70
    y = h - 110

    c.setFont("Helvetica", 14)

    cin = "CIN : 20369785412547852"
    udyam = "Udyam Registration Number : UDYAM-5689-120356"

    c.drawString(w/2 - size*3, y, cin)
    y -= 20
    c.drawString(w/2 - size*3, y, udyam)

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(w/2-size*2, y, "Salary Record") 

    c.setFont("Times-Roman", 10)

    worker_data = [
        [f"Name of the Employee : {worker.name}", "PF Number : NA"],
        ["Nature of Work : Domestic Help", "Account Number : 2222222222222222"],
        ["Bank Name : HDFC Bank", "IFSC Code : NA"],
        ["ESI Number : NA", f"UPI ID : {worker.upi_id}"]
    ]

    worker_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.078, 0.33, 0.45)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 100),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
    ])


    worker_table = Table(worker_data)
    worker_table.setStyle(worker_style)
    m,n = worker_table.wrapOn(c,0,0)
    y -= 135
    worker_table.drawOn(c,x, y)

    receipt_data = []
    receipt_data.append(["Sr. No.", "Employer Code", "Mode", "Reference", "Salary", "Variable Pay"])

    rows = 0

    total_transactions = db.query(models.worker_employer).filter(models.worker_employer.c.worker_number == workerNumber).all()
    total_salary = 0
    
    ct = 1
    for transaction in total_transactions:
        order_id = transaction.order_id
        status = check_order_status(order_id=order_id)
        if status == "PAID":
            single_row = [ct, transaction.employer_number, "UPI", transaction.worker_number, transaction.salary_amount, "Variable Pay"]
            receipt_data.append(single_row)
            ct += 1
            total_salary += transaction.salary_amount

        else:
            continue
        
    receipt_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.078, 0.33, 0.45)),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    y = y - rows*25 - 70
    receipt_table = Table(receipt_data)
    receipt_table.setStyle(receipt_style)
    receipt_table.wrapOn(c, 0, 0)
    receipt_table.drawOn(c, x, y)

    c.setFont("Times-Roman", 10)
    issued = f"Salary Slip issued on : {current_date} for the month of {current_month} {current_year}"
    y -= 25
    c.drawString(x, y, text=issued)

    c.setFont("Helvetica-Bold", 10)
    y -= 30
    salary_in_words = amount_to_words.amount_to_words(total_salary)
    c.drawString(x, y, f"Total Salary Credited INR {total_salary}/- Only")
    c.drawString(x, y-20, f"Amount in Words : {salary_in_words} Only")
          

    note = """NOTE : This is a digitally issued salary slip and does not require attestation.
The money has been debited in the corresponding bank account."""
    lines = note.split('\n')
    c.setFont("Helvetica", 8)

    y = 110
    for line in lines:
        c.drawString(x, y, line)
        y -= 10

    y -= 10

    c.drawImage(circular_logo, 25, y-20 , 30, 30)

    declaration = """Declaration : The transaction trail is verified with an employment agreement between the employer and the 
employee basis which the salary slip is issued. Propublica Finance and Investment Services Pvt. Ltd. is not the 
employer for the worker for whom salary record is generated."""

    lines = declaration.split('\n')
    for line in lines:
        c.drawString(x, y, line)
        y -= 10


    c.setFont("Helvetica", 10)
    c.rect(0,0,w,30, fill=True)
    c.setFillColorRGB(1,1,1)
    c.drawString(x, 12.5, "Phone : +91 86603 52558")
    c.drawString(x+ 150, 12.5, "website : www.sampatticard.in          support : vrashali@sampatticard.in")

    c.showPage()
    c.save()
import os
from fastapi import HTTPException, status
from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from textwrap import wrap
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models
from .cashfree_api import check_order_status

def generate_salary_slip(workerNumber, db:Session) :

    worker = db.query(models.Domestic_Worker).filter(models.Domestic_Worker.workerNumber == workerNumber).first()

    if not worker :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The domestic worker is not registered. You must register the worker first.")
    
    static_dir = os.path.join(os.getcwd(), 'static')
    pdf_path = os.path.join(static_dir, f"{workerNumber}_salary_slip.pdf")

    if not os.path.exists('static'):
        os.makedirs('static')
    w, h = A3
    c = canvas.Canvas(pdf_path, pagesize=A3)

    c.setFont("Helvetica-Bold", 30)

    c.setFillColorRGB(0.078, 0.33, 0.45)
    text = "Propublica Finance and Investment Services Pvt. Ltd."
    size = len(text)
    c.drawString(w/2 - size*7, h-100, text=text)

    x = 70
    y = h - 150

    c.setFont("Helvetica", 20)

    cin = "CIN : 20369785412547852"
    udyam = "Udyam Registration Number : UDYAM-5689-120356"

    c.drawString(w/2 - size*4, y, cin)
    c.drawString(w/2 - size*4, y - 30, udyam)

    y = y - 40

    y = y - 40
    c.setFont("Helvetica-Bold", 20)
    c.drawString(w/2-size*2.5, y, "Salary Record") 

    y = y - 8

    c.setFont("Times-Roman", 25)
    name = worker.name

    worker_data = [
        [f"Name of the Employee : {name}", "PF Number : NA"],
        ["Nature of Work : Domestic Help", "Account Number : 2222222222222222"],
        ["Bank Name : HDFC Bank", "IFSC Code : NA"],
        ["ESI Number : NA", "UPI ID : NA"]
    ]

    worker_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.078, 0.33, 0.45)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 100),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
    ])


    worker_table = Table(worker_data)
    worker_table.setStyle(worker_style)
    m,n = worker_table.wrapOn(c,0,0)
    y = y - 200
    worker_table.drawOn(c,x, y)

    c.setFont("Times-Roman", 15)

    issued = "Salary Slip issued on : 01-01-2024 for the month of January 2024"

    y = y - 50
    c.drawString(x, y, text=issued)

    receipt_data = []
    receipt_data.append(["Sr. No.", "Employer Code", "Mode", "Reference", "Salary", "Variable Pay"])

    rows = 0

    total_transactions = db.query(models.worker_employer).filter(models.worker_employer.c.worker_number == workerNumber).all()
    
    ct = 1
    for transaction in total_transactions:
        order_id = transaction.order_id
        status = check_order_status(order_id=order_id)
        if status == "PAID":
            single_row = [ct, transaction.employer_number, "UPI", transaction.worker_number, transaction.salary_amount, "Variable Pay"]
            receipt_data.append(single_row)
            ct += 1

        else:
            continue

        
    receipt_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.078, 0.33, 0.45)),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
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

    c.setFont("Helvetica-Bold", 15)
    y = y - 70
    c.drawString(x, y, "Total Salary Credited INR 4000/- Only")
    c.drawString(x, y-30, "Amount in Words : FOUR THOUSAND /- Only")


    note = "NOTE : This is a digitally issued salary slip and does not require attestation."
    c.setFont("Helvetica", 15)

    y = y - 100
    c.drawString(x, y, text=note)
    note = "The money has been debited in the corresponding bank account."
    c.drawString(x, y-20, text=note)

    y = y - 70

    t = c.beginText()
    t.setFont("Helvetica", 15)
    t.setTextOrigin(x, y)

    declaration = "Declaration : The transaction trail is verified with an employment agreement between the employer and the employee basis which the salary slip is issued. Propublica Finance and Investment Services Pvt. Ltd. is not the employer for the worker for whom salary record is generated. "
    wrapped_declaration = "\n".join(wrap(declaration, 90))
    t.textLines(wrapped_declaration)
    c.drawText(t)

    c.showPage()
    c.save()
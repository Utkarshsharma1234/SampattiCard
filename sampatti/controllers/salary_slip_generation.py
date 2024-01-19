from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from textwrap import wrap

def salary_slip_generation(request) :
    w, h = A3
    c = canvas.Canvas("salary_slip.pdf", pagesize=A3)

    c.drawImage("logo.png", w/2-25, h-70, height=50, width=50)
    c.setFont("Helvetica", 30)

    c.setFillColorRGB(0.2, 0.1, 0.7)
    text = "Propublica Finance and Investment"
    size = len(text)
    c.drawString(w/2 - size*6, h-100, text=text)
    c.drawString(w/2 - size*3, h-140, text="Services Pvt. Ltd.")

    x = 50
    y = h - 200

    c.setFont("Helvetica-Bold", 15)
    c.drawString(x, y, "Address : ")
    t = c.beginText()
    t.setFont("Helvetica", 15)
    t.setTextOrigin(x + 80,y)

    address = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
    wrapped_address = "\n".join(wrap(address, 40))
    t.textLines(wrapped_address)
    c.drawText(t)

    cin = "CIN : 20369785412547852"
    udyam = "udyam reg. no. : UDYAM-5689-120356"

    c.drawString(w/2 + 60, y, cin)
    c.drawString(w/2 + 60, y - 20, udyam)

    y = y - 40
    c.line(0, y, w, y)

    y = y - 30
    c.setFont("Helvetica-Bold", 20)
    c.drawString(w/2-45, y, "Pay Slip") 

    y = y - 8
    c.line(w/2-48, y, w/2 + 35, y)

    c.setFont("Times-Roman", 25)
    name = "Utkarsh Sharma"

    worker_data = [
        [f"Name of the Employee : {name}", "PF Number : NA"],
        ["Nature of Work : Domestic Help", "Account Number : 2222222222222222"],
        ["Bank Name : HDFC Bank", "IFSC Code : NA"],
        ["ESI Number : NA", "UPI ID : NA"],
        ["UAN Number : NA", "Tax no. : NA"]
    ]

    worker_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
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
    c.setFillColorRGB(0,0,0)

    issued = "Salary Slip issued on : 01-01-2024 for the month of January 2024"

    y = y - 50
    c.drawString(x, y, text=issued)

    receipt_data = [
        ["Sr. No.", "Emp Code", "Mode", "Reference", "Salary", "Variable Pay", "Income Tax", "Prof.Tax", "PF"], 
        [1,1,"UPI", 221318092006, 4000, 0, 0, 0, 0]
    ]

    receipt_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])


    y = y - 200
    receipt_table = Table(receipt_data)
    receipt_table.setStyle(receipt_style)
    p,q = receipt_table.wrapOn(c, 0, 0)
    receipt_table.drawOn(c, x, y)

    c.setFont("Helvetica-Bold", 15)

    y = y - 100
    c.drawString(x, y, "Total Salary Credited INR 4000/- Only")
    c.drawString(x, y-30, "Amount in Words : FOUR THOUSAND /- Only")


    note = "NOTE : This is a digitally issued salary slip and does not require attestation."
    c.setFont("Helvetica", 15)

    y = y - 150
    c.drawString(x, y, text=note)
    note = "The money has been debited in the corresponding bank account."
    c.drawString(x, y-20, text=note)

    y = y - 100
    declare = "Declaration : "
    c.setFont('Helvetica-Bold', 15)
    c.drawString(x, y, declare)

    t = c.beginText()
    t.setFont("Helvetica", 15)
    t.setTextOrigin(150, y)

    declaration = "This transaction trail is verified with a contract between the employer and employee basis which this salary slip has been issued. Sampatti Card is not the employer of the person for which the salary slip is being issued"
    wrapped_declaration = "\n".join(wrap(declaration, 80))
    t.textLines(wrapped_declaration)
    c.drawText(t)


    c.showPage()
    c.save()
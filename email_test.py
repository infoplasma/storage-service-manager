import os
import smtplib
from email.message import EmailMessage


def send_email():

    #EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')  # load email address from an environment veriable
    #EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') # load password from envrinoment variable
    EMAIL_ADDRESS = 'lamante@dxc.com'
    EMAIL_PASSWORD = input("PWD:")

    print(EMAIL_ADDRESS)
    msg = EmailMessage()
    msg['Subject'] = "[STORCOM_INFO]: NEW LUN REQUEST"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = 'lorenzoamante@infoplasma.com'

    with open("output.txt", "r") as f:
        email_text = f.read()

    msg.set_content(email_text)

    with open("vars/output_params.yaml") as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data, filename=file_name)

    print("I AM HERE")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        # login to mail server

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


import win32com.client
import os


def send_email():
    with open("output.txt", "r") as f:
        email_text = f.read()

    att = os.path.join(os.getcwd(), "vars", "params.yaml")

    outlook = win32com.client.Dispatch("Outlook.Application")

    msg = outlook.CreateItem(0)
    msg.To = "lamante@dxc.com"
    msg.Subject = "[STORCOM]: PIZZA DELIVERY UPDATE"
    msg.Body = email_text
    msg.Attachments.Add(att)
    msg.Send()



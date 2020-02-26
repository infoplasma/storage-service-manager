import os
import win32com.client
from jinja2 import Environment, FileSystemLoader
from yaml import safe_dump


def dump_and_render(data, email_template="email_templo.j2"):

    # dump parameters to yaml file
    with open("vars/params.yaml", "w", encoding='utf-8') as handle:
        safe_dump(data, handle, allow_unicode=True)

    # render jinja2 template
    j2_env = Environment(loader=FileSystemLoader("."), trim_blocks=True, autoescape=True)
    template = j2_env.get_template(f"templos/{email_template}")
    config = template.render(data=data)

    # write rendered text to output text file
    with open("output.txt", "w") as output:
        output.write(config)


def send_email(subj="PIZZA DELIVERY"):
    with open("output.txt", "r") as f:
        email_text = f.read()

    att = os.path.join(os.getcwd(), "vars", "params.yaml")

    outlook = win32com.client.Dispatch("Outlook.Application")

    msg = outlook.CreateItem(0)
    msg.To = "lamante@dxc.com"
    msg.Subject = f"[STORCOM]: {subj}"
    msg.Body = email_text
    msg.Attachments.Add(att)
    msg.Send()
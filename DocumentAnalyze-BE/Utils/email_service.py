# utils/email_service.py
import smtplib
import requests
from email.message import EmailMessage
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

def send_email_with_attachment(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str = None,
    attachment_filename: str = None
):
    try:
        # Step 1: Download the file from the blob URL
        response = requests.get(attachment_path)
        response.raise_for_status()  # raise error if download fails
        file_data = response.content  # bytes
        file_type = attachment_filename.split('.')[-1]

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = os.getenv("EMAIL_FROM") 
        msg['To'] = to_email
        msg.set_content(body)

        # Attach file if provided
        if attachment_path and attachment_filename:
            msg.add_attachment(file_data, maintype='application', subtype=file_type, filename=attachment_filename)

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)

        print("✅ Email sent successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
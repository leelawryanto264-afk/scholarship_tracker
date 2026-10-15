import os
import imaplib
import email
import re
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Loads environment and retrieve configuration settings
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")


# Raises an error if email or password is missing from .env file
if not EMAIL or not PASSWORD:
    raise ValueError("EMAIL and PASSWORD must be set in the .env file.")

# Checks email if it's multipart or singlepart and extracts the content
def get_email(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode(errors="ignore")
            elif content_type == "text/html" and "attachment" not in content_disposition:
                html = part.get_payload(decode=True).decode(errors="ignore")
                return BeautifulSoup(html, "html.parser").get_text()

    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            return msg.get_payload(decode=True).decode(errors="ignore")
        elif content_type == "text/html":
            html = msg.get_payload(decode=True).decode(errors="ignore")
            return BeautifulSoup(html, "html.parser").get_text()
    return ""

# Parses through email contents and extracts relevant data into a structured format using regex
def extract_details(text, subject):
    name = subject
    amount_match = re.search(r"\$\s?([\d,]+(?:\.\d{2})?)", text)
    amount = amount_match.group(0) if amount_match else "Not specified"

    essay = "Not Found"
    requirements = "Not Found"

    essay_match = re.search(r"(?:Essay Prompt|Essay Requirement|Essay):/s*(.*?)(?:\n|$)", text, re.IGNORECASE)
    if essay_match:
        essay = essay_match.group(1).strip()

    req_match = re.search(r"(?:Requirements|Eligibility|Criteria):/s*(.*?)(?:\n|$)", text, re.IGNORECASE)
    if req_match:
        requirements = req_match.group(1).strip()

    return name, amount, essay, requirements

# Connects to the IMAP server over SSL and fetches the last 100 emails containing the keyword "scholarship"
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
email_data = []

try:
    print("Logging in...")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    print("Fetching emails...")
    status, messages = mail.search(None, "(BODY \"scholarship\")")
    if status != "OK":
        raise RuntimeError(f"Unable to search inbox: {status}")

    email_ids = messages[0].split() if messages and messages[0] else []
    last_100_emails = email_ids[-100:]

    for e_id in last_100_emails:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        if status != "OK":
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg.get("Subject", "No Subject")
                body_text = get_email(msg)

                s_name, s_amount, s_essay, s_reqs = extract_details(body_text, subject)

                email_data.append({
                    "Date": msg.get("Date"),
                    "Sender": msg.get("From"),
                    "Scholarship Name": msg.get("Subject"),
                    "Name": s_name,
                    "Amount": s_amount,
                    "Essay": s_essay,
                    "Requirements": s_reqs
                })
finally:
    try:
        mail.logout()
        print("Connnection with Gmail closed...")
    except:
        pass

# Exports data 
if email_data:
    try: 
        df = pd.DataFrame(email_data)
        df.to_excel("scholarship_tracker.xlsx", index=False)
        print("Excel spreadsheet 'scholarship_tracker.xlsx' created successfully.")
    except:
        print("Error in creating spreadsheet.")
else:
    print("No emails found or no data was retrieved.")
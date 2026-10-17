import os
import imaplib
import email
import re
import pandas as pd
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
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
    else:
        essay_context = re.search(r"(:essay)(?:.*?)\s+(.*)", text, re.IGNORECASE)
        if essay_context:
            essay = f"{essay_context.group(1).strip()}"

    req_match = re.search(r"(?:Requirements|Eligibility|Criteria):/s*(.*?)(?:\n|$)", text, re.IGNORECASE)
    if req_match:
        requirements = req_match.group(1).strip()
    else:
        req_context = re.search(r"(?:eligibility|eligible|requirements|require)(?:,*?)\s+(.*)", text, re.IGNORECASE)
        if req_context:
            requirements = f"{req_context.group(1).strip()}"

    return name, amount, essay, requirements

# Checks for repeating email and removes duplicates
existing_scholarships = {}
if os.path.exists("scholarship.xlsx"):
    try:
        existing_df = pd.read_excel(str(row.get("Date"))), str(row.get("Sender")), str(row.get("Scholarship_name"))
        for _, row in existing_df.iterrows():
            unique_key = str(row.get("Date")), str(row.get("Sender")), str(row.get("Scholarship_name"))
            existing_scholarships[unique_key] = dict(row)
        print(f"Loaded {len(existing_scholarships)} existing ")
    except:
        print(f"Counld not read existing file")

# Connects to the IMAP server over SSL and fetches the last 100 emails containing the keyword "scholarship"
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
email_data = []
new_count = 0

try:
    print("Logging in...")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    print("Fetching emails...")
    status, messages = mail.search(None, '(TEXT "scholarship")')
    if status != "OK":
        raise RuntimeError(f"Unable to search inbox: {status}")

    email_ids = messages[0].split() if messages and messages[0] else []
    last_500_emails = email_ids[-500:]

    for e_id in last_500_emails:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        if status != "OK":
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg.get("Subject", "No Subject")
                body_text = get_email(msg)

        msg_date = msg.get("Date")    
        msg_sender = msg.get("From")  
        msg_subject = msg.get("Subject") 
        email_key = (str(msg_date), str(msg_sender), str(msg_subject)) 

        if email_key in existing_scholarships:
            continue

        body_text = get_email(msg)
        s_name, s_amount, s_essay, s_reqs = extract_details(body_text, subject)
        existing_scholarships[email_key] = {
            "Date": msg_date,
            "Sender": msg_sender,
            "Scholarship": subject,
            "Amount": s_amount,
            "Essay": s_essay,
            "Requirements": s_reqs, 
            "Status": "Not Applied"
        }
        new_count += 1

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

        wb = openpyxl.load_workbook("scholarship_tracker.xlsx")
        ws = wb.active
        dv = DataValidation(type = "list", formula1='"Not Applied, Applied, In Review, Rejected, Accepted"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add("G2:G500")
        
        wb.save("scholarship_tracker.xlsx")
        print(f"Excel spreadsheet 'scholarship_tracker.xlsx' updated {new_count} entries successfully.")
    except PermissionError:
        print(f"Error: Close your Excel file if you have it open and run it again.")
else:
    print("No emails found or no data was retrieved.")
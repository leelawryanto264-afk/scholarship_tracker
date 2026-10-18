import os
import re
import json
import imaplib
import email
import pandas as pd
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from parser import get_email, extract_details
from cloud_sync import upload_row, sheet_url, credentials_file

#add a time delay, alomst done :'D

# Loads environment and retrieve configuration settings
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")


# Raises an error if email or password is missing from .env file
if not EMAIL or not PASSWORD:
    raise ValueError("EMAIL and PASSWORD must be set in the .env file.")

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
with open(credentials_file, 'r') as f:
    creds_data = json.load(f)
if "private_key" in creds_data:
    creds_data["private_key"] = creds_data["private_key"].replace("\\n", "\n")

creds = Credentials.from_service_account_info(creds_data, scopes=scope)
client = gspread.authorize(creds)

wb = client.open_by_url(sheet_url)
sheet = wb.sheet1

existing_scholarships = {}

# Checks for repeating email and removes duplicates
if existing_scholarships is None:
    existing_scholarships = {}


# Connects to the IMAP server over SSL and fetches the last 100 emails containing the keyword "scholarship"
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
new_count = 0

try:
    print("Logging in...")
    mail.login(EMAIL, PASSWORD)
    mail.select('"[Gmail]/All Mail"')

    print("Fetching emails...")
    status, messages = mail.search(None, '(OR SUBJECT "scholarship" BODY "scholarship")')
    if status != "OK":
        raise RuntimeError(f"Unable to search inbox: {status}")

    if messages and messages[0]:
        email_ids = messages[0].split()
        email_ids.reverse()
    else: 
        email_ids = []
    
    last_500_emails = email_ids[:500]
    print(f"DEBUG: Found {len(email_ids)} emails")
    print(f"DEBUG: Spreadsheet URL is {sheet_url}")

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
                if "no-reply@google.com" in msg_sender.lower() or "security alert" in subject.lower():
                    continue
                email_key = (str(msg_date), str(msg_sender), str(msg_subject)) 
 
                # removes duplicates via key created for each email
                if email_key in existing_scholarships:
                    continue

                s_name, s_amount = extract_details(body_text, subject)

                payload = {
                    "Date": str(msg_date),
                    "Sender": str(msg_sender),
                    "Scholarship Name": str(s_name),
                    "Amount": str(s_amount),
                    "Status": "Not Applied"
                }
                print(f"DEBUG3: Extracted payload details cleanly > {payload['Scholarship Name']} & {payload['Amount']}")
                print(f"DEBUG3: payload to sheet is {sheet} ")
                upload_row(sheet, payload)
                existing_scholarships[email_key] = payload
                new_count += 1

finally:
    try:
        mail.logout()
        print("Connnection with Gmail closed...")
    except:
        pass

# Exports data 
if existing_scholarships:
    df = pd.DataFrame(list(existing_scholarships.values()) )

    total_tracked = len(df)

    status_count = df["Status"].value_counts()
    not_applied_count = status_count.get("Not Applied", 0)
    applied_count = status_count.get("Applied", 0)
    review_count = status_count.get("In Review", 0)

    total_value = 0
    if "Amount" in df.columns:
        for amount in df["Amount"]:
            if amount != "Not Specified":
                clear_amount = re.sub(r"[^\d.]", "", str(amount))
                if clear_amount:
                    total_value += float(clear_amount)

    print("\n"+ "=" * 50)
    print("Scholarship Tracker Status Report")
    print("="*50)
    print(f"API Engine status               : ACTIVE")
    print(f"Cloud Records                   : {total_tracked} rows synced")
    print(f"Potential Scholarship Awards    : ${total_value:,.2f}")
    print(f"Not Applied:                    : {not_applied_count}")
    print(f"Applied:                        : {applied_count}")
    print(f"In Review:                      : {review_count}")
    print("=" * 50+ "\n")

else:
    print("No emails found or no data was retrieved.") 
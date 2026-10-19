import os
import re
import time
import imaplib
import email
import email.utils
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from format import format_sheet
from parser import get_email, extract_details
from cloud_sync import upload_row, sheet_url, connect_cloud


# Loads environment and retrieve configuration settings
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")

# Raises an error if email or password is missing from .env file
if not EMAIL or not PASSWORD:
    raise ValueError("EMAIL and PASSWORD must be set in the .env file.")

sheet = connect_cloud(sheet_url)
if sheet is None:
    print("sheet is none")
    

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
    
    last_100_emails = email_ids[:100]

    for e_id in last_100_emails:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        if status != "OK":
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg.get("Subject", "No Subject")
                body_text = get_email(msg)
                raw_date = msg.get("Date")  
                try:
                    parsed_date = email.utils.parsedate_to_datetime(raw_date)
                    msg_date = parsed_date.strftime("%m/%d/%Y %H:%M")
                except Exception as e:
                    print(e)
                msg_sender = msg.get("From")  
                msg_subject = msg.get("Subject") 

                if "no-reply@google.com" in msg_sender.lower() or "security alert" in subject.lower() or "linkedin" in msg_sender.lower():
                    continue
                if "scholarship" not in subject.lower():
                    continue
                # removes duplicates via key created for each email
                email_key = (str(msg_date), str(msg_sender), str(msg_subject)) 
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

                upload_row(sheet, payload)
                existing_scholarships[email_key] = payload
                new_count += 1
                time.sleep(2)

finally:
    try:
        mail.logout()
        print("Connection with Gmail closed...")
    except:
        pass

try:
    all_records = sheet.get_all_records()
    if all_records:
        df = pd.DataFrame(all_records)
        total_tracked = len(df)

        status_count = df["Status"].value_counts() if "Status" in df.columns else pd.Series()
        not_applied_count = status_count.get("Not Applied", 0)
        applied_count = status_count.get("Applied", 0)
        rejected_count = status_count.get("Rejected", 0)
        accepted_count = status_count.get("Accepted", 0)

        total_value = 0.0
        if "Amount" in df.columns:
            for amount in df["Amount"]:
                if amount and str(amount) != "Not Specified":
                    clear_amount = re.sub(r"[^\d.]", "", str(amount))
                    if clear_amount:
                        try:
                            total_value += float(clear_amount)
                        except ValueError:
                            pass
        print("\n" + "=" * 50)
        print("Scholarship Tracker Status Report")
        print("=" * 50)
        print(f"API Engine Status                   : ACTIVE")
        print(f"Cloud Records                       :{total_tracked} rows synced")
        print(f"Potential Scholarship Awards        : ${total_value:,.2f}")
        print(f"Not Applied                         : {not_applied_count}")
        print(f"Applied                             : {applied_count}")
        print(f"Rejected                            : {rejected_count}")
        print(f"Accepted                            : {accepted_count}")
        print("=" * 50 + "\n")

    else:
        print("\n No entries found inside the spreadsheet")
except Exception as e:
    print("Failed to compile Status Report")

if sheet is not None:
    format_sheet(sheet)
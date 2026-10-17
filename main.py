import os
import imaplib
import email
import re
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font
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

    return name, amount

# Checks for repeating email and removes duplicates
existing_scholarships = {}
if os.path.exists("scholarship.xlsx"):
    try:
        existing_df = pd.read_excel("scholarship_tracker.xlsx")
        for _, row in existing_df.iterrows():
            unique_key = str(row.get("Date")), str(row.get("Sender")), str(row.get("Scholarship_name"))
            existing_scholarships[unique_key] = dict(row)
        print(f"Loaded {len(existing_scholarships)} existing entries.")
    except:
        print(f"Counld not read existing file")

# Connects to the IMAP server over SSL and fetches the last 100 emails containing the keyword "scholarship"
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
new_count = 0

try:
    print("Logging in...")
    mail.login(EMAIL, PASSWORD)
    mail.select('"[Gmail]/All Mail"')

    print("Fetching emails...")
    status, messages = mail.search(None, '(OR (TEXT "scholarship") (SUBJECT "scholarship"))')
    if status != "OK":
        raise RuntimeError(f"Unable to search inbox: {status}")

    email_ids = messages[0].split() if messages and messages[0] else []
    email_ids.reverse()
    last_500_emails = email_ids[: 500]

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

        body_text = get_email(msg)
        s_name, s_amount = extract_details(body_text, subject)
        existing_scholarships[email_key] = {
            "Date": msg_date,
            "Sender": msg_sender,
            "Scholarship": subject,
            "Amount": s_amount,
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
if existing_scholarships:
    try:
        email_data = list(existing_scholarships.values()) 
        df = pd.DataFrame(email_data)
        df.to_excel("scholarship_tracker.xlsx", index=False)

        total_tracked = len(df)

        status_count = df["Status"].value_counts()
        not_applied_count = status_count.get("Not Applied", 0)
        applied_count = status_count.get("Applied", 0)
        review_count = status_count.get("In Review", 0)

        total_value = 0
        for amount in df["Amount"]:
            if amount != "Not Specified":
                clear_amount = re.sub(r"[^\d.]", "", str(amount))
                if clear_amount:
                    total_value += float(clear_amount)
        print("\n"+ "=" * 50)
        print("Scholarship Tracker Status Report")
        print("="*50)
        print("System Status                    : ACTIVE")
        print(f"Total Email Recorded            : {total_tracked}")
        print(f"Potential Scholarship Awards    : ${total_value:,.2f}")
        print(f"Not Applied:                    : {not_applied_count}")
        print(f"Applied:                        : {applied_count}")
        print(f"In Review:                      : {review_count}")
        print("=" * 50+ "\n")
        print(f"Excel spreadsheet 'scholarship_tracker.xlsx' updated {new_count} entries successfully.")
    except PermissionError:
        print(f"Error: Close your Excel file if you have it open and run it again.")
else:
    print("No emails found or no data was retrieved.")
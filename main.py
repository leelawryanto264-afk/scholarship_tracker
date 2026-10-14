import os
import imaplib
import email
import pandas as pd

EMAIL = os.getenv("EMAIL", "email@example.com")
PASSWORD = os.getenv("PASSWORD", "password")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")

mail = imaplib.IMAP4_SSL(IMAP_SERVER)

try:
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    if status != "OK":
        raise RuntimeError(f"Unable to search inbox: {status}")

    email_ids = messages[0].split() if messages and messages[0] else []
    last_50_emails = email_ids[-50:]
    email_data = []

    for e_id in last_50_emails:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        if status != "OK":
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_data.append({
                    "Date": msg.get("Date"),
                    "Sender": msg.get("From"),
                    "Subject": msg.get("Subject"),
                })
finally:
    mail.logout()

if email_data:
    df = pd.DataFrame(email_data)
    df.to_excel("gmail_emails.xlsx", index=False)
    print("Excel spreadsheet 'gmail_emails.xlsx' created successfully.")
else:
    print("No emails found or no data was retrieved.")
import re



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
                clean_text = re.sub(r'<[^>]+>', ' ', html)
                return clean_text

    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            return msg.get_payload(decode=True).decode(errors="ignore")
        elif content_type == "text/html":
            html = msg.get_payload(decode=True).decode(errors="ignore")
            clean_text = re.sub(r"<[^>]+>", " ", html)
            return clean_text
    return ""

# Parses through email contents and extracts relevant data into a structured format using regex
def extract_details(text, subject):
    name = subject.strip() if subject else "Unknown Scholarship"
    name = re.sub(r"^\x20-\x7E", "", name)
    clean_text = " ".join(text.split())
    amount_match = re.search(r"\$\s?([\d,]+(?:\.\d{2})?)", subject)
    amount = amount_match.group(0) if amount_match else "Not specified"
    return name, amount
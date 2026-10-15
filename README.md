# Scholarship Email Parser

A python script that automatically extracts scholarship information from Gmail and saves it directly into an Excel spreadsheet.

## Features

- **IMAP Fetching Email:** Connects to any standard email server over SSL to pull its contents dynamically
- **Regex:** Uses pattern matching to find
- **Pandas:** Compiles relevant data and parsed information
- **Excel Export:** Auto-creates a tracker file with one script

## Data Extracted

- **Date Received:** Timestamp metadata
- **Organization:** Decoded string
- **Scholarship Name:** Title pulled from the subject line
- **Amount:** Financial award given
- **Essay:** States if an essay prompt/reuirement is needed
- **Requirements:** Requirements needed to receive scholarship
- status?

## Requirements and Installations

### 1. Dependencies

The python script relies on pandas for handling spreadsheets and openpyxl as manipulating the spreadsheet and standard python libraries, re, and email

```bash
pip install pandas openpyxl
```

### 2. Configure Email Settings

To protect your personal information:

- **Gmail Users:** Set up 2-Step Verification on your account, then generate a 16 letter code
- **Outlook/Yahoo Users:** Check your email settings to confirm that IMAP access is on

## Script Configuration and Usage

1. open main.py and replace values for your account details

```
EMAIL = your_email@gmail.com
PASSWORD = xxxx xxxx xxxx
IMAP_SERVER = imap.gmail.com
```

2. Run the processor from your terminal:

```
python main.py
```

3. Open the generated 'scholarship_tracker.xlsx' document in Excel

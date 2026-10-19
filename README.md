# Scholarship Email Parser

A python script automation system that logs into the user's email via IMAP, extracts its contents into organized rows and columns, and syncs them directly into Google Sheets. Some extra featuresinclude a CLI status report detailing your total funding pools and a file that can let the user customize their own theme.

---

## Directory Structure

- **main.py** - The central engine loop that controls email
- **cloud_sync** - Handles authentication and row uploads
- **parser.py** - Uses a simple script made with regex patterns to extract content
- **format.py** - Dynamically applies data validation and layout custom themes

---

## Tech Stack, Features, and Installment

### Tech Stack

- **Pandas:** Compiles relevant data and parsed information
- **IMAP Fetching Email:** Connects to any standard inboxes and pull its contents dynamically
- **Regex:** Uses pattern recognition in the email to find reward amount and dates
- **Dotenv:** Loads private .env keys away from the source execute tracking
- **Google-auth:** Access scopes using client service account needed for Google APIs
- **Gspread:** Simplifies read, write, and cell formating by direct cloud interface
- **Python 3.0+:** Core programming language
- **Google Sheets API:** Serves as the cloud layer for entry synchronization

---

### Features

- **Automated Inbox Scanning:** Securely connects to your inbox using IMAP to fetch scholarship data
- **Smart Reward Extraction:** Uses regular expressions to target subject lines and isolate cash values
- **App-Style Cloud Tracking:** Connects to Google Sheets to organize entries into a pastel-themed layout

---

### Data Extracted

- **Date:** Timestamp metadata matching when the email was received
- **Sender:** The parsed email address originating the message
- **Scholarship Name:** Title pulled from the subject line via regex
- **Amount:** Financial award potentially given using regex patterns
- **Status** Set automatically to a baseline of "Not Applied"

---

## Requirements and Installations

### 1. Install Your Virtual Environment

Open your terminal and type:

```bash
Linux:
source myenv/bin activate

Windows:
myenv/bin/activate
```

### 2. Install Required External Packages

```bash
pip install pandas google-auth gspread python-dotenv
```

### 3. Open main.py and replace values for your account details

```
EMAIL = your_email@gmail.com
PASSWORD = xxxx xxxx xxxx xxxx
IMAP_SERVER = imap.gmail.com
```

### 4. Run main.py on Your Terminal:

```
python main.py
```

### 5. Open the generated 'Scholarship Tracker' in Google Sheets

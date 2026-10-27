# Scholarship Email Parser

A python script automation system that logs into the user's email via IMAP, extracts its contents into organized rows and columns, and syncs them directly into Google Sheets. Some extra features include a CLI status report detailing your total funding pools and a file that can let the user customize their own theme.

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
# Create the Environment
python -m venv myenv

# Linux:
source myenv/bin/activate

```

### 2. Install Required External Packages

```bash
pip install pandas google-auth gspread python-dotenv
```

### 3. Create and Configure your .env File:

```
EMAIL = your_email@gmail.com
PASSWORD = xxxxxxxxxxxxxxxx
SHEET_URL = *leave blank*
```

### 4. Generate Your Gmail Password

1. Go to your Google Account Settings
2. Make sure 2 step verification is on
3. Click on 2 step verification and select app passwords
4. Provide a name and click create
5. Copy the password and paste it into PASSWORD in .env (remove any extra spaces)

### 5. Google Service Account & google_credentials.json Setup

To allow the application to securely connect and sync data with Google Sheets:

1. Go to the Google Cloud Console.
2. Create a new project (or select an existing one).
3. In the search bar at the top, look for **Google Sheets API** and click **Enable**. Do the exact same thing for the **Google Drive API**.
4. Navigate to **IAM & Admin** > **Service Accounts** from the left-hand sidebar menu.
5. Click the **Create Service Account** button at the top, give it a name (like `scholarship-tracker`), and click **Done** (you can skip the optional role settings).
6. Find your newly created Service Account in the list and click on its email address.
7. Switch to the **Keys** tab at the top, then click **Add Key** > **Create New Key**.
8. Select **JSON** as the key type and click **Create**. This will automatically download a file to your computer.
9. **Rename** that downloaded file to exactly `google_credentials.json` and place it directly into the root folder of this project (next to `main.py` or your release binary).
10. **Crucial Step:** Open your `google_credentials.json` file, copy the unique `"client_email"` address listed inside it, open your target Google Sheet in your web browser, click **Share**, and add that client email address as an **Editor**.

```

### 6. Run main.py on Your Terminal:

```

python main.py

```

```

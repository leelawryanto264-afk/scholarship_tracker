import os
import json
import gspread
from google.oauth2.service_account import Credentials


sheet_url = os.environ.get("SHEET_URL")
credentials_file = "google_credentials.json"

def connect_cloud(sheet_url=sheet_url):
	if not os.path.exists(credentials_file):
		print(f"\n Cloud sync error: {credentials_file} missing from project directory")
		return None
	else:
		try:
			scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
			with open(credentials_file, "r") as f:
				creds_data = json.load(f)

			if "private_key" in creds_data:
				creds_data["private_key"] = creds_data["private_key"].replace("\\n", "\n")

			creds = Credentials.from_service_account_info(creds_data, scopes=scope)
			client = gspread.authorize(creds)

			if sheet_url:
				wb = client.open_by_url(sheet_url)
			else:
				wb = client.create("Scholarship Tracker")
				print(f"New spreadsheet created! Please add the following url to your configuration file")
				print(f"URL: {wb.url}")

			return wb.sheet1
		except Exception as e:
			print(e)
			return None

def upload_row(sheet, payload):
	if sheet is None:
		return
	try:
		sheet.append_row([
			payload["Date"],
			payload["Sender"],
			payload["Scholarship Name"],
			payload["Amount"],
			payload["Status"]
		])
		print("...")
	except Exception as e:
			print(e)
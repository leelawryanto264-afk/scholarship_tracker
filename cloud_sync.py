import os

sheet_name = "Scholarship Tracker"
sheet_url = "https://docs.google.com/spreadsheets/d/1IAZSTeuVZYa5wJgka9djEf2TsWVKleUGtJQ3bfrO3dI/edit?gid=0#gid=0"
credentials_file = "google_credentials.json"

def connect_cloud(sheet_url=sheet_url):
  scope = ["spreadsheets", "drive"]


  if not os.path.exists(credentials_file):
    print(f"\n Cloud sync error: {credentials_file} missing from project directory")
    return None, {}

def upload_row(sheet, payload):
  if sheet is None:
    print("fahh")
    return
  try:
    sheet.append_row([
      payload["Date"],
      payload["Sender"],
      payload["Scholarship Name"],
      payload["Amount"],
      payload["Status"]
    ])
    print("yippie")
  except Exception as e:
      print(e)
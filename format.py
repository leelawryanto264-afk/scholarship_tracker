from gspread.utils import ValidationConditionType

def format_sheet(sheet):
	if sheet is None:
		return
	
	colors = {
		"header_bg": {"red": 0.11, "green": 0.13, "blue": 0.16},
		"text_light": {"red": 0.95, "green": 0.96, "blue": 0.98},
		"grid_lines":{"red": 0.88, "green": 0.91, "blue": 0.93},
		"text_dark": {"red": 0.18, "green": 0.20, "blue": 0.24}
	}
	
	sheet.batch_format([
		{
			"range":"A1:E1",
			"format": {
				"backgroundColor": colors["header_bg"],
				"textFormat": {
					"fontFamily": "Roboto",
					"fontSize": 11,
					"bold": True,
					"foregroundColor": colors["text_light"]
				},
				"horizontalAlignment": "CENTER",
				"verticalAlignment": "MIDDLE"
			}
		},
		{
			"range": "A2:A600",
			"format": {"horizontalAlignment": "CENTER"}
		},
		{
			"range": "D2:D600",
			"format": {"horizontalAlignment": "RIGHT"}
		},
		{
			"range": "E2:E600",
			"format": {"horizontalAlignment": "CENTER"}
		}
	])

	conditional_rules = [
		{"value": "Accepted", "bg": {"red": 0.85, "green": 0.94, "blue": 0.88}, "text": {"red": 0.11, "green": 0.41, "blue": 0.23}},
		{"value": "Applied", "bg": {"red": 0.84, "green": 0.91, "blue": 0.97}, "text": {"red": 0.08, "green": 0.35, "blue": 0.65}},
		{"value": "Rejected", "bg": {"red": 0.98, "green": 0.85, "blue": 0.85}, "text": {"red": 0.69, "green": 0.11, "blue": 0.11}},
		{"value": "Not Applied", "bg": {"red": 0.99, "green": 0.95, "blue": 0.81}, "text": {"red": 0.61,"green": 0.44, "blue": 0.03}}
	]

	rules_payload = []

	for rule in conditional_rules:
		rules_payload.append({
			"addConditionalFormatRule": {
				"rule": {
					"ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": 600, "startColumnIndex": 4, "endColumnIndex": 5}],
					"booleanRule": {
						"condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": rule["value"]}]},
						"format": {
							"backgroundColor": rule["bg"],
							"textFormat": {"foregroundColor": rule["text"], "bold": True}
						}
					}
				},
				"index": 0
			}
		})

	sheet.spreadsheet.batch_update({"requests": rules_payload})


	status_options = ["Not Applied", "Applied", "Rejected", "Accepted"]

	sheet.add_validation(
		"E2:E500",
		ValidationConditionType.one_of_list,
		status_options,
		showCustomUi=True,
		strict=True
	)
	sheet.spreadsheet.batch_update({
		"requests": [
			{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
			{"autoResizeDimensions": {"dimensions": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 5}}}
		]
	})
from gspread.utils import ValidationConditionType

def format_sheet(sheet):
	if sheet is None:
		return
	
	colors = {
		"header_bg": {"red": 0.93, "green": 0.81, "blue": 0.76},
		"text_dark": {"red": 0.44, "green": 0.34, "blue": 0.31},
		"cell_bg": {"red": 0.96, "green": 0.89, "blue": 0.86},
		"text": {"red": 1.00, "green": 1.00, "blue": 1.0},
		"border_line": {"red": 0.89, "green": 0.82, "blue":0.79 }
	}
	
	sheet.batch_format([
		{
			"range":"A1:E1",
			"format": {
				"backgroundColor": colors["header_bg"],
				"textFormat": {
					"fontFamily": "Roboto",
					"fontSize": 12,
					"bold": True,
					"foregroundColor": colors["text"]
				},
				"horizontalAlignment": "CENTER",
				"verticalAlignment": "MIDDLE"
			}
		},
		{
			"range": "A2:E100",
			"format": {
				"backgroundColor": colors["cell_bg"],
				"textFormat": {
					"fontFamily": "Roboto",
					"fontSize": 10,
					"foregroundColor": colors["text_dark"]
				},
				"verticalAlignment": "MIDDLE"
			}
		},
		{
			"range": "A2:A100",
			"format": {"horizontalAlignment": "LEFT"}
		},
		{
			"range": "D2:D100",
			"format": {"horizontalAlignment": "RIGHT"}
		},
		{
			"range": "E2:E100",
			"format": {"horizontalAlignment": "CENTER"}
		}
	])

	conditional_rules = [
		{"value": "Accepted", "bg": {"red": 0.88, "green": 0.93, "blue": 0.89}, "text": {"red": 0.28, "green": 0.45, "blue": 0.31}},
		{"value": "Applied", "bg": {"red": 0.86, "green": 0.90, "blue": 0.93}, "text": {"red": 0.25, "green": 0.38, "blue": 0.49}},
		{"value": "Rejected", "bg": {"red": 0.94, "green": 0.86, "blue": 0.85}, "text": {"red": 0.58, "green": 0.27, "blue": 0.24}},
		{"value": "Not Applied", "bg": {"red": 0.95, "green": 0.89, "blue": 0.84}, "text": {"red": 0.51,"green": 0.38, "blue": 0.27}}
	]

	rules_payload = []

	for rule in conditional_rules:
		rules_payload.append({
			"addConditionalFormatRule": {
				"rule": {
					"ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": 100, "startColumnIndex": 4, "endColumnIndex": 5}],
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
	rules_payload += [
		{
			"updateSheetProperties": {
				"properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}},
				"fields": "gridProperties.frozenRowCount"
			}
		},
		{
			"autoResizeDimensions": {
				"dimensions": {
						"sheetId": sheet.id,
						"dimension": "COLUMNS",
						"startIndex": 0,
						"endIndex": 5				
				}
			}
		},
		{
			"updateDimensionProperties": {
				"range": {
					"sheetId": sheet.id,
					"dimension": "ROWS",
					"startIndex": 1,
					"endIndex": 100
				},
				"properties": {"pixelSize": 32},
				"fields": "pixelSize"
			}
		},
		{
			"updateBorders": {
				"range": {
					"sheetId":sheet.id,
					"startRowIndex": 0,
					"endRowIndex": 100,
					"startColumnIndex": 0,
					"endColumnIndex": 5
				},
				"bottom": {"style": "SOLID", "color": colors["border_line"]},
				"innerHorizontal": {"style": "SOLID", "color": colors["border_line"]}
			}
		},
	]
		
	sheet.spreadsheet.batch_update({"requests": rules_payload})


	status_options = ["Not Applied", "Applied", "Rejected", "Accepted"]

	sheet.add_validation(
		"E2:E500",
		ValidationConditionType.one_of_list,
		status_options,
		showCustomUi=True,
		strict=True
	)
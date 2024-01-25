import gspread
import math
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('ad_astra')

score_table = SHEET.worksheet("highscore")

def get_score():
    score_rows = score_table.get_all_values()
    score_list = []
    for row in score_rows:
        score_list.append(f'{row[0]}{"  "}{"-"*(72-len(row[0])-len(row[1]))}{"  "}{row[1]}')
    return score_list

import gspread
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

MAX_ENTRIES = 10

def get_score() -> list:
    score_rows = get_rows()
    score_list = []
    for row in score_rows:
        # Pre-format names and scores for output
        score_list.append(f'{row[0]}{"  "}{"-"*(72-len(row[0])-len(row[1]))}{"  "}{row[1]}')
    return score_list

def get_rows():
    return score_table.get_all_values()

def write_score(new_score: int, new_name: str):
    # get score list
    score_list = get_rows()
    # count entries
    entries_num = len(score_list)
    # compare last entry to new score
    last_score = int(score_list[-1][1])
    # add score to list and sort
    if entries_num < MAX_ENTRIES:
        score_list.append([new_name, new_score])
        print(score_list)
        new_score_list = sorted(score_list, key=lambda entry: int(entry[1]), reverse=True)
        score_table.update(values=new_score_list, range_name='A1:B10')
        print(new_score_list)
    else:
        if new_score > last_score:
            score_list.append([new_name, new_score])
            print(score_list)
            new_score_list = sorted(score_list, key=lambda entry: int(entry[1]), reverse=True)
            new_score_list.pop(-1)
            score_table.update(values=new_score_list, range_name='A1:B10')

            print(new_score_list)


    # write list to sheet
    
    return

#write_score(80, 'hoho')

import gspread
from google.oauth2.service_account import Credentials
import textwrap

class Sheet:
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
    texts =  SHEET.worksheet("texts")

    # Max highscore entries
    MAX_ENTRIES = 10
    GREEN = "\033[32m"
    RESET = "\033[0m"


    def __init__(self):
        self.messages = self.texts.get_all_values()
        self.msg_dict = dict(self.messages)
        #print(self.msg_dict)
        #input()
        
        
    def get_score(self) -> list:
        score_rows = self.get_rows()
        score_list = []
        for row in score_rows:
            # Pre-format names and scores for output
            score_list.append(f'{self.GREEN}{row[0]}{"  "}{"⋅"*(72-len(row[0])-len(row[1]))}{"  "}{row[1]}{self.RESET}')
        return score_list

    def get_rows(self):
        return self.score_table.get_all_values()

    def write_score(self, new_score: int, new_name: str):
        # get score list
        score_list = self.get_rows()
        # count entries
        entries_num = len(score_list)
        # compare last entry to new score
        last_score = int(score_list[-1][1])
        # add score to list and sort
        if entries_num < self.MAX_ENTRIES:
            score_list.append([new_name, new_score])
            #print(score_list)
            new_score_list = sorted(score_list, key=lambda entry: int(entry[1]), reverse=True)
            self.score_table.update(values=new_score_list, range_name='A1:B10')
            #print(new_score_list)
        else:
            if new_score > last_score:
                score_list.append([new_name, new_score])
            # print(score_list)
                new_score_list = sorted(score_list, key=lambda entry: int(entry[1]), reverse=True)
                new_score_list.pop(-1)
                self.score_table.update(values=new_score_list, range_name='A1:B10')

            # print(new_score_list)


    def get_mission_msg(self, role, level, success, fname):
        key = f'ml_{role[:3].lower()}_{level}_{"suc" if success else "fail"}'
        return self.msg_dict[key].format(name=fname)


    def get_text(self, key):
        if '\n' in self.msg_dict[key] or len(self.msg_dict[key]) > 76:
            message_raw = self.msg_dict[key].split("\n")
            message_wrapped = []
            message = []
            message_wrapped.extend(textwrap.wrap(el, 76) if el else " " for el in message_raw)
            for el in message_wrapped:
                message.extend(el)
        else:
            message = self.msg_dict[key]
        return message
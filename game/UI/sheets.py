"""Contains the class Sheet which establishes a connection to Google sheet

The class accesses the data in the spreadsheet, formats and returns the data
on demand, and writes new data into the spreadsheet.
"""
import textwrap
import gspread
from google.oauth2.service_account import Credentials


class Sheet:
    """Establishes connection to Google sheet and handles data input/output

    Opens the worksheet 'highscore' containing the highscore table and the
    worksheet 'texts' containing all messages that will be shown to the player.
    On instantiation, all messages from the sheet 'texts' are loaded into a
    dictionary. Each message has a unique ID with which it can be accessed.

    Attributes:
        SCOPE: List with scope URLs
        CREDS: The constructed credentials
        SCOPED_CREDS: Credentials prepared by oauth2 module
        GSPREAD_CLIENT: Client instance for authorized Google API access
        SHEET: Spreadsheet instance for Google sheet 'ad_astra' returned by
            gspread module
        score_table: Worksheet instance for 'highscore'
        texts: Worksheet instance for 'texts'
        MAX_ENTRIES (int): Maximum highscore entries allowed
        GREEN, RESET (str): ANSI style codes
        
    Methods:
        get_score(): Retrieves list with formatted highscore entries
        write_score(): Writes new name and score into highscore sheet
        get_mission_msg(): Retrieves specific description of mission results
            for each cadet
        get_text(): Retrieves formatted message for specific key
    """
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
    texts = SHEET.worksheet("texts")
    # Max highscore entries allowed
    MAX_ENTRIES = 10
    # ANSI color codes
    GREEN = "\033[32;1m"
    RESET = "\033[0m"

    def __init__(self):
        # Build a dictionary with all messages in the 'texts' worksheet
        self.messages = self.texts.get_all_values()
        self.msg_dict = dict(self.messages)

    def get_score(self) -> list:
        """Reads highscore table from worksheet and returns it in list form

        The returned list contains preformatted strings that can be fed into
        the Display module.

        Returns:
            list: A list with MAX_ENTRIES entries (default: 10) 
        """
        score_rows = self.score_table.get_all_values()
        score_list = []
        for i, row in enumerate(score_rows, 1):
            # Pre-format names and scores for output
            score_list.append(
                f'{self.GREEN}{i}{". "}{row[0]}{"  "}'
                f'{"⋅"*(60-len(str(i))-len(row[0])-len(row[1]))}'
                f'{"  "}{row[1]}{self.RESET}')
        return score_list

    def write_score(self, new_score: int, new_name: str):
        """Writes player name and score into the highscore table

        Args:
            new_score (int): Player score to write into the highscore table
            new_name (str): Player name to write into the highscore table
        """
        # Get score list from highscore worksheet
        score_list = self.score_table.get_all_values()
        entries_num = len(score_list)
        # Get lowest score in the table
        last_score = int(score_list[-1][1])
        # If less than max amount of entries: append new score to list
        if entries_num < self.MAX_ENTRIES:
            score_list.append([new_name, new_score])
            # Sort all entries by score in descending order
            new_score_list = sorted(
                score_list, key=lambda entry: int(entry[1]), reverse=True)
            # Update worksheet with the new sorted list
            self.score_table.update(values=new_score_list, range_name='A1:B10')
        else:
            # If new player score is high enough for the highscore:
            if new_score > last_score:
                # Append, sort, and remove the last (lowest) entry
                score_list.append([new_name, new_score])
                new_score_list = sorted(
                    score_list, key=lambda entry: int(entry[1]), reverse=True)
                new_score_list.pop(-1)
                self.score_table.update(
                    values=new_score_list, range_name='A1:B10')

    def get_mission_msg(self, role: str, level: str, success: bool,
                        fname: str) -> str:
        """Construct ID from args and retrieve the appropriate message

        Args:
            role (str): Name of the role such as Captain, Doctor etc
            level (str): 'low', 'mid', or 'high', depending on task difficulty
            success (bool): Whether the cadet succeeded at the task 
            fname (str): First name of the cadet

        Returns:
            str: Descriptive text for the specific role and cadet
        """
        key = f'ml_{role[:3].lower()}_{level}_{"suc" if success else "fail"}'
        return self.get_text(key, fname)

    def get_text(self, key: str, value=None) -> str:
        """Retrieves and formats message from the dictionary for specified key
        
        Takes the message ID as key and returns the message string or a list
        with wrapped message strings.

        Args:
            key (str): Message ID

        Returns:
            str: Preformatted message
        """
        if value:
            message_raw = self.msg_dict[key].format(value=value)
        else:
            message_raw = self.msg_dict[key]
        if '\n' in message_raw or len(message_raw) > 76:
            message_list = message_raw.split("\n")
            message = []
            message_wrapped = []
            for row in message_list:
                if len(row) > 76:
                    message_wrapped = textwrap.wrap(row, 76)
                    message.extend(message_wrapped)
                elif len(row) == 0:
                    message.append(" ")
                else:
                    message.append(row)
        else:
            message = message_raw
        return message

    def get_list(self, key: str) -> list:
        """Retrieves items from the message dictionary based on specified key

        Takes a key as input and retrieves the corresponding value from the
        message dictionary. The value must be a string containing items
        separated by commas (', '). The function splits the string and returns
        a list of items.

        Args:
            key (str): Message ID to access the list in the message dictionary

        Returns:
            list: A list of items retrieved from the message dictionary
        """
        list_raw = self.msg_dict[key]
        return list_raw.split(', ')

import math
#import msvcrt
import random
import os
import time
from typing import Union

# TODO: remove redundant screen drawings
class Display:
    """Processes text and renders the screen output
    
    Contains viewport and output formatting data, formats and handles all
    print operations.
    
    Attributes:
        HEIGHT (int): Max allowed viewport height minus input line
        WIDTH (int): Max allowed viewport width
        BORDER_CHAR (str): Character to use for the outer border
        INPUT_PROMPT (str): Characters to show before the input line
        EMPTY_ROW (str): Empty row string with border chars
        ERROR_ROW_NR int): Index of the row with error output
        MENU_ROW_NR (int): Index of the row with menu elements
        rows (list): 23 strings containing all screen output
    
    Methods:
        clear(): Inserts empty rows to clear terminal output
        build_screen():  Formats and builds a list of strings passed from
            other functions to prepare terminal output
        build_menu(): Formats and builds menu string and error string
            to prepare terminal output
        build_input(): Formats input prompt and calls _draw to draw screen
    """
    HEIGHT = 22
    WIDTH = 80
    BORDER_CHAR = "▓"
    INPUT_PROMPT = '▓▓▓ :: '
    EMPTY_ROW = f'{BORDER_CHAR}{" ":<78}{BORDER_CHAR}'
    ERROR_ROW_NR = 21
    MENU_ROW_NR = 20
    ENTER = 'Press ENTER to continue :: '


    def __init__(self):
        self.rows = []
        self.empty_screen()
        self.filled = []
        self.first_time = True


    def empty_screen(self):
        """Creates a list of rows containing border chars and empty space"""
        self.rows = [str(self.BORDER_CHAR * self.WIDTH)]
        self.rows.extend([self.EMPTY_ROW for _ in range(self.HEIGHT - 4)])
        self.rows.extend([self.BORDER_CHAR * self.WIDTH for _ in range(2)])
        self.rows.append(str(self.BORDER_CHAR * self.WIDTH))


    def clear(self, indexes=[_ for _ in range(1, 19)], is_error=False):
        """Clears specific rows in the terminal
        
        Receives indexes to clear in the terminal and overwrites them in the 
        self.row attribute with empty rows.

        Args:
            indexes (list, optional): List with indexes to be cleared.
                Defaults to all rows above the menu row.
            is_error (bool, optional): States whether the row to clear is
                the error row. Defaults to False.
        """
        if is_error:
            self.rows[self.ERROR_ROW_NR] = self.BORDER_CHAR * self.WIDTH
        else:
            for index in indexes:
                self.rows[index] = self.EMPTY_ROW


    def build_screen(self, text: Union[str, list, dict], row_nr=1, center=False, center_logo=False) -> None:
        """Prepares a text for terminal output above the menu row
        
        Receives a string, list, or dictionary, formats its contents,
        and overwrites the specified rows of self.rows with the contents.

        Args:
            text (str, list, dict): Message to print on screen.
            row_nr (int, optional): Row index at which to start. Defaults to 1.
            center (bool, optional): States whether the message should be
                centered on screen. Defaults to False.
        """
        result = ''
        if text:
            # String processing
            if isinstance(text, str):
                result = (f'{self.BORDER_CHAR}{" "}{text:<76}{" "}'
                         f'{self.BORDER_CHAR}')
                self.rows[row_nr] = result
            # List processing
            elif isinstance(text, list):

                if center_logo:
                    # Draw screen filled with border chars, list form
                    # make list out of each row of finished logo screen
                    # make list with coord tuples
                    # choose random tuple, remove from tuple list
                    # set char to logo char
                    
                    # TODO: just do it once at game start
                    if self.first_time:
                        self.first_time = False
                        time.sleep(0.5)
                        rows_matrix_logo = []
                        for idx, line in enumerate(text):
                            result = (f'{self.BORDER_CHAR}{" "*26 + line:<78}'
                                        f'{self.BORDER_CHAR}')
                            self.rows[row_nr + idx] = result

                        # list with finished logo screen
                        for row in self.rows:
                            rows_matrix_logo.append(list(row))
                        #print(rows_matrix_logo)
                        #input()

                        # list with filled screen
                        self.rows = [str(self.BORDER_CHAR * self.WIDTH) for _ in range(self.HEIGHT)]
                        rows_matrix_filled = []
                        for row in self.rows:
                            rows_matrix_filled.append(list(row))
                        #input(self.build_input())
                        
                        # list wth coord tuples
                        coord_list = [(x, y) for x in range(self.HEIGHT) for y in range(self.WIDTH)]
                        len_coord = len(coord_list)
                        for x in range(math.floor(len_coord/60)-3):
                            for _ in range(10+x*5):
                                if len(coord_list) > 0:
                                    idx = random.choice(range(len(coord_list)))
                                    rows_matrix_filled[coord_list[idx][0]][coord_list[idx][1]] = rows_matrix_logo[coord_list[idx][0]][coord_list[idx][1]]
                                    coord_list.pop(idx)
                                else:
                                    break
                            for i in range(len(self.rows)):
                                self.rows[i] = ''.join(rows_matrix_filled[i])
                            self.draw()
                            time.sleep(0.03)
                            # Disable keyboard input while sleeping
                            #while msvcrt.kbhit():
                            #    msvcrt.getwch()
                        return
                    else:
                        for idx, line in enumerate(text):
                            result = (f'{self.BORDER_CHAR}{" "*26 + line:<78}'
                                        f'{self.BORDER_CHAR}')
                            self.rows[row_nr + idx] = result
                        return
                    
                # fix to have loop inside if else
                for idx, line in enumerate(text):
                    if center:
                        str_len = len(line)
                        result = (f'{self.BORDER_CHAR}{" "*math.ceil((78-str_len)/2) + line:<78}'
                                  f'{self.BORDER_CHAR}')
                    else:
                        result = (f'{self.BORDER_CHAR}{" "}{line:<76}{" "}'
                                 f'{self.BORDER_CHAR}')

                    # Fill the final list starting at specified row index
                    self.rows[row_nr + idx] = result
            # Dictionary processing:
            # The received dictionaries have the following format:
            # {key : ['', ..., '']}
            elif isinstance(text, dict):
                # Counter to keep track of current row index
                k = 0
                for key, value in text.items():
                    temp_list = [f'{key}: ']
                    # Make one list containing the key and all values
                    try:
                        for val in value:
                            temp_list.append(val)
                    except:
                        print("Internal error: Dictionary value is not a list")
                        input()
                    # Make sure key string is aligned to the left while all
                    # value strings start at column 17
                    for i in range(1, len(temp_list)):
                        if i == 1:
                            result = (f'{self.BORDER_CHAR}{" "}'
                                      f'{temp_list[0]:<16}{temp_list[i]:<61}'
                                      f'{self.BORDER_CHAR}')
                            self.rows[row_nr + k] = result
                        else:
                            result = (f'{self.BORDER_CHAR}{" " * 17}'
                                      f'{temp_list[i]:<61}{self.BORDER_CHAR}')
                            self.rows[row_nr + i + k - 1] = result
                    # Update row index to skip already added lines
                    k += i
            else:
                print("Internal error: text is not str, list, or dict")
                input()
                return
                
        else:
            #print("Internal error: text is empty")
            #input()
            return
            

    def build_menu(self, text: str, is_error=False,):
        """Prepares the menu row for terminal output
        
        Formats the string and overwrites the specified row index in self.rows.
        
        Args:
            text (str): String containing the menu elements, max 76 chars
            is_error (bool, optional): States if text is an error message.
                Defaults to False.
        """
        if is_error:
            result = f'{self.BORDER_CHAR}{" "}{text:>76}{" "}{self.BORDER_CHAR}'
            self.rows[self.ERROR_ROW_NR] = result
        else:
            result = f'{self.BORDER_CHAR}{" "}{text:<76}{" "}{self.BORDER_CHAR}'
            self.rows[self.MENU_ROW_NR] = result


    def build_input(self, prompt='', prompt_enter=False) -> str:
        """Draws the terminal and returns a user input prompt
        
        Calls __draw() to draw the terminal. Thus, the screen is only re-drawn
        whenever user input is required.

        Args:
            prompt (str, optional): Prompt to put before the user input.
                Defaults to ''.
            prompt_enter (bool, optional): States whether player should be
                prompted for the ENTER key

        Returns:
            str: String with user input decoration and prompt
        """
        self.draw()
        if prompt_enter:
            prompt = self.ENTER
            
        return self.INPUT_PROMPT + prompt

    def draw(self):
        """Clears the previous screen and re-draws the new terminal
        
        This function is usually called by build_input() to draw the screen
        just before receiving user input. It should be used on its own only
        before time.sleep() in order to avoid unnecessary re-drawing of the
        screen when the user can't even see the result.
        """
        os.system('cls||clear')
        #os.system("clear")
        for row in self.rows:
            print(f'{row}')


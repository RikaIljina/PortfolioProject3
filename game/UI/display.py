"""Contains Display class which handles all screen output"""
import math
import random
import os
import time
from typing import Union
from colorama import just_fix_windows_console


class Display:
    """Processes text and renders the screen output

    Contains screen and output formatting data, formats and handles all
    print operations.
    All Display methods expect strings or list elements with <76 characters.

    The Display class is used to print on screen:
    - Print menu choices on the screen:
        display.build_menu(menu_text_string)
    - Print an error message on the screen:
        display.build_menu(error_message_string, is_error=True)
    - Print a text above the menu:
        display.build_screen(
            str||list||dict, starting_row_nr, center, ansi)
        Valid starting_row_nr values: 1-18.
        Set 'center=True' to center the string or list.
        Set 'ansi=11' if the passed string or list elements contain ANSI codes.  
    - Clear error message:
        display.clear(is_error=True)
    - Clear menu line:
        display.menu('')
    - Clear all text above the menu:
        display.clear()
    - Clear specific rows:
        display.clear([1,2,...])
    - Take user input with correct placement and formatting of the prompt:
        input(self.display.build_input()).strip()

    The output is finally rendered on screen only when input() is called.
    To render output in-between (for example when using time.sleep), call
    display.draw().
    
    Args:
        sheet (object): Reference to Sheet class instance

    Attributes:
        HEIGHT (int): Max allowed viewport height minus input line
        WIDTH (int): Max allowed viewport width
        BORDER_CHAR (str): Character to use for the outer border
        INPUT_PROMPT (str): Characters to show before the input line
        EMPTY_ROW (str): Empty row string with border chars
        ERROR_ROW_NR int): Index of the row with error output
        MENU_ROW_NR (int): Index of the row with menu elements
        RED, GREEN, RESET (str): ANSI color codes
        rows (list): 23 strings containing all screen output
        first_time (bool): True if Display is being initialized for the first
            time; needed to only play loading animation once
        enter_prompt (str): String to show in the input prompt when expecting
            the player to only press ENTER

    Methods:
        empty_screen(): Builds an empty screen with borders
        clear(): Inserts empty rows to clear terminal output
        build_screen(): Formats and builds a string, a list of strings or a 
            dictionary passed from other functions to prepare terminal output
        build_menu(): Formats and builds menu string and error string
            to prepare terminal output
        build_input(): Formats input prompt and calls draw to draw screen
        draw(): Draws the screen; only needed when input prompt is not used
    """
    HEIGHT = 22
    WIDTH = 80
    BORDER_CHAR = "▓"
    INPUT_PROMPT = '▓▓▓ ⁞⁞ '
    EMPTY_ROW = f'{BORDER_CHAR}{" ":<78}{BORDER_CHAR}'
    ERROR_ROW_NR = 21
    MENU_ROW_NR = 20
    # ANSI codes for text styling
    RED_BG = "\033[41;1m"
    BRIGHT_GREEN = "\033[92;1m"
    RESET = "\033[0m"

    def __init__(self, sheet):
        self.sheet = sheet
        self.rows = []
        # Make sure the logo reveal animation is only played on first game load
        self.first_time = True
        self.enter_prompt = self.sheet.get_text('prompt_continue')
        self.empty_screen()
        # From colorama; makes sure ANSI codes are rendered correctly on
        # Windows
        just_fix_windows_console()

    def empty_screen(self):
        """Creates a list of rows containing border chars and empty space"""
        self.rows = [str(self.BORDER_CHAR * self.WIDTH)]
        self.rows.extend([self.EMPTY_ROW for _ in range(self.HEIGHT - 4)])
        self.rows.extend([self.BORDER_CHAR * self.WIDTH for _ in range(2)])
        self.rows.append(str(self.BORDER_CHAR * self.WIDTH))

    def clear(self, indexes=None, is_error=False):
        """Clears specific rows in the terminal

        Receives indexes to clear in the terminal and overwrites them in the 
        self.row attribute with empty rows.
        The value passed as 'indexes' is expected to be a list, even if it only
        contains one element (e.g. [10] to clear row 10).

        Args:
            indexes (list, optional): List with indexes to be cleared.
                Defaults to all rows above the menu row.
            is_error (bool, optional): States whether the row to clear is
                the error row. Defaults to False.
        """
        if indexes is None:
            indexes = list(range(1, 19))
        if is_error:
            self.rows[self.ERROR_ROW_NR] = self.BORDER_CHAR * self.WIDTH
        else:
            for index in indexes:
                self.rows[index] = self.EMPTY_ROW

    def build_screen(self, text: Union[str, list, dict], row_nr=1,
                     center=False, center_logo=False, ansi=0):
        """Prepares a text for terminal output above the menu row

        Receives a string, list, or dictionary and passes it on to the
        appropriate private method for processing.

        Args:
            text (str, list, dict): Message to print on screen.
            row_nr (int, optional): Row index at which to start. Defaults to 1.
            center (bool, optional): States whether the message should be
                centered on screen. Defaults to False.
            center_logo (bool, optional): States whether the message is the
                logo, which requires its own build logic and animation.
            ansi (int, optional): Amount of ANSI chars to subtract from the
                string length when building the correct string with borders;
                ansi=11 seems to work for all cases in this game
        """
        if not text:
            return
        # String processing
        if isinstance(text, str):
            self.__build_from_string(text, row_nr, center, ansi)
        # List processing
        elif isinstance(text, list):
            if center_logo:
                self.__build_logo_from_list(text, row_nr)
            else:
                self.__build_from_list(text, row_nr, center, ansi)
        # Dictionary processing:
        elif isinstance(text, dict):
            self.__build_from_dict(text, row_nr)
        else:
            raise TypeError("Internal error: text is not str, list, or dict")

    def build_menu(self, text: str, is_error=False,):
        """Prepares the menu and error rows for terminal output

        Formats the string and overwrites the row index of menu row or error
        row in in self.rows dictionary.

        Args:
            text (str): String containing the menu elements, max 76 chars
            is_error (bool, optional): States if text is an error message.
                Defaults to False.
        """
        if is_error:
            result = (f'{self.BORDER_CHAR}{self.RED_BG}{" "}{text:>76}{" "}'
                      f'{self.RESET}{self.BORDER_CHAR}')
            self.rows[self.ERROR_ROW_NR] = result
        else:
            result = (f'{self.BORDER_CHAR}{self.BRIGHT_GREEN}{"▶ "}{text:<74}'
                      f'{"◀ "}{self.RESET}{self.BORDER_CHAR}')
            self.rows[self.MENU_ROW_NR] = result

    def build_input(self, prompt='', prompt_enter=False) -> str:
        """Draws the terminal and returns a user input prompt

        Calls draw() to draw the terminal. Thus, the screen is always re-drawn
        whenever user input is required.

        Args:
            prompt (str, optional): Prompt to put before the user input.
                Defaults to ''.
            prompt_enter (bool, optional): States whether player should be
                prompted for the ENTER key.

        Returns:
            str: String with user input decoration and prompt
        """
        self.draw()
        if prompt_enter:
            prompt = self.enter_prompt

        return self.BRIGHT_GREEN + self.INPUT_PROMPT + prompt + self.RESET

    def draw(self, shallow_clear=False):
        """Clears the previous screen and re-draws the new terminal

        This function is usually called by build_input() to draw the screen
        just before receiving user input. It should be used on its own only
        before time.sleep() in order to avoid unnecessary re-drawing of the
        screen when the user can't even see the result.
        
        Args:
            shallow_clear (bool, optional): Indicates if it is sufficient to
                move the cursor into row 1 column 1 of the terminal instead of
                clearing the entire terminal. Reduces flickering while an
                animation is being rendered. Defaults to False.
        """
        # Info found on https://stackoverflow.com/questions/2084508/
        # clear-the-terminal-in-python
        if shallow_clear:
            # Only moves the cursor to row 1 column 1 without clearing the
            # screen or the input prompt
            print('\033[1;1H', end='')
        else:
            # Clears the entire screen including previous output and input
            # prompt
            print('\033c', end='')
        for row in self.rows:
            print(f'{row}')

    def __build_from_string(self, text: str, row_nr: int, center: bool,
                            ansi: int):
        """Prepares a string for terminal output
        
        Receives a string, formats its contents, and overwrites the specified
        row of self.rows with the contents.
        
        Args:
            text (str): Raw string with <76 characters to be prepared for
                terminal output 
            row_nr (int): Row number at which to display the string
            center (bool): True if the string must be centered on the screen 
            ansi (int): Amount of ANSI color code chars to be subtracted
        """
        # If the text will be centered, it must be prefaced with the
        # following amount of whitespaces:
        # max screen width (80) minus 2 border chars (->78)
        # minus length of text, result divided by 2.
        # If an ANSI code is present, the amount of ANSI chars must be
        # subtracted from the text length and added to the total width
        # to achieve the correct row length.
        if center:
            width = "<" + str(78 + ansi)
            str_len = len(text) - ansi
            result = (f'{self.BORDER_CHAR}'
                      f'{" "*math.ceil((78-str_len)/2) + text:{width}}'
                      f'{self.BORDER_CHAR}')
            self.rows[row_nr] = result
            return

        # Build a row from a string, aligned to the left
        width = "<" + str(76 + ansi)
        result = (f'{self.BORDER_CHAR}{" "}{text:{width}}{" "}'
                    f'{self.BORDER_CHAR}')
        self.rows[row_nr] = result

    def __build_logo_from_list(self, text: list, row_nr: int):
        """Prepares the logo for terminal output
        
        Receives the logo as a list, formats the contents of each element,
        and overwrites the specified rows of self.rows with the contents,
        starting at row_nr.
        If this method is called for the first time at game start, the logo
        reveal animation is played.
        
        Args:
            text (str): List with raw strings with <76 characters each to be
                prepared for terminal output 
            row_nr (int): Row number at which to display the first element
        """
        if self.first_time:
            # This bool makes sure that the reveal animation is only played
            # once at game start, not every time the player reaches the outer
            # menu.
            self.first_time = False
            time.sleep(0.5)
            self.flush_input()
            # Build the formatted screen rows with the logo inside
            for idx, line in enumerate(text):
                result = (f'{self.BORDER_CHAR}{" "*24 + line:<78}'
                          f'{self.BORDER_CHAR}')
                self.rows[row_nr + idx] = result
            # Turn the logo screen into a list with 23 rows where each row
            # contains a list of single characters
            rows_matrix_logo = []
            for row in self.rows:
                rows_matrix_logo.append(list(row))
            # Overwrite the screen to fill it with block characters
            self.rows = [str(self.BORDER_CHAR * self.WIDTH)
                         for _ in range(self.HEIGHT)]
            # Turn the filled screen into a list with 23 rows where each row
            # contains a list of single block characters
            rows_matrix_filled = []
            for row in self.rows:
                rows_matrix_filled.append(list(row))
            # Create a list with coordinate tuples for 23 rows and 80 columns
            coord_list = [(x, y) for x in range(self.HEIGHT)
                          for y in range(self.WIDTH)]
            len_coord = len(coord_list)
            # Loop over the coordinates list, randomly select several coords,
            # overwrite the filled screen characters with the logo screen
            # characters at the selected coordinates, and draw the screen.
            # 26 reps are needed to reveal the logo screen, but since
            # len_coord/60 is 29, 3 must be subtracted.
            for x in range(math.floor(len_coord/60)-3):
                # 10+x*5 makes sure that with each loop, more characters are
                # revealed at once.
                for _ in range(10+x*5):
                    if len(coord_list) > 0:
                        idx = random.choice(range(len(coord_list)))
                        row = coord_list[idx][0]
                        col = coord_list[idx][1]
                        rows_matrix_filled[row][col] = \
                            rows_matrix_logo[row][col]
                        coord_list.pop(idx)
                    else:
                        break
                # Join the single characters of the revealed logo to form
                # proper strings again
                for i in range(len(self.rows)):
                    self.rows[i] = ''.join(rows_matrix_filled[i])
                self.draw(shallow_clear=True)
                time.sleep(0.06)
                # Disable keyboard input while sleeping
                self.flush_input()
            return

        # Build logo without animation on subsequent playthroughs
        for idx, line in enumerate(text):
            result = (f'{self.BORDER_CHAR}{" "*24 + line:<78}'
                      f'{self.BORDER_CHAR}')
            self.rows[row_nr + idx] = result
        return

    def __build_from_list(self, text: list, row_nr: int, center:bool,
                          ansi:int):
        """Prepares a list for terminal output
        
        Receives a list, formats the contents of each element, and overwrites
        the specified rows of self.rows with the contents, starting at row_nr.
        
        Args:
            text (str): List with raw strings with <76 characters each to be
                prepared for terminal output 
            row_nr (int): Row number at which to display the first line
            center (bool): True if the lines must be centered on the screen 
            ansi (int): Amount of ANSI color code chars to be subtracted from
                each line
        """
        if center:
            # If the text will be centered, it must be prefaced with the
            # following amount of whitespaces:
            # max screen width (80) minus 2 border chars (->78)
            # minus length of text, result divided by 2.
            # If an ANSI code is present, the amount of ANSI chars must be
            # subtracted from the text length and added to the total width
            # to achieve the correct row length.
            for idx, line in enumerate(text):
                width = "<" + str(78 + ansi)
                str_len = len(line) - ansi
                result = (f'{self.BORDER_CHAR}'
                          f'{" "*math.ceil((78-str_len)/2) + line:{width}}'
                          f'{self.BORDER_CHAR}')
                # Fill the final list starting at specified row index
                self.rows[row_nr + idx] = result
            return

        # Build left-aligned list
        for idx, line in enumerate(text):
            width = "<" + str(76 + ansi)
            result = (f'{self.BORDER_CHAR}{" "}{line:{width}}{" "}'
                        f'{self.BORDER_CHAR}')
            # Fill the final list starting at specified row index
            self.rows[row_nr + idx] = result

    def __build_from_dict(self, text: dict, row_nr: int):
        """Prepares a dictionary for terminal output
        
        The dictionary contents will be presented as follows:
        Key1:     Value 1 string 1
                  Value 1 string 2
        LongKey2: Value 2 string 1
                  Value 2 string 2
                  
        The key must consist of max 14 characters.
        Each element in the value list must consist of max 60 characters. 

        Args:
            text (dict): The passed dictionary is expected to have the
                following format: {key: list(str(), ...)}
            row_nr (int): Row number at which to display the first line
        """
        # Counter to keep track of current row index
        k = 0
        for key, value in text.items():
            # Make one list containing the key and all sub-elements from value
            temp_list = [f'{key}: ']
            # This function expects the value to be a list
            if not isinstance(value, list):
                raise TypeError(
                    "Internal error: Dictionary value is not a list")
                #input()
                #return
            for val in value:
                temp_list.append(val)

            # Make sure the string containing the key is aligned to the left
            # while all other strings start at column 17.
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

    # Function copied from:
    # https://stackoverflow.com/questions/67083097/
    # how-to-prevent-user-input-into-console-when-program-is-running-in-python
    def flush_input(self):
        """ Flushes any pending user input from the input buffer
        
        This function is needed in scenarios where time.sleep is used to create
        a delay in the program execution before the next input prompt.
        By flushing the input, the user is presented with a clean input prompt,
        even if they pressed keys while waiting.

        Note: This function may not work as expected in all environments.
        """
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            import sys
            # For linux/unix
            import termios
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)

# Write your code to expect a terminal of 80 characters wide and 24 rows high

import os
import sys
import random
import math
import textwrap
import time
#import keyboard
#from pynput import keyboard


# Establish connection to Google sheets for highscore management
# Create Worksheet object for access to texts and highscore

class Player:
    """Contains player data and performs player-related operations
    
    Attributes:
        name (str): Player name as entered by user, set by a method in 
            the Menu object
        score (int): Player score as calculated by class method
        
    Methods:
        calculate_score(): Calculates player score at the end of the game
    
    """
    def __init__(self):
        self.name = ""
        self.score = 0


    def calculate_score(self, trial_runs: int, trial_max_runs: int, \
                        mission_data: object) -> int:
        """Calculates player score at the end of the game

        Args:
            trial_runs: Played trial runs as stored in Trial class instance
            trial_max_runs: Max trial runs as stored in Trial class instance
            mission_data: Reference to Mission class instance

        Returns:
            int: Resulting player score
        """
        mission_failed_penalty = 0 if mission_data.score >= 3 else 500
        mission_score_penalty = (5 - mission_data.score) * 100
        mission_prognosis_penalty = 100 - mission_data.prognosis
        skill_penalty = 500 - sum([value[1]
                                 for value in mission_data.crew.values()]) * 10
        trial_run_bonus = 0 if mission_failed_penalty != 0 else (
                trial_max_runs - trial_runs) * 10
        mission_difficulty_bonus = 0 if mission_failed_penalty != 0 else \
                mission_data.difficulty - mission_data.prognosis
        result = 1000 - mission_failed_penalty - mission_score_penalty \
            - mission_prognosis_penalty - skill_penalty \
            + mission_difficulty_bonus + trial_run_bonus

        return result

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
    HEIGHT = 23
    WIDTH = 80
    BORDER_CHAR = "▓"
    INPUT_PROMPT = '▓▓▓ :: '
    EMPTY_ROW = f'{BORDER_CHAR}{" ":<78}{BORDER_CHAR}'
    ERROR_ROW_NR = 21
    MENU_ROW_NR = 20


    def __init__(self):
        self.rows = []
        self.empty_screen()


    def empty_screen(self):
        """Creates a list of rows containing border chars and empty space"""
        self.rows = [str(self.BORDER_CHAR * self.WIDTH)]
        self.rows.extend([self.EMPTY_ROW for _ in range(self.HEIGHT - 5)])
        self.rows.extend([self.BORDER_CHAR * self.WIDTH for _ in range(3)])
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


    def build_screen(self, text: str|list|dict, row_nr=1, center=False, center_logo=False) -> None:
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
                for idx, line in enumerate(text):
                    if center_logo:
                        result = (f'{self.BORDER_CHAR}{" "*26 + line:<78}'
                                  f'{self.BORDER_CHAR}')
                    elif center:
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
            

    def build_menu(self, text: str, is_error=False):
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


    def build_input(self, prompt='') -> str:
        """Draws the terminal and returns a user input prompt
        
        Calls __draw() to draw the terminal. Thus, the screen is only re-drawn
        whenever user input is required.

        Args:
            prompt (str, optional): Prompt to put before the user input.
                Defaults to ''.

        Returns:
            str: String with user input decoration and prompt
        """
        self.__draw()

        return self.INPUT_PROMPT + prompt


    def __draw(self):
        """Clears the previous screen and re-draws the new terminal"""
        os.system('cls||clear')
        for row in self.rows:
            print(f'{row}')


class Cadets:
    """Cadet object
    
    Contains all cadet-related data and creates a cadets dictionary with
    names, skills, and skill values.
    
    Args:
        display (object): Reference to Display class instance
        player_name (object): Reference to Player class instance
    
    Attributes:
        SKILLS (list): Five skills the cadets are being tested for
        NAMES (list): Names to randomly choose from when building dict
        cadets (dict): Dict in the format {name: {skill: value, ...}, ... }
        display (object): Reference to Display class instance
        player_name (str): Name chosen by the user
        
    Methods:
        recruit(): Builds cadet dict and outputs message on screen
    """
    SKILLS = ["Captain", "Security Chief", "Engineer", "Doctor", "Pilot"]
    ALL_NAMES = ["Cadet Janeway", "Cadet Picard", "Cadet Kirk", "Cadet Kim",
                 "Cadet Paris", "Cadet Whorf", "Cadet Crusher", "Cadet Torres",
                 "Cadet Spock", "Cadet Yar", "Cadet Troi", "Cadet Sisko"]
    MAX_POINTS = 25
    LOWEST_SKILL = 1
    HIGHEST_SKILL = 10


    def __init__(self, display: object, player_name: object):
        self.display = display
        self.player_name = player_name
        self.names = random.sample(self.ALL_NAMES, 6)
        self.cadets = {}


    def recruit(self):
        """Initializes cadet dictionary
    
        Builds initial cadet dictionary with 6 cadets and their respective
        secret skill values. Outputs a message to the player.
        """
        self.cadets = {key: dict(zip(
                                 self.SKILLS, self.__cadet_skill_generator()))
                                 for key in self.names}
        message = [f'Welcome to Cat, {self.player_name}!', '',
                   ('The following cadets have volunteered for the upcoming '
                    'mission:'), '']
        message.extend(textwrap.wrap(f'{", ".join(self.names)}',
                                     self.display.WIDTH - 4))
        self.display.build_screen(message, row_nr=2)


    def __cadet_skill_generator(self) -> list:
        """Generates a list with 5 random skill values
        
        Each value lies between LOWEST_SKILL and HIGHEST_SKILL (1 - 10),
        with a total sum of MAX_POINTS (25).
        
        Attributes:
            MAX_POINTS (int): Total amount of skill points to divide among all 
                skills for each cadet
            LOWEST_SKILL (int): Lowest possible skill value
            HIGHEST_SKILL (int): Highest possible skill value
            skill_points (list): Five skill values
            skill_amount (int): Amount of skills currently used in the game (5)
        """
        skill_points = []
        skill_amount = len(self.SKILLS)

        for i in range(1, skill_amount + 1):
            # The 5th skill to be calculated always takes the remaining 
            # difference between the maximum possible points and the sum of 
            # used-up points
            if i == 5:
                points = self.MAX_POINTS - sum(skill_points)

            # The 4th skill to be calculated needs an upper range and a lower
            # range for the randomizer:
            # - upper range is the remaining points minus the minimum necessary
            # points for the last skill OR HIGHEST_SKILL, depending on which 
            # is lower
            # - lower range is the remainder of the remaining points divided by
            # (HIGHEST_SKILL*2)
            # # For example:
            # - The numbers [1,1,3] have been chosen for i 1-3. 20 points
            # remain to be distributed, which equals to (HIGHEST_SKILL*2).
            # As a result, lower_range is set to HIGHEST_SKILL (10) to make
            # sure that the last two skills receive enough points to add up
            # to 20.
            # - The numbers [10,1,1] have been chosen for i 1-3. 13 points
            # remain to be distributed, which is lower than (HIGHEST_SKILL*2)
            # but higher than HIGHEST_SKILL. As a result, lower_range is set to
            # the maximum of 1 or (13%(10*1)), which is 3. This makes sure that
            # the skill on i=4 receives at least 3 points, leaving max 10 
            # for i=5.
            elif i == 4:
                upper_range = min(self.MAX_POINTS - sum(skill_points[0:i-1])
                                  - (skill_amount-i) + 1, self.HIGHEST_SKILL + 1)
                if (self.MAX_POINTS - sum(skill_points[0:i-1])) < self.HIGHEST_SKILL:
                    lower_range = self.LOWEST_SKILL
                elif ((self.MAX_POINTS - sum(skill_points[0:i-1])) 
                      == self.HIGHEST_SKILL * 2):
                    lower_range = self.HIGHEST_SKILL
                else:
                    lower_range = max((self.MAX_POINTS - sum(skill_points[0:i-1]))
                                     % (self.HIGHEST_SKILL * (skill_amount-i)), 1)
                points = random.randrange(lower_range, upper_range)

            elif i == 3:
            # Analogous to 4th skill calculations
                upper_range = min(self.MAX_POINTS - sum(skill_points[0:i-1])
                                  - (skill_amount-i) + 1, self.HIGHEST_SKILL + 1)
                if (self.MAX_POINTS - sum(skill_points[0:i-1])) < self.HIGHEST_SKILL*2:
                    lower_range = self.LOWEST_SKILL
                else:
                    lower_range = max(
                        (self.MAX_POINTS - sum(skill_points[0:i-1]))
                        % (self.HIGHEST_SKILL * (skill_amount-i)), 1)
                points = random.randrange(lower_range, upper_range)

            else:
            # The first two values can be chosen randomly
                points = random.randrange(self.LOWEST_SKILL, self.HIGHEST_SKILL + 1)

            skill_points.append(points)

        return skill_points


class Trials:
    """Calculates and stores results of the 'Trials' game phase
    
    Calculates the results of two competing cadets and collects all results
    in a trials log. Keeps track of the maximum allowed amount of trial runs.
    
    Args:
        display (object): Reference to Display class instance
        
    Attributes:
        skill (str): Name of the skill to test the cadets for
        c1 (str): Name of the first cadet to test
        c2 (str): Name of the second cadet to test
        trials_log (dict): Contains all results, format {skill: [result]}
        runs (int): Current count of trial runs
        MAX_RUNS (int): Maximum allowed amount of trial runs
        
    Methods:
        fill_trials(): Receives cadet indexes and starts the trial run
        show_log(): Outputs the trial results for each skill
    """
    MAX_RUNS = 15


    def __init__(self, display: object):
        self.display = display
        self.skill = ""
        self.c1 = ""
        self.c2 = ""
        self.trials_log = {}
        self.runs = 0


    def fill_trials(self, cadets: object, skill_nr: int, c1: int, c2: int) \
                    -> bool:
        """Receives cadet indexes from the menu and starts the trial run

        Calls __run_trials() for each skill and cadet pair, outputs the
        results to the terminal, and keeps track of the amount of allowed runs.
        
        Returns:
            bool: True if more trials can be run, False if max amount reached
        """
        # In case the player skips the skill choice, the previous skill is used
        self.skill = cadets.SKILLS[skill_nr] if skill_nr is not None \
                                             else self.skill
        self.c1 = cadets.names[c1]
        self.c2 = cadets.names[c2]
        self.__run_trials(cadets)
        self.display.build_screen(self.trials_log, row_nr=1)

        if self.runs == self.MAX_RUNS:
            self.display.build_screen(
                "No more time for trials! On to the real mission!", 18)  # TODO: delay
            return False
        
        self.display.build_screen(
            f'{self.MAX_RUNS - self.runs} trials left', 18)  # TODO: align to the right
        return True


    def __run_trials(self, cadets: object):
        """Compares skill values for a cadet pair and logs result

        Args:
            cadets (object): Reference to Cadet class instance
        """
        skill_c1 = cadets.cadets[self.c1][self.skill]
        skill_c2 = cadets.cadets[self.c2][self.skill]
        if skill_c1 - skill_c2 <= -4:
            result_string = (f'{self.c1} performed much worse than {self.c2}')
        elif skill_c1 - skill_c2 < 0:
            result_string = (f'{self.c1} performed worse than {self.c2}')
        elif skill_c1 - skill_c2 >= 4:
            result_string = (f'{self.c1} performed much better than {self.c2}')
        elif skill_c1 - skill_c2 > 0:
            result_string = (f'{self.c1} performed better than {self.c2}')
        else:
            result_string = (f'{self.c1} and {self.c2} performed equally well')

        if self.trials_log.get(self.skill):
            self.trials_log[self.skill].append(result_string)
        else:
            # Result must be stored as a list to ensure correct processing by
            # the Display class
            self.trials_log[self.skill] = [result_string]
        self.runs += 1
        

    def show_log(self, skill: str) -> list:
        """Return the trial results for the specified skill

        Args:
            skill (str): Name of the skill for which to return the results 

        Returns:
            list: All trial results for this particular skill
        """
        if self.trials_log.get(skill):
            return self.trials_log[skill]
        else:
            self.trials_log[skill] = ["No trials for this skill"]
            return self.trials_log[skill]


class Mission:
    """Calculates and stores the results of the mission phase
    
    Args:
        roles (list): List with cadet skills
        display (object): Reference to Display class instance
    
    Attributes:
        crew (dict): Dict with all roles as keys and a cadet and their 
            skill value for each role
        prognosis (int): Probability value for crew success
        score (int): Indicates how many cadets succeeded in their roles 
        difficulty (int): Average of the 5 randomly chosen mission parameters
        mission_log (dict): Collection of all mission result texts
    
    Methods:
        assemble_crew(): Lets player assign cadets to the roles via the menu
        calculate_prognosis(): Calculates the probability for crew success
        calculate_success(): Calculates the success of the chosen crew
        show_results():
    """
    DIFF_MIN = 2
    DIFF_MAX = 10

    def __init__(self, roles: list, display: object):
        self.roles = roles
        self.display = display
        self.prognosis = 0
        self.difficulty = 0
        self.score = 0
        self.mission_log = {}
        self.crew = {}


    def assemble_crew(self, menu: object, trials: object, cadets: object):
        """Lets player assign cadets to the roles via the menu
        
        Outputs the trial log entries for each skill.
        
        Args:
            menu (object): Reference to Menu class instance
            trials (object): Reference to Trials class instance
            cadets (object): Reference to Cadets class instance
        """
        available_cadets = cadets.names[:]
        self.display.build_screen("Please assemble the crew:", 1)
        self.display.build_screen(trials.trials_log, 2)
        for skill in self.roles:
            self.display.build_screen(f'For {skill}: ', 18)
           # self.display.build_screen(trials.show_log(skill), 5)
            index = menu.run_mission_loop(available_cadets)
            self.crew[skill] = [available_cadets[index],
                                cadets.cadets[available_cadets[index]][skill]]
            available_cadets.pop(index)


    def calculate_prognosis(self) -> int:
        """Calculates the probability value for crew success
        
        The calculation is based on cadet skill values.

        Returns:
            int: Probability value for crew success
        """
        result = sum([value[1]*10 for value in self.crew.values()])
        self.prognosis = math.floor(result/len(self.crew.values()))

        return self.prognosis


    def calculate_success(self):
        """Calculates the success of the chosen crew
        
        The mission difficulty can be adjusted by changing the MIN/MAX values.
        THe value 5 is the amount of available skills/roles.
        """
        # TODO: implement wait
        
        mission_parameters = [random.randrange(self.DIFF_MIN, self.DIFF_MAX+1) for _ in range(5)]
        self.difficulty = (sum(mission_parameters)/5)*10
        
        # Output mission data before the actual mission start
        self.display.build_screen(f"Predicted crew success rate: {self.calculate_prognosis()}", 1)
        self.display.build_screen(f'The mission difficulty is '
                                  f'{self.difficulty}', 3)
        self.display.build_menu("Press ENTER to continue :: ")
        input(self.display.build_input())

        # Assign mission description according to each mission parameter and
        # calculate success for each cadet.
        for param, (key, value) in zip(mission_parameters, self.crew.items()):
            cadet_performance = f'{value[0]} has {"succeeded" if value[1] >= param else "failed"}'
            self.mission_log[key] = [cadet_performance]
            #print(self.mission_log[key])
            #input()
            # TODO: Move strings into a Google sheet or use gettext module
            match key:
                case 'Captain':
                    if param >= 7:
                        msg = "This was a real diplomatic crisis!"
                    elif 4 < param < 7:
                        msg = "This mission had challenging diplomatic issues."
                    else:
                        msg = "There was only a minor diplomatic issue on this mission."
                    if value[1] >= param:
                        self.score += 1
                        msg2 = f"{value[0]} solved it masterfully."
                    else:
                        msg2 = f"Unfortunately, {value[0]} was unable to deal with it."
                case 'Doctor':
                    if param >= 7:
                        msg = "This was a real medical crisis! A planet-wide outbreak!"
                    elif 4 < param < 7:
                        msg = "An alien guest had a challenging medical problem."
                    else:
                        msg = "A couple crew members sustained minor injuries on the Holodeck."
                    if value[1] >= param:
                        self.score += 1
                        msg2 = f"{value[0]} was a real miracle worker!"
                    else:
                        msg2 = f"Unfortunately, {value[0]} was unable to handle the stress of the medical profession."
                case 'Security Chief':
                    if param >= 7:
                        msg = "This was a real scientific crisis!"
                    elif 4 < param < 7:
                        msg = "An alien guest had a challenging scientific problem."
                    else:
                        msg = "There was a minor scientific issue."
                    if value[1] >= param:
                        self.score += 1
                        msg2 = f"{value[0]} was a real miracle worker!"
                    else:
                        msg2 = f"Unfortunately, {value[0]} was unable to handle the stress of being a scientist."
                case 'Pilot':
                    if param >= 7:
                        msg = "This was a real piloting crisis!"
                    elif 4 < param < 7:
                        msg = "An alien guest had a challenging piloting problem."
                    else:
                        msg = "There was a minor piloting issue."
                    if value[1] >= param:
                        self.score += 1
                        msg2 = f"{value[0]} was a real miracle worker!"
                    else:
                        msg2 = f"Unfortunately, {value[0]} was unable to handle the stress of being a pilot."
                case 'Engineer':
                    if param >= 7:
                        msg = "This was a real engineering crisis!"
                    elif 4 < param < 7:
                        msg = "An alien guest had a challenging engineering problem."
                    else:
                        msg = "There was a minor engineering issue."
                    if value[1] >= param:
                        self.score += 1
                        msg2 = f"{value[0]} was a real miracle worker!"
                    else:
                        msg2 = f"Unfortunately, {value[0]} was unable to handle the stress of being an engineer."
                case _:
                    # TODO: print in error message row
                    print("Internal error: no such role in the crew")
                    input()
                
            self.mission_log[key].extend(textwrap.wrap(msg, 70))
            self.mission_log[key].extend(textwrap.wrap(msg2, 70))


    def show_results(self, player: object, trials: object):
        """Collects mission calculations and results in one place, outputs them

        Args:
            player (object): Reference to Player class instance
            trials (object): Reference to Trials class instance
        """
        self.display.clear()
        # Method prints mission info to the screen and builds mission log
        self.calculate_success()

        for key, value in self.mission_log.items():
            self.display.build_screen([f'{key}: '], 2, center=True) # TODO: Fix to accept strings for centering
            self.display.build_screen(value, 3, center=True)
            input(self.display.build_input())
            self.display.clear()

        self.display.build_screen("Calculating final player score:", 1)
        final_score = player.calculate_score(trials.runs, trials.MAX_RUNS, self)
        self.display.build_screen(f'{final_score}', 2)
        input(self.display.build_input())



def show_highscore(*args):
    return


class Menu():
    """Builds menu elements and handles all relevant user input
    
    The purpose of the Menu class is:
    - to create and render static and dynamic menu elements
    - to take player choices and react to them by
        * displaying an error message
        * calling a function
        * returning the chosen value
        
    The Display class object is used to print on screen:
    - Print menu choices on the screen:
        self.display.build_menu(menu_text_string)
    - Print an error message on the screen:
        self.display.build_menu(error_message_string, is_error=True)
    - Print a text above the menu:
        self.display.build_screen(str|list|dict, starting_row_nr)
        Valid starting_row_nr values: 1-18.
    - Clear error message:
        self.display.clear(is_error=True)
    - Clear all text above the menu:
        self.display.clear()
    - Clear specific rows:
        self.display.clear([1,2,...])
    - Take user input with correct placement and formatting of the prompt:
        input(self.display.build_input()).strip()
        
    The output is finally rendered on screen only when input() is called.
    
    Args:
    display (object): Reference to Display class instance
    run_game (object): Reference to global function run()
    """
    def __init__(self, display: object, run_game: object):
        self.display = display
        self.outer_loop_texts = "1. Start game     2. New player     3. Show highscore     4. Exit game"
        self.outer_loop_funcs = {'1': run_game, '3': show_highscore}
        self.trial_loop_texts = "1. Choose skill              2. Choose cadets              3. End trials"
        self.trial_loop_funcs = {'1': self.run_skill_choice,
                            '2': self.run_cadet_choice}
        self.run_game = run_game
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.active_player = None
        # Is the player accessing the trial menu for the first time?
        self.first_time = True


    def run_outer_loop(self):
        """Displays the outer menu choices and waits for player input
        
        
        """
        while True:
            self.display.build_menu(self.outer_loop_texts)
            loading_screen(self.display, part=1)
            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)
            self.display.clear()
            if choice == '2':
                # Restart the game without re-initializing the player
                self.run_game(self, None, self.display)
            elif choice == '4':
                # Return to main() and exit game
                return
            else:
                try:
                    self.outer_loop_funcs[choice](
                        self, self.active_player, self.display)
                except:
                    self.display.build_menu(
                        f"--- Please provide a valid choice ---", is_error=True)


    def run_player_init(self):
        self.display.clear(is_error=True)
        loading_screen(self.display, part=2)
        self.display.build_menu("Please enter your name:")
        name = input(self.display.build_input()).strip()
        self.active_player.name = name
        self.display.clear()


    def run_trial_loop(self, trials: object, cadets: object) -> None:
        self.display.clear()
        if self.first_time:
            self.display.build_screen("First, choose a skill.", 1)
        while True:
            self.display.build_menu(self.trial_loop_texts)
            if not self.stay_in_trial_menu:
                self.display.clear(is_error=True)
                self.display.clear()
                break

            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)

            if choice == '3':
                self.display.clear(is_error=True)
                self.display.clear()
                break
            try:
                self.trial_loop_funcs[choice]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid choice ---", is_error=True)
            else:
                if self.first_time and choice is not '2':
                    self.display.clear()
                    self.first_time = False
                self.trial_loop_funcs[choice](trials, cadets)

        # Returns to run()
        return


    def run_skill_choice(self, trials: object, cadets: object):
        self.display.clear(is_error=True)
        skill_choice_texts = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(cadets.SKILLS, 1)])

        while True:
            self.display.build_menu(skill_choice_texts)
            skill_nr = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)

            try:
                skill_nr = int(skill_nr) - 1
                cadets.SKILLS[skill_nr]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid skill choice ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        self.chosen_skill = cadets.SKILLS[skill_nr]
        self.run_cadet_choice(trials, cadets, skill_nr)

        # Returns to run_trial_loop()


    def run_cadet_choice(self, trials: object, cadets: object, skill_nr=None):
        if self.chosen_skill is None:
            self.first_time = True
            self.display.build_menu(
                "--- Please choose a skill first ---", is_error=True)
            return
        else:
            self.display.clear(is_error=True)
            trial_status = ['Active trial:']
            trial_status.append(f'{self.chosen_skill}:  ')
            self.display.build_screen(trial_status, row_nr=16)

        short_names = [name.split(" ")[1] for name in cadets.names]
        cadet_choice_texts = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
        self.display.build_menu(cadet_choice_texts)
        while True:
            c1 = input(self.display.build_input(
                "Choose first cadet :: ")).strip()
            try:
                c1 = int(c1) - 1
                cadets.names[c1]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid choice for first cadet ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        trial_status[1] += f'{cadets.names[c1]} vs ...'
        self.display.build_screen(trial_status, row_nr=16)

        while True:
            c2 = input(self.display.build_input(
                "Choose second cadet :: ")).strip()
            self.display.clear(is_error=True)

            try:
                c2 = int(c2) - 1
                cadets.names[c2]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid choice for second cadet ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        trial_status[1] = trial_status[1][:-3] + f'{cadets.names[c2]}'
        self.display.build_screen(trial_status, row_nr=16)
        time.sleep(0.5)

        trials.fill_trials(cadets, skill_nr, c1, c2)
        self.stay_in_trial_menu = True if trials.MAX_RUNS > trials.runs else False
        # Returns to run_skill_choice() or run_trial_loop()


    def run_mission_loop(self, available_cadets: list) -> int:
        short_names = [name.split(" ")[1] for name in available_cadets]
        mission_loop_texts = ' '.join([
            f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
        self.display.build_menu(mission_loop_texts)
        while True:
            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)
            try:
                choice = int(choice) - 1
                available_cadets[choice]
                break
            except:
                self.display.build_menu(
                    f"---Please provide a valid choice for the Cadet to fill this role---", is_error=True)
        
        return choice

    def reset_menu(self):
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.first_time = True


def loading_screen(display: object, part=1):
    match part:
        case 1:
            logo = ['         AD ASTRA',
                    '          ______',
                    '       _-´ .   .`-_',
                    "   |/ /  .. . '   .\ \|",
                    '  |/ /            ..\ \|',
                    '\|/ |: .   ._|_ .. . | \|/',
                    ' \/ |   _|_ .| . .:  | \/',
                    '\ / |.   |  .  .    .| \ /',
                    ' \||| .  . .  _|_   .|||/',
                    '\__| \  . :.  .|.  ./ |__/',
                    '  __| \_  .    .. _/ |__',
                    "   __|  `-______-'  |__",
                    '      -,____  ____,-',
                    '        ---´  `---',
                    'UNITED FEDERATION OF PLANETS']
            display.clear()
            display.build_screen(logo, 2, center_logo=True)
            return
        case 2:
            message = ['Welcome, Assessor!', ' ']
            message.extend(textwrap.wrap(
                'I am Cat, short for "Cadet Assessment Terminal". Since the speech module is currently undergoing a personality adjustment, I ask you to use your keyboard today (if you can remember how).', 76))
            message.append("")
            message.extend(textwrap.wrap("As usual, you will be assessing a group of young cadets who have volunteered to go on an important mission. The mission requires a crew, and each role on the crew must be filled with one cadet. Please run a few trials where you let two cadets compete against each other, and note their performance. The sooner you finish the trials, the better, of course. Be as thorough as you need to, but don't miss the deadline!", 76))
            message.extend(
                ["", "Don't forget to provide your full name for the log."])
            display.clear()
            display.build_screen(message)


def run(menu: object, player: object, display: object):
    """_summary_

    Args:
        menu (object): _description_
        player (object): _description_
        display (object): _description_
    """

    menu.reset_menu()

    if player:
        player.score = 0
        menu.active_player = player
    else:
        player = Player()
        menu.active_player = player
        menu.run_player_init()

    cadets = Cadets(display, player.name)
    cadets.recruit()

    display.build_menu('Press ENTER when ready')
    input(display.build_input())

    trials = Trials(display)
    menu.run_trial_loop(trials, cadets)

    # Final mission
    final_mission = Mission(cadets.SKILLS, display)
    # menu.run_mission_loop(final_mission, cadets, trials)
    final_mission.assemble_crew(menu, trials, cadets)

    final_mission.show_results(player, trials)

    display.empty_screen()

    # returns to menu lvl1


def main():
    """
    """
    os.system('cls||clear')
    display = Display()
    menu = Menu(display, run)
    menu.run_outer_loop()
    sys.exit()


if __name__ == '__main__':
    main()


# https://www.youtube.com/watch?v=qUeud6DvOWI
# https://www.youtube.com/watch?v=woIkysZytSs
# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

from pprint import pprint
import random
import math
import os
import textwrap
import time


# Establish connection to Google sheets for highscore management


class Player:
    """
    Contains player data and performs player-related operations.
    """
    def __init__(self):
        """
        Initializes attributes:
            self.name - Player name as entered by user
            self.score - Player score as calculated by class method            
        """
        self.name = ""
        self.score = 0


    def calculate_score(self, trial_runs, trial_max_runs, mission_data):
        """
        Calculates Player score at the end of the game.

        Args:
            trial_runs (int): Played trial runs as stored in Trial class
            trial_max_runs (int): Max trial runs as stored in Trial class
            mission_data (class): Reference to Mission class

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
    """
    Contains viewport and output formatting data, formats and handles all
    print operations.
    ------------
    Attributes:
        self.HEIGHT        - Max allowed viewport height minus input line
        self.WIDTH         - Max allowed viewport width
        self.BORDER_CHAR   - Character to use for the outer border
        self.INPUT_PROMPT  - Characters to show before the input line
        self.EMPTY_ROW     - Empty row string with border chars
        self.ERROR_ROW_NR  - Index of the row with error output
        self.MENU_ROW_NR   - Index of the row with menu elements
        self.rows          - List of 23 strings containing all screen output
    ------------
    Methods:
        __init__()       - Initializes all class attributes
        __empty_screen() - Creates a list of strings for an empty terminal
                           with all border chars in place
        clear()          - Inserts empty rows to clear terminal output
        build_screen()   - Formats and builds a list of strings passed from
                           other functions to prepare terminal output
        build_menu()     - Formats and builds menu string and error string
                           to prepare terminal output
        build_input()    - Formats input prompt and calls _draw to draw screen
        __draw()         - Draws the screen from self.rows attribute
    """
    def __init__(self):
        """"
        Initializes attributes
        """
        self.HEIGHT = 23
        self.WIDTH = 80
        self.BORDER_CHAR = "▓"
        self.INPUT_PROMPT = '▓▓▓ :: '
        self.EMPTY_ROW = f'{self.BORDER_CHAR}{" ":<78}{self.BORDER_CHAR}'
        self.ERROR_ROW_NR = 21
        self.MENU_ROW_NR = 20
        self.rows = self.__empty_screen()


    def __empty_screen(self):
        """
        Creates a list of rows containing the border chars and empty space.

        Returns:
            list: Empty terminal screen with borders
        """
        rows = [str(self.BORDER_CHAR * self.WIDTH)]
        rows.extend([self.EMPTY_ROW for _ in range(self.HEIGHT - 5)])
        rows.extend([self.BORDER_CHAR * self.WIDTH for _ in range(3)])
        rows.append(str(self.BORDER_CHAR * self.WIDTH))
        
        return rows


    def clear(self, indexes=[i for i in range(1, 19)], is_error=False):
        """
        Receives indexes to clear in the terminal and overwrites them in the 
        self.row attribute with empty rows.

        Args:
            indexes (list, optional)  - List with indexes to be cleared.
                                        Defaults to all rows above the menu.
            is_error (bool, optional) - States whether the row to clear is
                                        the error row. Defaults to False.
        """
        if is_error:
            self.rows[self.ERROR_ROW_NR] = self.BORDER_CHAR * self.WIDTH
        else:
            for index in indexes:
                self.rows[index] = self.EMPTY_ROW
        
        return


    def build_screen(self, text, row_nr=1, center=False):
        """
        Prepares a text for terminal output above the menu row:
        Receives a string, list, or dictionary, formats its contents,
        and overwrites the specified rows of self.rows with the contents.

        Args:
            text (str, list, dict)  - Message to print on screen.
            row_nr (int, optional)  - ROW index at which to start.
                                      Defaults to 1.
            center (bool, optional) - States whether the message should be
                                      centered on screen. Defaults to False.
        
        Local var:
            result (str)            - String containing one assembled row
        """
        result = ''
        if text:
            # String processing
            if type(text) == str:
                result = (f'{self.BORDER_CHAR}{" "}{text:<76}{" "}'
                         f'{self.BORDER_CHAR}')
                self.rows[row_nr] = result
            # List processing
            elif type(text) == list:
                for i in range(len(text)):
                    result = (f'{self.BORDER_CHAR}{" "*26 + text[i]:<78}'
                              f'{self.BORDER_CHAR}' if center 
                              else f'{self.BORDER_CHAR}{" "}{text[i]:<76}{" "}'
                              f'{self.BORDER_CHAR}')
                    # Fill the final list starting at received row index
                    self.rows[row_nr + i] = result
            # Dictionary processing:
            # The dictionaries passed have the following format:
            # {key : ['', ..., '']}
            elif type(text) == dict:
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
                    k += i
            else:
                print("Internal error: text is not str, list, or dict")
                input()
                
                return
        else:
            print("Internal error: text is empty")
            input()
            
            return


    def build_menu(self, text, is_error=False):
        """
        Prepares the menu row for terminal output:
        Formats the string and overwrites the specified row index in self.rows.
        
        Args:
            text (str)                - String containing the menu elements, 
                                        max 76 chars
            is_error (bool, optional) - States if text is an error message.
                                        Defaults to False.
        """
        if is_error:
            result = f'{self.BORDER_CHAR}{" "}{text:>76}{" "}{self.BORDER_CHAR}'
            self.rows[self.ERROR_ROW_NR] = result
        else:
            result = f'{self.BORDER_CHAR}{" "}{text:<76}{" "}{self.BORDER_CHAR}'
            self.rows[self.MENU_ROW_NR] = result
        
        return


    def build_input(self, prompt=''):
        """
        Calls __draw() to draw the terminal and returns a user input prompt.
        Thus, the screen is only re-drawn whenever user input is required.

        Args:
            prompt (str, optional) - Prompt to put before the user input.
                                     Defaults to ''.

        Returns:
            str: String with user input decoration and prompt
        """
        self.__draw()
        
        return self.INPUT_PROMPT + prompt
    
    
    def __draw(self):
        """
        Clears the previous input and draws the new terminal from self.rows.
        """
        os.system('cls||clear')
        for row in self.rows:
            print(f'{row}')


class Cadets:
    """
    
    Attributes:
        self.SKILLS       -
        self.NAMES        -
        self.cadets       -
        self.display      -
        self.player_name  -
        
    Methods:
        __init__()              -
        recruit()               -
        cadet_skill_generator() -
        
    """

    def __init__(self, display, player_name):
        # The skills which the cadets are being tested for
        self.SKILLS = ["Captain", "Security Chief",
                       "Engineer", "Doctor", "Pilot"]
        # Selection of names for cadets (TODO: randomize selection!)
        self.NAMES = random.sample(["Cadet Janeway", "Cadet Picard", "Cadet Kirk", "Cadet Kim", "Cadet Paris",
                                    "Cadet Whorf", "Cadet Crusher", "Cadet Torres", "Cadet Spock", "Cadet Troi"], 6)
        self.cadets = {}
        self.display = display
        self.player_name = player_name

    def recruit(self):
        # Build initial cadet dictionary with 6 cadets and their respective random skill values.
        # The player has no access to these values.
        self.cadets = {key: {key: value for key, value in zip(
            self.SKILLS, self.cadet_skill_generator())} for key in self.NAMES}
        message = [f'Welcome to CAT, the Cadet Assessment Terminal, {self.player_name}!',
                   '', f'The following cadets have volunteered for the upcoming mission:', '']
        message.extend(textwrap.wrap(
            f'{", ".join(self.NAMES)}', self.display.WIDTH - 4))
        self.display.build_screen(message, row_nr=2)

        return

    def cadet_skill_generator(self):
        """
        This function generates and returns a list with 5 random skill numbers,
        each between LOWEST_SKILL and HIGHEST_SKILL (1 - 10), with a total sum of
        MAX_POINTS (25).
        """
        # Total amount of skill points to divide among all skills for each cadet
        MAX_POINTS = 25
        # Lowest and highest possible skill level on a scale of 1-10
        LOWEST_SKILL = 1
        HIGHEST_SKILL = 10
        skill_points = []
        skill_amount = len(self.SKILLS)

        for i in range(1, skill_amount + 1):
            # The 5th skill to be calculated always takes the remaining difference
            # between the maximum possible points and the sum of used-up points
            if i == 5:
                points = MAX_POINTS - sum(skill_points)

            # The 4th skill to be calculated needs an upper range and a lower range for the randomizer:
            # - upper range is the remaining points minus the minimum necessary points for the
            #   last skill OR HIGHEST_SKILL, depending on which is lower
            # - lower range is the remainder of the remaining points divided by (HIGHEST_SKILL * 2)
            # For example:
            # - The numbers [1,1,3] have been chosen for i 1-3. 20 points remain to be distributed,
            # which equals (HIGHEST_SKILL * 2). As a result, lower_range is set to HIGHEST_SKILL (10)
            # to make sure that the last two skills receive enough points to add up to 20.
            # - The numbers [10,1,1] have been chosen for i 1-3. 13 points remain to be distributed,
            # which is lower than (HIGHEST_SKILL * 2) but higher than HIGHEST_SKILL. As a result,
            # lower_range is set to the maximum of 1 or (13%(10*1)), which is 3.
            # This makes sure that the skill on i=4 receives at least 3 points, leaving max 10 for i=5.
            elif i == 4:
                upper_range = min(
                    MAX_POINTS - sum(skill_points[0:i-1]) - (skill_amount - i) + 1, HIGHEST_SKILL + 1)
                if (MAX_POINTS - sum(skill_points[0:i-1])) < HIGHEST_SKILL:
                    lower_range = LOWEST_SKILL
                elif (MAX_POINTS - sum(skill_points[0:i-1])) == HIGHEST_SKILL*2:
                    lower_range = HIGHEST_SKILL
                else:
                    lower_range = max(
                        (MAX_POINTS - sum(skill_points[0:i-1])) % (HIGHEST_SKILL*(skill_amount - i)), 1)
                points = random.randrange(lower_range, upper_range)

            elif i == 3:
                upper_range = min(
                    MAX_POINTS - sum(skill_points[0:i-1]) - (skill_amount - i) + 1, HIGHEST_SKILL + 1)
                if (MAX_POINTS - sum(skill_points[0:i-1])) < HIGHEST_SKILL*2:
                    lower_range = LOWEST_SKILL
                else:
                    lower_range = max(
                        (MAX_POINTS - sum(skill_points[0:i-1])) % (HIGHEST_SKILL*(skill_amount - i)), 1)
                points = random.randrange(lower_range, upper_range)

            else:
                points = random.randrange(LOWEST_SKILL, HIGHEST_SKILL + 1)

            skill_points.append(points)

        # print(sum(skill_points))
        return skill_points


class Trials:
    def __init__(self, display):
        self.display = display
        self.skill = ""
        self.c1 = ""
        self.c2 = ""
        self.trials_log = {}
        self.runs = 0
        self.MAX_RUNS = 5

    def fill_trials(self, cadets, skill_nr, c1, c2):

        self.skill = cadets.SKILLS[skill_nr] if skill_nr is not None else self.skill
        # print(self.skill)

        self.c1 = cadets.NAMES[c1]
        self.c2 = cadets.NAMES[c2]

        result = self.run_trials(cadets)
        self.display.build_screen(result, 1)
        # print(self.trials_log.values())
        # input()
        self.display.build_screen(self.trials_log, 1)

        if self.runs == self.MAX_RUNS:
            self.display.build_screen(
                "No more time for trials! On to the real mission!", 18)
            return False
        else:
            self.display.build_screen(
                f'{self.MAX_RUNS - self.runs} trials left', 18)  # align to the right
            return True

    def run_trials(self, cadets):
        # print(f'Comparing cadets {self.c1} and {self.c2} for skill {self.skill}:')
        skill_c1 = cadets.cadets[self.c1][self.skill]
        skill_c2 = cadets.cadets[self.c2][self.skill]
        if skill_c1 - skill_c2 <= -4:
            result_string = (f'{self.c1} is much worse than {self.c2}')
        elif skill_c1 - skill_c2 < 0:
            result_string = (f'{self.c1} is worse than {self.c2}')
        elif skill_c1 - skill_c2 >= 4:
            result_string = (f'{self.c1} is much better than {self.c2}')
        elif skill_c1 - skill_c2 > 0:
            result_string = (f'{self.c1} is better than {self.c2}')
        else:
            result_string = (f'{self.c1} and {self.c2} are equals')

        if self.trials_log.get(self.skill):
            self.trials_log[self.skill].append(result_string)
        else:
            self.trials_log[self.skill] = [result_string]

        self.runs += 1
        return f'{self.skill}: {result_string}'

    def show_log(self, skill):
        if self.trials_log.get(skill):
            return (self.trials_log[skill])
        else:
            self.trials_log[skill] = ["No trials for this skill"]
            return (self.trials_log[skill])


# Add Mission class with roles and crew, it handles the assignment of cadets

class Mission:
    def __init__(self, roles, display):
        self.crew = {key: [] for key in roles}
        self.roles = roles
        self.prognosis = 0
        self.score = 0
        self.difficulty = 0
        self.mission_log = {}
        self.display = display

    def assemble_crew(self, menu, trials, cadets):

        # cadet_list = []
        available_cadets = cadets.NAMES
        self.display.build_screen("Please assemble the crew", 1)
        for skill in self.roles:
            self.display.build_screen(f'For {skill}: ')
            self.display.build_screen(trials.show_log(skill), 5)
            print(f'\n{skill}: Please assign a cadet:')
            print(available_cadets)

            index = menu.run_lvl2_mission(available_cadets)
            self.crew[skill] = [available_cadets[index],
                                cadets.cadets[available_cadets[index]][skill]]
            available_cadets.pop(index)

        # get list from menu
        # loop through skills and cadet list
        print("assembling")
        # self.crew.update({skill: [cadet, cadets.cadets[cadet][skill]] for cadet, skill in zip(cadet_list, self.roles)}) #
        # i = 0
        # for skill in self.roles:
        #     self.crew[skill] = [cadet_list[i], cadets.cadets[cadet_list[i]][skill]]
        #     i += 1
        print(self.crew)
        return

    def calculate_prognosis(self):
        result = 0
        for value in self.crew.values():
            result += value[1]*10
        self.prognosis = math.floor(result/len(self.crew.values()))
        return self.prognosis

    def calculate_success(self):
        # Mission difficulty starts at 2
        # 5 should be replaced with len(skills)
        mission_parameters = [random.randrange(2, 11) for _ in range(5)]
        self.difficulty = (sum(mission_parameters)/5)*10
        print(f'The mission difficulty is {self.difficulty}')
        i = 0
        for key, value in self.crew.items():
            descriptor = ""
            print(key)
            cadet_performance = f'{value[0]} has {"succeeded" if value[1] >= mission_parameters[i] else "failed"}'
            self.mission_log[key] = [cadet_performance]
            print(self.mission_log[key])
            input()
            # TODO: Move strings into a Google sheet or use gettext module
            match key:
                case 'Captain':
                    if mission_parameters[i] >= 7:
                        self.mission_log[key].append(
                            "This was a real diplomatic crisis!")
                    elif 4 < mission_parameters[i] < 7:
                        self.mission_log[key].append(
                            "This mission had challenging diplomatic issues.")
                    else:
                        self.mission_log[key].append(
                            "There was only a minor diplomatic issue on this mission.")
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        self.mission_log[key].append(
                            f"{value[0]} solved it masterfully.")
                    else:
                        self.mission_log[key].append(
                            f"Unfortunately, {value[0]} was unable to deal with it.")
                case 'Doctor':
                    if mission_parameters[i] >= 7:
                        self.mission_log[key].append(
                            "This was a real medical crisis! A planet-wide outbreak!")
                    elif 4 < mission_parameters[i] < 7:
                        self.mission_log[key].append(
                            "An alien guest had a challenging medical problem.")
                    else:
                        self.mission_log[key].append(
                            "A couple crew members sustained minor injuries on the Holodeck.")
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        self.mission_log[key].append(
                            f"{value[0]} was a real miracle worker!")
                    else:
                        self.mission_log[key].append(
                            f"Unfortunately, {value[0]} was unable to handle the stress of the medical profession.")
                case 'Security Chief':
                    if mission_parameters[i] >= 7:
                        self.mission_log[key].append(
                            "This was a real scientific crisis!")
                    elif 4 < mission_parameters[i] < 7:
                        self.mission_log[key].append(
                            "An alien guest had a challenging scientific problem.")
                    else:
                        self.mission_log[key].append(
                            "There was a minor scientific issue.")
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        self.mission_log[key].append(
                            f"{value[0]} was a real miracle worker!")
                    else:
                        self.mission_log[key].append(
                            f"Unfortunately, {value[0]} was unable to handle the stress of being a scientist.")
                case 'Pilot':
                    if mission_parameters[i] >= 7:
                        self.mission_log[key].append(
                            "This was a real piloting crisis!")
                    elif 4 < mission_parameters[i] < 7:
                        self.mission_log[key].append(
                            "An alien guest had a challenging piloting problem.")
                    else:
                        self.mission_log[key].append(
                            "There was a minor piloting issue.")
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        self.mission_log[key].append(
                            f"{value[0]} was a real miracle worker!")
                    else:
                        self.mission_log[key].append(
                            f"Unfortunately, {value[0]} was unable to handle the stress of being a pilot.")
                case 'Engineer':
                    if mission_parameters[i] >= 7:
                        self.mission_log[key].append(
                            "This was a real engineering crisis!")
                    elif 4 < mission_parameters[i] < 7:
                        self.mission_log[key].append(
                            "An alien guest had a challenging engineering problem.")
                    else:
                        self.mission_log[key].append(
                            "There was a minor engineering issue.")
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        self.mission_log[key].append(
                            f"{value[0]} was a real miracle worker!")
                    else:
                        self.mission_log[key].append(
                            f"Unfortunately, {value[0]} was unable to handle the stress of being an engineer.")
                case _:
                    print("Internal error: no such role in the crew")
                    input()

            # print(
            #     f'{value[0]} has {"succeeded" if value[1] >= mission_parameters[i] else "failed"}')

            i += 1

        self.display.build_screen(self.mission_log, 1)  # should be a dictionary
        input(self.display.build_input())
        return

    def calculate_results(self, player, trials):
        """

        Args:
            player (class Player): player object
            mission (class Mission): mission object
            trials (class Trials): trials object
        """
        # Calculate mission success

        print("Success rate: ", self.calculate_prognosis())
        print("Mission success: ", self.calculate_success())

        print("Calculating final player score:")
        print(player.calculate_score(trials.runs, trials.MAX_RUNS,
                                     self))
        return


def show_highscore(*args):
    return

# Add Menu class with Stage 1 - name input, Stage 2 - cadet trial runs,
# Stage 3 - assignments, Stage 4 - final mission start,
# Stage 5 - view highscore, restart, exit


class Menu():
    def __init__(self, display):  # rename levels
        self.display = display
        self.texts_lvl1_loader = "1. Start game             2. New player             3. Show highscore"
        self.lvl1_loader = {'1': run, '3': show_highscore}
        self.texts_lvl2_trials = "1. Choose skill              2. Choose cadets              3. End trials"
        self.lvl2_trials = {'1': self.run_lvl3_skill,
                            '2': self.run_lvl4_cadets}
        self.texts_lvl3_skill = ""
        self.texts_lvl4_cadets = ""
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.active_player = None

    def run_lvl0_player(self):
        self.display.clear(is_error=True)
        loading_screen(self.display, part=2)
        self.display.build_menu("Please enter your name:")
        name = input(self.display.build_input()).strip()
        self.active_player.name = name
        self.display.clear()
        return

    def run_lvl1_loader(self):
        while True:
            self.display.build_menu(self.texts_lvl1_loader)
            loading_screen(self.display, part=1)
            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)
            self.display.clear()
            if choice == '2':
                run(self, None, self.display)
            else:
                try:
                    self.lvl1_loader[choice](
                        self, self.active_player, self.display)
                except:
                    self.display.build_menu(
                        f"--- Please provide a valid choice ---", is_error=True)

    def run_lvl2_trials(self, trials, cadets):
        while True:
            self.display.build_menu(self.texts_lvl2_trials)
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
                self.lvl2_trials[choice]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid choice ---", is_error=True)
            else:
                self.display.clear()
                self.lvl2_trials[choice](trials, cadets)
               # self.display.clear([], is_error=True)

    def run_lvl3_skill(self, trials, cadets):
        self.display.clear(is_error=True)
        self.display.clear([1])
        self.texts_lvl3_skill = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(cadets.SKILLS, 1)])

        while True:
            self.display.build_menu(self.texts_lvl3_skill)
            skill_nr = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)

            try:
                skill_nr = int(skill_nr)-1
                cadets.SKILLS[skill_nr]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid skill choice ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        self.chosen_skill = cadets.SKILLS[skill_nr]
        self.run_lvl4_cadets(trials, cadets, skill_nr)
        return

    def run_lvl4_cadets(self, trials, cadets, skill_nr=None):
        # self.display.clear([2,3])
        if self.chosen_skill is None:
            self.display.build_menu(
                "--- Please choose a skill first ---", is_error=True)
            return
        else:
            self.display.clear(is_error=True)
            trial_status = ['Active trial:']
            trial_status.append(f'{self.chosen_skill}:  ')
            self.display.build_screen(trial_status, row_nr=16)

        short_names = [name.split(" ")[1] for name in cadets.NAMES]
        self.texts_lvl4_cadets = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
        self.display.build_menu(self.texts_lvl4_cadets)
        while True:
            c1 = input(self.display.build_input(
                "Choose first cadet :: ")).strip()
            try:
                c1 = int(c1) - 1
                cadets.NAMES[c1]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid choice for first cadet ---", is_error=True)
            else:
                self.display.clear([], is_error=True)
                break

        trial_status[1] += f'{cadets.NAMES[c1]} vs ...'
        self.display.build_screen(trial_status, row_nr=16)

        while True:
            c2 = input(self.display.build_input(
                "Choose second cadet :: ")).strip()
            self.display.clear(is_error=True)

            try:
                c2 = int(c2) - 1
                cadets.NAMES[c2]
            except:
                self.display.build_menu(
                    f"--- Please provide a valid choice for second cadet ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        trial_status[1] = trial_status[1][:-3] + f'{cadets.NAMES[c2]}'
        self.display.build_screen(trial_status, row_nr=16)
        time.sleep(0.5)

        self.stay_in_trial_menu = trials.fill_trials(cadets, skill_nr, c1, c2)
        return

    def run_lvl2_mission(self, available_cadets):
        short_names = [name.split(" ")[1] for name in available_cadets]
        self.texts_lvl2_mission = ' '.join([
            f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
        self.display.build_menu(self.texts_lvl2_mission)
        while True:
            choice = input(self.display.build_input()).strip()
            self.display.clear([], is_error=True)
            try:
                choice = int(choice) - 1
                available_cadets[choice]
                break
            except:
                self.display.build_menu(
                    f"---Please provide a valid choice for the Cadet to fill this role---", is_error=True)
        # self.display.build_screen(available_cadets[choice])
        return choice

    def reset_menu(self):
        self.texts_lvl3_skill = ""
        self.texts_lvl4_cadets = ""
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        return


def loading_screen(display, part=1):
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
            display.build_screen(logo, 2, center=True)
            return
        case 2:
            message = ['Welcome, Assessor!', ' ']
            message.extend(textwrap.wrap(
                'I am Cat, short for "Cadet Assessment Terminal". Since the speech module is currently undergoing a personality adjustment, I ask you to use your keyboard today (if you can remember how).'))
            message.append("")
            message.extend(textwrap.wrap("As usual, you will be assessing a group of young cadets who have volunteered to go on an important mission. The mission requires a crew, and each role on the crew must be filled with one cadet. Please run a few trials where you let two cadets compete against each other, and note their performance. The sooner you finish the trials, the better, of course. Be as thorough as you need to, but don't miss the deadrow!"))
            message.extend(
                ["", "Don't forget to provide your full name for the log."])
            display.clear()
            display.build_screen(message)


# Game Manager that will instantiate objects, pass them to their
# respective functions


def run(menu, player, display):

    menu.reset_menu()

    if player:
        print(f'Hello {player.name}')
        player.score = 0
        menu.active_player = player
    else:
        player = Player()
        menu.active_player = player
        menu.run_lvl0_player()

    cadets = Cadets(display, player.name)
    cadets.recruit()

    trials = Trials(display)
    menu.run_lvl2_trials(trials, cadets)

    # Final mission
    final_mission = Mission(cadets.SKILLS, display)
    # menu.run_lvl2_mission(final_mission, cadets, trials)
    final_mission.assemble_crew(menu, trials, cadets)

    final_mission.calculate_results(player, trials)

    return          # returns to menu lvl1


def main():
    """
    """
    os.system('cls||clear')
    display = Display()
    # menu1 = menu.Menu(display) # Menu(display)
    menu = Menu(display)
    menu.run_lvl1_loader()


if __name__ == '__main__':
    main()

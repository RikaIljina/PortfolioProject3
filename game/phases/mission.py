"""Contains the Mission class which handles all mission operations and data"""
import math
import random
import textwrap


class Mission:
    """Calculates and stores the results of the mission phase

    The mission difficulty can be adjusted by changing the MIN/MAX values.


    Args:
        roles (list): List with cadet roles
        display (object): Reference to Display class instance
        sheet (object): Reference to Sheet class instance

    Attributes:
        DIFF_MIN (int): Lower threshold for the random mission parameters
        DIFF_MAX (int): Upper threshold for the random mission parameters
        RED, GREEN, BRIGHT_RED, BRIGHT_CYAN, RESET (str): ASCII color codes
        prognosis (int): Average skill value of the crew times 10
        score (int): Indicates how many cadets succeeded in their roles
        mission_log (dict): Collection of all mission result texts
        crew (dict): Dict with all roles as keys and a cadet and their 
            skill value for each role
        mission_parameters (list): 5 random values that decide the difficulty
            of the mission and to which the cadet skills will be compared.
            The value range is [DIFF_MIN, DIFF_MAX]
        difficulty (int): Average of the 5 randomly chosen mission parameters
        suffix (str): String needed to construct a message ID

    Methods:
        assemble_crew(): Lets player assign cadets to the roles via the menu
        calculate_prognosis(): Calculates the probability for crew success
        calculate_success(): Calculates the success of the chosen crew
        show_results():
        show_mission_logs():
    """
    DIFF_MIN = 3
    DIFF_MAX = 10
    RED = '\033[31;1m'
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_CYAN = '\033[96;1m'
    RESET = '\033[0m'

    def __init__(self, roles: list, display: object, sheet: object):
        self.roles = roles
        self.display = display
        self.sheet = sheet
        self.prognosis = 0
        self.score = 0
        self.mission_log = {}
        self.crew = {}
        self.mission_parameters = [random.randrange(
            self.DIFF_MIN, self.DIFF_MAX+1) for _ in range(5)]
        self.difficulty = int((sum(self.mission_parameters)/5)*10)
        self.suffix = ''

    def assemble_crew(self, menu: object, trials: object, cadets: object):
        """Lets player assign cadets to the roles via the menu

        This method outputs the trial log entries to help player choose the
        crew along with other info text. It also calls a menu method so that
        the player can choose cadets for each role.
        The menu method makes sure that the index is valid.

        Args:
            menu (object): Reference to Menu class instance
            trials (object): Reference to Trials class instance
            cadets (object): Reference to Cadets class instance
        """
        available_cadets = cadets.names[:]
        self.display.build_screen(trials.trials_log, 1)
        crew_list = [self.sheet.get_text('scr_mission_welcome')]
        for role in self.roles:
            self.display.build_screen(
                self.sheet.get_text(
                    "scr_mission_role",
                    f'{self.BRIGHT_CYAN}{role}{self.RESET}'), 18, ansi=11)
            # Get the next cadet index via user input in the menu
            index = menu.run_mission_loop(available_cadets)
            # Construct string from role and cadet last name
            crew_list.append(
                f'{role} {available_cadets[index].split(" ")[1]}')
            self.display.build_screen(textwrap.wrap(
                ', '.join(crew_list)+'!', 76), 16)
            # Construct the crew dictionary from role, cadet name and
            # cadet skill
            self.crew[role] = [available_cadets[index],
                               cadets.cadets[available_cadets[index]][role]]
            available_cadets.pop(index)
        # Clear menu and wait for player to read the output and press ENTER
        self.display.build_screen(self.BRIGHT_CYAN + self.sheet.get_text(
            'scr_mission_embark') + self.RESET, 18, center=True, ansi=11)
        self.display.build_menu('')
        input(self.display.build_input(prompt_enter=True))

    def calculate_prognosis(self):
        """Calculates the average skill level of the crew

        The calculation is based on the individual cadet skill values.

        Returns:
            int: Average skill level of the crew
        """
        result = sum([value[1]*10 for value in self.crew.values()])
        self.prognosis = math.floor(result/len(self.crew.values()))
        self.calculate_disparity()

    def calculate_disparity(self):
        """Calculates disparity between the mission prognosis and difficulty

        This method calculates the difference between the mission prognosis
        value and difficulty to determine the disparity level and set an
        appropriate suffix. This suffix is used by
        menu.info_screen('5_red_alert') as a key to get info text from the
        message dictionary.

        Attributes:
            self.prognosis (int): The prognosis level of the mission.
            self.difficulty (int): The difficulty level of the mission.
        """
        disparity = self.prognosis - self.difficulty
        if disparity > 10:
            self.suffix = 'pos'
        elif disparity < -10:
            self.suffix = 'neg'
        else:
            self.suffix = 'zero'

    def calculate_success(self):
        """Calculates the success of the chosen crew, writes the mission log

        The success is calculated by comparing the cadet skill to the
        respective mission parameter.
        The messages for the mission log are constructed as follows:
        sheet.get_mission_msg() assembles the message ID from the following
        parts:
        - Name of the role (found as keys in self.crew dict)
        - Difficulty indicator (found in diff_values dict; key is the randomly
          chosen mission parameter)
        - Bool for mission success (has_succeeded)
        sheet.get_mission_msg() also needs the cadet name to insert it into the
        mission description.
        """
        self.calculate_prognosis()
        diff_values = {1: "low", 2: "low", 3: "low", 4: "low",
                       5: "low", 6: "mid", 7: "mid", 8: "mid",
                       9: "high", 10: "high"}
        # Assign mission description according to each mission parameter and
        # calculate success for each cadet.
        for param, (key, value) in zip(self.mission_parameters,
                                       self.crew.items()):
            if value[1] >= param:
                self.score += 1
                has_succeeded = True
            else:
                has_succeeded = False
            fname = value[0].split(" ")[1]
            try:
                # Get the appropriate message from the Google sheet
                msg = self.sheet.get_mission_msg(
                    key, diff_values[param], has_succeeded, fname)
            except (TypeError, KeyError) as e:
                print("Internal error: dictionary issue, no such key:")
                print(key, diff_values[param], has_succeeded, fname, e)
                input()
                raise e
            success_text = self.sheet.get_text('ml_succeeded')
            fail_text = self.sheet.get_text('ml_failed')
            cadet_performance = \
                f'{self.BRIGHT_GREEN}{value[0]}{success_text}{self.RESET}' \
                if has_succeeded else \
                f'{self.BRIGHT_RED}{value[0]}{fail_text}{self.RESET}'
            # Build the mission log
            self.mission_log[key] = [cadet_performance]
            if isinstance(msg, list):
                self.mission_log[key].extend(msg)
            else:
                self.mission_log[key].append(msg)

    # TODO: move to menu info screens
    def show_mission_logs(self):
        """Prepares mission logs for output, sends them to Display

        Adds ANSI styles to certain lines and positions them correctly on
        the screen.
        """
        self.display.clear()
        # Print mission log to the screen
        for key, value in self.mission_log.items():
            self.display.build_screen(f'{self.BRIGHT_CYAN}{key}:{self.RESET}',
                                      3, ansi=11)
            self.display.build_screen(value[0], 5, ansi=11)
            self.display.build_screen(value[1:], 7)
            input(self.display.build_input(prompt_enter=True))
            self.display.clear()

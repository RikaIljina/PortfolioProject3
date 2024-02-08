"""Contains Menu class which builds menu elements and handles user input

The Menu class was supposed to handle menu choice logic and call appropriate
functions where needed. However, it has grown into an overarching class that
handles all relevant user input and shows informational screens in-between.
"""
import time


class Menu():
    """Builds menu elements and handles all relevant user input

    The purpose of the Menu class is:
    - to create and render static and dynamic menu elements
    - to take player choices and react to them by
        * displaying an error message
        * calling a function
        * returning the chosen value
    - to render info screens

    The Display class object is used to print on screen:
    - Print menu choices on the screen:
        self.display.build_menu(menu_text_string)
    - Print an error message on the screen:
        self.display.build_menu(error_message_string, is_error=True)
    - Print a text above the menu:
        self.display.build_screen(str||list||dict, starting_row_nr)
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
        sheet (object): Reference to Sheet class object
        run_game (object): Reference to global function run() in run.py

    Attributes:
        GREEN, RESET: ANSI style codes
        stay_in_trial_menu (bool):
        trial_first_time (bool): States whether the player has accessed the
            trial loop for the first time; needed to show the appropriate
            info screen.

    Methods:
    run_outer_loop(): Displays the outer menu choices and waits for player
        input
    run_player_init(): Prompts user to enter a player name until valid name is
        entered
    run_trial_loop(): Displays trial phase choices and waits for user input
    run_skill_choice(): Displays skill choices and waits for valid user input
    run_cadet_choice(): Displays cadet names as menu choices and waits for
        valid user input
    run_mission_loop(): Displays cadet names as menu choices and waits for
        valid user input
    reset_menu(): Resets menu values on repeated playthrough
    info_screen(): Prepares and displays all info screens
    """
    BRIGHT_GREEN = "\033[92;1m"
    BRIGHT_RED = "\033[91;1m"
    BRIGHT_CYAN = '\033[96;1m'
    RESET = "\033[0m"

    def __init__(self, display: object, sheet: object, run_game: object):
        self.display = display
        self.sheet = sheet
        self.run_game = run_game
        self.chosen_skill = None
        self.active_player = None
        # Does the player still have trial runs left?
        self.stay_in_trial_menu = True
        # Is the player accessing the trial menu for the first time?
        self.trial_first_time = True

    def run_outer_loop(self):
        """Displays the outer menu choices and waits for player input

        All other functions except for main() trace back to this function
        in the end, which returns to main() on game exit.
        """
        while True:
            # Before the input: Build the screen content
            self.info_screen('1_logo')
            self.display.build_menu(self.sheet.get_text('menu_outer'))
            # Draw the screen and take input
            choice = input(self.display.build_input()).strip()
            # After the input: Clear error messages and previous screen content
            self.display.clear(is_error=True)
            self.display.clear()
            match choice:
                case '1':
                    # Call the game manager function
                    self.run_game(self, self.active_player, self.display,
                                  self.sheet)
                case '2':
                    # Restart the game without passing the old player so that
                    # run() can re-initialize the Player class
                    self.run_game(self, None, self.display, self.sheet)
                case '3':
                    self.info_screen('9_highscore')
                case '4':
                    # Return to main() and exit game
                    return
                case _:
                    self.display.build_menu(self.sheet.get_text('err_outer'),
                                            is_error=True)

    def run_player_init(self):
        """Prompts user to enter a player name until valid name is entered"""
        self.display.clear(is_error=True)
        self.info_screen('2_welcome')
        self.display.build_menu(self.sheet.get_text('prompt_name'))
        while True:
            name = input(self.display.build_input()).strip()
            if self.active_player.set_name(name):
                break
            self.display.build_menu(self.sheet.get_text('err_player'),
                                    is_error=True)
        self.display.clear(is_error=True)
        self.display.clear()

    def run_trial_loop(self, trials: object, cadets: object, mission: object):
        """Displays trial phase choices and waits for valid user input

        During the trial phase, the player can choose to select a specific
        career track (skill) as well as two cadets to test, or to end the
        trial phase and start the mission. This method handles the choice of
        track and cadets ... 

        Args:
            trials (object): Reference to Trials class instance
            cadets (object): reference to Cadets class instance
        """
        self.display.clear()
        if self.trial_first_time:
            self.info_screen('4_trials_desc', mission.difficulty)
            self.display.build_screen(
                f'{self.sheet.get_text("trials_left", trials.MAX_RUNS):>76}',
                18)
        while True:
            self.display.build_menu(self.sheet.get_text('menu_trial'))
            # Exit the menu loop if no more trial runs available
            if not self.stay_in_trial_menu:
                self.display.build_menu("")
                self.display.clear([16, 17, 18])
                self.display.build_screen(self.sheet.get_text(
                    'no_more_trials'), 16)
                input(self.display.build_input(prompt_enter=True))
                self.display.clear(is_error=True)
                self.display.clear()
                break

            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)

            match choice:
                case '1':
                    if self.trial_first_time:
                        self.display.clear(list(range(1, 18)))
                        self.trial_first_time = False
                    self.run_skill_choice(trials, cadets)
                    continue
                case '2':
                    # Make sure that a career track has been chosen before
                    # allowing the player to choose cadets
                    if not self.chosen_skill:
                        self.display.build_menu(self.sheet.get_text(
                            'err_skill_first'), is_error=True)
                        continue
                    self.run_cadet_choice(trials, cadets)
                    continue
                case '3':
                    # Return to run() to start mission phase
                    self.display.clear(is_error=True)
                    self.display.clear()
                    break
                case _:
                    self.display.build_menu(
                        self.sheet.get_text('err_trial'), is_error=True)
        # Returns to run() to start mission phase

    def run_skill_choice(self, trials: object, cadets: object):
        """Displays skill choices and waits for valid user input

        This method creates an enumerated menu string from the cadet skills
        and waits for the user to choose a valid index. Once an index has been
        received, the method calls run_cadet_choice().

        Args:
            trials (object): Reference to Trials class instance
            cadets (object): Reference to Cadets class instance
        """
        self.display.clear(is_error=True)
        trial_status = self.sheet.get_text('scr_trial_active')
        skill_choice_texts = ' '.join(
            [f'⁞{c[0]}⁞ {c[1]} ⁞' for c in enumerate(cadets.skills, 1)])

        while True:
            self.display.build_menu(skill_choice_texts)
            self.display.build_screen(trial_status, 16)
            skill_nr = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)
            try:
                # Convert user input into a valid index
                skill_nr = int(skill_nr) - 1
                cadets.skills[skill_nr]
            # Not specifying an error type here because all invalid user input
            # shall be handled the same - by showing an error message and
            # continuing the menu loop
            except:
                self.display.build_menu(
                    self.sheet.get_text('err_skill'), is_error=True)
            else:
                self.display.clear(is_error=True)
                break
        self.chosen_skill = cadets.skills[skill_nr]
        self.run_cadet_choice(trials, cadets, skill_nr)
        # Returns to run_trial_loop()

    def run_cadet_choice(self, trials: object, cadets: object, skill_nr=None):
        """Displays cadet names as menu choices and waits for valid user input

        This method creates an enumerated menu string from the cadet names
        and waits for the user to choose a valid index. Once two indexes have
        been received, the method calls trials.fill_trials() and passes on
        the chosen skill index and the cadet indexes.

        This method also keeps track of how many trial runs the player has left
        by comparing the variables 'MAX_RUNS' and 'runs' from the trials
        object.

        Args:
            trials (object): Reference to Trials class instance
            cadets (object): Reference to Cadets class instance
            skill_nr (int, optional): Passed from run_skill_choice(). Indicates
                chosen skill for the trials. Defaults to None.
        """
        # Build info messages and menu elements
        self.display.clear(is_error=True)
        trial_status = [self.sheet.get_text('scr_trial_active')]
        trial_status.append(f'{self.chosen_skill}:  ')
        self.display.build_screen(trial_status, row_nr=16)
        # Use only second part of cadet name to fit all cadets in one row
        short_names = [name.split(" ")[1] for name in cadets.names]
        cadet_choice_texts = ' '.join(
            [f'⁞{c[0]}⁞ {c[1]}' for c in enumerate(short_names, 1)])
        self.display.build_menu(cadet_choice_texts)
        # Get player input for first cadet
        while True:
            c1 = input(self.display.build_input(
                self.sheet.get_text('prompt_cadet_1'))).strip()
            try:
                # Enumeration starts at 1, therefore "- 1" to get index
                c1 = int(c1) - 1
                # Check if player entered a valid index for the list before
                # running trials
                cadets.names[c1]
            # Not specifying an error type here because all invalid user input
            # shall be handled the same - by showing an error message and
            # continuing the cadet choice loop
            except:
                self.display.build_menu(
                    self.sheet.get_text('err_cadet_1'), is_error=True)
            else:
                self.display.clear(is_error=True)
                break
        # Build info message
        vs = self.sheet.get_text('menu_trials_vs')
        trial_status[1] += f'{cadets.names[c1]}{vs}'
        self.display.build_screen(trial_status, row_nr=16)
        # Get player input for second cadet
        while True:
            c2 = input(self.display.build_input(
                self.sheet.get_text('prompt_cadet_2'))).strip()
            if str(c1+1) == c2:
                self.display.build_menu(self.sheet.get_text(
                    'err_cadet_twice'), is_error=True)
                continue
            self.display.clear(is_error=True)

            try:
                c2 = int(c2) - 1
                cadets.names[c2]
            # Not specifying an error type here because all invalid user input
            # shall be handled the same - by showing an error message and
            # continuing the cadet choice loop
            except:
                self.display.build_menu(
                    self.sheet.get_text('err_cadet_2'), is_error=True)
            else:
                self.display.clear(is_error=True)
                break
        # Build info message at the bottom of the terminal
        trial_status[1] = trial_status[1][:-3] + f'{cadets.names[c2]}'
        self.display.build_screen(trial_status, row_nr=16)
        # Start the trial for the chosen cadet pair
        trials.fill_trials(cadets, skill_nr, c1, c2)
        # Remove cadet pair from screen but leave active skill
        self.display.build_screen((f'{self.chosen_skill}:  '), 17)
        # Check if all allowed trial runs have been exhausted
        self.stay_in_trial_menu = trials.MAX_RUNS >= trials.runs
        # Return to run_trial_loop()

    def run_mission_loop(self, available_cadets: list) -> int:
        """Displays cadet names as menu choices and waits for valid user input

        This method creates a menu choice string from the available_cadets list
        and waits for the user to choose a valid index. The list is created by
        the Mission class method assemble_crew() and is shrinking with each
        chosen index. The chosen index is returned to assemble_crew().

        Args:
            available_cadets (list): Shrinking list of available cadets as set
                in Mission class method assemble_crew()

        Returns:
            int: Index for available_cadets list
        """
        # Use only second part of cadet name to fit all cadets in one row
        short_names = [name.split(" ")[1] for name in available_cadets]
        # Create menu elements out of the dynamic list
        mission_loop_texts = ' '.join([
            f'⁞{c[0]}⁞ {c[1]}' for c in enumerate(short_names, 1)])
        self.display.build_menu(mission_loop_texts)
        while True:
            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)
            try:
                # Enumeration starts at 1, therefore "- 1" to get index
                choice = int(choice) - 1
                # Check if the player entered a valid index for the list
                available_cadets[choice]
                break
            except:
                self.display.build_menu(
                    self.sheet.get_text('err_role'), is_error=True)

        # Returns to assemble_crew()
        return choice

    def reset_menu(self):
        """Resets menu values on repeated playthrough"""
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.trial_first_time = True

    def info_screen(self, part, value=None):
        """Prepares and displays all info screens

        Args:
            part (string): ID of the info screen to show
            value (optional): This argument can contain one value of any type
                needed for the specific info screen. Defaults to None.
        """
        match part:
            case '1_logo':
                logo = [f'{"    🟇 🟍 ✵  AD ASTRA ✵ 🟍 🟇":<32}']
                logo.extend(self.sheet.get_text('logo_ad_astra'))
                self.display.clear()
                self.display.build_screen(logo, 2, center_logo=True)
                return
            case '2_welcome':
                message = self.sheet.get_text('welcome')
                self.display.clear()
                self.display.build_screen(message)
                return
            case '3_recruit':
                # Value is a list with cadet names
                cadet_names = value
                message = self.sheet.get_text(
                    'recruit_msg', self.active_player.name)
                message.extend(cadet_names)
                self.display.build_screen(message, row_nr=2)
                # Wait for the user to read screen and press ENTER before starting trials
                self.display.build_menu('')
                input(self.display.build_input(prompt_enter=True))
                return
            case '4_trials_desc':
                # Value is an int with mission difficulty
                message = self.sheet.get_text('trials_desc', str(value))
                self.display.build_screen(message, 2)
                return
            case '5_red_alert':
                # Value is the Mission class object
                mission = value
                # Red alert screen
                self.display.clear()
                self.display.draw()
                time.sleep(0.7)
                self.display.flush_input()
                self.display.clear()
                alert_header = (f'{self.BRIGHT_RED}{"▓"*33}'
                                f'{self.sheet.get_text("red_alert_header")}'
                                f'{"▓"*32}{self.RESET}')
                alert = self.sheet.get_text('red_alert_msg')
                choices = self.sheet.get_text('red_alert_choices')
                self.display.build_screen(alert_header,
                                          2, center=True, ansi=11)
                self.display.build_screen(alert, 4)
                self.display.build_menu(choices)
                while True:
                    # The following choice is only needed for storytelling;
                    # it doesn't impact the game
                    choice = input(self.display.build_input())
                    self.display.clear(is_error=True)
                    match choice:
                        case '1':
                            message_1 = self.sheet.get_text(
                                'red_alert_y', self.active_player.name)
                        case '2':
                            message_1 = self.sheet.get_text(
                                'red_alert_n', self.active_player.name)
                        case _:
                            error = self.sheet.get_text('err_red_alert')
                            self.display.build_menu(error, is_error=True)
                            continue
                    self.display.clear(list(range(3, 19)))
                    self.display.build_screen(message_1, 4)
                    # The content of this message depends on the
                    # proportionality of mission difficulty and average
                    # cadet skill level
                    message_2 = self.sheet.get_text(
                        f"prediction_{mission.suffix}", mission.prognosis)
                    self.display.build_screen(message_2, 10)
                    self.display.build_menu('')
                    input(self.display.build_input(prompt_enter=True))
                    return
            case '6_ship_anim':
                self.display.clear()
                ship = self.sheet.get_text('ship_anim')
                parsed_ship = [f'{" "*80}{row:73}' for row in ship]
                for i in range(-2, -153, -2):
                    all_lines = []
                    for line in parsed_ship:
                        all_lines.append(line[i:-1 if i >= -76 else i+76])
                    self.display.build_screen(all_lines, 3)
                    self.display.draw()
                    time.sleep(0.05)
                self.display.flush_input()
                return
            case '7_mission_score':
                # value is final mission score here
                self.display.build_menu("")
                message = self.sheet.get_text(f'mission_score_{value}')
                self.display.build_screen(
                    self.BRIGHT_CYAN + message[0] + self.RESET, 3, ansi=11)
                if value in [0, 1, 2]:
                    self.display.build_screen(
                        self.BRIGHT_RED + message[1] + self.RESET, 5, ansi=11)
                else:
                    self.display.build_screen(
                        self.BRIGHT_GREEN + message[1] + self.RESET, 5, ansi=11)
                self.display.build_screen(message[2:], 6)
                input(self.display.build_input(prompt_enter=True))
                return
            case '8_player_score':
                # Displays the detailed player score
                self.display.build_screen(
                    self.sheet.get_text('scores_header'), 2)
                input(self.display.build_input(
                    self.sheet.get_text('prompt_highscore')))
                return
            case '9_highscore':
                self.display.build_menu(self.sheet.get_text('please_wait'))
                self.display.draw()
                self.display.build_screen(f"{self.BRIGHT_GREEN}"
                                          f"{self.sheet.get_text('hs_header')}"
                                          f"{self.RESET}",
                                          3, center=True, ansi=11)
                self.display.build_screen(
                    self.sheet.get_score(), 6, center=True, ansi=11)
                self.display.build_menu("")
                input(self.display.build_input(prompt_enter=True))
                return
            case '10_say_goodbye':
                # Constructs and shows the exit screen with the credits
                fill_sym = "⸾"
                scr = []
                self.display.clear()
                self.display.clear(is_error=True)
                self.display.build_menu('')
                scr = [f'{fill_sym*76}']*7
                scr.append(f'{fill_sym*25}{" "*27}{fill_sym*24}')
                scr.append(f'{fill_sym*25}'
                           f'{self.sheet.get_text("exit_live_long")}'
                           f'{fill_sym*24}')
                scr.append(f'{fill_sym*25}{" "*27}{fill_sym*24}')
                scr.extend([f'{fill_sym*76}']*5)
                scr.append(f'{fill_sym*17}{self.sheet.get_text("exit_by")}'
                           f'{fill_sym*17}')
                scr.append(f'{fill_sym*17}{self.sheet.get_text("exit_mail")}'
                           f'{fill_sym*17}')
                scr.append(f'{fill_sym*76}')
                self.display.build_screen(scr, 1, center=True)
                self.display.draw()

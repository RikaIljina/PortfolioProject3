
import os
import textwrap
import time


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
    run_game (object): Reference to global function run()
    """
    outer_loop_texts = "1. Start game     2. New player     3. Show highscore     4. Exit game"
    trial_loop_texts = "1. Choose skill              2. Choose cadets              3. Start mission"


    def __init__(self, display: object, run_game: object):
        self.display = display
        self.outer_loop_funcs = {'1': run_game, '3': self.show_highscore}
        self.trial_loop_funcs = {'1': self.run_skill_choice,
                            '2': self.run_cadet_choice}
        self.run_game = run_game
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.active_player = None
        # Is the player accessing the trial menu for the first time?
        self.first_time = True


    def run_outer_loop(self):
        """Displays the outer menu choices and waits for player input"""
        while True:
            # Before the input: Build the screen content
            self.display.build_menu(self.outer_loop_texts)
            self.loading_screen(self.display, part=1) # should come from a dict from Sheet class
            # Draw the screen and take input
            choice = input(self.display.build_input()).strip()
            # After the input: Clear error messages and previous screen content
            self.display.clear(is_error=True)
            self.display.clear()
            match choice:
                case '1':
                    self.run_game(self, self.active_player, self.display)
                case '2':
                    # Restart the game without re-initializing the player
                    self.run_game(self, None, self.display)
                case '3':
                    self.show_highscore()
                case '4':
                    # Return to main() and exit game
                    return
                case _:
                    self.display.build_menu(
                        "--- Please provide a valid choice ---", is_error=True)


    def run_player_init(self):
        """Prompts user to enter a player name until valid name is entered"""
        self.display.clear(is_error=True)
        self.loading_screen(self.display, part=2)
        self.display.build_menu("Please enter your full name:")
        while True:
            name = input(self.display.build_input()).strip()
            if self.active_player.set_name(name):
                break
            else:
                self.display.build_menu(
                    "--- Please only enter between 1 and 50 latin letters and whitespaces ---",
                    is_error=True)
        self.display.clear(is_error=True)
        self.display.clear()


    def run_trial_loop(self, trials: object, cadets: object):
        """Displays trial phase choices and waits for user input
        
        During the trial phase, the player can choose to select a specific
        as well as two cadets to test, or to end the trial phase and start
        the mission.

        Args:
            trials (object): Reference to Trials class instance
            cadets (object): reference to Cadets class instance
        """
        self.display.clear()
        if self.first_time:
            # TODO: add description
            self.display.build_screen("First, choose a skill.", 1)
        while True:
            self.display.build_menu(self.trial_loop_texts)
            # Exit the menu loop if no more trial runs available
            if not self.stay_in_trial_menu:
                self.display.build_menu("")
                break

            choice = input(self.display.build_input()).strip()
            self.display.clear(is_error=True)

            match choice:
               # case '1':
                 #   self.run_skill_choice(trials, cadets)
                #case '2':
                case '3':
                    self.display.clear(is_error=True)
                    self.display.clear()
                    break
            try:
                self.trial_loop_funcs[choice]
            except:
                self.display.build_menu(
                    "--- Please provide a valid choice ---", is_error=True)
            else:
                if self.first_time and choice != '2':
                    self.display.clear()
                    self.first_time = False
                self.trial_loop_funcs[choice](trials, cadets)

        # Returns to run() to start mission phase


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
                    "--- Please provide a valid skill choice ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        self.chosen_skill = cadets.SKILLS[skill_nr]
        self.run_cadet_choice(trials, cadets, skill_nr)

        # Returns to run_trial_loop()


    def run_cadet_choice(self, trials: object, cadets: object, skill_nr=None):
        """Lets player choose two cadets to compete against each other

        Calls the Trials method fill_trials() after validating all choices.

        Args:
            trials (object): Reference to Trials class instance
            cadets (object): Reference to Cadets class instance
            skill_nr (int, optional): Passed from run_skill_choice(). Indicates
                chosen skill for the trials. Defaults to None.
        """
        if self.chosen_skill is None:
            self.first_time = True
            self.display.build_menu(
                "--- Please choose a skill first ---", is_error=True)
            return

        # Build info messages and menu elements
        self.display.clear(is_error=True)
        trial_status = ['Active trial:']
        trial_status.append(f'{self.chosen_skill}:  ')
        self.display.build_screen(trial_status, row_nr=16)
        # Use only second part of cadet name to fit all cadets in one row
        short_names = [name.split(" ")[1] for name in cadets.names]
        cadet_choice_texts = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
        self.display.build_menu(cadet_choice_texts)
        # Get player input for first cadet
        while True:
            c1 = input(self.display.build_input(
                "Choose first cadet :: ")).strip()
            try:
                # Enumeration starts at 1, therefore "- 1" to get index
                c1 = int(c1) - 1
                # Check if player entered a valid index for the list before
                # running trials
                cadets.names[c1]
            except:
                self.display.build_menu(
                    "--- Please provide a valid choice for first cadet ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break
        # Build info message
        trial_status[1] += f'{cadets.names[c1]} vs ...'
        self.display.build_screen(trial_status, row_nr=16)
        # Get player input for second cadet
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
        # Build info message
        trial_status[1] = trial_status[1][:-3] + f'{cadets.names[c2]}'
        self.display.build_screen(trial_status, row_nr=16)
        # Start the trial for the chosen cadet pair
        trials.fill_trials(cadets, skill_nr, c1, c2)
        self.display.clear([17])
        # Check if all allowed trial runs have been exhausted
        self.stay_in_trial_menu = trials.MAX_RUNS > trials.runs
        # Returns to run_skill_choice() or run_trial_loop()


    def run_mission_loop(self, available_cadets: list) -> int:
        """Lets player choose one cadet for a crew role in the Mission phase

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
            f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
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
                    f"---Please provide a valid choice for the Cadet to fill this role---", is_error=True)

        # Returns to assemble_crew()
        return choice


    def reset_menu(self):
        """Resets menu values on repeated playthrough"""
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.first_time = True


    def show_highscore(self, *args):
        return


    # TODO: should go into Sheet class
    def loading_screen(self, display: object, part=1):
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
                
            case 3:
                display.clear()
                ship = ["                                          ________.-._____",
                        "                               _____.----'--'-------------`-------._____",
                        " ,------.______________.----._'=========================================`",
                        " ]======================<|# |_)------- `----._____________.----'",
                        " `------.______________.----'[  ,--------/        `-'",
                        "          `-.---.-'    _____/__/___     /",
                        "        ____|   |-----'            `---<",
                        "       /||__|---|________             //",
                        "       `------------._       _______ //",
                        "                      \        ---- //",
                        "                       |__________.-'"]
                parsed_ship = [f'{" "*80}{row:73}' for row in ship]
                for i in range(-2,-153,-2):
                    all_lines = []
                    for line in parsed_ship:
                        all_lines.append(line[i:-1 if i>=-76 else i+76])
                    display.build_screen(all_lines, 3)
                    display.draw()
                    #x = ((i*-1)**2)/100000
                    # TODO: make speed curve
                    time.sleep(0.07)
                input()


import math
import random
import textwrap
# from game.UI.sheets import Sheet


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

    def __init__(self, roles: list, display: object, sheet: object):
        self.roles = roles
        self.display = display
        self.sheet = sheet
        self.prognosis = 0
        self.difficulty = 0
        self.score = 0
        self.mission_log = {}
        self.crew = {}
        self.mission_parameters = [random.randrange(
            self.DIFF_MIN, self.DIFF_MAX+1) for _ in range(5)]
        self.difficulty = (sum(self.mission_parameters)/5)*10

    def assemble_crew(self, menu: object, trials: object, cadets: object):
        """Lets player assign cadets to the roles via the menu

        Outputs the trial log entries for each skill.

        Args:
            menu (object): Reference to Menu class instance
            trials (object): Reference to Trials class instance
            cadets (object): Reference to Cadets class instance
        """
        available_cadets = cadets.names[:]
        self.display.build_screen(trials.trials_log, 1)
        crew_list = ['Welcome onboard']
        for skill in self.roles:
            self.display.build_screen(
                f'Please assemble the crew. For the role of {skill}: ', 18)
            index = menu.run_mission_loop(available_cadets)
            crew_list.append(
                f'{skill} {available_cadets[index].split(" ")[1]}')
            self.display.build_screen(textwrap.wrap(
                ', '.join(crew_list)+'!', 76), 16)
            self.crew[skill] = [available_cadets[index],
                                cadets.cadets[available_cadets[index]][skill]]
            available_cadets.pop(index)
        # Clear menu and wait for player to read the output and press ENTER
        self.display.clear([18])
        self.display.build_menu("")
        input(self.display.build_input(prompt_enter=True))

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
        # Output mission data before the actual mission start
        self.display.build_screen(
            f"Predicted crew success rate: {self.calculate_prognosis()}", 1)
        self.display.build_screen(f'The mission difficulty is '
                                  f'{self.difficulty}', 3)
        self.display.build_menu("")
        input(self.display.build_input(prompt_enter=True))
        diff_values = {1: "low", 2: "low", 3: "low", 4: "low",
                       5: "low", 6: "mid", 7: "mid", 8: "mid", 9: "high", 10: "high"}
        # Assign mission description according to each mission parameter and
        # calculate success for each cadet.
        for param, (key, value) in zip(self.mission_parameters, self.crew.items()):
            fname = value[0].split(" ")[1]
            if value[1] >= param:
                self.score += 1
                success = True
            else:
                success = False
            try:
                # Get the appropriate message from the Google sheet
                msg = self.sheet.get_mission_msg(
                    key, diff_values[param], success, fname)
            except:
                print("Internal error: dictionary issue")
                input()
            cadet_performance = f'{value[0]} has {"succeeded" if success else "failed"}'
            self.mission_log[key] = [cadet_performance]
            self.mission_log[key].extend(textwrap.wrap(msg, 70))

    def show_results(self, player: object, trials: object):
        """Collects mission calculations and results in one place, outputs them

        Args:
            player (object): Reference to Player class instance
            trials (object): Reference to Trials class instance
        """
        self.display.clear()
        # Method prints mission info to the screen and builds mission log
        self.calculate_success()
        self.display.clear()
        # Print mission log to the screen
        for key, value in self.mission_log.items():
            self.display.build_screen([f'{key}: '], 4, center=True)
            self.display.build_screen(value, 5, center=True)
            input(self.display.build_input())
            self.display.clear()

        self.display.build_screen("Calculating final player score:", 1)
        final_score = player.calculate_score(
            trials.runs, trials.MAX_RUNS, self)
        # Save player score to highscore table
        self.sheet.write_score(final_score, player.name)
        self.display.build_screen(f'{final_score}', 2)
        input(self.display.build_input())

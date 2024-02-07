"""Contains the Player class which handles all player-related operations"""
import re


class Player:
    """Contains player data and performs player-related operations

    Attributes:
        name (str): Player name as entered by user, set by a method in 
            the Menu object
        score (int): Player score as calculated by class method

    Methods:
        set_name(): Validates player name entry during player initialization
        build_detailed_score(): Calculates player score at the end of the game
    """
    STARTING_SCORE = 1500

    def __init__(self):
        self.name = ""
        self.score = 0

    def set_name(self, name):
        """Validates player name entry

        Checks if the name contains only latin letters and whitespaces
        and makes sure that the name contains at least one letter.
        Saves player name in self.name attribute.
        Returns a bool to menu loop run_player_init():
        - True if name has been set,
        - False if name was invalid.

        Args:
            name (str): User input for the player name

        Returns:
            bool: True if name valid, False if name invalid
        """
        pattern = r'^[A-Za-z\s]{1,30}$'
        if re.match(pattern, name) and re.search(r'[a-zA-Z]', name):
            # Remove redundant whitespaces from user name
            self.name = ' '.join(name.split())
            return True
        return False

    def __calculate_score(self, trial_runs: int, trial_max_runs: int,
                        mission: object) -> tuple:
        """Calculates player score at the end of the game

        Args:
            trial_runs: Used-up trial runs from Trial class instance
            trial_max_runs: Max trial runs from Trial class instance
            mission: Reference to Mission class instance

        Returns:
            tuple: Resulting player score and detailed score elements
        """
        # Reset score in case same player starts a new game
        self.score = 0
        mission_failed_penalty = 0 if mission.score >= 3 else 700
        mission_score_penalty = (5 - mission.score) * 100
        mission_prognosis_penalty = 100 - mission.prognosis
        skill_penalty = 500 - sum([value[1]
                                   for value in mission.crew.values()]) * 10
        trial_run_bonus = 0 if mission_failed_penalty != 0 else (
            trial_max_runs - trial_runs + 1) * 10
        mission_difficulty_bonus = 0 if mission_failed_penalty != 0 else int(
            mission.difficulty - mission.prognosis)
        result = int(self.STARTING_SCORE - mission_failed_penalty
            - mission_score_penalty - mission_prognosis_penalty
            - skill_penalty + mission_difficulty_bonus + trial_run_bonus)

        return (max(0, result),
                mission_failed_penalty,
                mission_score_penalty,
                mission_prognosis_penalty,
                skill_penalty,
                trial_run_bonus,
                mission_difficulty_bonus)

    def build_detailed_score(self, trial_runs: int, trial_max_runs: int,
                             mission: object, display: object, sheet: object):
        """Builds detailed score overview and updates Display
        
        Calls __calculate_score() and constructs a screen view out of all
        received score elements.

        Args:
            trial_runs (int): Used-up trial runs from Trial class instance
            trial_max_runs (int): Max trial runs from Trial class instance
            mission (object): Reference to Mission class instance
            display (object): Reference to Display class instance
            sheet (object): Reference to Sheet class instance
        """
        scores = self.__calculate_score(trial_runs, trial_max_runs, mission)
        self.score = scores[0]
        for idx, score in enumerate(scores, 0):
            if idx == 0:
                display.build_screen(sheet.get_text(
                    f'scores_{idx}', str(score)), 13)
            else:
                display.build_screen(sheet.get_text(
                    f'scores_{idx}', str(score)), idx+4)
        display.build_screen(sheet.get_text(
            'scores_default', str(self.STARTING_SCORE)), 4)

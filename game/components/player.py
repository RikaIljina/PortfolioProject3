import re


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


    def set_name(self, name):
        """Validates player name entry
        
        Checks if the name contains only latin letters and whitespaces
        and makes sure that the name contains at least one letter.
        Saves player name in self.name attribute.

        Args:
            name (str): User input for the player name

        Returns:
            bool: True if name valid, False if name invalid
        """
        pattern = r'^[A-Za-z\s]{1,30}$'
        if re.match(pattern, name) and re.search(r'[a-zA-Z]', name):
            self.name = name
            return True
        else:
            return False


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
        # Reset score in case same player starts a new game
        self.score = 0
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

        return max(0, result)
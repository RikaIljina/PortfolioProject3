import random
import textwrap


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
                 "Cadet Spock", "Cadet Yar", "Cadet Troi", "Cadet Sisko",
                 "Cadet Ro", "Cadet Rom", "Cadet Nog", "Cadet Dax",
                 "Cadet Kira", "Cadet Hansen", "Cadet LaForge", "Cadet McCoy",
                 "Cadet Scott", "Cadet Uhura", "Cadet Chekov", "Cadet Sulu"]
    MAX_POINTS = 25
    LOWEST_SKILL = 1
    HIGHEST_SKILL = 10

    def __init__(self, display: object, player_name: object, sheet: object):
        self.display = display
        self.player_name = player_name
        self.sheet = sheet
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
        message = self.sheet.get_text('recruit_msg', self.player_name)
        message.extend(self.names)
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
                skills_sum = sum(skill_points[0:i-1])
                upper_range = min(self.MAX_POINTS - skills_sum
                                  - (skill_amount-i) + 1,
                                  self.HIGHEST_SKILL + 1)
                if (self.MAX_POINTS - skills_sum) < self.HIGHEST_SKILL:
                    lower_range = self.LOWEST_SKILL
                elif ((self.MAX_POINTS - skills_sum)
                      == self.HIGHEST_SKILL * 2):
                    lower_range = self.HIGHEST_SKILL
                else:
                    lower_range = max((self.MAX_POINTS - skills_sum)
                                     % (self.HIGHEST_SKILL * (skill_amount-i)),
                                     1)
                points = random.randrange(lower_range, upper_range)

            elif i == 3:
            # Analogous to 4th skill calculations
                skills_sum = sum(skill_points[0:i-1])
                upper_range = min(self.MAX_POINTS - skills_sum
                                  - (skill_amount-i) + 1,
                                  self.HIGHEST_SKILL + 1)
                if (self.MAX_POINTS - skills_sum) < self.HIGHEST_SKILL*2:
                    lower_range = self.LOWEST_SKILL
                else:
                    lower_range = max(
                        (self.MAX_POINTS - skills_sum)
                        % (self.HIGHEST_SKILL * (skill_amount-i)), 1)
                points = random.randrange(lower_range, upper_range)

            else:
            # The first two values can be chosen randomly
                points = random.randrange(self.LOWEST_SKILL,
                                          self.HIGHEST_SKILL + 1)

            skill_points.append(points)

        return skill_points

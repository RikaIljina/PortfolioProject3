"""Contains the Cadet object which handles cadet creation"""
import random


class Cadets:
    """Handles cadet creation

    Contains all cadet-related data and creates a cadets dictionary with
    names, skills, and skill values.

    Args:
        sheet (object): Reference to Sheet class instance

    Attributes:
        skills (list): Five skills the cadets are being tested for
        all_names (list): Names to randomly choose from when building dict
        names (list): Random sample of 6 names from all_names variable
        cadets (dict): Dict in the format {name: {skill: value, ...}, ... }

    Methods:
        recruit(): Builds cadet dict and outputs message on screen
    """
    MAX_POINTS = 25
    LOWEST_SKILL = 1
    HIGHEST_SKILL = 10

    def __init__(self, sheet: object):
        self.skills = sheet.get_list('skill_list')
        self.all_names = sheet.get_list('name_list')
        self.names = random.sample(self.all_names, 6)
        self.cadets = {}

    def recruit(self):
        """Initializes cadet dictionary

        Builds initial cadet dictionary with 6 cadets and their respective
        secret skill values.
        """
        self.cadets = {key: dict(zip(
                                 self.skills, self.__cadet_skill_generator()))
                       for key in self.names}

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
        skill_amount = len(self.skills)

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

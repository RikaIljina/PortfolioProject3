# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

from pprint import pprint
import random
import math
import os

# Establish connection to Google sheets for highscore management


# Total amount of skill points to divide among all skills for each cadet
MAX_POINTS = 25
# Lowest and highest possible skill level on a scale of 1-10
LOWEST_SKILL = 1
HIGHEST_SKILL = 10
# The skills which the cadets are being tested for
SKILLS = ["Diplomacy", "Science", "Engineering", "Medicine", "Pilot"]
# Selection of names for cadets
NAMES = ["Cadet Janeway", "Cadet Picard", "Cadet Kirk", "Cadet Kim", "Cadet Paris",
         "Cadet Whorf", "Cadet Crusher", "Cadet Torres", "Cadet Spock"][0:6]


# Add Menu class with Stage 1 - name input, Stage 2 - cadet trial runs,
# Stage 3 - assignments, Stage 4 - final mission start,
# Stage 5 - view highscore, restart, exit

class Menu:
    def __init__(self):
        self.texts_lvl1 = {"1. Print x   2. Print y"}
        self.lvl1 = {'1': print_x, '2': print_y}

    def run_lvl1(self):
        while True:
            print(self.texts_lvl1)
            k = input()
            try:
                self.lvl1[k]()
            except:
                print(f"Wrong input")


def print_x():
    print('Printing x!!!')
    print(cadet_skill_generator())


def print_y():
    print("Printing y!!!")


# Add Display class to gather all prints and produce output (80x24)


# Add logic: generate cadet dict with random skills, run trials and
# save results in a new dict

def cadet_skill_generator():
    """
    This function generates and returns a list with 5 random skill numbers, 
    each between LOWEST_SKILL and HIGHEST_SKILL (1 - 10), with a total sum of 
    MAX_POINTS (25). 
    """
    skill_points = []
    skill_amount = len(SKILLS)

    for i in range(1, skill_amount + 1):
        # The 5th skill to be calculated always takes the remaining difference
        # between the maximum possible points and the sum of used-up points
        if i == 5:
            points = MAX_POINTS - sum(skill_points)
            skill_points.append(points)

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
            skill_points.append(points)
        elif i == 3:
            upper_range = min(
                MAX_POINTS - sum(skill_points[0:i-1]) - (skill_amount - i) + 1, HIGHEST_SKILL + 1)
            if (MAX_POINTS - sum(skill_points[0:i-1])) < HIGHEST_SKILL*2:
                lower_range = LOWEST_SKILL
            else:
                lower_range = max(
                    (MAX_POINTS - sum(skill_points[0:i-1])) % (HIGHEST_SKILL*(skill_amount - i)), 1)
            points = random.randrange(lower_range, upper_range)
            skill_points.append(points)
        else:
            points = random.randrange(LOWEST_SKILL, HIGHEST_SKILL + 1)
            skill_points.append(points)

    print(sum(skill_points))
    return skill_points


# Add Game Manager (for each stage?) that will instantiate objects, pass them to their
# respective functions


def game_manager():
    m = Menu()
    m.run_lvl1()


if __name__ == '__main__':
    game_manager()

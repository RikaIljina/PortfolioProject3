# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

from pprint import pprint
import random
import math
import os
from typing import Any


# Establish connection to Google sheets for highscore management


# Player object with name and score
class Player:
    def __init__(self):
        self.name = ""
        self.score = 0

    def get_name(self):
        # All print statements should be passed to class Display later
        print("Please enter your name:")
        self.name = input()

    # mission_score, mission_difficulty, mission_prognosis):
    def calculate_score(self, trial_runs, trial_max_runs, mission_data):
        mission_failed_penalty = 0 if mission_data.score >= 3 else 500
        mission_score_penalty = (5 - mission_data.score) * 100
        mission_prognosis_penalty = 100 - mission_data.prognosis
        skill_penalty = 500 - sum([value[1]
                                  for value in mission_data.crew.values()])*10
        trial_run_bonus = 0 if mission_failed_penalty != 0 else (
            trial_max_runs - trial_runs) * 10
        mission_difficulty_bonus = 0 if mission_failed_penalty != 0 else mission_data.difficulty - \
            mission_data.prognosis
        print(f'{trial_runs} {trial_run_bonus} {mission_failed_penalty} + {mission_score_penalty} + {mission_prognosis_penalty} + {skill_penalty}')
        print(mission_difficulty_bonus)
        result = 1000 - mission_failed_penalty - mission_score_penalty - \
            mission_prognosis_penalty - skill_penalty + \
            mission_difficulty_bonus + trial_run_bonus
        return result


# Add Menu class with Stage 1 - name input, Stage 2 - cadet trial runs,
# Stage 3 - assignments, Stage 4 - final mission start,
# Stage 5 - view highscore, restart, exit

class Menu:
    def __init__(self):
        self.texts_lvl1 = "1. Print x   2. Print y"
        self.lvl1 = {'1': print_x, '2': print_y}

    def run_lvl1(self):
        while True:
            print(self.texts_lvl1)
            k = input()
            try:
                self.lvl1[k]()
            except:
                print(f"Wrong input")
                break


def print_x():
    print('Printing x!!!')


def print_y():
    print("Printing y!!!")


# Add Display class to gather all prints and produce output (80x24)


# Add logic: generate cadet dict with random skills, run trials and
# save results in a new dict


class Cadets:

    def __init__(self):
        # The skills which the cadets are being tested for
        self.SKILLS = ["Diplomacy", "Science",
                       "Engineering", "Medicine", "Pilot"]
        # Selection of names for cadets (TODO: randomize selection!)
        self.NAMES = random.sample(["Cadet Janeway", "Cadet Picard", "Cadet Kirk", "Cadet Kim", "Cadet Paris",
                                    "Cadet Whorf", "Cadet Crusher", "Cadet Torres", "Cadet Spock", "Cadet Troi"], 6)
        self.cadets = {}

    def recruit(self):
        # Build initial cadet dictionary with 6 cadets and their respective random skill values.
        # The player has no access to these values.
        self.cadets = {key: {key: value for key, value in zip(
            self.SKILLS, self.cadet_skill_generator())} for key in self.NAMES}

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

        print(sum(skill_points))
        return skill_points


class Trials:
    def __init__(self):
        self.skill = ""
        self.c1 = ""
        self.c2 = ""
        self.trials_log = {}
        self.runs = 0
        self.MAX_RUNS = 15

    def run_trials(self, cadets):
        print(self.trials_log)
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
    def __init__(self, roles):
        self.crew = {key: [] for key in roles}
        self.prognosis = 0
        self.score = 0
        self.difficulty = 0
        self.mission_log = ""

    def calculate_prognosis(self):
        result = 0
        for value in self.crew.values():
            result += value[1]*10
        self.prognosis = math.floor(result/len(self.crew.values()))
        return self.prognosis

    def calculate_success(self):
        # Mission difficulty starts at 5
        mission_parameters = [random.randrange(2, 11) for _ in range(5)]
        self.difficulty = (sum(mission_parameters)/5)*10
        print(f'The mission difficulty is {self.difficulty}')
        i = 0
        for key, value in self.crew.items():
            descriptor = ""
            print(key)

            # TODO: Move strings into a Google sheet
            match key:
                case 'Diplomacy':
                    if mission_parameters[i] >= 7:
                        descriptor += "This was a real diplomatic crisis!"
                    elif 4 < mission_parameters[i] < 7:
                        descriptor += "This mission had challenging diplomatic issues."
                    else:
                        descriptor += "There was only a minor diplomatic issue on this mission."
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        descriptor += f"{value[0]} solved it masterfully."
                    else:
                        descriptor += f"Unfortunately, {value[0]} was unable to deal with it."
                case 'Medicine':
                    if mission_parameters[i] >= 7:
                        descriptor += "This was a real medical crisis! A planet-wide outbreak!"
                    elif 4 < mission_parameters[i] < 7:
                        descriptor += "An alien guest had a challenging medical problem."
                    else:
                        descriptor += "A couple crew members sustained minor injuries on the Holodeck."
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        descriptor += f"{value[0]} was a real miracle worker!"
                    else:
                        descriptor += f"Unfortunately, {value[0]} was unable to handle the stress of the medical profession."
                case 'Science':
                    if mission_parameters[i] >= 7:
                        descriptor += "This was a real scientific crisis!"
                    elif 4 < mission_parameters[i] < 7:
                        descriptor += "An alien guest had a challenging scientific problem."
                    else:
                        descriptor += "There was a minor scientific issue."
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        descriptor += f"{value[0]} was a real miracle worker!"
                    else:
                        descriptor += f"Unfortunately, {value[0]} was unable to handle the stress of being a scientist."
                case 'Pilot':
                    if mission_parameters[i] >= 7:
                        descriptor += "This was a real piloting crisis!"
                    elif 4 < mission_parameters[i] < 7:
                        descriptor += "An alien guest had a challenging piloting problem."
                    else:
                        descriptor += "There was a minor piloting issue."
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        descriptor += f"{value[0]} was a real miracle worker!"
                    else:
                        descriptor += f"Unfortunately, {value[0]} was unable to handle the stress of being a pilot."
                case 'Engineering':
                    if mission_parameters[i] >= 7:
                        descriptor += "This was a real engineering crisis!"
                    elif 4 < mission_parameters[i] < 7:
                        descriptor += "An alien guest had a challenging engineering problem."
                    else:
                        descriptor += "There was a minor engineering issue."
                    if value[1] >= mission_parameters[i]:
                        self.score += 1
                        descriptor += f"{value[0]} was a real miracle worker!"
                    else:
                        descriptor += f"Unfortunately, {value[0]} was unable to handle the stress of being an engineer."

            self.mission_log += descriptor

            print(
                f'{value[0]} has {"succeeded" if value[1] >= mission_parameters[i] else "failed"}')
            i += 1

        print(self.mission_log)


# Add Game Manager (for each stage?) that will instantiate objects, pass them to their
# respective functions

def game_manager():
    '''
    '''

    player = Player()
    player.get_name()               # maybe just player.name = input()
    print(f'Hello {player.name}')
    active_cadets = Cadets()
    # Can be modified to allow n cadets to be recruited instead of 6
    active_cadets.recruit()
    pprint(active_cadets.cadets)

    print("\nStarting trials:")
    trials = Trials()

    for _ in range(3):

        print(active_cadets.SKILLS)
        s = int(input("Skill number:"))
        trials.skill = active_cadets.SKILLS[s]
        print(active_cadets.NAMES)
        n1 = int(input("Cadet number 1:"))
        trials.c1 = active_cadets.NAMES[n1]
        print(active_cadets.NAMES)
        n2 = int(input("Cadet number 2:"))
        trials.c2 = active_cadets.NAMES[n2]
        print(trials.run_trials(active_cadets))

    # Final mission

    final_mission = Mission(active_cadets.SKILLS)
    available_cadets = active_cadets.NAMES
    for skill in active_cadets.SKILLS:
        print(trials.show_log(skill))  # print on demand!
        lst = list(f'{c[0]}. {c[1]} ' for c in enumerate(available_cadets))
        for l in lst:
            print(l, end="")
        print(f'\n{skill}: Please assign a cadet:')
        index = int(input())
        cadet_name = available_cadets[index]
        final_mission.crew[skill] = [cadet_name,
                                     active_cadets.cadets[cadet_name][skill]]
        available_cadets.pop(index)

    print(final_mission.crew)

    # Calculate mission success

    print("Success rate: ", final_mission.calculate_prognosis())
    print("Mission success: ", final_mission.calculate_success())

    print("Calculating final player score:")
    print(player.calculate_score(trials.runs, trials.MAX_RUNS,
          final_mission))

    m = Menu()
    m.run_lvl1()

    print("end")


if __name__ == '__main__':
    game_manager()

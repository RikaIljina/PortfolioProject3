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
NAMES = ["Cadet Janeway", "Cadet Picard", "Cadet Kirk", "Cadet Kim", "Cadet Paris", "Cadet Whorf", "Cadet Crusher", "Cadet Torres", "Cadet Spock"][0:6]



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
    
    for i in range(skill_amount):
        points = random.randrange(LOWEST_SKILL, HIGHEST_SKILL + 1)
        skill_points.append(points)
    
    return skill_points


# Add Game Manager (for each stage?) that will instantiate objects, pass them to their
# respective functions

    
def game_manager():
    m = Menu()
    m.run_lvl1()



if __name__ == '__main__':
    game_manager()
# coding=utf-8
# Write your code to expect a terminal of 80 characters wide and 24 rows high
import os
import sys
from game.components.player import Player
from game.UI.display import Display
from game.components.cadets import Cadets
from game.phases.trials import Trials
from game.phases.mission import Mission
from game.UI.menu import Menu
from game.UI.sheets import Sheet

# Establish connection to Google sheets for highscore management
# Create Worksheet object for access to texts and highscore


def run(menu: object, player: object, display: object, sheet: object):
    """Starts the different game phases

    Args:
        menu (object): Reference to Menu class instance
        player (object): Reference to Player class instance
        display (object): Reference to Display class instance
    """
    menu.reset_menu()

    # Only run player initialization if the game is running for the first time
    # or if the user chooses to enter a new name in the outer menu
    if player is None:
        player = Player()
        menu.active_player = player
        menu.run_player_init()

    cadets = Cadets(display, player.name, sheet)
    cadets.recruit()

    # Wait for the user to read screen and press ENTER before starting trials
    display.build_menu('')
    input(display.build_input(prompt_enter=True))

    trials = Trials(display)
    mission = Mission(cadets.SKILLS, display, sheet)
    menu.run_trial_loop(trials, cadets, mission)

    # Final mission
    mission.assemble_crew(menu, trials, cadets)
    mission_score = mission.calculate_success()
    menu.loading_screen(3, mission)
    menu.loading_screen(4)
    menu.loading_screen(6, mission_score)
    # rename
    mission.show_mission_logs(player, trials)
    player.build_detailed_score(
        trials.runs, trials.MAX_RUNS, mission, display, sheet)
    # Save player score to highscore table
    menu.loading_screen(7, mission)
    sheet.write_score(player.score, player.name)
    display.clear()
    menu.show_highscore()

    display.empty_screen()

    # returns to menu lvl1


def main():
    """Initializes Menu and Display class and starts outer menu choice loop"""
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")
    sheet = Sheet()
    display = Display()
    menu = Menu(display, sheet, run)
    menu.run_outer_loop()
    sys.exit()


if __name__ == '__main__':
    main()


# https://www.youtube.com/watch?v=qUeud6DvOWI
# https://www.youtube.com/watch?v=woIkysZytSs

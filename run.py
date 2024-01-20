# Write your code to expect a terminal of 80 characters wide and 24 rows high
import os
import sys
from player import Player
from display import Display
from cadets import Cadets
from trials import Trials
from mission import Mission
from menu import Menu

# Establish connection to Google sheets for highscore management
# Create Worksheet object for access to texts and highscore


def run(menu: object, player: object, display: object):
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

    cadets = Cadets(display, player.name)
    cadets.recruit()

    # Wait for the user to read screen and press ENTER before starting trials
    display.build_menu('')
    input(display.build_input(prompt_enter=True))

    trials = Trials(display)
    menu.run_trial_loop(trials, cadets)
    display.clear([16, 17, 18])
    input(display.build_input(prompt_enter=True))
    display.clear()
    display.build_screen(
    ["No more time for trials! On to the real mission!"], 10, center=True)
    input(display.build_input(prompt_enter=True))
    display.clear(is_error=True)
    display.clear()
    # Final mission
    final_mission = Mission(cadets.SKILLS, display)
    final_mission.assemble_crew(menu, trials, cadets)
    menu.loading_screen(display, 3)
    final_mission.show_results(player, trials)

    display.empty_screen()

    # returns to menu lvl1


def main():
    """Initializes Menu and Display class and starts outer menu choice loop"""
    #os.system('cls||clear')
    os.system("clear||cls")
    display = Display()
    menu = Menu(display, run)
    menu.run_outer_loop()
    sys.exit()


if __name__ == '__main__':
    main()


# https://www.youtube.com/watch?v=qUeud6DvOWI
# https://www.youtube.com/watch?v=woIkysZytSs

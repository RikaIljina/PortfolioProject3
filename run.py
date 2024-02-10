"""Main game file that must be run in order to start the game"""
# coding=utf-8
import sys
from game.UI.sheets import Sheet
from game.UI.display import Display
from game.UI.menu import Menu
from game.components.player import Player
from game.components.cadets import Cadets
from game.phases.trials import Trials
from game.phases.mission import Mission


def run(menu: object, player: object, display: object, sheet: object):
    """Game manager function; starts the different game phases

    This function initializes the game component and phases classes, calls the
    different game phases in the correct order and shows info screens.

    Args:
        menu (object): Reference to Menu class instance
        player (object): Reference to Player class instance
        display (object): Reference to Display class instance
        sheet (object): Reference to Sheet class instance
    """
    # Some menu variables must be reset when the game is played in several
    # playthroughs in one session
    menu.reset_menu()
    # Only run player initialization if the game is running for the first time
    # or if the user chooses to enter a new name in the outer menu. If a player
    # has already been initialized, the player object is passed from the menu
    # to run().
    if player is None:
        player = Player()
        menu.active_player = player
        menu.run_player_init()
    # Initialize cadets and show their names
    cadets = Cadets(sheet)
    cadets.recruit()
    menu.info_screen('3_recruit', cadets.names)
    # Initialize trials;
    # initialize mission to show the mission difficulty to the player
    trials = Trials(display, sheet)
    mission = Mission(cadets.skills, display, sheet)
    # Start trials phase via the menu
    menu.run_trial_loop(trials, cadets, mission)
    # Start mission phase
    mission.assemble_crew(menu, trials, cadets)
    mission.calculate_success()
    menu.info_screen('5_red_alert', mission)
    menu.info_screen('6_ship_anim')
    menu.info_screen('7_mission_score', mission.score)
    mission.show_mission_logs()
    player.build_detailed_score(
        trials.runs, trials.MAX_RUNS, mission, display, sheet)
    # Save player score to highscore table
    menu.info_screen('8_player_score', mission)
    display.build_menu(sheet.get_text('please_wait'))
    display.draw()
    sheet.write_score(player.score, player.name)
    display.clear()
    menu.info_screen('9_highscore')
    # Return to menu.run_outer_loop()


def main():
    """Initializes UI classes and starts the outer menu choice loop

    This function starts the game by clearing the screen, initializing the UI
    classes Sheet, Display and Menu, and running the outer menu choice loop.
    On game exit, the function calls say_goodbye() to show the credits and exit
    the program.
    """
    # Clear the screen
    print('\033c', end='')
    sheet = Sheet()
    display = Display(sheet)
    menu = Menu(display, sheet, run)
    try:
        menu.run_outer_loop()
        menu.info_screen('10_say_goodbye')
    except KeyError as e:
        print("Internal error: invalid dictionary key ", e)
    sys.exit()


if __name__ == '__main__':
    main()

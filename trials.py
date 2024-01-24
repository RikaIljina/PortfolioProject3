# import msvcrt
import time


class Trials:
    """Calculates and stores results of the 'Trials' game phase
    
    Calculates the results of two competing cadets and collects all results
    in a trials log. Keeps track of the maximum allowed amount of trial runs.
    
    Args:
        display (object): Reference to Display class instance
        
    Attributes:
        skill (str): Name of the skill to test the cadets for
        c1 (str): Name of the first cadet to test
        c2 (str): Name of the second cadet to test
        trials_log (dict): Contains all results, format {skill: [result]}
        runs (int): Current count of trial runs
        MAX_RUNS (int): Maximum allowed amount of trial runs
        
    Methods:
        fill_trials(): Receives cadet indexes and starts the trial run
        show_log(): Outputs the trial results for each skill
    """
    MAX_RUNS = 15


    def __init__(self, display: object):
        self.display = display
        self.skill = ""
        self.c1 = ""
        self.c2 = ""
        self.trials_log = {}
        self.runs = 0


    def fill_trials(self, cadets: object, skill_nr: int, c1: int, c2: int) \
                    -> bool:
        """Receives cadet indexes from the menu and starts the trial run

        Calls __run_trials() for each skill and cadet pair, outputs the
        results to the terminal, and keeps track of the amount of allowed runs.
        """
        trials_left = f'{self.MAX_RUNS - self.runs} trial{"s" if self.MAX_RUNS - self.runs > 1 else ""} left'
        self.display.build_screen('... Trial ongoing ...' + f"{trials_left:>55}", row_nr=18)
        self.display.draw()
        time.sleep(1)
        self.flush_input()
        #while msvcrt.kbhit():
        #    msvcrt.getwch()
        self.display.clear([15])

        # In case the player skips the skill choice, the previous skill is used
        self.skill = cadets.SKILLS[skill_nr] if skill_nr is not None \
                                             else self.skill
        self.c1 = cadets.names[c1]
        self.c2 = cadets.names[c2]
        self.__run_trials(cadets)
        self.display.build_screen(self.trials_log, row_nr=1)
        self.display.build_screen(f"{trials_left:>76}", 18)


    def __run_trials(self, cadets: object):
        """Compares skill values for a cadet pair and logs result

        Args:
            cadets (object): Reference to Cadet class instance
        """
        skill_c1 = cadets.cadets[self.c1][self.skill]
        skill_c2 = cadets.cadets[self.c2][self.skill]
        if skill_c1 - skill_c2 <= -4:
            result_string = (f'{self.c1} performed much worse than {self.c2}')
        elif skill_c1 - skill_c2 < 0:
            result_string = (f'{self.c1} performed worse than {self.c2}')
        elif skill_c1 - skill_c2 >= 4:
            result_string = (f'{self.c1} performed much better than {self.c2}')
        elif skill_c1 - skill_c2 > 0:
            result_string = (f'{self.c1} performed better than {self.c2}')
        else:
            result_string = (f'{self.c1} and {self.c2} performed equally well')

        if self.trials_log.get(self.skill):
            self.trials_log[self.skill].append(result_string)
        else:
            # Result must be stored as a list to ensure correct processing by
            # the Display class
            self.trials_log[self.skill] = [result_string]
        self.runs += 1
        

    def show_log(self, skill: str) -> list:
        """Return the trial results for the specified skill

        Args:
            skill (str): Name of the skill for which to return the results 

        Returns:
            list: All trial results for this particular skill
        """
        if self.trials_log.get(skill):
            return self.trials_log[skill]
        else:
            self.trials_log[skill] = ["No trials for this skill"]
            return self.trials_log[skill]


    # https://stackoverflow.com/questions/67083097/how-to-prevent-user-input-into-console-when-program-is-running-in-python    
    def flush_input(self):
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            import sys, termios    #for linux/unix
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)


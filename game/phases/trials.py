"""Contains the Trials class which handles the Trials phase logic and data"""
import time


class Trials:
    """Calculates and stores results of the 'Trials' game phase

    Calculates the results of two competing cadets and collects all results
    in a trials log. Keeps track of the maximum allowed amount of trial runs.

    Args:
        display (object): Reference to Display class instance
        sheet (object): Reference to Sheet class instance

    Attributes:
        skill (str): Name of the skill to test the cadets for
        last_skill (str): Name of the previously chosen skill
        c1 (str): Name of the first cadet to test
        c2 (str): Name of the second cadet to test
        trials_log (dict): Contains all results in text form,
            format {skill: [result_string]}
        runs (int): Current count of trial runs
        MAX_RUNS (int): Maximum allowed amount of trial runs

    Methods:
        fill_trials(): Receives cadet indexes and starts the trial run
    """
    MAX_RUNS = 3
    BRIGHT_CYAN = '\033[96;1m'
    RESET = '\033[0m'

    def __init__(self, display: object, sheet: object):
        self.display = display
        self.sheet = sheet
        self.skill = ""
        self.last_skill = ""
        self.c1 = ""
        self.c2 = ""
        self.trials_log = {}
        self.runs = 1

    def fill_trials(self, cadets: object, skill_nr: int, c1: int, c2: int):
        """Receives skill and cadet indexes from the menu, starts the trial run

        Calls __run_trials() for each skill and cadet pair, outputs the
        results to the terminal, and keeps track of the amount of allowed runs.

        Args:
            cadets (object): Reference to Cadets class instance
            skill_nr (int): Index of the chosen skill to compare
            c1 (int): Index of the first cadet
            c2 (int): Index of the second cadet
        """
        trials_left = self.MAX_RUNS - self.runs
        sing_plural = self.sheet.get_text("trials_hours_left") \
            if trials_left + 1 != 1 \
            else self.sheet.get_text("trials_hour_left")
        trials_left_str = (f'{trials_left + 1}{sing_plural}')
        self.display.build_screen(self.sheet.get_text('trial_ongoing')
                                  + f'{trials_left_str:>55}', row_nr=18)
        self.display.draw()
        # Artificial waiting period for ongoing trial phase
        time.sleep(1)
        self.display.flush_input()
        # If the player has skipped the skill choice, the previous skill is
        # used. The previous function makes sure that self.skill is set before
        # allowing the player to skip the skill choice.
        self.skill = cadets.skills[skill_nr] if skill_nr is not None \
            else self.skill
        self.c1 = cadets.names[c1]
        self.c2 = cadets.names[c2]
        self.__run_trials(cadets)
        self.display.build_screen(self.trials_log, row_nr=1)
        # Updated countdown after running the trial
        trials_left_str = (
            f'{trials_left}'
            f' hour{"s" if trials_left != 1 else ""} left')
        self.display.build_screen(f"{trials_left_str:>76}", 18)

    def __run_trials(self, cadets: object):
        """Compares skill values for a cadet pair and logs the result

        The result string depends on the difference in skill points for the
        tested cadets.

        Args:
            cadets (object): Reference to Cadet class instance
        """
        skill_c1 = cadets.cadets[self.c1][self.skill]
        skill_c2 = cadets.cadets[self.c2][self.skill]
        skill_diff = skill_c1 - skill_c2
        if skill_diff <= -4:
            performance = self.sheet.get_text('trials_performance_mw')
            result_string = f'{self.c1}{performance}{self.c2}'
        elif skill_diff < 0:
            performance = self.sheet.get_text('trials_performance_w')
            result_string = f'{self.c1}{performance}{self.c2}'
        elif skill_diff >= 4:
            performance = self.sheet.get_text('trials_performance_mb')
            result_string = f'{self.c1}{performance}{self.c2}'
        elif skill_diff > 0:
            performance = self.sheet.get_text('trials_performance_b')
            result_string = f'{self.c1}{performance}{self.c2}'
        else:
            performance = self.sheet.get_text('trials_performance_eq')
            and_string = self.sheet.get_text('trials_performance_and')
            result_string = f'{self.c1}{and_string}{self.c2}{performance}'

        if self.trials_log.get(self.skill):
            self.__remove_highlight()
            # Add and highlight the current result
            self.trials_log[self.skill].append(
                f'{self.BRIGHT_CYAN}{result_string:<61}{self.RESET}')
        else:
            self.__remove_highlight()
            # Add and highlight the current result.
            # Result must be stored as a list to ensure correct processing by
            # the Display class
            self.trials_log[self.skill] = [
                f'{self.BRIGHT_CYAN}{result_string:<61}{self.RESET}']
        self.last_skill = self.skill
        self.runs += 1

    def __remove_highlight(self):
        """Removes highlight from previously highlighted entry
        
        The last added list element for the previously chosen skill in the
        trials_log dictionary is highlighted in cyan. This highlight must be
        removed as soon as the next element is added and highlighted.
        """
        if self.last_skill:
            color_string = self.trials_log[self.last_skill][-1]
            color_string = color_string.replace('\x1b[96;1m', '')
            color_string = color_string.replace('\x1b[0m', '')
            self.trials_log[self.last_skill][-1] = color_string

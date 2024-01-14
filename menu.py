class Menu():
    def __init__(self, display):  # rename levels
        self.display = display
        self.texts_lvl1_loader = "1. Start game             2. New player             3. Show highscore"
        self.lvl1_loader = {'1': run, '3': show_highscore}
        self.texts_lvl2_trials = "1. Choose skill              2. Choose cadets              3. End trials"
        self.lvl2_trials = {'1': self.run_lvl3_skill,
                            '2': self.run_lvl4_cadets}
        self.texts_lvl3_skill = ""
        self.texts_lvl4_cadets = ""
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        self.active_player = None

    def run_lvl0_player(self):
        self.display.clear(is_error=True)
        loading_screen(self.display, part=2)
        self.display.draw_menu("Please enter your name:")
        name = input(self.display.draw_input()).strip()
        self.active_player.name = name
        self.display.clear()
        return

    def run_lvl1_loader(self):
        while True:
            self.display.draw_menu(self.texts_lvl1_loader)
            loading_screen(self.display, part=1)
            choice = input(self.display.draw_input()).strip()
            self.display.clear(is_error=True)
            self.display.clear()
            if choice == '2':
                run(self, None, self.display)
            else:
                try:
                    self.lvl1_loader[choice](
                        self, self.active_player, self.display)
                except:
                    self.display.draw_menu(
                        f"--- Please provide a valid choice ---", is_error=True)

    def run_lvl2_trials(self, trials, cadets):
        while True:
            self.display.draw_menu(self.texts_lvl2_trials)
            if not self.stay_in_trial_menu:
                self.display.clear(is_error=True)
                self.display.clear()
                break

            choice = input(self.display.draw_input()).strip()
            self.display.clear(is_error=True)

            if choice == '3':
                self.display.clear(is_error=True)
                self.display.clear()
                break
            try:
                self.lvl2_trials[choice]
            except:
                self.display.draw_menu(
                    f"--- Please provide a valid choice ---", is_error=True)
            else:
                self.display.clear()
                self.lvl2_trials[choice](trials, cadets)
               # self.display.clear([], is_error=True)

    def run_lvl3_skill(self, trials, cadets):
        self.display.clear(is_error=True)
        self.display.clear([1])
        self.texts_lvl3_skill = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(cadets.SKILLS, 1)])

        while True:
            self.display.draw_menu(self.texts_lvl3_skill)
            skill_nr = input(self.display.draw_input()).strip()
            self.display.clear(is_error=True)

            try:
                skill_nr = int(skill_nr)-1
                cadets.SKILLS[skill_nr]
            except:
                self.display.draw_menu(
                    f"--- Please provide a valid skill choice ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        self.chosen_skill = cadets.SKILLS[skill_nr]
        self.run_lvl4_cadets(trials, cadets, skill_nr)
        return

    def run_lvl4_cadets(self, trials, cadets, skill_nr=None):
        # self.display.clear([2,3])
        if self.chosen_skill is None:
            self.display.draw_menu(
                "--- Please choose a skill first ---", is_error=True)
            return
        else:
            self.display.clear(is_error=True)
            trial_status = f'{self.chosen_skill}:  '
            self.display.draw_screen(trial_status, line_nr=1)

        short_names = [name.split(" ")[1] for name in cadets.NAMES]
        self.texts_lvl4_cadets = ' '.join(
            [f'{c[0]}. {c[1]} ' for c in enumerate(short_names, 1)])
        self.display.draw_menu(self.texts_lvl4_cadets)
        while True:
            c1 = input(self.display.draw_input(
                "Choose first cadet :: ")).strip()
            try:
                c1 = int(c1) - 1
                cadets.NAMES[c1]
            except:
                self.display.draw_menu(
                    f"--- Please provide a valid choice for first cadet ---", is_error=True)
            else:
                self.display.clear([], is_error=True)
                break

        trial_status += f'{cadets.NAMES[c1]} vs ...'
        self.display.draw_screen(trial_status, line_nr=1)

        while True:
            c2 = input(self.display.draw_input(
                "Choose second cadet :: ")).strip()
            self.display.clear(is_error=True)

            try:
                c2 = int(c2) - 1
                cadets.NAMES[c2]
            except:
                self.display.draw_menu(
                    f"--- Please provide a valid choice for second cadet ---", is_error=True)
            else:
                self.display.clear(is_error=True)
                break

        trial_status = trial_status[:-3] + f'{cadets.NAMES[c2]}'
        self.display.draw_screen(trial_status, line_nr=1)

        self.stay_in_trial_menu = trials.fill_trials(cadets, skill_nr, c1, c2)
        return

    def run_lvl2_mission(self, available_cadets):
        self.texts_lvl2_mission = ' '.join([
            f'{c[0]}. {c[1]} ' for c in enumerate(available_cadets, 1)])
        self.display.draw_menu(self.texts_lvl2_mission)
        while True:
            choice = input(self.display.draw_input()).strip()
            self.display.clear([], is_error=True)
            try:
                choice = int(choice) - 1
                available_cadets[choice]
                break
            except:
                self.display.draw_menu(
                    f"---Please provide a valid choice for the Cadet to fill this role---", is_error=True)
        # self.display.draw_screen(available_cadets[choice])
        return choice

    def reset_menu(self):
        self.texts_lvl3_skill = ""
        self.texts_lvl4_cadets = ""
        self.chosen_skill = None
        self.stay_in_trial_menu = True
        return

if __name__ == '__main__':
    main()

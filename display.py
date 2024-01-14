
# Add Display class to gather all prints and produce output (80x24)

class Display:
    def __init__(self):
        self.HEIGHT = 23
        self.WIDTH = 80
        self.BORDER_CHAR = "▓"
        self.INPUT_PROMPT = '▓▓▓ :: '
        self.EMPTY_LINE = f'{self.BORDER_CHAR}{" ":<78}{self.BORDER_CHAR}'
        self.ERROR_LINE_NR = 21
        self.MENU_LINE_NR = 20
        self.current_text = ""
        self.lines = self.empty_screen(self)

    def empty_screen(self):
        lines = [str(self.BORDER_CHAR*self.WIDTH)]
        lines.extend([self.EMPTY_LINE for _ in range(self.HEIGHT-5)])
        lines.extend([self.BORDER_CHAR*self.WIDTH for _ in range(3)])
        lines.append(str(self.BORDER_CHAR*self.WIDTH))
        return lines

    def clear(self, indexes=[i for i in range(1, 19)], is_error=False):
        if is_error:
            self.lines[self.ERROR_LINE_NR] = self.BORDER_CHAR * \
                self.WIDTH  # self.EMPTY_LINE
        else:
            for index in indexes:
                self.lines[index] = self.EMPTY_LINE

    def draw(self):
        os.system('cls||clear')
        for line in self.lines:
            # time.sleep(0.05)
            print(f'{line}')

    def draw_screen(self, text=None, line_nr=1, center=False):
       # os.system('cls||clear')

        if text:
            if type(text) == list:
                text_len = len(text)
                for i in range(text_len):
                    result = f'{self.BORDER_CHAR}{" "*26 + text[i]:<77} {self.BORDER_CHAR}' if center else f'{self.BORDER_CHAR} {text[i]:<77}{self.BORDER_CHAR}'
                    self.lines.pop(line_nr + i)
                    self.lines.insert(line_nr + i, result)
            else:
                result = f'{self.BORDER_CHAR} {text:<77}{self.BORDER_CHAR}'
                self.lines.pop(line_nr)
                self.lines.insert(line_nr, result)

        self.draw()

    def draw_menu(self, text, is_error=False):

        if is_error:
            result = f'{self.BORDER_CHAR} {text:>77}{self.BORDER_CHAR}'
            self.lines.pop(self.ERROR_LINE_NR)
            self.lines.insert(self.ERROR_LINE_NR, result)

        else:
            result = f'{self.BORDER_CHAR} {text:<77}{self.BORDER_CHAR}'
            self.lines.pop(self.MENU_LINE_NR)
            self.lines.insert(self.MENU_LINE_NR, result)

    def draw_input(self, prompt=''):
        self.draw()
        return self.INPUT_PROMPT + prompt

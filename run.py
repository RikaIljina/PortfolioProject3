# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high


# Establish connection to Google sheets for highscore management


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
    

def print_y():
    print("Printing y!!!") 
    
    
def game_manager():
    m = Menu()
    m.run_lvl1()


# Add Display class to gather all prints and produce output (80x24)


# Add Game Manager (for each stage?) that will instantiate objects, pass them to their
# respective functions


# Add logic: generate cadet dict with random skills, run trials and
# save results in a new dict

if __name__ == '__main__':
    game_manager()
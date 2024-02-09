# "What d'you know" - Testing

## CONTENTS

- [MANUAL TESTING](#manual-testing)
  - [Testing User Stories](#testing-user-stories)
  - [Full Testing](#full-testing)
- [BUGS](#bugs)
  - [Encountered issues](#issues)
  - [Known bugs](#known-bugs)
  - [Solved bugs](#solved-bugs)

## Manual Testing

### Testing user stories

| Goals | How are they achieved? |
|---|---|
| As a player, I want to be able to easily understand how to start the game. | Players are greeted by a loading screen with a menu line which contains the option "Start game" along with the associated number to enter. |
| As a player, I want to be able to quickly understand what the game is about. | After starting the game, a one-page description is shown to the player explaining how the game works. |
| As a player, I want to be notified if my entry or menu choice is invalid.  | A highlighted error line is shown whenever the player enters invalid input, prompting them to choose something valid. |
| As a player, I want to receive instant feedback when entering my choice.  | Feedback is given in the form of changing screens and appropriate info texts. |
| As a player, I want to be receive feedback to let me know how well I did in the game.  | After each playthrough, the player is shown a score table detailing the points they achieved or lost. |
| As a player, I want to see how well I did compared with other players.  | After each playthrough, the game checks whether the player's score is high enough to be entered into the highscore. The highscore table with player names and top scores is shown to the player. |

### Full Testing

The website was tested on:
 - Laptop: 
    - HP EliteBook x360 1030 G3 13.3''

  Due to the unresponsiveness of the embedded Python terminal, the game is not suitable for mobile phones.

On the laptop, the site was tested in the following browsers:
 - Chrome
 - Opera
 - Microsoft Edge


The following features were thoroughly tested:

| Feature | Result |
|---|---|
| There are no spelling errors in the game | Pass |
| The player name input prompt accepts only the allowed character set | Pass |
| All menu choices lead to the correct screen or start the correct function | Pass |
| No printed lines are longer than the terminal rows; long imported lines are wrapped correctly | Pass |
| All texts intended for one screen view fit into the terminal without breaking the borders | Pass |
| All colors are displayed correctly | Pass |
| In case of invalid input, the error handling functionality kicks in and notifies the player about the nature of the error | Pass |
| In case of database errors, the error handling functionality kicks in and notifies the player about the nature of the error | Pass |

## Bugs

### Solved bugs

The following issues came up during the testing process and were fixed:

| Issue | Fix | Screenshot |
|---|---|---|
| During development, I had several bugs because I did not take into consideration that Python interprets the number 0 and empty strings as `False`. Certain values would not be shown and functions would not be triggered because of that. | I either converted `0` to a string or rephrased my `if`-statements to say `if x is None:` instead of `if x:` to solve the bugs. ||
| When implementing the Display module, I noticed that my screen was being redrawn too often, even when invisible to the player. | I discovered that I was calling it from within my `build_screen()` method which is only supposed to assemble the terminal into a drawable list. I made sure to only call the `draw()` method when it is relevant to the player: whenever the input prompt is shown or when the `time.sleep()` function is used to create screen changes without needing user input. |
| When using `time.sleep()`, the player could type something on the keyboard that would then be visible in the input prompt. | I found a code snippet on [stackoverflow](https://stackoverflow.com/questions/67083097/how-to-prevent-user-input-into-console-when-program-is-running-in-python) that flushes the input stream under Windows and Linux.||
| I'm using ANSI escape sequences to add color to my game. However, I encountered issues due to the specific process I use to build my screen: the length of the string must be considered when fitting it into 80 columns and surrounding it with border elements. If an ANSI sequence is present, it adds to the string length despite being invisible, thus disrupting the screen output. | Whenever an ANSI sequence is present in a string, a certain amount of characters must be added to the total row width to achieve the correct result. Trial and error has shown that 11 characters must be added when an ANSI color code and an ANSI reset code are present. It works to properly build the screen, but I have not yet found out why it must be precisely 11. ||
| The player could break the terminal display by entering a long sequence spanning over two rows into the prompt. While the input was ignored by the game as invalid, its presence in the terminal added extra rows and made the whole terminal scrollable, showing broken parts of the previous screen. | I was unable to find a way to limit the length of the input itself, but I found a way to clear the terminal more thoroughly than with cls/clear: `print('\033c', end='')`  |

### Known bugs and persisting issues


- I am not sure whether the `flush_input()` function will work on all systems to flush the input stream.
- I have no insight into how exactly Unicode characters are rendered by the Python terminal embedded in an HTML page. Therefore I am not sure whether all Unicode characters that I use for decoration will be shown correctly by all browsers and on all systems.
- 
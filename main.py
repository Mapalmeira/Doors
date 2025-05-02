import curses
from getpass import getuser

from game import game_loop

WIDTH = 230
HEIGHT = 60

def get_game_specs(stdscr):
    max_y, max_x = stdscr.getmaxyx()

    true_middle = (max_y // 2, max_x // 2)
    
    starting_y = true_middle[0] - HEIGHT // 2
    final_y = starting_y + HEIGHT - 1
    y_range = (starting_y, final_y)

    starting_x = true_middle[1] - WIDTH // 2
    final_x = starting_x + WIDTH - 1
    x_range = (starting_x, final_x)

    virtual_middle = ((final_y - starting_y)//2, (final_x - starting_x)//2)

    username = getuser()

    return {
        "stdscr": stdscr,
        "max_x": max_x,
        "max_y": max_y,
        "x_range": x_range,
        "y_range": y_range,
        "virtual_middle": virtual_middle,
        "true_middle": true_middle,
        "username": username
    }

def invalid_screen_size(game_specs):
    stdscr = game_specs["stdscr"]

    msg1 = "Dimensões insuficientes! O jogo requer pelo menos 230x60"
    msg2 = "Pressione ctrl + '-' no terminal para diminuir o zoom."

    stdscr.addstr(game_specs["true_middle"][0], game_specs["true_middle"][1]-len(msg1)//2, msg1)
    stdscr.addstr(game_specs["true_middle"][0]+1, game_specs["true_middle"][1]-len(msg2)//2, msg2)
        
    stdscr.refresh()
    key = stdscr.getch()

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    game_specs = get_game_specs(stdscr)
    if game_specs["max_x"] < WIDTH or game_specs["max_y"] < HEIGHT:
        invalid_screen_size(game_specs=game_specs)
        return
    
    game_loop(game_specs)

curses.wrapper(main)
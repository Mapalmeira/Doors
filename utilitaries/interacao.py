import curses
import time

from . import pincel
from . import animador

MAP = {
    (0, 4): [(0, 3)],
    (0, 3): [(0, 4), (0, 2)],
    (0, 2): [(0, 3), (0, 1)],
    (0, 1): [(0, 2), (0, 0)],
    (0, 0): [(0, 1), (0, -1)],
    (0, -1): [(0, 0), (0, -2)],
    (0, -2): [(0, -1), (0, -3), (1, -2), (-1, -2)],
    (0, -3): [(0, -2), (1, -3), (-1, -3)],
    (-1, -2): [(0, -2)],
    (1, -2): [(0, -2)],
    (-1, -3): [(0, -3)],
    (1, -3): [(0, -3)],
}

def start_interacao(gs, f, c):
    global game_specs, game_coords, frames, stdscr
    game_specs = gs
    game_coords = c
    frames = f
    stdscr = gs["stdscr"]

# KEYBOARD INTERACTIONS
def move(key):
    DIRECTIONS = {
        curses.KEY_UP: (0, 1),
        curses.KEY_DOWN: (0, -1),
        curses.KEY_RIGHT: (1, 0),
        curses.KEY_LEFT: (-1, 0),
    }

    dxdy = DIRECTIONS.get(key)
    if dxdy is None:
        return False

    x, y = game_coords
    dx, dy = dxdy
    goal = (x + dx, y + dy)

    if goal in MAP.get((x, y), []):
        game_coords[0] += dx
        game_coords[1] += dy
        return True

    return False

def pressed_enter(key):
    return key == 13 or key == 10 or key == curses.KEY_ENTER

def pressed_valid_textual_input(key):
    return ord('a') <= key <= ord('z') or ord('A') <= key <= ord('Z') or ord('0') <= key <= ord('9') or key == ord(' ') or key == 32

def pressed_backspace(key):
    return key == 127 or key == 8 or key == curses.KEY_BACKSPACE

def pressed_esc(key):
    return key == 27

def pressed_exit_char(key):
    return key == curses.KEY_DOWN or pressed_esc(key)

def flashlight_tutorial_box():
    box = {
        'y_alignment': 'middle', 
        'x_alignment': 'middle',
        'y_coord': 10, 
        'x_coord': 0,
        'height': 7,
        'width': 80,
        'vertical_margin': 0,
        'horizontal_margin': 0
    }

    box_text = {
        'content': ['Aperte L para acender ou apagar a lanterna.'], 
        'y_alignment': 'middle', 
        'x_alignment': 'middle',
        'y_coord': 10, 
        'x_coord': 0,
    }

    pincel.generate_box_content(box)
    pincel.draw(box)
    pincel.draw(box_text)

def toggle_flashlight(events, counters, key):
    if events['has_flashlight'] and (key == ord('L') or key == ord('l')):
        events['flashlight_on'] = not events['flashlight_on']
        if events['flashlight_on']:
            counters['flashlight_usages'] += 1
        return True
    return False

# DOOR LOOP
def door_stay_loop_iteration(events, counters, door_coord, key, object_behind=None, can_flashlight=True):
    flashlight_toggled = toggle_flashlight(events, counters, key) if can_flashlight else False
    movement = move(key)

    stay = True
    if flashlight_toggled:
        events['flashlight_tutorial_done'] = True

        pincel.draw(frames[tuple(door_coord)], flashlight=events['flashlight_on'])
        pincel.draw(object_behind, flashlight=events['flashlight_on'])

        if door_coord == [1, -2] and events['flashlight_on']:
            counters['flashlight_on_moon_usages'] += 1
        stdscr.refresh()
        time.sleep(0.1)

    if movement:
        animador.close_door(events, door_coord, object_behind=object_behind)
        stay = False

    return stay
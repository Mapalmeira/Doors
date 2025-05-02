import curses
import time
from random import randint, shuffle

from . import cineasta
from . import pincel
from . import interacao

def start_animador(gs, f, c):
    global game_specs, game_coords, frames, stdscr
    game_specs = gs
    game_coords = c
    frames = f
    stdscr = gs["stdscr"]

# ANIMATIONS
def open_door(events, counters, game_coord, object_behind=None, t=0.3):
    time.sleep(t)
    
    counters['doors_opened'] += 1
    door = frames[tuple(game_coord)]
                  
    # PRE-LOADS THE OBJECT BEHIND THE DOOR
    cineasta.change_frame_state(door, "aberto")
    pincel.draw(door, flashlight=events['flashlight_on'])
    pincel.draw(object_behind, flashlight=events['flashlight_on'])

    # LOADS SEMI-OPENED DOOR
    cineasta.change_frame_state(door, "semiaberto")
    pincel.draw(door, flashlight=events['flashlight_on'])
    if events['has_flashlight'] and not events['flashlight_tutorial_done'] and events['can_tutorial_appear']:
        interacao.flashlight_tutorial_box()
    stdscr.refresh()
    time.sleep(t)

    # LOADS COMPLETELY OPENED DOOR
    cineasta.change_frame_state(frames[tuple(game_coord)], "aberto")
    pincel.draw(door, flashlight=events['flashlight_on'])
    pincel.draw(object_behind, flashlight=events['flashlight_on'])
    if events['has_flashlight'] and not events['flashlight_tutorial_done'] and events['can_tutorial_appear']:
        interacao.flashlight_tutorial_box()
    stdscr.refresh()

def close_door(events, game_coord, t=0.3, object_behind=None):
    door = frames[tuple(game_coord)]

    # LOADS OPEN DOOR
    pincel.draw(door, flashlight=events['flashlight_on'])
    pincel.draw(object_behind, flashlight=events['flashlight_on'])
    if events['has_flashlight'] and not events['flashlight_tutorial_done'] and events['can_tutorial_appear']:
        interacao.flashlight_tutorial_box()
    stdscr.refresh()
    time.sleep(t)

    # LOADS SEMI-CLOSED DOOR
    cineasta.change_frame_state(door, "semiaberto")
    pincel.draw(door, flashlight=events['flashlight_on'])
    if events['has_flashlight'] and not events['flashlight_tutorial_done'] and events['can_tutorial_appear']:
        interacao.flashlight_tutorial_box()
    stdscr.refresh()
    time.sleep(t)

    # LOADS DOOR COMPLETELY CLOSED
    cineasta.change_frame_state(door, "0")
    pincel.draw(door, flashlight=events['flashlight_on'])
    if events['has_flashlight'] and not events['flashlight_tutorial_done'] and events['can_tutorial_appear']:
        interacao.flashlight_tutorial_box()
    stdscr.refresh()
    time.sleep(t)

def knock(y_coord, x_coord, flashlight):
    animation = ['..*..', '.*#*.']

    knock_text = {
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': y_coord, 
        'x_coord': x_coord
    }

    for i in range(len(animation)):
        knock_text['content'] = [animation[i]]
        pincel.draw(knock_text, flashlight=flashlight)
        stdscr.refresh()
        time.sleep(0.05)

    knock_text['content'] = ['KNOCK!']
    pincel.draw(knock_text, flashlight=flashlight)
    stdscr.refresh()
    
    time.sleep(0.3)
    pincel.erase(knock_text)
    stdscr.refresh()

    for i in range(len(animation)-1, -1, -1):
        knock_text['string'] = [animation[i]]
        pincel.draw(knock_text, flashlight=flashlight)
        stdscr.refresh()
        time.sleep(0.05)

    pincel.erase(knock_text, flashlight=flashlight)
    stdscr.refresh()

def knock_knock_door(y_offset=0, flashlight=False):
    knock(-2+y_offset, -4, flashlight)
    knock(2+y_offset, 4, flashlight)

# ANIMATE DRAWING
def animate_drawing(drawing, t, interactive=False):
    current_character = 0
    how_many_chars = sum(len(s.strip(pincel.TRANSPERENCY_CHAR)) for s in drawing['content'])

    curses.flushinp()
    interrupted = False
    stdscr.nodelay(True)
    while True:
        if (current_character > how_many_chars):
            break

        key = stdscr.getch()

        if interactive and interacao.pressed_exit_char(key):
            interrupted = True
            break
        if interactive and interacao.pressed_enter(key):
            current_character = how_many_chars

        pincel.draw(drawing, char_limit=current_character)
        current_character += 1
        stdscr.refresh()
        time.sleep(t)
    
    stdscr.nodelay(False)
    return not interrupted

# RAINFALL
def rainfall():
    droplet_order = list(range(
        max(0, game_specs['x_range'][0]-1), 
        min(game_specs['x_range'][1]+1, game_specs['max_x'])+1
    ))
    shuffle(droplet_order)

    droplets_on_screen = {}
    base_droplet_str = generate_droplet_text(50)
    most_recent_droplet = 0
    before = time.time()

    while True:
        draw_droplets(droplets_on_screen)
        stdscr.refresh()

        # condição para gerar nova gota
        now = time.time()
        if now - before >= 2 * 1.25 ** (-most_recent_droplet) and most_recent_droplet < len(droplet_order):
            before = now
            droplet_x_coord = droplet_order[most_recent_droplet]
            most_recent_droplet += 1
            generate_droplet(droplets_on_screen, base_droplet_str, droplet_x_coord)

        # condição de parada: não há mais gotas sendo geradas nem caindo
        if most_recent_droplet >= len(droplet_order) and len(droplets_on_screen) == 0:
            break

        time.sleep(0.05)

def generate_droplet(droplets_on_screen, base_droplet_str, x_coord):
    droplet_size = randint(7, 20)

    begin = randint(0, len(base_droplet_str)-droplet_size-1)
    end = begin + droplet_size
    droplet_string = base_droplet_str[begin:end]

    color_code = pincel.calculate_color_pair_id(pincel.COLOR_MAP["green"], pincel.COLOR_MAP["black"])
    color_map = [[color_code] for _ in range(droplet_size)]
    color_map[-1] = [pincel.calculate_color_pair_id(pincel.COLOR_MAP["white"], pincel.COLOR_MAP["black"])]

    droplets_on_screen.update({x_coord: {
        'content': list(droplet_string), 
        'color_map': color_map, 
        'y_alignment': 'absolute', 
        'x_alignment': 'absolute', 
        'y_coord':-droplet_size, 
        'x_coord': x_coord,
    }})

def draw_droplet(droplet):
    pincel.erase(droplet)
    droplet['y_coord'] += 1
    pincel.draw(droplet)

def draw_droplets(droplets_on_screen):
    for key in list(droplets_on_screen.keys()):
        droplet = droplets_on_screen[key]
        draw_droplet(droplet)
        if droplet['y_coord'] >= game_specs['max_y'] + len(droplet['content']):
            droplets_on_screen.pop(key)

def generate_droplet_text(size):
    droplet = []
    for _ in range(size):
        droplet.append(str(randint(0, 1)))
    return "".join(droplet)


import curses
import time

from utilitaries import pincel
from utilitaries import interacao
from utilitaries import cineasta

movements = {
    curses.KEY_UP: (-1, 0),
    curses.KEY_DOWN: (1, 0),
    curses.KEY_LEFT: (0, -1),
    curses.KEY_RIGHT: (0, 1)
}

grid = {
    'content': cineasta.open_txt('assets/images/grid.txt'), 
    'y_alignment': 'middle', 
    'x_alignment': 'middle', 
    'y_coord': 0, 
    'x_coord': 1
}

wall_template = {
    'content': cineasta.open_txt('assets/images/parede.txt'), 
    'y_alignment': 'absolute', 
    'x_alignment': 'absolute'
}

initial_map = [
    [None, 'wall', 'wall'],
    ['wall', 'wall', 'wall'],
    ['wall', None, 'player']
]

player = {}

# The barriers' coordinates follows this logic:
#    a b
# A _|_|_
# B _|_|_
#    | |
# Examples
# a1 means the first barrier of line 'a'.
# b2 means the second barrier of line 'b'.
# A3 means the third barrier of line 'A'.
barriers_codes = ['b3', 'a1']
cell_height = 14
cell_width = 28

def start_fliperama(gs, f, c):
    global game_specs, game_coords, frames, stdscr
    game_specs = gs
    game_coords = c
    frames = f
    stdscr = gs["stdscr"]

# BARRIERS
def has_barrier_between_cells(cell1, cell2):
    cell1_y, cell1_x = cell1
    cell2_y, cell2_x = cell2

    if cell1_y == cell2_y and abs(cell1_x-cell2_x) == 1:
        barrier_disposition = 'vertical'
    elif cell1_x == cell2_x and abs(cell1_y-cell2_y) == 1:
        barrier_disposition = 'horizontal'
    else:
        return False

    if barrier_disposition == 'vertical':
        if min(cell1_x, cell2_x) == 1:
            line = 'a'
        else:
            line = 'b'
        num = str(cell1_y) # could be cell2_y too -- they're equal
    elif barrier_disposition == 'horizontal':
        if min(cell1_y, cell2_y) == 1:
            line = 'A'
        else:
            line = 'B'
        num = str(cell1_x) # could be cell2_x too -- they're equal

    barrier_code = line + num
    return barrier_code in barriers_codes

def generate_barrier(barrier_code):
    barrier_char = '█'

    b = barrier_code
    y, x = grid_coords_to_absolute_coords((1, 1), x_offset=-2, y_offset=-1)

    line = b[0]
    line_i = int(b[1])
    if line == 'a' or line == 'b':
        barrier_content = []
        for _ in range(cell_height):
            barrier_content.append([2 * barrier_char])

        y += (line_i - 1) * (cell_height-1)
        if line == 'a':
            x += (cell_width-2)
        elif line == 'b':
            x += 2 * (cell_width-2)

    if line == 'A' or line == 'B':
        barrier_content = [barrier_char * cell_width]
        x += (line_i - 1) * (cell_width-2)
        if line == 'A':
            y += cell_height-1
        elif line == 'B':
            y += 2 * (cell_height-1)

    barrier = {
        'content': barrier_content, 
        'y_alignment': 'absolute', 
        'x_alignment': 'absolute', 
        'y_coord': y, 
        'x_coord': x
    }

    return barrier

def draw_barriers(barriers):
    for b in barriers:
        pincel.draw(b)

# GRID MAP
def grid_coords_to_absolute_coords(grid_coords, y_offset=0, x_offset=0):
    y, x = grid_coords
    
    absolute_y = grid_tip[0] + (y-1) * (cell_height-1) + y_offset
    absolute_x = grid_tip[1] + (x-1) * (cell_width-2) + x_offset

    return (absolute_y, absolute_x)

def generate_grid_map(initial_map, player):
    drawing_id_to_pos = {}
    pos_to_drawing = {}

    grid_map = {
        'counter': 0,
        'drawing_id_to_pos': drawing_id_to_pos,
        'pos_to_drawing': pos_to_drawing
    }

    for line in range(len(initial_map)):
        for column in range(len(initial_map[0])):
            element = initial_map[line][column]
            if element is None:
                continue
            elif element == 'player':
                drawing = player
            elif element == 'wall':
                drawing = wall_template.copy()
            else:
                raise ValueError("The arcade map contains invalid values")

            grid_y = line+1
            grid_x = column+1

            drawing.update({
                'id': grid_map['counter']
            })
            grid_map['counter'] += 1

            drawing_id_to_pos[drawing['id']] = (grid_y, grid_x)
            pos_to_drawing[(grid_y, grid_x)] = drawing
    
    return grid_map

def add_to_grid(grid_map, y_grid, x_grid, drawing):
    grid_map['pos_to_drawing'][(y_grid, x_grid)] = drawing
    grid_map['drawing_id_to_pos'][drawing['id']] = (y_grid, x_grid)

def remove_from_grid(grid_map, y_grid, x_grid):
    drawing = grid_map['pos_to_drawing'].pop((y_grid, x_grid), None)
    if drawing:
        grid_map['drawing_id_to_pos'].pop(drawing['id'], None)

# DRAWINGS
def get_all_drawings(grid_map):
    return list(grid_map['pos_to_drawing'].values())

def draw_grid_drawings(grid_map):
    drawings = get_all_drawings(grid_map)
    for drawing in drawings:
        grid_coords = grid_map['drawing_id_to_pos'][drawing['id']]
        set_drawing_real_coords(grid_coords, drawing)
        pincel.draw(drawing)

def set_drawing_real_coords(grid_coords, drawing):
    y, x = grid_coords_to_absolute_coords(grid_coords)
    drawing.update({
        'y_coord': y,
        'x_coord': x,
        'y_alignment': 'absolute',
        'x_alignment': 'absolute'
    })

# CURSOR
def draw_cursor(cursor):
    y_grid, x_grid = cursor['y_grid'], cursor['x_grid']
    y, x = grid_coords_to_absolute_coords((y_grid, x_grid), y_offset=-1, x_offset=-2)
    cursor.update({
        'y_coord': y,
        'x_coord': x
    })
    pincel.draw(cursor, text_color=cursor['text_color'])

def cursor_blink(cursor, barriers):
    cursor['text_color'] = 'red'
    draw_cursor(cursor)
    draw_barriers(barriers)
    stdscr.refresh()

    time.sleep(0.3)

    cursor['text_color'] = 'blue'
    draw_cursor(cursor)
    draw_barriers(barriers)
    stdscr.refresh()

def catch_drawing(grid_map, cursor):
    cursor_pos = (cursor['y_grid'], cursor['x_grid'])
    drawing_caught = grid_map['pos_to_drawing'].get(cursor_pos)

    if drawing_caught is None:
        return False

    cursor.update({
        'held_drawing': drawing_caught,
        'text_color': 'red'
    })

    draw_cursor(cursor)
    remove_from_grid(grid_map, cursor_pos[0], cursor_pos[1])
    set_drawing_real_coords(cursor_pos, drawing_caught)
    pincel.erase(drawing_caught)
    stdscr.refresh()

    return True

def drop_drawing(grid_map, cursor):
    cursor_pos = (cursor['y_grid'], cursor['x_grid'])
    drawing_dropped = cursor['held_drawing']
    underneath = grid_map['pos_to_drawing'].get(cursor_pos)

    if underneath is not None:
        return False
    
    cursor.update({
        'held_drawing': None,
        'text_color': 'blue'
    })

    add_to_grid(grid_map, cursor_pos[0], cursor_pos[1], drawing_dropped)
    set_drawing_real_coords(cursor_pos, drawing_dropped)
    pincel.draw(drawing_dropped)

    return True

def move_cursor_freely(cursor, key):
    y, x = cursor['y_grid'], cursor['x_grid']

    if key in movements:
        dy, dx = movements[key]
        new_y, new_x = y + dy, x + dx

        if 1 <= new_y <= 3 and 1 <= new_x <= 3:
            cursor.update({
                'y_grid': new_y,
                'x_grid': new_x
            })

def move_cursor_restricted(cursor, grid_map, key):
    begin_pos = (y, x) = cursor['y_grid'], cursor['x_grid']

    pos_to_drawing = grid_map['pos_to_drawing']
    
    if key in movements:
        dy, dx = movements[key]
        new_y, new_x = y + dy, x + dx
        desired_pos = (new_y, new_x)

        within_grid = (1 <= new_y <= 3) and (1 <= new_x <= 3)
        destination_empty = pos_to_drawing.get(desired_pos, None) is None
        if within_grid and destination_empty and not has_barrier_between_cells(begin_pos, desired_pos):
            cursor.update({
                'y_grid': new_y,
                'x_grid': new_x
            })

# GAME LOOP
def game_loop(got_glasses):
    global grid_tip

    player.update({
        'content': cineasta.open_txt('assets/images/troll.txt') if got_glasses else cineasta.open_txt('assets/images/oculos.txt'),
        'y_alignment': 'absolute',
        'x_alignment': 'absolute'
    })
    
    cursor = {
        'content': cineasta.open_txt('assets/images/cursor.txt'), 
        'y_alignment': 'absolute', 
        'x_alignment': 'absolute',
        'y_grid': 3,
        'x_grid': 3,
        'held_drawing': None,
        'text_color': 'blue'
    }
    
    grid_tip = pincel.calculate_drawing_real_coords(grid)
    grid_tip = (grid_tip[0] + 13, grid_tip[1] + 77)
    grid_map = generate_grid_map(initial_map, player)

    barriers = []
    for b in barriers_codes:
        barrier = generate_barrier(b)
        barriers.append(barrier)

    won_game = False
    elapsed_time = None
    initial_time = time.time()

    while True:
        pincel.draw(grid)

        draw_cursor(cursor)
        draw_grid_drawings(grid_map)
        draw_barriers(barriers)

        # CHECKS WHETHER USER WON THE GAME
        if grid_map['drawing_id_to_pos'].get(player['id'], None) == (1, 1):
            won_game = True

            final_time = time.time()
            elapsed_time = final_time - initial_time

            stdscr.refresh()
            time.sleep(1.5)
            break

        curses.flushinp()
        key = stdscr.getch()

        # IF PRESSED ESC, LEAVES THE GAME 
        if interacao.pressed_esc(key):
            break

        # CURSOR CATCHES DRAWING UNDERNEATH
        if interacao.pressed_enter(key) and cursor['held_drawing'] is None:
            if not catch_drawing(grid_map, cursor):
                cursor_blink(cursor, barriers)
            continue
        
        # CURSOR DROPS DRAWING UNDERNEATH
        if interacao.pressed_enter(key) and cursor['held_drawing'] is not None:
            if not drop_drawing(grid_map, cursor):
                raise RuntimeError("The cursor should've never reached an occupied cell")
            continue

        #O MOVE CURSOR
        if cursor['held_drawing'] is None:
            move_cursor_freely(cursor, key)
        else:
            move_cursor_restricted(cursor, grid_map, key)

        stdscr.refresh()
    
    return won_game, elapsed_time
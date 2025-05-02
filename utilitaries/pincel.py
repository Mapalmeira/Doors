import curses
import copy
import re

from utilitaries import cineasta

TRANSPERENCY_CHAR = '€'
DELETION_CHAR = 'Œ'

COLOR_MAP = {
    "white": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "black": 7
}

REVERSE_COLOR_MAP = {
    0: curses.COLOR_WHITE,
    1: curses.COLOR_RED,
    2: curses.COLOR_GREEN,
    3: curses.COLOR_YELLOW,
    4: curses.COLOR_BLUE,
    5: curses.COLOR_MAGENTA,
    6: curses.COLOR_CYAN,
    7: curses.COLOR_BLACK
}

def start_pincel(gs):
    global stdscr, game_specs
    game_specs = gs
    stdscr = gs.get("stdscr")

    #Initiates text-background color pairs identified from 1 to 64
    curses.start_color()
    for text_color_id in range(0, 8):
        text_color = REVERSE_COLOR_MAP[text_color_id]
        for background_color_id in range(0, 8):
            background_color = REVERSE_COLOR_MAP[background_color_id]
            color_pair = calculate_color_pair_id(text_color_id, background_color_id)
            curses.init_pair(color_pair, text_color, background_color)

def calculate_color_pair_id(text_color_id, background_color_id):
    return (text_color_id) + (background_color_id * 8) + 1

def calculate_drawing_real_coords(drawing):
    def align(virtual_coord, align_type, range_min, range_max, middle, size):
        if align_type == 'middle':
            return middle - size // 2 + virtual_coord + range_min
        elif align_type in ('left', 'upper', 'custom'):
            return range_min + virtual_coord
        elif align_type in ('right', 'bottom'):
            return range_max + virtual_coord - size + 1
        elif align_type == 'absolute':
            return virtual_coord
        else:
            raise ValueError("Alignment type not supported.") 
        
    virtual_middle = game_specs['virtual_middle']
    x_range = game_specs['x_range']
    y_range = game_specs['y_range']

    drawing_width = len(drawing['content'][0])
    drawing_height = len(drawing['content'])

    x = align(
        virtual_coord=drawing['x_coord'], 
        align_type=drawing['x_alignment'], 
        range_min=x_range[0], range_max=x_range[1], 
        middle=virtual_middle[1], 
        size=drawing_width
    )

    y = align(
        virtual_coord=drawing['y_coord'], 
        align_type=drawing['y_alignment'], 
        range_min=y_range[0], range_max=y_range[1], 
        middle=virtual_middle[0], 
        size=drawing_height
    )

    return y, x

def generate_box_content(box):
    content = []
    for y in range(box['height']):
        line = ''
        if y == 0 or y == box['height']-1:
            line = '░' * box['width']
        else:
            line = '░' + ' ' * (box['width']-2) + '░'
        content.append(line)

    box.update({
        'content': content,
        'lines_available': box['height'] - 2*box['vertical_margin']
    })

def in_bounds(y, x):
    max_x = game_specs['max_x']
    max_y = game_specs['max_y']
    return (0 <= x < max_x and 0 <= y < max_y) and not (x == max_x - 1 and y == max_y - 1)

def draw(drawing, char_limit=float('+inf'), flashlight=False, text_color='white', background_color='black'):
    if drawing is None: 
        return
    if not flashlight and "dark_object" in drawing and drawing['dark_object'] == True:
        return
    if text_color not in COLOR_MAP or background_color not in COLOR_MAP:
        raise ValueError("Color not supported.")

    y_coord, x_coord = calculate_drawing_real_coords(drawing)
    default_color_id = calculate_color_pair_id(COLOR_MAP[text_color], COLOR_MAP[background_color])

    # Drawing
    char_count = 0
    for i, line in enumerate(drawing['content']):
        for j, char in enumerate(line):
            y = y_coord + i
            x = x_coord + j

            if char_count >= char_limit: 
                break
            if not in_bounds(y, x):
                continue

            color_id = drawing['color_map'][i][j] if 'color_map' in drawing else default_color_id
            stdscr.attron(curses.color_pair(color_id))
            
            if char == DELETION_CHAR:
                stdscr.addstr(y, x, ' ')
                char_count += 1
            elif char != TRANSPERENCY_CHAR:
                stdscr.addstr(y, x, char)
                char_count += 1

            stdscr.attroff(curses.color_pair(color_id))

    if flashlight:
        flashlight_mask = {
            'content': cineasta.open_txt('assets/images/mascara_lanterna.txt'), 
            'y_alignment':'custom', 
            'x_alignment':'custom', 
            'y_coord':0, 
            'x_coord':0
        }
        flashlight_area = mask_drawing(drawing, flashlight_mask)
        lighten(flashlight_area)
        draw(flashlight_area, flashlight=False)

def erase(drawing, flashlight=False):
    if drawing is None: return

    blank_drawing = copy.deepcopy(drawing)
    blank_drawing['content'] = [
        [DELETION_CHAR if char != TRANSPERENCY_CHAR else char for char in line]
        for line in drawing['content']
    ]
    draw(blank_drawing, flashlight=flashlight)

def generate_color_map(drawing, reserved_colorful_words, text_color='white', background_color='black'):
    if not reserved_colorful_words:
        return
    
    default_color_id = calculate_color_pair_id(COLOR_MAP[text_color], COLOR_MAP[background_color])
    color_map = []

    # Generates regex with reserved words
    pattern = '|'.join(re.escape(word) for word in reserved_colorful_words)
    regex = re.compile(pattern)

    for line in drawing['content']:
        line_color = [default_color_id] * len(line)

        for match in regex.finditer(line):
            word = match.group()
            start, end = match.start(), match.end()

            text_color_str, background_color_str = reserved_colorful_words[word]
            color_id = calculate_color_pair_id(COLOR_MAP[text_color_str], COLOR_MAP[background_color_str])

            for i in range(start, end):
                line_color[i] = color_id

        color_map.append(line_color)

    drawing['color_map'] = color_map

def mask_drawing(drawing, mask):
    def get_mask_char(i, j):
        if 0 <= i < len(mask['content']):
            line = mask['content'][i]
            if 0 <= j < len(line):
                return line[j]
        return None

    drawing_y_coord, drawing_coord_x = calculate_drawing_real_coords(drawing)
    mask_y_coord, mask_coord_x = calculate_drawing_real_coords(mask)
    
    mask_y_offset = drawing_y_coord - mask_y_coord
    mask_horizontal_offset = drawing_coord_x - mask_coord_x
    
    new_content = []
    for i, line in enumerate(drawing['content']):
        new_line = []
        for j, char in enumerate(line):
            mask_i = mask_y_offset + i
            mask_j = mask_horizontal_offset + j
            mask_char = get_mask_char(mask_i, mask_j)

            if mask_char == DELETION_CHAR:
                new_char = TRANSPERENCY_CHAR
            elif mask_char == TRANSPERENCY_CHAR or mask_char is None:
                new_char = char
            else:
                raise ValueError("Invalid mask character.")
            
            new_line.append(new_char)
        new_content.append("".join(new_line))

    new_drawing = {
        'content': new_content,
        'y_alignment':'absolute', 
        'x_alignment':'absolute',
        'y_coord': drawing_y_coord,
        'x_coord': drawing_coord_x
    }

    return new_drawing

def lighten(drawing):
    light_gradient = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@']
    light_map = {c: light_gradient[i + 1] for i, c in enumerate(light_gradient[:-1])}

    for i, line in enumerate(drawing['content']):
        new_chars = []
        for char in line:
            if char in light_map:
                new_chars.append(light_map[char])
            elif char == DELETION_CHAR:
                new_chars.append(light_gradient[1])
            else:
                new_chars.append(char)
        drawing['content'][i] = ''.join(new_chars)

def draw_border():
    max_y = game_specs['max_y']
    max_x = game_specs['max_x']
    y_range = game_specs['y_range']
    x_range = game_specs['x_range']

    border_char = '░'
    border_content = []

    height = y_range[1] - y_range[0] + 1
    width = x_range[1] - x_range[0] + 1

    has_side_border = max_x >= width + 2
    has_top_bottom_border = max_y >= height + 2
    coord_x = x_range[0] - 1 if has_side_border else x_range[0]
    coord_y = y_range[0] - 1 if has_top_bottom_border else y_range[0]

    # right and left borders
    for _ in range(height):
        line = [TRANSPERENCY_CHAR] * width
        if has_side_border:
            line.insert(0, border_char)  # left
            line.append(border_char)     # right
        border_content.append(''.join(line))

    # upper and bottom border
    if has_top_bottom_border:
        top_line = [border_char] * (width + 2 if has_side_border else width)
        border_content.insert(0, ''.join(top_line))
        border_content.append(''.join(top_line))

    border = {
        'content': border_content,
        'y_alignment': 'absolute',
        'x_alignment': 'absolute',
        'y_coord': coord_y,
        'x_coord': coord_x,
    }

    draw(border)
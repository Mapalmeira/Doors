import curses

from . import pincel
from . import interacao
from . import animador

def start_orador(gs, f, c):
    global game_specs, game_coords, frames, stdscr
    game_specs = gs
    game_coords = c
    frames = f
    stdscr = gs["stdscr"]

def format_text_on_box(box, text, y_offset=0, first_line_horizontal_offset=0, every_line_horizontal_offset=0, colorful_words={}):
    y_box, x_box = pincel.calculate_drawing_real_coords(box)

    horizontal_margin = box['horizontal_margin']
    lines_available = box['lines_available']-y_offset
    horizontal_space = len(box['content'][0]) - 2 * horizontal_margin - 2 - every_line_horizontal_offset
    
    aligned_text = '€'*first_line_horizontal_offset + text
    x_text = x_box + horizontal_margin + every_line_horizontal_offset
    y_text = calculate_line_y_coord_on_box(box, y_offset)
    
    lines = slice_text_to_lines(aligned_text, horizontal_space, lines_available)

    formatted = {
        'content': lines,
        'y_alignment': 'absolute',
        'x_alignment': 'absolute',
        'y_coord': y_text,
        'x_coord': x_text,
        'y_offset': y_offset,
        'uncut_content': text,
    }

    pincel.generate_color_map(formatted, colorful_words)
    
    return formatted

def calculate_line_y_coord_on_box(box, y_offset):
    y_box, x_box = pincel.calculate_drawing_real_coords(box)
    return y_box + box['vertical_margin'] + y_offset

def slice_text_to_lines(text, space, lines_available):
    if text == "":
        return [""]
    total_lines = (len(text) + space - 1) // space
    if total_lines > lines_available:
        raise ValueError("The text couldn't fit in the specified box.")

    lines = [text[i * space:(i + 1) * space] for i in range(total_lines)]
    return lines

def start_dialogue(box, phrases, t, interactive, colorful_words={}):
    finished = False
    current_line = 0
    current_phrase = 0

    while True:
        stdscr.refresh()

        phrase = phrases[current_phrase]
        formatted_phrase = format_text_on_box(box, text=phrase, y_offset=current_line, colorful_words=colorful_words)
        current_line += len(formatted_phrase['content'])
        current_phrase += 1
  
        interrupted = not animador.animate_drawing(formatted_phrase, t, interactive)

        # exit condition
        if interrupted:
            break
        elif current_phrase >= len(phrases):
            if interactive:
                stdscr.getch()
            finished = True
            break

    return finished

def answer_prompt(box, prompt, aligned_to_prompt_margin=False):
    curses.flushinp()
    input_text = []
    surpassed_box_char_limit = False
    on_limit = False
    interrupted = False
    should_leave = False
    formatted_input = None
    while not should_leave:
        key = stdscr.getch()
        if (interacao.pressed_valid_textual_input(key)) and not on_limit:
            input_text.append(chr(key))
        elif (interacao.pressed_backspace(key)) and len(input_text) > 0:
            input_text.pop()
            pincel.erase(formatted_input)
        elif interacao.pressed_enter(key):
            should_leave = True
        elif interacao.pressed_exit_char(key):
            interrupted = True
            break

        try:
            formatted_input = format_text_on_box(
                box=box, 
                text="".join(input_text),
                y_offset=prompt['y_offset'],
                first_line_horizontal_offset=len(prompt['content'][-1]) if not aligned_to_prompt_margin else 0, 
                every_line_horizontal_offset=len(prompt['content'][-1]) if aligned_to_prompt_margin else 0
            )
            if surpassed_box_char_limit:
                on_limit = True
                surpassed_box_char_limit = False
            else:
                on_limit = False
        except ValueError:
            surpassed_box_char_limit = True
            input_text.pop()
            
        pincel.draw(formatted_input)
        stdscr.refresh()

    return formatted_input if not interrupted else None
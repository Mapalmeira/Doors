import time
import curses

from utilitaries import pincel
from utilitaries import interacao
from utilitaries import orador
from utilitaries import animador
from utilitaries import cineasta
from assets import falas
from doors import fliperama

def start_portas(gs, f, c):
    global game_specs, game_coords, frames, stdscr
    game_specs = gs
    game_coords = c
    frames = f
    stdscr = gs["stdscr"]

# MAIN DOOR
def p1t_dialogue():
    username = game_specs['username']
    dialogue_phrases = falas.assets_p1test(username)

    box = {
        'height': 20,
        'width': 160,
        'y_alignment': 'middle',
        'x_alignment': 'middle',
        'y_coord': 15,
        'x_coord': 0,
        'vertical_margin': 5,
        'horizontal_margin': 10
    }
    pincel.generate_box_content(box)
    pincel.draw(box)
    colorful_words = {'P1-TEST': ('red', 'black'), '<P1-TEST>': ('red', 'black'), f'<{username}>': ('cyan', 'black')}

    finished_dialogue = orador.start_dialogue(box, dialogue_phrases, t=0.05, interactive=True, colorful_words=colorful_words)
    return finished_dialogue

def p1t_answer_box(flashlight):
    box = {
        'height': 14,
        'width': 80,
        'y_alignment': 'middle',
        'x_alignment': 'middle',
        'y_coord': 15,
        'x_coord': 0,
        'vertical_margin': 5,
        'horizontal_margin': 10
    }

    pincel.generate_box_content(box)
    y_box, x_box = pincel.calculate_drawing_real_coords(box)

    p1t_question = {
        'content': ['QUAL É A MAIOR FRAQUEZA DO P1-TEST?'], 
        'y_alignment': 'absolute', 
        'x_alignment': 'middle', 
        'y_coord': y_box+4,
        'x_coord': 0
    }


    p1t_prompt = orador.format_text_on_box(box, 'RESPOSTA: ', y_offset=2)

    pincel.draw(box)
    pincel.draw(p1t_question)
    pincel.draw(p1t_prompt)

    answer = orador.answer_prompt(box, p1t_prompt, aligned_to_prompt_margin=True)
    
    if answer is None:
        pincel.draw(frames[tuple(game_coords)], flashlight=flashlight)
        stdscr.refresh()
        time.sleep(0.1)
        return False

    pincel.erase(answer)
    if answer['uncut_content'].strip() != 'OR4CUL0':
        incorrect_answer_return = orador.format_text_on_box(
            box=box, 
            text='❌', 
            y_offset=2, 
            first_line_horizontal_offset=len(p1t_prompt['uncut_content'])
        )
        pincel.draw(incorrect_answer_return)
        stdscr.refresh()
        _ = stdscr.getch()
        return False
    else:
        stdscr.refresh()
        time.sleep(0.5)

        correct_answer_return = orador.format_text_on_box(
            box=box, 
            text='...Você acertou!', 
            y_offset=2, 
            first_line_horizontal_offset=len(p1t_prompt['uncut_content'])
        )
        animador.animate_drawing(correct_answer_return, 0.2)
        time.sleep(1)
        return True

# MOON DOOR
def moon_door_loop(events, counters):
    qr_code = {
        'content': cineasta.open_txt('assets/images/qr.txt'), 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord': 0,
        'dark_object': True
    }
    trollface = {
        'content': cineasta.open_txt('assets/images/troll.txt'), 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord': 0,
        'dark_object': True
    }

    door_coord = [1, -2]
    
    animador.open_door(events, counters, door_coord, object_behind=qr_code)
    
    counters['flashlight_on_moon_usages'] = 0
    door_stay = True
    while door_stay:
        if counters['flashlight_on_moon_usages'] == 8:
            object_behind = trollface
            events['moon_trollface'] = True
        else:
            object_behind = qr_code
        
        curses.flushinp()
        key = stdscr.getch()
        
        door_stay = interacao.door_stay_loop_iteration(events, counters, door_coord, key, object_behind)      

# SUN DOOR
def boot_sunOS(monitor_box):
    sun_logo = {
        'content': cineasta.open_txt('assets/images/sol.txt'), 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord': 1
    }
    sun_os_text = {
        'content': ['Booting SunOs'], 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord':17, 
        'x_coord':-1
    }
    y_text, x_text = pincel.calculate_drawing_real_coords(sun_os_text)
    ellipsis = {
        'content': ['...'], 
        'y_alignment': 'middle', 
        'x_alignment': 'absolute', 
        'y_coord':17, 
        'x_coord':x_text+len(sun_os_text['content'][0])
    }
    sun_boot_text, _, _ = falas.assets_sun(game_specs['username'])

    pincel.draw(sun_logo)
    pincel.draw(sun_os_text)
    stdscr.refresh()

    for _ in range(3):
        animador.animate_drawing(ellipsis, t=0.3)
        pincel.erase(ellipsis)
    
    pincel.erase(sun_os_text)
    pincel.erase(sun_logo)
    stdscr.refresh()

    orador.start_dialogue(
        box=monitor_box,
        phrases=sun_boot_text,
        t=0.05,
        interactive=False
    )

def sun_door_loop(events, counters):
    if not events['has_flashlight']:
        flashlight_drawing = {
            'content': cineasta.open_txt('assets/images/lanterna.txt'), 
            'y_alignment': 'middle', 
            'x_alignment': 'middle', 
            'y_coord': 3, 
            'x_coord': 0}
    else:
        flashlight_drawing = None

    door_coord = [-1, -2]

    animador.open_door(
        events=events,
        counters=counters,
        game_coord=door_coord, 
        object_behind=flashlight_drawing,
    )

    door_stay = True
    while door_stay:
        curses.flushinp()
        key = stdscr.getch()
        
        if not events['has_flashlight']:
            if interacao.pressed_enter(key):
                events['has_flashlight'] = True
                pincel.erase(flashlight_drawing)
                flashlight_drawing = None
                stdscr.refresh()

        door_stay = interacao.door_stay_loop_iteration(
            events=events, 
            counters=counters,
            key=key,
            door_coord=door_coord, 
            object_behind=flashlight_drawing
        )

def terminal_sunOS_loop(events):
    username = game_specs['username']
    _, sun_prompt_text, binary_code_text = falas.assets_sun(username)

    monitor_box = {
        'width': 132,
        'height': 47,
        'y_alignment': 'middle',
        'x_alignment': 'middle',
        'y_coord': 0,
        'x_coord': 1,
        'vertical_margin': 7,
        'horizontal_margin': 14
    }
    colorful_words = {f'{username}@sunOS': ('green', 'black'), '~': ('blue', 'black')}
    unlocked_message = 'Master key detected. Starting door unlocking sequence'
    exit_text = 'Done! Press DOWN arrow key or ESC then ENTER to open door.'
    
    binary_code = {
        'content': binary_code_text, 
        'y_alignment': 'absolute', 
        'x_alignment': 'middle', 
        'x_coord': -len(binary_code_text[1])//2+2
    }
    troll = {
        'content': cineasta.open_txt('assets/images/troll.txt'), 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord': 0
    }

    door_coord = [-1, -2]
    
    pincel.generate_box_content(monitor_box)
    boot_sunOS(monitor_box=monitor_box)
    stdscr.refresh()

    line_counter = 11

    def line_counter_overflow(new_lines=0, reset=False):
        nonlocal line_counter
        line_counter += new_lines
        if line_counter >= monitor_box['lines_available'] or reset:
            line_counter = 0
            pincel.draw(frames[tuple(door_coord)])
            stdscr.refresh()
    
    def deliver_enigma():
        y_coord = orador.calculate_line_y_coord_on_box(monitor_box, line_counter)
        binary_code['y_coord'] = y_coord
        pincel.draw(binary_code)
        time.sleep(0.1)
        line_counter_overflow(len(binary_code['content']))
    
    def deliver_easter_egg():
        time.sleep(0.1)
        line_counter_overflow(reset=True)
        pincel.draw(troll)
        stdscr.refresh()
        time.sleep(1)
        line_counter_overflow(reset=True)
        events['sun_trollface'] = True

    def unlocking_sequence():
        time.sleep(0.1)
        # PREVIOUSLY ALLOCATE NEEDED LINES
        line_counter_overflow(3)

        message = orador.format_text_on_box(
            box=monitor_box, 
            text=unlocked_message, 
            y_offset=line_counter-3)
        exit_message = orador.format_text_on_box(
            box=monitor_box, 
            text=exit_text, 
            y_offset=line_counter-1
        )
        y_message, x_message = pincel.calculate_drawing_real_coords(message)
        ellipsis = {
            'content': ['...'], 
            'y_alignment': 'absolute', 
            'x_alignment': 'absolute', 
            'y_coord':y_message, 
            'x_coord':x_message+len(unlocked_message)
        }

        events['sun_door_unlocked'] = True
        pincel.draw(message)
        stdscr.refresh()

        for _ in range(3):
            animador.animate_drawing(ellipsis, t=0.3)
            pincel.erase(ellipsis)

        pincel.draw(exit_message)
        stdscr.refresh()

    while True:
        sun_prompt = orador.format_text_on_box(
            box=monitor_box, 
            text=sun_prompt_text,
            y_offset=line_counter,
            colorful_words=colorful_words
        )
        pincel.draw(sun_prompt)

        # GET ANSWER FROM USER
        answer = orador.answer_prompt(box=monitor_box, prompt=sun_prompt)
        if not answer:
            break
    
        line_counter_overflow(len(answer['content']))

        answer_text = answer['uncut_content'].strip()
        if answer_text == 'enigma':
            deliver_enigma()
        elif answer_text == 'luz':
            unlocking_sequence()
        elif answer_text == 'trollface':
            deliver_easter_egg()

# EYE DOOR
def finished_dalton_dialogue(phrases, height=20, width=160, y_offset=0, interactive=True):
    box = {
        'width': width,
        'height': height,
        'y_alignment': 'middle',
        'x_alignment': 'middle',
        'y_coord': 15+y_offset,
        'x_coord': 0,
        'vertical_margin': 5,
        'horizontal_margin': 10
    }
    colorful_words = {
        '<DALTON>': ('green', 'black'), 
        f'<{game_specs['username']}>': ('cyan', 'black'), 
        'OR4CUL0': ('red', 'black')
    }
    
    pincel.generate_box_content(box)
    pincel.draw(box)
    
    dialogue_finished = orador.start_dialogue(
        box=box,
        phrases=phrases,
        t=0.05,
        interactive=interactive,
        colorful_words=colorful_words
    )
    
    stdscr.refresh()

    return dialogue_finished

def answer_dalton():
    box = {
        'width': 80,
        'height': 15,
        'y_alignment': 'middle',
        'x_alignment': 'middle',
        'y_coord': 15,
        'x_coord': 0,
        'vertical_margin': 5,
        'horizontal_margin': 10
    }
    pincel.generate_box_content(box)

    prompt_text = 'RESPOSTA: '
    prompt = orador.format_text_on_box(box=box, text=prompt_text, y_offset=2)
    incorrect_output = orador.format_text_on_box(
        box=box, 
        text='❌', 
        first_line_horizontal_offset=len(prompt['uncut_content']),
        y_offset=2,
    )

    y_box, x_box = pincel.calculate_drawing_real_coords(box)
    final_question = {
        'content': ['QUAL É A PALAVRA SECRETA DE DALTON'], 
        'y_alignment': 'absolute', 
        'x_alignment': 'middle', 
        'y_coord': y_box+4, 
        'x_coord': 0
    }

    pincel.draw(box)
    pincel.draw(final_question)
    pincel.draw(prompt)

    curses.flushinp()
    answer = orador.answer_prompt(
        box=box,
        prompt=prompt,
        aligned_to_prompt_margin=True
    )

    if not answer:
        return False

    pincel.erase(answer)
    stdscr.refresh()

    if answer['uncut_content'].strip().upper() == 'VIM':
        return True
    
    pincel.draw(incorrect_output)
    stdscr.refresh()
    stdscr.getch()
    return False
        
def eye_door_loop(events, counters):
    door_coord = [-1, -3]

    def load_dalton():
        path = 'assets/images/dalton_com_oculos.txt' if events['gave_dalton_glasses'] else 'assets/images/dalton_sem_oculos.txt'
        return {
            'content': cineasta.open_txt(path),
            'y_alignment': 'custom',
            'x_alignment': 'middle',
            'y_coord': 9,
            'x_coord': 0
        }

    # MAKES SURE THE DIALOGUE IS FINISHED. OTHERWISE, CLOSES DOOR AND RETURN FALSE
    def ensure_dialogue_or_close_door(dialogue, **kwargs):
        success = finished_dalton_dialogue(dialogue, **kwargs)
        if not success:
            animador.close_door(events=events, game_coord=door_coord, object_behind=dalton)
        return success
    
    # DELIVERS FIRST DALTON DIALOGUE
    def handle_first_dialogue():
        success = True
        
        if events['first_eye_dialogue']:
            return success

        success = finished_dalton_dialogue(dalton_dialogues[0], height=16)
        events['first_eye_dialogue'] = success

        return success

    # UNLOCKS OR OPEN DOOR IF ALREADY UNLOCKED
    def handle_unlocking():
        success = True

        if events['eye_door_unlocked']:
            animador.open_door(events=events, counters=counters, game_coord=door_coord, object_behind=dalton)
            return success
        
        # ANSWER DALTON SECRET WORD
        pincel.draw(frames[tuple(door_coord)], flashlight=events['flashlight_on'])
        if not answer_dalton():
            success = False

        # OPENS DOOR
        if success:
            animador.open_door(events=events, counters=counters, game_coord=door_coord, object_behind=dalton)
            success = ensure_dialogue_or_close_door(
                ['<DALTON> Bixo esperto.'], 
                height=11, 
                width=80, 
                y_offset=3, 
                interactive=False
            )

        # UNLOCK DOOR COMPLETELY
        if success:
            events['eye_door_unlocked'] = True
            curses.flushinp()
            stdscr.getch()

        return success

    # DELIVERS GLASSES TO DALTON AFTER HIS SECOND DIALOGUE, IF NOT ALREADY
    def handle_glasses_delivery():
        success = True

        if not events['gave_dalton_glasses']:
            success = ensure_dialogue_or_close_door(dalton_dialogues[1], height=12, y_offset=3)
            if success and events['got_glasses']:
                events['gave_dalton_glasses'] = True

        return success

    # DALTON FINAL DIALOGUE
    def handle_final_dialogue():
        success = True

        if events['gave_dalton_glasses']:
            dalton_update()
            success = ensure_dialogue_or_close_door(dalton_dialogues[2], height=13, y_offset=3)
        
        return success

    # UPDATE DALTON DRAWING CONTENT
    def dalton_update():
        nonlocal dalton
        dalton = load_dalton()

    dalton_dialogues = falas.assets_eye(game_specs['username'])
    dalton = load_dalton()
    stay_loop = True
    
    for step in (handle_first_dialogue, handle_unlocking, handle_glasses_delivery, handle_final_dialogue):
        if not step():
            stay_loop = False
            break

    dalton_update()
    while stay_loop:
        pincel.draw(frames[tuple(door_coord)], flashlight=events['flashlight_on'])
        pincel.draw(dalton, flashlight=events['flashlight_on'])
        stdscr.refresh()

        curses.flushinp()
        key = stdscr.getch()
        if not interacao.door_stay_loop_iteration(
            events=events,
            counters=counters,
            key=key,
            door_coord=door_coord,
            object_behind=dalton
        ):
            break

# ARCADE DOOR
def loading_arcade(boot, t=0):
    arcade_logo = {
        'content': cineasta.open_txt('assets/images/arcade_logo.txt'), 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord': 0
    }
    
    ellipsis = {
        'content': ['...'], 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord':17, 
        'x_coord':0
    }

    pincel.draw(arcade_logo)
    stdscr.refresh()
    time.sleep(t)

    if boot:
        for _ in range(3):
            animador.animate_drawing(ellipsis, t=0.2)
            pincel.erase(ellipsis)

    pincel.erase(arcade_logo)
    stdscr.refresh()

def arcade_door_loop(events, counters):
    door_coord = [1, -3]
    events['flashlight_on'] = False
    events['can_tutorial_appear'] = False

    animador.open_door(events=events, counters=counters, game_coord=door_coord)
    door_opened = True

    def run_arcade_sequence():
        if events['got_glasses']:
            events['arcade_trollface'] = True

        cineasta.change_frame_state(frames[tuple(door_coord)], new_state='monitor')
        pincel.draw(frames[tuple(door_coord)])
        stdscr.refresh()

        time.sleep(0.33)
        loading_arcade(boot=True)
        time.sleep(0.66)

        won_game, time_elapsed = fliperama.game_loop(events['got_glasses'])

        display_result_screen(won_game)
        if won_game:
            handle_result_outcome(time_elapsed)
        leaving_arcade_screen()
        if won_game and not events['got_glasses']:
            deliver_glasses()

    def display_result_screen(won):
        result_path = 'assets/images/you_win.txt' if won else 'assets/images/game_over.txt'
        result_screen = {
            'content': cineasta.open_txt(result_path),
            'y_alignment': 'middle',
            'x_alignment': 'middle',
            'y_coord': 3,
            'x_coord': 1
        }
        pincel.draw(result_screen)
        stdscr.refresh()
        time.sleep(1.5)

    def handle_result_outcome(time_elapsed):
        if time_elapsed < counters['arcade_record_time']:
            counters['arcade_record_time'] = time_elapsed

        record_message = {
            'content': [f'Parabéns! Você terminou o jogo em {time_elapsed:.2f} seg.'],
            'y_alignment': 'middle',
            'x_alignment': 'middle',
            'y_coord': 20,
            'x_coord': 0
        }
        animador.animate_drawing(record_message, 0.1)

        if not events['got_glasses']:
            prize = {
                'content': ['Sua recompensa por tamanho feito será um óculos.'],
                'y_alignment': 'middle',
                'x_alignment': 'middle',
                'y_coord': 22,
                'x_coord': 0
            }
            colorful_words = {'óculos': ('green', 'black')}
            pincel.generate_color_map(prize, colorful_words)
            animador.animate_drawing(prize, 0.1)

        time.sleep(1.5)

    def leaving_arcade_screen():
        pincel.draw(frames[tuple(door_coord)])
        loading_arcade(boot=False, t=1)
        
        time.sleep(0.5)

        cineasta.change_frame_state(frames[tuple(door_coord)], new_state='aberto')
        pincel.draw(frames[tuple(door_coord)])
        stdscr.refresh()

    def deliver_glasses():
        glasses = {
            'content': cineasta.open_txt('assets/images/oculos_transparente.txt'),
            'y_alignment': 'custom',
            'x_alignment': 'middle',
            'y_coord': 52,
            'x_coord': 0
        }

        pincel.draw(glasses)
        stdscr.refresh()
        time.sleep(1)

        key = stdscr.getch()
        pincel.erase(glasses)
        stdscr.refresh()

        events['got_glasses'] = True
        time.sleep(0.33)

    while door_opened:
        curses.flushinp()
        key = stdscr.getch()

        if interacao.pressed_enter(key):
            run_arcade_sequence()

        stay_loop = interacao.door_stay_loop_iteration(
            events=events,
            counters=counters,
            door_coord=door_coord,
            key=key
        )
        if not stay_loop:
            break

        time.sleep(0.2)
    events['can_tutorial_appear'] = True

# FINAL SEQUENCE
def ending_sequence(events, counters):
    events['flashlight_on'] = False
    events['flashlight_tutorial_done'] = True
    check = {
        'content': cineasta.open_txt('assets/images/check.txt'), 
        'color_map': cineasta.open_txt('assets/images/checkcor.txt', color_map=True), 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 4, 
        'x_coord': 0
    }

    credits_drawing = {
        'content': [
            'Onde? Universidade Federal de Campina Grande',
            'Quando? Setembro de 2024',
            'Quem? Matheus Palmeira Leite Rocha'], 
        'x_alignment': 'middle', 
        'y_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord':50
    }
    
    final_thanks = {
        'content': ['Obrigado por jogar!'], 
        'x_alignment': 'middle', 
        'y_alignment': 'middle', 
        'y_coord': 5, 
        'x_coord':50
    }

    door_coord = [0, 4]

    pincel.draw(frames[tuple(door_coord)])
    stdscr.refresh()
    time.sleep(1)

    animador.open_door(events=events, counters=counters, game_coord=door_coord, t=0.6)
    time.sleep(1)
    
    pincel.draw(check)
    stdscr.refresh()
    time.sleep(2)

    animador.rainfall()
    time.sleep(1)

    animador.animate_drawing(credits_drawing, 0.1)
    time.sleep(1)

    pincel.draw(frames['fim'])
    stdscr.refresh()
    time.sleep(1)

    animador.animate_drawing(final_thanks, 0.1)
    time.sleep(2)

def final_statistics(events, counters):
    stdscr.clear()
    stdscr.refresh()
    time.sleep(1)

    title = {
        'content': ['Estatísticas do jogo'], 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': -10, 
        'x_coord': 0
    }
    pincel.draw(title)
    stdscr.refresh()
    time.sleep(1)

    easter_eggs = int(events['moon_trollface']) + int(events['sun_trollface']) + int(events['arcade_trollface'])
    statistics_content = [
        f'Você abriu portas {counters["doors_opened"]} vez(es).',
        f'Usou a lanterna {counters["flashlight_usages"]} vez(es).',
        f'Viu {easter_eggs} de 3 easter eggs pelo mapa.',
        f'E deu um total de {counters["steps_taken"]} passos.'
    ]
    if counters["arcade_record_time"] != float('+inf'):
        statistics_content.insert(-1, f'Teve um tempo minimo no fliperama de {counters["arcade_record_time"]:.3f} segundos.')
    for i in range(len(statistics_content)):
        line = {
            'content': [statistics_content[i]], 
            'y_alignment': 'middle', 
            'x_alignment': 'middle', 
            'y_coord': -7+i, 
            'x_coord': 0
        }
        animador.animate_drawing(line, 0.1)
    time.sleep(1)

    press_to_exit = {
        'content': ['[Pressione qualquer tecla para continuar]'], 
        'y_alignment': 'middle', 
        'x_alignment': 'middle', 
        'y_coord': 0, 
        'x_coord': 0
    }
    pincel.draw(press_to_exit)
    stdscr.refresh()

    curses.flushinp()
    stdscr.getch()
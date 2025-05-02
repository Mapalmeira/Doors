import time
import curses

from utilitaries import cineasta
from utilitaries import pincel
from utilitaries import orador
from utilitaries import animador
from utilitaries import interacao
from doors import portas
from doors import fliperama

def game_loop(game_specs):  
    game_coords = [0, 0]
    stdscr = game_specs['stdscr']
    frames = cineasta.load_frames(folder='assets/frames')

    pincel.start_pincel(game_specs)
    interacao.start_interacao(game_specs, frames, game_coords)  
    portas.start_portas(game_specs, frames, game_coords)
    orador.start_orador(game_specs, frames, game_coords)
    animador.start_animador(game_specs, frames, game_coords)
    fliperama.start_fliperama(game_specs, frames, game_coords)

    pincel.draw(frames[(0, 0)])
    pincel.draw_border()

    events = {
        'p1t_dialogue': False,
        'sun_door_unlocked': False,
        'has_flashlight': False,
        'flashlight_on': False,
        'flashlight_tutorial_done': False,
        'can_tutorial_appear': True,
        'knocked_arcade': False,
        'knocked_moon': False,
        'knocked_p1t': False,
        'knocked_eye': False,
        'arcade_trollface': False,
        'moon_trollface': False,
        'sun_trollface': False,
        'first_eye_dialogue': False,
        'gave_dalton_glasses': False,
        'eye_door_unlocked': False,
        'got_glasses': False
    }

    counters = {
        'steps_taken': 0,
        'flashlight_usages': 0,
        'flashlight_on_moon_usages': 0,
        'arcade_record_time': float('+inf'),
        'doors_opened': 0
    }

    while True:
        key = stdscr.getch()

        had_movement = interacao.move(key)
        if had_movement:
            counters['steps_taken'] += 1

        # FLASHLIGHT TOGGLE ON/OFF
        flashlight_interaction = interacao.toggle_flashlight(events, counters, key)

        # MAIN DOOR INTERACTION
        if game_coords == [0, 4] and interacao.pressed_enter(key):
            if not events['p1t_dialogue']:
                if not events['knocked_p1t']:
                    animador.knock_knock_door(flashlight=events['flashlight_on'])
                    events['knocked_p1t'] = True

                finished_dialogue = portas.p1t_dialogue()
                events['p1t_dialogue'] = finished_dialogue
            else:
                correct_answer = portas.p1t_answer_box(flashlight=events['flashlight_on'])
                if correct_answer:
                    portas.ending_sequence(events, counters)
                    portas.final_statistics(events, counters)
                    return

        # SUN DOOR INTERACTION
        if game_coords == [-1, -2] and interacao.pressed_enter(key):
            if not events['sun_door_unlocked']:
                cineasta.change_frame_state(frame=frames[tuple([-1, -2])], new_state="monitor")
                pincel.draw(frames[tuple([-1, -2])])

                portas.terminal_sunOS_loop(events)
                cineasta.change_frame_state(frame=frames[tuple([-1, -2])], new_state="0")

            else:
                portas.sun_door_loop(events, counters)
                had_movement = True

        # MOON DOOR INTERACTION
        if game_coords == [1, -2] and interacao.pressed_enter(key):
            if not events['knocked_moon']:
                animador.knock_knock_door(y_offset=7, flashlight=events['flashlight_on'])
                events['knocked_moon'] = True
            portas.moon_door_loop(events, counters)
            had_movement = True

        # EYE DOOR INTERACTION
        if game_coords == [-1, -3] and interacao.pressed_enter(key):
            if not events['knocked_eye']:
                animador.knock_knock_door(y_offset=7, flashlight=events['flashlight_on'])
                events['knocked_eye'] = True

            events['can_tutorial_appear'] = False
            portas.eye_door_loop(events, counters)
            events['can_tutorial_appear'] = True
            movement = True

        # ARCADE DOOR INTERACTION
        if game_coords == [1, -3] and interacao.pressed_enter(key):
            if not events['knocked_arcade']:
                animador.knock_knock_door(y_offset=7, flashlight=events['flashlight_on'])
                events['knocked_arcade'] = True

            portas.arcade_door_loop(events, counters)
            movement = True

        # DRAWS CURRENT FRAME
        pincel.draw(frames[tuple(game_coords)], flashlight=events['flashlight_on'])

        # FLASHLIGHT TUTORIAL BOX
        if flashlight_interaction:
            events['flashlight_tutorial_done'] = True
        if not events['flashlight_tutorial_done'] and events['has_flashlight'] and events['can_tutorial_appear']:
            interacao.flashlight_tutorial_box()
        
        stdscr.refresh()

        # LIMITS MOVEMENT SPEED
        if had_movement or flashlight_interaction:
            curses.flushinp()
            time.sleep(0.3)
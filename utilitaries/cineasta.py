import os
import ast
import sys

from . import pincel

def load_frames(folder):
    if not os.path.isabs(folder):
        project_root = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        folder = os.path.join(project_root, folder)

    frames = {}

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        name = file.removesuffix('.txt')

        try:
            y_str, x_str, state = name.split('_')
            coords = (int(y_str), int(x_str))
        except ValueError:
            coords = name
            state = '0'

        if coords not in frames:
            frames[coords] = {
                'states': {},
                'current_state': '0'
            }

        frames[coords]['states'][state] = open_txt(path)

    for coords, frame in frames.items():
        frame.update({
            'content': frame['states'][frame['current_state']],
            'y_alignment': 'custom',
            'x_alignment': 'custom',
            'y_coord': 0,
            'x_coord': 0
        })
        if "aberto" not in frame['states']:
            frame['states']['aberto'] = open_txt(os.path.join(folder, "porta_aberta.txt"))

    return frames

def change_frame_state(frame, new_state):
    if new_state not in frame['states']:
        raise ValueError("The specified state is not in frame possible states.")
    frame['current_state'] = new_state
    frame['content'] = frame['states'][frame['current_state']]

def open_txt(path, color_map=False):
    if not os.path.isabs(path):
        project_root = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        path = os.path.join(project_root, path)

    with open(path, 'r', encoding='UTF-8') as file:
        if color_map:
            content = file.read()
            return ast.literal_eval(content)
        else:
            return [line.strip() for line in file]

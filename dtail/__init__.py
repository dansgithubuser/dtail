import glob
import os
import re
import signal
import time

class File:
    def __init__(self, path, end=False):
        self.stream = open(path)
        if end:
            self.stream.seek(0, 2)

    def read(self):
        return self.stream.read()

def color_to_circumfix(color):
    if color.startswith('#'):
        prefix = f'\x1b[38;5;{color[1:]}m'
    else:
        prefix = {
            'black': '\x1b[30m',
            'red': '\x1b[31m',
            'green': '\x1b[32m',
            'yellow': '\x1b[33m',
            'blue': '\x1b[34m',
            'magenta': '\x1b[35m',
            'cyan': '\x1b[36m',
            'white': '\x1b[37m',
            'lightblack': '\x1b[30;1m',
            'lightred': '\x1b[31;1m',
            'lightyellow': '\x1b[33;1m',
            'lightgreen': '\x1b[32;1m',
            'lightblue': '\x1b[34;1m',
            'lightmagenta': '\x1b[35;1m',
            'lightcyan': '\x1b[36;1m',
            'lightwhite': '\x1b[37;1m',
        }[color]
    return prefix, '\x1b[0m'

def color(text, color_regexes):
    for color, regex in color_regexes:
        prefix, suffix = color_to_circumfix(color)
        text = re.sub(f'({regex})', rf'{prefix}\1{suffix}', text, re.IGNORECASE)
    return text

def main(file_glob, color_regexes):
    files = {path: File(path, end=True) for path in glob.glob(file_glob) if os.path.isfile(path)}
    print_last = None
    main.done = False
    def finish(): main.done = True
    signal.signal(signal.SIGINT, lambda *args: finish())
    while not main.done:
        for path in glob.glob(file_glob):
            if path in files:
                continue
            if not os.path.isfile(path):
                continue
            files[path] = File(path)
        printed = False
        for path, file in files.items():
            text = file.read()
            if not text:
                continue
            if print_last != path:
                print(f'\n*** {path} ***')
                print_last = path
            print(color(text, color_regexes), end='')
            printed = True
        if not printed:
            time.sleep(0.1)

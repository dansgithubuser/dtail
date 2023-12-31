#! /usr/bin/env python3

#===== imports =====#
import argparse
import datetime
import os
import re
import signal
import subprocess
import sys

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('--run', '-r', nargs='*')
parser.add_argument('--publish', '-p', action='store_true')
args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    out=False,
    handle_signal=False,
    quiet=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        print(blue('-'*40))
        print(timestamp())
        print(os.getcwd()+'$', end=' ')
        if any([re.search(r'\s', i) for i in args]):
            print()
            for i in args: print(f'\t{i} \\')
        else:
            for i, v in enumerate(args):
                if i != len(args)-1:
                    end = ' '
                else:
                    end = ';\n'
                print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = os.environ.copy()
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    elif handle_signal:
        p = subprocess.Popen(args, **kwargs)
        signal.signal(signal.SIGINT, lambda *args: p.send_signal(signal.SIGINT))
        p.wait()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if out: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if out:
            result = result.stdout.decode('utf-8')
            if out != 'exact': result = result.strip()
        return result

#===== main =====#
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.run != None:
    invoke('bin/dtail', *args.run, env={'PYTHONPATH': '.'})

if args.publish:
    invoke('python3 -m build')
    invoke('python3 -m twine upload dist/*')

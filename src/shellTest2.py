#!/usr/bin/env python2.6

from __future__ import print_function

import readline
import threading

PROMPT = '> '

def interrupt():
    print() # Don't want to end up on the same line the user is typing on.
    print('Interrupting cow -- moo!')
    print(PROMPT, readline.get_line_buffer(), sep='', end='')

def cli():
    while True:
        cli = str(raw_input(PROMPT))

if __name__ == '__main__':
    threading.Thread(target=cli).start()
    threading.Timer(2, interrupt).start()
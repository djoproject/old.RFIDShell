#!/usr/bin/python2.6

import readline
import threading
import time
import sys

class REPL():
    def __init__(self, prompt = ":>"):
        self.prompt = prompt
        readline.set_completer(self.complete)
        
    def event(self,Ev):
        print ""
        print Ev
        
        #readline.redisplay() marche pas genial
        #this is needed because after an input, the readline buffer isn't always empty
        if len(readline.get_line_buffer()) == 0 or readline.get_line_buffer()[-1] == '\n':
            sys.stdout.write(self.prompt)
        else:
            sys.stdout.write(self.prompt + readline.get_line_buffer())
        
        sys.stdout.flush()
    
    def complete(self, prefix, index):
        print prefix
    
    def getNextCmd(self):
        cmd = raw_input(self.prompt)#readline empty the buffer here
        
Repl = REPL("toto:>")

def testAffiche():
    for i in range(0,10):
        time.sleep(2)
        Repl.event("plopsaa")
        
tr = threading.Thread(None, testAffiche, None)
tr.start()
readline.parse_and_bind('tab: complete')

while True:
    try:
        cmd = Repl.getNextCmd()
        #print "cmd : " + cmd
        
    except SyntaxError:
        print "syntax error"
        continue
    except EOFError:
        print "end of stream"
        break
        
print "exit"  
exit()

#!/usr/bin/python2.6

import os, sys
import readline
from keyList import keys
from smartcard.System import readers
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver

prompt_string = "rfid>"

###############################################################################################
##### Readline REPL ###########################################################################
###############################################################################################
def printOnShell(EventToPrint):
    print ""
    print EventToPrint
    
    #this is needed because after an input, the readline buffer isn't always empty
    if len(readline.get_line_buffer()) == 0 or readline.get_line_buffer()[-1] == '\n':
        sys.stdout.write(prompt_string)
    else:
        sys.stdout.write(prompt_string + readline.get_line_buffer())
    
    sys.stdout.flush()

###############################################################################################
##### Monitor reader ##########################################################################
###############################################################################################

class ReaderManager( ReaderObserver ):
    """A simple reader observer that is notified
    when readers are added/removed from the system and
    prints the list of readers
    """
    
    def __init__(self):
        self.readermonitor = ReaderMonitor()
        self.enable = False
        
    def update( self, observable, (addedreaders, removedreaders) ):
        r = ""
        if addedreaders != None and len(addedreaders) > 0:
            r += "Added readers" + str(addedreaders) 
        
        if removedreaders != None and len(removedreaders) > 0:
            
            if len(r) > 0:
                r += "\n"
            
            r += "Removed readers" + str(removedreaders)
        
        if len(r) > 0:
            printOnShell(r)
        
    def activate(self):
        if not self.enable:
            self.readermonitor.addObserver( self )
        
        self.enable = True
        
    def desactivate(self):
        if self.enable:
            self.readermonitor.deleteObserver(self)
        
        self.enable = False

readerobserver = ReaderManager()
#readerobserver.activate()

###############################################################################################
##### Monitor card ############################################################################
###############################################################################################

class printobserver( CardObserver ):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    def update( self, observable, (addedcards, removedcards) ):
        printOnShell("+Inserted: "+str(addedcards))
        printOnShell("-Removed: "+str(removedcards))

#cardmonitor = CardMonitor()
#cardobserver = printobserver()
#cardmonitor.addObserver( cardobserver )

###############################################################################################
##### Monitor datas ###########################################################################
###############################################################################################

#TODO

###############################################################################################

if __name__ == "__main__":
    while True:
        try:
            cmd = raw_input(prompt_string)
        except SyntaxError:
            print "syntax error"
            continue
        except EOFError:
            print "end of stream"
            break
        
        if cmd == None or len(cmd) == 0 or cmd[0] == '#' or cmd[0] == '%' or (cmd[0] == '/' and len(cmd) > 1 and cmd[1] == '/'):
            continue
    
        cmd = cmd.split(" ")
        if len(cmd) < 0 :
            print "split command error"
            continue
        
        if cmd[0] == "exit" or cmd[0] == "quit" or cmd[0] == "q" or cmd[0] == "bye":
            print "   disconnection from the reader, please wait"
            break
        elif cmd[0] == "help":
            print "  rfid shell help : "
            print "     lsk                                         : list keys name"#ok
            print "     setk NAME BYTE1 ... BYTE8 [... BYTE 16]     : add a volatile key"#ok
            print "          or add a persistent key into keyList.py"
            print "     debug                                       : enable/disable debug mode" #ok
            print "     exit                                        : exit shell" #ok
            print "     lsaddons                                    : list addons"
            print "     load NAME                             : load addon NAME"

    ########################################################################
    # LIST KEY NAME ########################################################
    ########################################################################
        elif cmd[0] == "lsk" or cmd[0] == "lskey":
            for k in keys:
                print k
    
    ########################################################################
    # SET KEY ##############################################################
    ########################################################################
        elif cmd[0] == "setk":
            if len(cmd) != 10 and len(cmd) != 18:
                print "   need a key name and 8 or 16 byte"
                continue
            
            key = []    
            for i in range(2,len(cmd)):
                try:
                    new = int(cmd[i])
                    
                except ValueError as ve:
                    print "value #"+str(i)+" is not a valid integer"
                    continue
                    
                if new < 0 or new > 255:
                    print "value #"+str(i)+" is not a valid Byte (0 to 255) : "+str(new)
                    continue
                    
                key.append(new)
                
            keys[cmd[1]] = key

    ########################################################################
    # ADDONS ###############################################################
    ########################################################################
        elif cmd[0] == "lsaddons":
            if os.path.exists("./addons/"):
                for dirname, dirnames, filenames in os.walk('./addons/'):
                    for name in filenames:
                        if name.endswith(".py"):
                            print name[0:-3]
            else:
                print "\tno addons directory"
            
        
        elif cmd[0] == "load":
            if len(cmd) < 2:
                print "   need an addons name"
                continue
            
            pass #TODO
    
    ########################################################################
    # READERS ##############################################################
    ########################################################################
        elif cmd[0] == "lsreader":
            
            indice = 0
            for r in readers():
                print "\t"+str(indice)+" : "+str(r)
                indice += 1
                
            if indice == 0:
                print "\tno reader available on this system"
                
        elif cmd[0] == "connect":
            pass #TODO
            
        elif cmd[0] == "disconnect":
            pass #TODO
            
    ########################################################################
    # MONITOR ##############################################################
    ########################################################################        
        elif cmd[0] == "monitor":
            
            """elif cmd[0] == "debug" or cmd[0] == "d":
                if debug:
                    debug = False
                    cardservice.connection.deleteObserver( observer )
                    print "debug OFF"
                else:
                    debug = True
                    observer=ConsoleCardConnectionObserver()
                    cardservice.connection.addObserver( observer )
                    print "debug ON"""
            if len(cmd) < 2:
                print "   need a kind of monitoring [all|card|reader|data]"
                continue
            
            #TODO
            
            #all
            if cmd[1] == "all":
                pass
            #card
            elif cmd[1] == "card":
                pass
            #reader
            elif cmd[1] == "reader":
                readerobserver.activate()
            #data
            elif cmd[1] == "data":
                pass
            else:
                print "   not a valid kind of monitoring : "+str(cmd[1])+", value expected : [all|card|reader|data]"
            
    ########################################################################
    # ELSE #################################################################
    ########################################################################
        elif cmd[0] == "disable":
            if len(cmd) < 2:
                print "   need a stuff to disable"
                continue
                
            if(cmd[1] == "monitor")

    ########################################################################
    # ELSE #################################################################
    ########################################################################
        else:
            print "   unknown command : "+str(cmd[0])
    
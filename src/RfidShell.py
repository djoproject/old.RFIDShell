#!/usr/bin/python2.6
from arg.args import *
import os, sys
from tries.multiLevelTries import buildDictionnary
from apdu.apduExecuter import Executer

def noneFun(envi,args):
    pass
    
def exitFun(envi,args):
    "Exit the program"
    exit()
    
def helperFun(envi,args):
    "print the help"
    #TODO
    #   add a usage message, print it when command is wrong
    #   build the usage with the arg list checker
    #
    
    StartNode = None
    if len(args) > 0:
        try:
            StartNode,args = envi["levelTries"].searchEntryFromMultiplePrefix(args,True)
        except triesException as e:
            print "   "+str(e)
            return
    
    if StartNode == None:
        StartNode = envi["levelTries"].levelOneTries
    
    dico = buildDictionnary(StartNode) 
    for k in sorted(dico):
        if dico[k].showInHelp:
            print "   "+k + " : " + dico[k].helpMessage
                
def listAddonFun(envi,args):
    "list the available addons"
    
    l = []
    if os.path.exists("./addons/"):
        for dirname, dirnames, filenames in os.walk('./addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    l.append(name[0:-3])

    return l

def loadAddonFun(name):
    "load an external shell addon"
    
    toLoad = "addons."+str(name)
    try:
        __import__(toLoad)
        print "   "+toLoad+" loaded !"
    except ImportError:
        print "unknwon module "+str(name)
    
def echo(args):
    "echo all the args"
    
    s = ""
    for a in args:
        s += str(a)+" "
        
    return s
    
def echo16(args):
    "echo all the args in hexa"
    
    s = ""
    for a in args:
        try:
            s += "0x%x "%int(a)
        except ValueError:
            s += str(a)+" "

    return s
    
def intToAscii(args):
    "echo all the args into chars"
    
    s = ""
    for a in args:
        try:
            s += chr(a)
        except ValueError:
            s += str(a)

    return s
    
#TODO make a forge command

if __name__ == "__main__":
    #Executer = CommandExecuter()
    Executer.envi["prompt"] = "rfid>"
    
    #TODO problem, the command line need to start with a white space :/
    c = Executer.addCommand(["%"]    ,False,noneFun)
    if c != None:
        c.name        = "Comment"
        c.helpMessage = "Comment a line"
        
    c = Executer.addCommand(["//"]   ,False,noneFun)
    if c != None:
        c.name        = "Comment"
        c.helpMessage = "Comment a line"
        
    c = Executer.addCommand(["#"]    ,False,noneFun)
    if c != None:
        c.name        = "Comment"
        c.helpMessage = "Comment a line"
        
    Executer.addCommand(["exit"]     ,True,exitFun)

    Executer.addCommand(["quit"]     ,True,exitFun)
    Executer.addCommand(["help"]     ,False,helperFun,AllTheSameChecker(ArgChecker(),"args"))
    
    Executer.addCommand(["lsaddons"] ,True,listAddonFun,None                                               ,stringListResultHandler)
    Executer.addCommand(["loadaddon"],True,loadAddonFun,DefaultArgsChecker([("name",stringArgChecker())]))
    Executer.addCommand(["echo"]     ,True,echo        ,AllTheSameChecker(ArgChecker(),"args")             ,printResultHandler)
    Executer.addCommand(["echo16"]   ,True,echo16      ,AllTheSameChecker(ArgChecker(),"args")             ,printResultHandler)
    Executer.addCommand(["toascii"]  ,True,intToAscii  ,AllTheSameChecker(ArgChecker(),"args")             ,printResultHandler)
    
    #TODO make the unload addon and the reload
    
    loadAddonFun("rfidDefault")
    #loadAddonFun("proxnroll")
    #loadAddonFun("acr122sam")
    #loadAddonFun("pn532")
    
    Executer.mainLoop()
    
    
    
    
    
    

#!/usr/bin/python2.6
from arg.args import *
import os, sys
from tries.multiLevelTries import buildDictionnary
from apdu.apduExecuter import Executer

def noneFun():
    pass
    
def exitFun():
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
            print "   "+str(k)+ " : " + str(dico[k].helpMessage)
            
def usageFun(envi,args):
    "print the usage of a fonction"
    
    if len(args) > 0:
        try:
            StartNode,args = envi["levelTries"].searchEntryFromMultiplePrefix(args)
        except triesException as e:
            print "   "+str(e)
            return
            
        print StartNode.value.argChecker.usage()
                
def listAddonFun():
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

def preTraitementForwardArgs(args):
    return args

if __name__ == "__main__":
    #Executer = CommandExecuter()
    Executer.envi["prompt"] = "rfid>"
    
    #TODO problem, the command line need to start with a white space :/
    c = Executer.addCommand(["%"])
    if c != None:
        c.name        = "Comment"
        c.helpMessage = "Comment a line"
        c.showInHelp = False
        
    c = Executer.addCommand(["//"])
    if c != None:
        c.name        = "Comment"
        c.helpMessage = "Comment a line"
        c.showInHelp = False
        
    c = Executer.addCommand(["#"])
    if c != None:
        c.name        = "Comment"
        c.helpMessage = "Comment a line"
        c.showInHelp = False
        
    Executer.addCommand(CommandStrings=["exit"]     ,process=exitFun)

    Executer.addCommand(CommandStrings=["quit"]     ,process=exitFun)
    Executer.addCommand(CommandStrings=["help"]     ,process=helperFun      ,argChecker=AllTheSameChecker(ArgChecker(),"args"))
    Executer.addCommand(CommandStrings=["usage"]    ,process=usageFun       ,argChecker=AllTheSameChecker(ArgChecker(),"args"))
    
    Executer.addCommand(CommandStrings=["lsaddons"] ,preProcess=listAddonFun,postProcess=stringListResultHandler)
    Executer.addCommand(CommandStrings=["loadaddon"],process=loadAddonFun   ,argChecker=DefaultArgsChecker([("name",stringArgChecker())]))
    Executer.addCommand(CommandStrings=["echo"]     ,process=echo           ,argChecker=AllTheSameChecker(ArgChecker(),"args")             ,postProcess=printResultHandler)        
    Executer.addCommand(CommandStrings=["echo16"]   ,process=echo16         ,argChecker=AllTheSameChecker(ArgChecker(),"args")             ,postProcess=printResultHandler)
    Executer.addCommand(CommandStrings=["toascii"]  ,process=intToAscii     ,argChecker=AllTheSameChecker(IntegerArgChecker(),"args")      ,postProcess=printResultHandler)
    
    #TODO make the unload addon and the reload
    
    loadAddonFun("rfidDefault")
    loadAddonFun("proxnroll")
    loadAddonFun("acr122V2")
    loadAddonFun("pn532")
    loadAddonFun("mifareUltralight")
    loadAddonFun("scl3711")
    
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            if Executer.executeFile(sys.argv[1]):
                exit()
     
    Executer.mainLoop()
    
    
    
    
    
    

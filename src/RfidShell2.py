#!/usr/bin/python2.6
from arg.args import *
import os, sys
from tries.multiLevelTries import buildDictionnary
from apdu.apduExecuter import Executer

def noneFun(envi,args):
    pass
    
def exitFun(envi,args):
    exit()
    
def helperFun(envi,args):
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
    #TODO don't list __init__
    
    if os.path.exists("./addons/"):
        for dirname, dirnames, filenames in os.walk('./addons/'):
            for name in filenames:
                if name.endswith(".py"):
                    print name[0:-3]
    else:
        print "\tno addons directory"

def loadAddonFun(envi,args):
    #TODO check the addon name

    toLoad = "addons."+str(args[0])
    __import__(toLoad)
    print "   "+toLoad+" loaded !"

if __name__ == "__main__":
    #Executer = CommandExecuter()
    Executer.envi["prompt"] = "rfid>"
    
    #TODO problem, the command line need to start with a white space :/
    Executer.addCommand(["%"],"Comment","Comment line",False,noneFun)
    Executer.addCommand(["//"],"Comment","Comment line",False,noneFun)
    Executer.addCommand(["#"],"Comment","Comment line",False,noneFun)
    Executer.addCommand(["exit"],"Exit","Exit the program",True,exitFun)
    Executer.addCommand(["quit"],"Quit","Exit the program",True,exitFun)
    Executer.addCommand(["help"],"Help","print help",False,helperFun,ArgsChecker())
    Executer.addCommand(["lsaddons"],"list addons","list the available addons",True,listAddonFun)
    Executer.addCommand(["loadaddon"],"load an addon","load an external shell addon",True,loadAddonFun,DefaultArgsChecker([stringArgChecker()]))
    
    #TODO make the unload addon and the reload
    
    loadAddonFun(Executer.envi,["rfidDefault"])
    #loadAddonFun(Executer.envi,["proxnroll"])
    #loadAddonFun(Executer.envi,["acr122sam"])
    
    Executer.mainLoop()
    
    
    
    
    
    

#!/usr/bin/python2.6
import inspect
from exception import argPostExecutionException

#
# this method check the args with respect to meth
#
# @argument args, the arguments to apply
# @argument meth, the method to wich apply the argument
# @return a dictionary with the argument bounded to the method
#
def selfArgChecker(args,meth,envi,printer,checker = None):
    #check the args
    if checker != None:
        argsValueDico = checker.checkArgs(args) # may raise argException
        #argsValueDico est un ordered dico
        
    else:
        argsValueDico = {}
        
    #parse the command to execute
    inspect_result = inspect.getargspec(meth)

    #print inspect_result

    nextArgs = {}   
    if inspect_result.args != None:
        
        #how many default argument?
        if inspect_result.defaults == None:
            lendefault = 0
        else:
            lendefault = len(inspect_result.defaults)
        
        #When the command has only one unknwon arg name, we bind to it all the args
        keyList = []
        index = 0
        for argname in inspect_result.args:
            if argname != "self" and argname != "envi" and argname != "printer" and argname != "args" and (index < (len(inspect_result.args) - lendefault)) :
                keyList.append(argname)
            
            index += 1
                
        if len(keyList) == 1 and keyList[0] not in argsValueDico:
            argsValueDico[keyList[0]] = args
        
        #bind the args
        index = 0
        for argname in inspect_result.args:
            if argname in argsValueDico:
                nextArgs[argname] = argsValueDico[argname]
                del argsValueDico[argname]
            elif argname == "self":
                pass
            #    nextArgs["self"] = self
            elif argname == "envi":
                nextArgs["envi"] = envi
            elif argname == "printer":
                nextArgs["printer"] = printer    
            elif argname == "args":
                #rebuilt a list with the args
                #nextArgs["args"] = [v for (k, v) in argsValueDico.iteritems()] #argsValueDico
                nextArgs["args"] = args
            else: #Default Value               
                if index < (len(inspect_result.args) - lendefault):
                    #on assigne a None
                    #self.printOnShell("WARNING unknwon arg <"+str(argname)+"> in command "+commandToExecute.name)
                    print ("WARNING unknwon arg <"+str(argname)+"> in command ")
                    nextArgs[argname] = None
                else:
                    #Si c'est un argument avec une valeur par defaut, ne pas assigner  
                    nextArgs[argname] = inspect_result.defaults[index - (len(inspect_result.args) - len(inspect_result.defaults))]

            index += 1
    
    #print nextArgs
    return nextArgs

class Command(object):
    #def __init__(self,envi,printer,preProcess=None,process=None,argChecker=None,postProcess=None):
    def __init__(self,preChecker=None,proChecker=None,postChecker=None):        
        self.preChecker  = preChecker
        self.proChecker  = proChecker
        self.postChecker = postChecker
        self.preInputBuffer  = None
        self.proInputBuffer  = None
        self.postInputBuffer = None

    #
    # set the next execution buffer of this command
    #
    def setBuffer(self,preBuffer,proBuffer,postBuffer):
        self.preInputBuffer  = preBuffer
        self.proInputBuffer  = proBuffer
        self.postInputBuffer = postBuffer

    #default preProcess
    def preProcess(self,args):
        return args

    #default process
    def process(self,args):
        return args
    
    #default postProcess
    def postProcess(self,args):
        #print str(args)
        pass
        
    #
    # this method convert a string list to an arguments list, then preprocess the arguments
    #
    # @argument args : a string list, each item is an argument
    # @return : a preprocess result
    #
    def preProcessExecution(self,args,printer,envi={}):
        nextArgs = selfArgChecker(args,self.preProcess,envi,printer,self.preChecker)
        return self.preProcess(**nextArgs) #may raise
        
    
    #
    # this method execute the process on the preprocess result
    # 
    # @argument args : the preprocess result
    # @return : the command result
    #    
    def ProcessExecution(self,args,printer,envi={}):
        nextArgs = selfArgChecker(args,self.process,envi,printer,self.proChecker)
        return self.process(**nextArgs)
    
    #
    # this method parse the result from the processExecution
    #
    # @argument args : the process result
    # @return : the unconsumed result
    #
    def postProcessExecution(self,args,printer,envi={}):
        nextArgs = selfArgChecker(args,self.postProcess,envi,printer,self.postChecker)
        return self.postProcess(**nextArgs)
#
# sepcial command class, with only one argchecker (the starting point)
#
#
class UniCommand(Command):
    def __init__(self,name,helpMessage,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):
        super(UniCommand,self).__init__()
        self.name = name
        self.helpMessage = helpMessage
        self.showInHelp = showInHelp
        
        self.argChecker = argChecker #not realy usefull but eaysier to retriver the only one checker if it sets
        
        checkSet = False
        if preProcess != None:
            self.preProcess = preProcess
            self.preChecker = argChecker
            checkSet = True
        
        if process != None:
            self.process = process
            if not checkSet:
                checkSet = True
                self.proChecker = argChecker
            
        if postProcess != None:
            self.postProcess = postProcess
            if not checkSet:
                self.postChecker = argChecker

class MultiCommand(list):
    def __init__(self,name,helpMessage,showInHelp=True):
        self.name = name
        self.helpMessage = helpMessage
        self.showInHelp = showInHelp
        
    def addProcess(self,preProcess=None,process=None,argChecker=None,postProcess=None):
        c = Command()
                
        checkSet = False
        if preProcess != None:
            c.preProcess = preProcess
            c.preChecker = argChecker
            checkSet = True
        
        if process != None:
            c.process = process
            if not checkSet:
                checkSet = True
                c.proChecker = argChecker
            
        if postProcess != None:
            c.postProcess = postProcess
            if not checkSet:
                c.postChecker = argChecker
        
        self.append(c)


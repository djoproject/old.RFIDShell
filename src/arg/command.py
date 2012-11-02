#!/usr/bin/python2.6
import inspect
from exception import argPostExecutionException

class Command(object):
    #def __init__(self,envi,printer,preProcess=None,process=None,argChecker=None,postProcess=None):
    def __init__(self,envi,printer,argChecker=None):

        #self.preProcess = preProcess
        #self.process = process
        #self.postProcess = postProcess
        self.argChecker = argChecker
        self.envi = envi
        self.printer = printer

    def preProcess(self):
        pass
        
    def postProcess(self):
        pass

    def process(self):
        pass

    #
    # this method check the args with respect to meth
    #
    # @argument args, the arguments to apply
    # @argument meth, the method to wich apply the argument
    # @return a dictionary with the argument bounded to the method
    #
    def selfArgChecker(self,args,meth):
        #check the args
        if self.argChecker != None:
            argsValueDico = self.argChecker.checkArgs(args) # may raise argException
            #argsValueDico est un ordered dico
            
        else:
            argsValueDico = {}
            
        #parse the command to execute
        inspect_result = inspect.getargspec(meth)

        #bind the args
        nextArgs = {}   

        if inspect_result.args != None:
            index = 0
            for argname in inspect_result.args:
                if argname in argsValueDico:
                    nextArgs[argname] = argsValueDico[argname]
                    del argsValueDico[argname]
                elif argname == "envi":
                    nextArgs["envi"] = self.envi
                elif argname == "printer":
                    nextArgs["printer"] = self.printer    
                elif argname == "args":
                    nextArgs["args"] = [v for (k, v) in argsValueDico.iteritems()] #argsValueDico
                else:
                    if inspect_result.defaults == None:
                        lendefault = 0
                    else:
                        lendefault = len(inspect_result.defaults)
                                        
                    if index < (len(inspect_result.args) - lendefault):
                        #on assigne a None
                        #self.printOnShell("WARNING unknwon arg <"+str(argname)+"> in command "+commandToExecute.name)
                        print ("WARNING unknwon arg <"+str(argname)+"> in command ")
                        nextArgs[argname] = None
                    else:
                        #Si c'est un argument avec une valeur par defaut, ne pas assigner  
                        nextArgs[argname] = inspect_result.defaults[index - (len(inspect_result.args) - len(inspect_result.defaults))]

                index += 1
        
        return nextArgs

    #
    # this method convert a string list to an arguments list, then preprocess the arguments
    #
    # @argument args : a string list, each item is an argument
    # @return : a preprocess result
    #
    def preProcessExecution(self,args):
        if self.preProcess == None:
            return args

        nextArgs = self.selfArgChecker(args,self.preProcess)
        return self.preProcess(**nextArgs) #may raise
    
    #
    # this method execute the process on the preprocess result
    # 
    # @argument args : the preprocess result
    # @return : the command result
    #    
    def ProcessExecution(self,args):
        if self.process != None:
            if self.preProcess == None:
                nextArgs = self.selfArgChecker(args,self.process)
                return self.process(**nextArgs)
            else:
                return self.process(args) #may raise argExecutionException

        return args 
    
    #
    # this method parse the result from the processExecution
    #
    # @argument args : the process result
    # @return : the unconsumed result
    #
    def postProcessExecution(self,args):
        if self.postProcess != None:
            
            if self.preProcess == None and self.process == None: #pas necessairement normal de gerer ca mais au cas ou
                nextArgs = self.selfArgChecker(args,self.postProcess)
                return self.postProcess(**nextArgs)
            
            inspect_result = inspect.getargspec(self.postProcess)
            
            if len(inspect_result.args) == 0:
                return self.postProcess()
            if len(inspect_result.args) == 1:
                return self.postProcess(args) 
            if len(inspect_result.args) == 2:
                return self.postProcess(self.envi,args)
            
            raise argPostExecutionException("unknwon post process prototype")
            
        return args

class UniCommand(Command):
    def __init__(self,name,helpMessage,envi,printer,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):
        super(UniCommand,self).__init__(envi,printer,preProcess,process,argChecker,postProcess)
        self.name = name
        self.helpMessage = helpMessage
        self.showInHelp = showInHelp

class MultiCommand(list):
    def __init__(self,name,helpMessage,showInHelp=True):
        self.name = name
        self.helpMessage = helpMessage
        self.showInHelp = showInHelp
        
    def addProcess(self,envi,printer,preProcess=None,process=None,argChecker=None,postProcess=None):
        self.append(Command(envi,printer,preProcess,process,argChecker,postProcess))


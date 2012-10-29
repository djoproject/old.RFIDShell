#!/usr/bin/python2.6

#Copyright (C) 2012  Jonathan Delvaux <jonathan.delvaux@uclouvain.be>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


from exception import argException,argExecutionException
from tries.exception import triesException
from tries.multiLevelTries import multiLevelTries
import readline
import os
import sys
import inspect
from ordereddict import OrderedDict
import traceback

histfile = os.path.join(os.path.expanduser("~"), ".rfidShell")
try:
    readline.read_history_file(histfile)
except IOError:
    pass

import atexit
atexit.register(readline.write_history_file, histfile)
del os, histfile      

class Command():
    
    def __init__(self,name,helpMessage,envi,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):
        self.name = name
        self.helpMessage = helpMessage
        self.preProcess = preProcess
        self.process = process
        self.postProcess = postProcess
        self.argChecker = argChecker
        self.showInHelp = showInHelp
        self.envi = envi

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
        index = 0

        for argname in inspect_result.args:
            if argname in argsValueDico:
                nextArgs[argname] = argsValueDico[argname]
                del argsValueDico[argname]
            elif argname == "envi":
                nextArgs["envi"] = self.envi
            elif argname == "args":
                nextArgs["args"] = [v for (k, v) in argsValueDico.iteritems()] #argsValueDico
            else:              
                if index < (len(inspect_result.args) - len(inspect_result.defaults)):
                    #on assigne a None
                    #self.printOnShell("WARNING unknwon arg <"+str(argname)+"> in command "+commandToExecute.name)
                    print ("WARNING unknwon arg <"+str(argname)+"> in command "+commandToExecute.name)
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
            
            return self.postProcess(args) #may probably raise some execution (TODO define this)
            
        return args 

class CommandExecuter():
    def __init__(self):
        self.envi = {}
        self.envi["prompt"] = ":>"
        self.levelTries = multiLevelTries()
        self.envi["levelTries"] = self.levelTries
        
        #def __init__(self,name,helpMessage,envi,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):
    def addCommand(self,CommandStrings,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):
        name = ""
        for s in CommandStrings:
            name += s+" "
        
        c = Command(name,preProcess.__doc__,self.envi,preProcess,process,argChecker,postProcess,showInHelp)
        
        try:
            self.levelTries.addEntry(CommandStrings,c)
            return c
        except triesException as e:
            print self.printOnShell(str(e))
            return None
            
    def addAlias(self,CommandStrings,AliasCommandStrings):
        #pas aussi simple
            #on doit pouvoir gerer des alias avec des arguments fixe
        
        pass #TODO
    
    #
    #
    # @return, true if no severe error or correct process, false if severe error
    #
    def executeCommand(self,cmd):
        cmd = cmd.split("|")
        if len(cmd) < 0 :
            print "   split command error"
            return False
        
        CommandStringsList = []    
        for inner in cmd:
            inner = inner.strip(' \t\n\r')
            if len(inner) > 0:
                inner = inner.split(" ")
                if len(inner) < 0 :
                    print "   split command error"
                    CommandStringsList = []
                    break
                
                finalCmd = []
                for cmd in inner:
                    cmd = cmd.strip(' \t\n\r')
                    if len(cmd) > 0 :
                        finalCmd.append(cmd)
                    
                if len(finalCmd) > 0:
                    CommandStringsList.append(finalCmd)
        
        if len(CommandStringsList) < 1:
            return False
        
        previousValue = None
        stack = []
        for indice in range(0,len(CommandStringsList)):
            CommandStrings = CommandStringsList[indice]
        
            #look after the command
            try:
                triesNode,args = self.levelTries.searchEntryFromMultiplePrefix(CommandStrings)
                #args est une liste
                
                commandToExecute = triesNode.value
            except triesException as e:
                self.printOnShell(str(e))
                return True
            
            stack.append(commandToExecute)
            
            #append the previous value to the args
            if previousValue != None:
                if isinstance(previousValue,list):
                    for item in previousValue:
                        args.append(item)
                else:
                    args.append(previousValue)

            #preProcess
            try:
                preResult = commandToExecute.preProcessExecution(args)
            except argException as aee:
                self.printOnShell(str(aee)+" at "+commandToExecute.name)
                self.printOnShell("USAGE : "+commandToExecute.name+" "+commandToExecute.argChecker.usage())
                return True
            except Exception as ex:
                self.printOnShell("SEVERE : "+str(ex)+" at "+commandToExecute.name)
                traceback.print_exc() #TODO remove after debug
                return False
            
            if indice == (len(CommandStringsList)-1):
                #Process
                try:
                    processResult = commandToExecute.ProcessExecution(preResult) #last item
                except argExecutionException as aee:
                    self.printOnShell(""+str(aee)+" at "+commandToExecute.name)
                    return True
                except argException as aee:
                    self.printOnShell(str(aee)+" at "+commandToExecute.name)
                    self.printOnShell("USAGE : "+commandToExecute.name+" "+commandToExecute.argChecker.usage())
                    return True
                except Exception as ex:
                    self.printOnShell("SEVERE : "+str(ex)+" at "+commandToExecute.name)
                    traceback.print_exc() #TODO remove after debug
                    return False
            else:
                previousValue = preResult
                continue #this is useless, it's just to show there is another loop from here

        #postProcess
        while len(stack) > 0:
            try:
                processResult = stack.pop().postProcessExecution(processResult)
            #TODO except specific execption
            except argExecutionException as aee:
                self.printOnShell(""+str(aee)+" at "+commandToExecute.name)
                return True
            except argException as aee:
                self.printOnShell(str(aee)+" at "+commandToExecute.name)
                self.printOnShell("USAGE : "+commandToExecute.name+" "+commandToExecute.argChecker.usage())
                return True
            except Exception as ex:
                self.printOnShell("SEVERE : "+str(ex)+" at "+commandToExecute.name)
                traceback.print_exc() #TODO remove after debug
                return False
                
        return True
        
    def mainLoop(self):
        while True:
            #readline.parse_and_bind("tab: complete")
            if(sys.platform == 'darwin'):
                import rlcompleter
                readline.parse_and_bind ("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")
            
            readline.set_completer(Executer.complete)
            
            try:
                cmd = raw_input(self.envi["prompt"])
            except SyntaxError:
                print "   syntax error"
                continue
            except EOFError:
                print "\n   end of stream"
                break
                
            self.executeCommand(cmd)        
    
    ###############################################################################################
    ##### Readline REPL ###########################################################################
    ###############################################################################################
    def printAsynchronousOnShell(self,EventToPrint):
        print ""
        print "   "+EventToPrint

        #this is needed because after an input, the readline buffer isn't always empty
        if len(readline.get_line_buffer()) == 0 or readline.get_line_buffer()[-1] == '\n':
            sys.stdout.write(self.envi["prompt"])
        else:
            sys.stdout.write(self.envi["prompt"] + readline.get_line_buffer())

        sys.stdout.flush()
        
    def printOnShell(self,toPrint):
        print "   "+str(toPrint)
        
    def complete(self,prefix,index):
        #TODO pas encore au point
        
        args = prefix.split(" ")
        if len(args) < 0 :
            print "   split command error"
            return None
        StartNode = None
        if len(args) > 0:
            try:
                #TODO, la methode searchEntryFromMultiplePrefix ne semble pas adaptee pour ici
                
                StartNode,args = self.envi["levelTries"].searchEntryFromMultiplePrefix(args,True)
                print StartNode.getCompleteName()
            except triesException as e:
                print "   "+str(e)
                return None
        if StartNode == None:
            StartNode = envi["levelTries"].levelOneTries
    
        key = StartNode.getAllPossibilities().keys()
        #print key
        try:
            return key[index]
        except IndexError:
            return None
    def executeFile(self,filename):
        f = open(filename, "r")
        exitOnEnd = True
        for line in f:
            print self.envi["prompt"]+line.strip('\n\r')
            if line.startswith("noexit"):
                exitOnEnd = False
            elif not self.executeCommand(line):
                break
                
        return exitOnEnd

###############################################################################################
##### limitChecker ############################################################################
###############################################################################################
class limitChecker(object):
    def checkLimit(self,prefixSize,argsSize):
        pass

class defaultLimitChecker(limitChecker):
    def __init__(self,limit=None):
        self.limit = limit

    def checkLimit(self,prefixCheckerSize,argsSize):
        #check limit
        limit = prefixCheckerSize
        if self.limit != None:
            limit += self.limit

        if argsSize < prefixCheckerSize or argsSize > limit:
            raise argException("Argument missing, expected at most "+str(limit)+", get "+str(argsSize))

class exactLimitChecker(limitChecker):
    def __init__(self,limit):
        self.limit = limit

    def checkLimit(self,prefixCheckerSize,argsSize):
        if argsSize != (self.limit + prefixCheckerSize):
            raise argException("Argument missing, expected at least "+str((self.limit + prefixCheckerSize))+", get "+str(argsSize))

class multiLimitChecker(limitChecker):
    def __init__(self,*limitCount):
        self.limitCount = limitCount

    def checkLimit(self,prefixCheckerSize,argsSize):
        #check limit
        if len(self.limitCount) == 0:
            if prefixCheckerSize == argsSize:
                return
            raise argException("Argument missing, expected "+str(prefixCheckerSize)+", get "+str(argsSize))

        expected = []
        for limit in self.limitCount:
            if argsSize == (limit + prefixCheckerSize):
                return
            expected.append(limit + prefixCheckerSize)

        raise argException("Argument missing, expected one of the following sier "+str(expected)+", get "+str(argsSize))
###############################################################################################
##### ArgsChecker #############################################################################
###############################################################################################
class ArgsChecker():
    "abstract arg checker"
    
    def __init__(self):
        pass
    
    #
    # @argsList, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList):
        pass
        
    def usage(self):
        pass
        
class DefaultArgsChecker(ArgsChecker):
    def __init__(self, argCheckerList,mandatoryCount=None):
        self.argCheckerList = OrderedDict(argCheckerList)
        
        if mandatoryCount == None:
            self.mandatoryCount = len(self.argCheckerList)
        else:
            if mandatoryCount > len(self.argCheckerList):
                raise argException("(DefaultArgsChecker) init, the mandatoryCount is bigger than the size of the arg checker list : "+str(mandatoryCount)+" > "+str(len(self.argCheckerList)))
            
            self.mandatoryCount = mandatoryCount
    
    def checkArgs(self,args):
        #check the arguments length
        if len(args) < self.mandatoryCount:
            raise argException("Argument missing, expected at least "+str(self.mandatoryCount)+", get "+str(len(args)))
        
        ret = OrderedDict()
        #check every argument
        #ret = []
        #for i in range(0,len(self.argCheckerList)):
        #    ret.append(self.argCheckerList[i].getValue(args[i],i))
        
        i=0
        for k in self.argCheckerList:
            if i >= len(args): #non mandatory argument
                break
            
            ret[k] = self.argCheckerList[k].getValue(args[i],i)
            i += 1

        return ret
        
    def usage(self):
        if len(self.argCheckerList) == 0:
            return "no args needed"
        
        ret = ""
        firstMandatory = False
        i=0
        for ac in self.argCheckerList:
            if self.mandatoryCount == i:
                ret += "["
            
            ret += ac+":"+self.argCheckerList[ac].getUsage()+" "
            i += 1
        
        if self.mandatoryCount < i:
            ret += "]"
        
        return ret
                
"""class MultiArgsChecker(ArgsChecker):
    #TODO ce serait plus interessant d'encapsuler des DefaultArgsChecker et des AllTheSameChecker
    
    def __init__(self, *argsCheckerList):
        self.argCheckerList = []
        for argsChecker in argsCheckerList:
            self.argCheckerList.append(OrderedDict(argsChecker))

    def checkArgs(self,args):
        expectedCount = []
        
        for checkerList in self.argCheckerList:
            
            #TODO si un checker avec un bon nombre d'argument ne match pas, essayer les suivant
            if len(checkerList) == len(args):
                #ret = []
                #for i in range(0,len(checkerList)):
                #    ret.append(checkerList[i].getValue(args[i],i))
                
                ret = OrderedDict()
                i=0
                for k in checkerList:
                    ret[k] = checkerList[k].getValue(args[i],i)
                    i += 1
                
                return ret
            
            expectedCount.append(len(checkerList))
        
        #build error message
        if len(expectedCount) > 0:
            s = ""
            f = True
            for i in expectedCount:
                if f:
                    s += str(i)
                    f = False
                else:
                    s += " or "+str(i)
            
            raise argException("Argument count is wrong, expected "+s+" arguments, get "+str(len(args)))
            
    def usage(self):
        ret = ""
        
        first = True
        for checkerList in self.argCheckerList:
            if first:
                first = False
            else:
                ret += " | "
                
            ret += "("
            
            innerFirst = True
            for k in checkerList:
                if innerFirst:
                    innerFirst = False
                else:
                    ret += " "
                    
                ret += k+":"+checkerList[k].getUsage()
            
            ret += ")"
            
        return ret"""
                
        
class AllTheSameChecker(ArgsChecker):
    def __init__(self, argChecker, argName,mini=None,maxi=None,uniqueValue=False):
        self.argChecker = argChecker
        self.maxi = maxi
        self.mini = mini
        self.argName = argName
        self.uniqueValue = uniqueValue
        
    def checkArgs(self,args):
        #check the arguments length
        if self.mini != None:
            if len(args) < self.mini:
                raise argException("Argument missing, expected at least "+str(self.mini)+" items, get "+str(len(args)))
            
            if self.maxi != None:
                if len(args) > self.maxi:
                    raise argException("too much Arguments, expected at most "+str(self.maxi)+", get "+str(len(args)))
        
        ret = []
        uniqueSet = []
        #check every argument
        for i in range(0,len(args)):
            ret.append(self.argChecker.getValue(args[i],i))
            
            if self.uniqueValue:
                if args[i] in uniqueSet:
                    raise argException("duplicate argument, each argument must be unique, the following seems to appear more than once : "+str(args[i]))
                    
                uniqueSet.append(args[i])
            
        return {self.argName:ret}
        
    def usage(self):
        if self.mini == None :
            if self.maxi == None :
                return self.argName+":("+self.argChecker.getUsage()+" .. "+self.argChecker.getUsage()+")"
            else:
                return self.argName+":("+self.argChecker.getUsage()+"0 .. "+self.argChecker.getUsage()+str(self.maxi)+")"
        else:
            return self.argName+":("+self.argChecker.getUsage()+"0 .. "+self.argChecker.getUsage()+str(self.mini)+"[ .. "+self.argChecker.getUsage()+str(self.maxi)+"])"
        
class InfiniteArgsChecker(ArgsChecker):
    #TODO le suffix checker devrait etre un AllTheSameChecker
    
    def __init__(self,suffixName,suffixChecker,prefixCheckers=[],limitChecker=defaultLimitChecker(),uniqueValue=False):
        self.suffixName = suffixName
        self.suffixChecker = suffixChecker
        self.prefixCheckers = OrderedDict(prefixCheckers)        
        self.limitChecker = limitChecker
        self.uniqueValue = uniqueValue
        
    def checkArgs(self,args):
        #check limit
        self.limitChecker.checkLimit(len(self.prefixCheckers),len(args))
        
        #init return value
        ret = OrderedDict()
        
        #check prefix
        i=0
        for k in self.prefixCheckers:
            ret[k] = self.prefixCheckers[k].getValue(args[i],i)
            i += 1
        
        #check suffix
        suffix = []
        uniqueSet = []
        for j in range(i,len(args)):
            suffix.append(self.suffixChecker.getValue(args[j],j))
            
            if self.uniqueValue:
                if args[j] in uniqueSet:
                    raise argException("duplicate argument, each argument must be unique, the following seems to appear more than once : "+str(args[j]))
                    
                uniqueSet.append(args[j])
        
        ret[self.suffixName] = suffix
        
        return ret
        
    def usage(self):
        ret = ""
        for ac in self.prefixCheckers:
            ret += ac+":"+self.prefixCheckers[ac].getUsage()+" "
        
        ret += self.suffixName+":("+self.suffixChecker.getUsage()+" .. "+self.suffixChecker.getUsage()+")"
        
        return ret
        
###############################################################################################
##### ArgChecker ##############################################################################
###############################################################################################

class ArgChecker(object):
    def __init__(self,size = 1):
        self.size = 1
    
    def __len__(self):
        return self.size
    
    #
    # @exception raise an argException if there is an error
    #   
    def checkValue(self,argNumber=None):
        pass
        
    def getValue(self,value,argNumber=None):
        self.checkValue(value)
        return value
        
    def getUsage(self):
        return "<any>"
        
class stringArgChecker(ArgChecker):
    def checkValue(self, value,argNumber=None):
        if value == None:
            if argNumber != None:
                raise argException("(String) Argument "+str(argNumber)+" : the string arg can't be None")
            else:
                raise argException("(String) Argument : the string arg can't be None")
            
        if type(value) != str:
            if argNumber != None:
                raise argException("(String) Argument "+str(argNumber)+" : this arg is not a valid string")
            else:
                raise argException("(String) Argument : this arg is not a valid string")
    def getUsage(self):
        return "<string>"
        
class IntegerArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        super(IntegerArgChecker,self).__init__(1)
        self.minimum = minimum
        self.maximum = maximum
    
    def checkValue(self, value,argNumber=None):
        if value == None:
            if argNumber != None:
                raise argException("(Integer) Argument "+str(argNumber)+" : the integer arg can't be None")
            else:
                raise argException("(Integer) Argument : the integer arg can't be None")
        
        try:
            castedValue = int(value)
        except ValueError:
            try:
                castedValue = int(value,16)
            except ValueError:
                if argNumber != None:
                    raise argException("(Integer) Argument "+str(argNumber)+" : this arg is not a valid integer or hexadecimal")
                else:
                    raise argException("(Integer) Argument : this arg is not a valid integer or hexadecimal")
        
        if self.minimum != None:
            if castedValue < self.minimum:
                if argNumber != None:
                    raise argException("(Integer) Argument "+str(argNumber)+" : the lowest value must be bigger or equal than "+str(self.minimum))
                else:
                    raise argException("(Integer) Argument : the lowest value must be bigger or equal than "+str(self.minimum))
                
        if self.maximum != None:
            if castedValue > self.maximum:
                if argNumber != None:
                    raise argException("(Integer) Argument "+str(argNumber)+" : the biggest value must be lower or equal than "+str(self.maximum))
                else:
                    raise argException("(Integer) Argument : the biggest value must be lower or equal than "+str(self.maximum))

    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        v = super(IntegerArgChecker,self).getValue(value,argNumber)
        
        try:
            return int(v)
        except ValueError:
            return int(v,16)        
        
    def getUsage(self):
        if self.minimum != None:
            if self.maximum != None:
                return "<int "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<int "+str(self.minimum)+"-*>"
        return "<int>"

class hexaArgChecker(IntegerArgChecker):
    def __init__(self, minimum=0x00, maximum=0xFF):
        super(hexaArgChecker,self).__init__(minimum,maximum)
        #self.minimum = minimum
        #self.maximum = maximum
    
    """def checkValue(self, value,argNumber=None):
        if value == None:
            if argNumber != None:
                raise argException("(hexadecimal) Argument "+str(argNumber)+" : the integer arg can't be None")
            else:
                raise argException("(hexadecimal) Argument : the integer arg can't be None")
        
        if type(value) != int:
            if type(value) == str and not (value.startswith("0x") or value.startswith("0X")):
                 if argNumber != None:
                     raise argException("(hexadecimal) Argument "+str(argNumber)+" : the string must start with 0x")
                 else:
                     raise argException("(hexadecimal) Argument : the string must start with 0x")
            
            try:
                castedValue = int(value,16)
            except ValueError:
                if argNumber != None:
                    raise argException("(hexadecimal) Argument "+str(argNumber)+" : this arg is not a valid integer")
                else:
                    raise argException("(hexadecimal) Argument : this arg is not a valid integer")
        else:
            castedValue = value
        
        if self.minimum != None:
            if castedValue < self.minimum:
                if argNumber != None:
                    raise argException("(hexadecimal) Argument "+str(argNumber)+" : the lowest value must be bigger or equal than "+str(self.minimum))
                else:
                    raise argException("(hexadecimal) Argument : the lowest value must be bigger or equal than "+str(self.minimum))
                
        if self.maximum != None:
            if castedValue > self.maximum:
                if argNumber != None:
                    raise argException("(hexadecimal) Argument "+str(argNumber)+" : the biggest value must be lower or equal than "+str(self.maximum))
                else:
                    raise argException("(hexadecimal) Argument : the biggest value must be lower or equal than "+str(self.maximum))

    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        v = super(hexaArgChecker,self).getValue(value,argNumber)
        if type(v) != int:
            return int(v,16)
        else:
            return v
            
    def getUsage(self):
        return "<hexa 0x%x-0x%x>"%(self.minimum,self.maximum)"""

class tokenValueArgChecker(stringArgChecker):
    #TODO stocker les tokens dans un tries
    
    def __init__(self, tokenDico):
        super(tokenValueArgChecker,self).__init__(1)
        #TODO if type(tokenDico) != dict
            #raise an exception
        
        self.tokenDico = tokenDico
    
    def checkValue(self, value,argNumber=None):
        super(tokenValueArgChecker,self).checkValue(value,argNumber)
            
        if value not in self.tokenDico:
            #TODO afficher les tokens dans le message d'erreur
            if argNumber != None:
                raise argException("(Token) Argument "+str(argNumber)+" : this arg is not a valid token")
            else:
                raise argException("(Token) Argument : this arg is not a valid token")
    
    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        
        return self.tokenDico[value]
        
    def getUsage(self):
        ret = "("
        
        first = True
        for k in self.tokenDico:
            if first:
                ret += k
                first = False
            else:
                ret += "|"+k
            
        ret += ")"
        return ret

###############################################################################################
##### anything   ##############################################################################
###############################################################################################
                
Executer = CommandExecuter()

def stringListResultHandler(result):
    if result == None or len(result) == 0:
        Executer.printOnShell("no item available")
        return
        
    for i in result:
        Executer.printOnShell(i)
        
def printResultHandler(result):
    if result != None:
        print str(result)
    
def listResultHandler(result):
    if result == None or len(result) == 0:
        Executer.printOnShell("no item available")
        return

    for i in result:
        Executer.printOnShell(str(i))

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

histfile = os.path.join(os.path.expanduser("~"), ".rfidShell")
try:
    readline.read_history_file(histfile)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)
del os, histfile

def defaultResultHandler(result):
    pass #print nothing
    #print str(result)        

class Command():
    
    def __init__(self,name,helpMessage,showInHelp,command,argChecker=None,resultHandler=defaultResultHandler):
        self.name = name
        self.helpMessage = helpMessage
        self.command = command
        self.argChecker = argChecker
        self.showInHelp = showInHelp
        self.resultHandler = resultHandler

class CommandExecuter():
    def __init__(self):
        self.envi = {}
        self.envi["prompt"] = ":>"
        self.levelTries = multiLevelTries()
        self.envi["levelTries"] = self.levelTries
        
    def addCommand(self,CommandStrings,showInHelp,com,argChecker=None,resultHandler=defaultResultHandler):
        name = ""
        for s in CommandStrings:
            name += s+""
        
        c = Command(name,com.__doc__,showInHelp,com,argChecker,resultHandler)
        try:
            self.levelTries.addEntry(CommandStrings,c)
            return c
        except triesException as e:
            print self.printOnShell(str(e))
            
    def addAlias(self,CommandStrings,AliasCommandStrings):
        #pas aussi simple
            #on doit pouvoir gerer des alias avec des arguments fixe
        
        pass #TODO
        
    def executeCommand(self,CommandStringsList):
        
        previousValue = None
        for indice in range(0,len(CommandStringsList)):
            CommandStrings = CommandStringsList[indice]
        
            #look after the command
            try:
                triesNode,args = self.levelTries.searchEntryFromMultiplePrefix(CommandStrings)
                commandToExecute = triesNode.value
            except triesException as e:
                print "   "+str(e)
                return
            
            #args est une liste
            
            #append the previous value to the args
            if previousValue != None:
                if isinstance(previousValue,list):
                    for item in previousValue:
                        args.append(item)
                else:
                    args.append(previousValue)
        
            #check the args
            if commandToExecute.argChecker != None:
                try:
                    argsValueDico = commandToExecute.argChecker.checkArgs(args)
                except argException as a:
                    print "   "+str(a)
                    return
            else:
                argsValueDico = {}
            
            #argsValueDico est un dico
            
            #parse the command to execute
            inspect_result = inspect.getargspec(commandToExecute.command)
        
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
                #elif argname == "previous":
                #    nextArgs["previous"] = previousValue
                else:              
                    if index < (len(inspect_result.args) - len(inspect_result.defaults)):
                        #on assigne a None
                        self.printOnShell("WARNING unknwon arg <"+str(argname)+"> in command "+commandToExecute.name)
                        nextArgs[argname] = None
                    else:
                        #Si c'est un argument avec une valeur par defaut, ne pas assigner  
                        nextArgs[argname] = inspect_result.defaults[index - (len(inspect_result.args) - len(inspect_result.defaults))]
        
                index += 1
                
            #call the function
            #TODO catch execution error
            
            try:
                result = commandToExecute.command(**nextArgs)
            except argExecutionException as aee:
                self.printOnShell(""+str(aee)+" at "+str(CommandStrings))
                return
            #TODO uncomment after debug
            #except Exception as ex:
            #    self.printOnShell("SEVERE : "+str(ex)+" at "+str(CommandStrings))
            #    return
            
            if indice == (len(CommandStringsList)-1):
                try:
                    commandToExecute.resultHandler(result) #last item
                except argExecutionException as aee:
                    self.printOnShell(""+str(aee)+" at "+str(CommandStrings))
                    return
                #TODO uncomment after debug
                #except Exception as ex:
                #    self.printOnShell("SEVERE : "+str(ex)+" at "+str(CommandStrings))
                #    return
            else:
                previousValue = result
        
    def mainLoop(self):
        while True:
            try:
                cmd = raw_input(self.envi["prompt"])
            except SyntaxError:
                print "   syntax error"
                continue
            except EOFError:
                print "\n   end of stream"
                break
            
            cmd = cmd.split("|")
            if len(cmd) < 0 :
                print "   split command error"
                continue
            
            innerCommand = []    
            for inner in cmd:
                inner = inner.strip(' \t\n\r')
                if len(inner) > 0:
                    inner = inner.split(" ")
                    if len(inner) < 0 :
                        print "   split command error"
                        innerCommand = []
                        break
                    
                    finalCmd = []
                    for cmd in inner:
                        cmd = cmd.strip(' \t\n\r')
                        if len(cmd) > 0 :
                            finalCmd.append(cmd)
                        
                    if len(finalCmd) > 0:
                        innerCommand.append(finalCmd)
            
            if len(innerCommand) < 1:
                continue
                    
            #print innerCommand
                        
                
            self.executeCommand(innerCommand)
    
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


###############################################################################################
##### ArgsChecker #############################################################################
###############################################################################################
class ArgsChecker():
    def __init__(self):
        pass
    
    #
    # @argsList, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList):
        pass
        
class DefaultArgsChecker(ArgsChecker):
    def __init__(self, argCheckerList):
        self.argCheckerList = OrderedDict(argCheckerList)
    
    def checkArgs(self,args):
        #check the arguments length
        if len(args) < len(self.argCheckerList):
            raise argException("Argument missing, expected "+str(len(self.argCheckerList))+", get "+str(len(args)))
        
        ret = OrderedDict()
        #check every argument
        #ret = []
        #for i in range(0,len(self.argCheckerList)):
        #    ret.append(self.argCheckerList[i].getValue(args[i],i))
        
        i=0
        for k in self.argCheckerList:
            ret[k] = self.argCheckerList[k].getValue(args[i],i)
            i += 1
        
        return ret
                
class MultiArgsChecker(ArgsChecker):
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
        
class AllTheSameChecker(ArgsChecker):
    def __init__(self, argChecker, argName,count=None):
        self.argChecker = argChecker
        self.count = count
        self.argName = argName
        
    def checkArgs(self,args):
        #check the arguments length
        if self.count != None:
            if len(args) < self.count:
                raise argException("Argument missing, expected "+str(self.count)+", get "+str(len(args)))
                
            limit = self.count
        else:
            limit = len(args)
        
        ret = []
        #check every argument
        for i in range(0,limit):
            ret.append(self.argChecker.getValue(args[i],i))
            
        return {self.argName:ret}
        
###############################################################################################
##### ArgChecker #############################################################################
###############################################################################################

class ArgChecker(object):
    
    #
    # @exception raise an argException if there is an error
    #   
    def checkValue(self,argNumber=None):
        pass
        
    def getValue(self,value,argNumber=None):
        self.checkValue(value)
        return value
        
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
        
class IntegerArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
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
            if argNumber != None:
                raise argException("(Integer) Argument "+str(argNumber)+" : this arg is not a valid integer")
            else:
                raise argException("(Integer) Argument : this arg is not a valid integer")
        
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
        self.checkValue(value)
        return int(super(IntegerArgChecker,self).getValue(value,argNumber))

class hexaArgChecker(ArgChecker):
    def __init__(self, minimum=0x00, maximum=0xFF):
        self.minimum = minimum
        self.maximum = maximum
    
    def checkValue(self, value,argNumber=None):
        if value == None:
            if argNumber != None:
                raise argException("(hexadecimal) Argument "+str(argNumber)+" : the integer arg can't be None")
            else:
                raise argException("(hexadecimal) Argument : the integer arg can't be None")
        
        if type(value) != int:
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

class tokenValueArgChecker(stringArgChecker):
    #TODO stocker les tokens dans un tries
    
    def __init__(self, tokenDico):
        #TODO if type(tokenDico) != dict
        
        self.tokenDico = tokenDico
    
    def checkValue(self, value,argNumber=None):
        super(tokenValueArgChecker,self).checkValue(value,argNumber)
            
        if value not in self.tokenDico:
            if argNumber != None:
                raise argException("(Token) Argument "+str(argNumber)+" : this arg is not a valid token")
            else:
                raise argException("(Token) Argument : this arg is not a valid token")
    
    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        
        return self.tokenDico[value]
                
Executer = CommandExecuter()

def stringListResultHandler(result):
    if result == None or len(result) == 0:
        Executer.printOnShell("no item available")
        return
        
    for i in result:
        Executer.printOnShell(i)
        
def printResultHandler(result):
    print str(result)

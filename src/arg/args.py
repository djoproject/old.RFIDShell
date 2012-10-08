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


from exception import argException
from tries.exception import triesException
from tries.multiLevelTries import multiLevelTries
import readline
import os
import sys

histfile = os.path.join(os.path.expanduser("~"), ".rfidShell")
try:
    readline.read_history_file(histfile)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)
del os, histfile

class Command():
    def __init__(self,name,helpMessage,showInHelp,command,argChecker=None):
        self.name = name
        self.helpMessage = helpMessage
        self.command = command
        self.argChecker = argChecker
        self.showInHelp = showInHelp

class CommandExecuter():
    def __init__(self):
        self.envi = {}
        self.envi["prompt"] = ":>"
        self.levelTries = multiLevelTries()
        self.envi["levelTries"] = self.levelTries
        
    def addCommand(self,CommandStrings,name,helpMessage,showInHelp,com,argChecker=None):
        c = Command(name,helpMessage,showInHelp,com,argChecker)
        try:
            self.levelTries.addEntry(CommandStrings,c)
        except triesException as e:
            print "   "+str(e)
        
    def executeCommand(self,CommandStrings):
        #look after the command
        try:
            triesNode,args = self.levelTries.searchEntryFromMultiplePrefix(CommandStrings)
            commandToExecute = triesNode.value
        except triesException as e:
            print "   "+str(e)
            return
        
        
        #check the args
        if commandToExecute.argChecker != None:
            try:
                argsValue = commandToExecute.argChecker.checkArgs(args)
            except argException as a:
                print "   "+str(a)
                return
        else:
            argsValue = []
        
        #call the function
        commandToExecute.command(self.envi,argsValue)
        
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
            
            cmd = cmd.split(" ")
            if len(cmd) < 0 :
                print "   split command error"
                continue
                
            #TODO retirer les commandes vide de la liste cmd
                
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

class ArgsChecker():
    def __init__(self):
        pass
    
    def checkArgs(self,args):
        return args
        
class DefaultArgsChecker(ArgsChecker):
    def __init__(self, argCheckerList):
        self.argCheckerList = argCheckerList
    
    def checkArgs(self,args):
        #check the arguments length
        if len(args) < len(self.argCheckerList):
            raise argException("Argument missing, expected "+str(len(self.argCheckerList))+", get "+str(len(args)))
        
        ret = []
        #check every argument
        for i in range(0,len(self.argCheckerList)):
            ret.append(self.argCheckerList[i].getValue(args[i],i))
            
        return ret
                
class MultiArgsChecker(ArgsChecker):
    def __init__(self, *argCheckerList):
        self.argCheckerList = argCheckerList

    def checkArgs(self,args):
        expectedCount = []
        
        for checkerList in self.argCheckerList:
            
            #TODO si un checker avec un bon nombre d'argument ne match pas, essayer les suivant
            if len(checkerList) == len(args):
                ret = []
                for i in range(0,len(checkerList)):
                    ret.append(checkerList[i].getValue(args[i],i))   
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
        

#######################################

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
    #TODO check hexa in forme FF or 0xFF
    pass

class tokenValueArgChecker(stringArgChecker):
    #TODO stocker les tokens dans un tries
    
    def __init__(self, tokenList):
        self.tokenList = tokenList
    
    def checkValue(self, value,argNumber=None):
        super(tokenValueArgChecker,self).checkValue(value,argNumber)
            
        if value not in self.tokenList:
            if argNumber != None:
                raise argException("(Token) Argument "+str(argNumber)+" : this arg is not a valid token")
            else:
                raise argException("(Token) Argument : this arg is not a valid token")
                
                
                
Executer = CommandExecuter()

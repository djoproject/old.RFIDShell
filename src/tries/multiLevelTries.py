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

from tries import *
from exception import triesException

class multiLevelTries():
    
    def __init__(self):
        self.levelOneTries = tries("")
    
    #
    #
    # @param commandStrings : array string of command
    # @param command : object to store
    #    
    def addEntry(self,commandStrings, command):
        
        #check commandStrings
        if commandStrings == None or type(commandStrings) != list or len(commandStrings) < 0:
            raise triesException("need string token to find a value, no token found")
        
        #search a similar commandString
        tries_tmp = self.levelOneTries
        for i in range(0,len(commandStrings)):
            tmp = tries_tmp.search(commandStrings[i])
            if tmp != None and tmp.value != None:
                if isinstance(tmp.value,tries) :
                    tries_tmp = tmp.value
                    continue
                #elif isinstance(tmp,commandShell) : #on ne sait pas encore ce qu'on va stocker dans le multitries
                #    raise triesException("a similar command chain already exists")
                else:
                    existingPath = ""
                    for k in range(0,i):
                        existingPath += commandStrings[k]
                        
                    raise triesException("can't insert a command here, another command already exists <"+existingPath+">")
            break
        
        #insert the new command string
        for j in range(i,len(commandStrings)-1):
            tries_tmp = tries_tmp.insert(commandStrings[j],tries("")).value
        else:
            j = len(commandStrings)-2
            
        tries_tmp.insert(commandStrings[j+1],command)
    
    def removeEntry(self,commandStrings):
        
        #check commandStrings
        if commandStrings == None or type(commandStrings) != list or len(commandStrings) < 0:
            raise triesException("need string token to find a value, no token found")
        
        #creer un tableau avec tous les tries composant la commande
        tries_tmp = self.levelOneTries
        tries_table = [self.levelOneTries]
        for i in range(0,len(commandStrings)):
            tmp = tries_tmp.searchUniqueFromPrefix(commandStrings[i])
            
            if tmp != None and tmp.value != None:
                if isinstance(tmp.value,tries) :
                    tries_tmp = tmp.value
                    tries_table.append(tries_tmp)
                    continue
                else:
                    if i == len(commandStrings)-1:
                        break
                    
                    raise triesException("the command string doesn't exist")
            else:
                raise triesException("unknown chain in level "+str(i)+" <"+commandStrings[i]+">")
        
        #on retire les elements du bas vers le haut
        for i in range(0,len(tries_table)):
            indice = len(tries_table)-1-i
            
            #le tries ne contient qu'un element?
            if tries_table[indice].countValue() == 1:
                if indice == 0:
                    tries_table[indice].remove(commandStrings[indice])
                else:
                    continue #on propage la suppression au noeud parent
            else:
                #supprimer la cle du tries
                tries_table[indice].remove(commandStrings[indice])
                break
    
    def updateEntry(self, commandStrings, newValue):
        node, args = self.searchEntry(commandStrings)
        node.value = newValue
    
    #
    # 
    # TODO difference avec searchEntryFromMultiplePrefix?
    #
    def searchEntry(self, commandStrings):
        return self.searchEntry(commandStrings)
    
    #
    #
    #
    def searchEntryFromMultiplePrefix(self,commandStrings,returnTriesValue = False):
        #check commandStrings
        if commandStrings == None or type(commandStrings) != list or len(commandStrings) < 0:
            raise triesException("need string token to find a value, no token found")
        
        #search string
        tries_tmp = self.levelOneTries
        for i in range(0,len(commandStrings)):
            tmp = tries_tmp.searchUniqueFromPrefix(commandStrings[i])
            
            if tmp != None and tmp.value != None:
                if isinstance(tmp.value,tries) :
                    tries_tmp = tmp.value
                    continue
                else:
                    return tmp,commandStrings[(i+1):]
            else:
                raise triesException("unknown chain in level "+str(i)+" <"+commandStrings[i]+">")
        
        if not returnTriesValue:
            raise triesException("uncomplete command")
            
        return tries_tmp,[]
    
    def __repr__(self):
        return repr(self.levelOneTries)
        
  
def buildDictionnary(current,stringStack = []):
    ret = {}
    #print current.key
    #print current.childs
    if current.value != None:
        if isinstance(current.value,tries):
            stringStack.append(current.getCompleteName())
            ret.update(buildDictionnary(current.value,stringStack))
            stringStack.pop()
        else:
            key = ""
            for s in stringStack:
                key += s+" "
            #print key
            key += current.getCompleteName()
            #print key
            ret[key] = current.value
            
    for child in current.childs:
        #print child.key
        ret.update(buildDictionnary(child))
            
    return ret
    
        
















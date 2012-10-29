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

#
# kind of node : "Value Node" (self.value != None) or "None node" (self.value == None)
# key properties  : all node has a key with at most 1 character
# intermediate node properties : a None node is always an intermediate node, never an end node. A Value node is a Value node or a None node
# end node properties : all the end node are Value node
# child properties : a None node has at least two children, a value node has zero or more child even if it is an intermediate node
#
# TODO verifier si tout fonctionne avec une racine differente de ""
#

from exception import triesException

def noneFunc(*args):
    return None

def charInCommons(char1, char2):
    common = 0
    for i in range(0,min(len(char1),len(char2))):
        if char1[i] != char2[i]:
            break
        common += 1
    
    return common

class tries():
    
    #
    #
    #
    def __init__(self, key, parent = None, value = None):
        #print "{"+key+"}"
        #if key == None or type(key) != str or len(key) == 0:
        #    raise triesException("the inserted key must be a string with a length bigger than zero")
        
        self.key = key
        self.childs = []
        self.value = value
        self.parent = parent
    
    #
    #
    #
    def remove(self, key):

        def exact(Node,prefix):
            return Node
        
        Node = self.searchNode(key,exact)
        if Node != None and Node.value != None:
            
            if Node.parent == None:
                if len(Node.key) > 0:
                    for child in Node.childs:
                        child.key = Node.key + child.key
                        
                    Node.key = ""
                Node.value = None

            elif len(Node.childs) == 1:
                Node.childs[0].key = Node.key + Node.childs[0].key
                Node.parent.childs.remove(Node)
                Node.parent.childs.append(Node.childs[0])
                Node.childs[0].parent = Node.parent
                del Node
                
            elif len(Node.childs) > 1:
                Node.value = None
                
            else: #len(Node.childs) == 0                
                Node.parent.childs.remove(Node)

                #cas limite, a t'on un parent None Node desequilibre?
                parent = Node.parent
                if parent.value == None and len(parent.childs) == 1:
                    
                    parent.childs[0].key = parent.key + parent.childs[0].key

                    #on est a la racine?
                    if parent.parent == None:
                        parent.key = ""
                    else:
                        parent.parent.childs.remove(parent)
                        parent.parent.childs.append(parent.childs[0])
                        parent.childs[0].parent = parent.parent
                        del parent
                del Node
            return
            
        raise triesException("key not found")
        
    #
    #
    #
    def update(self, key, newValue):

        def exact(Node,prefix):
            return Node
            
        Node = self.searchNode(key,exact)
        if Node != None and Node.value != None:
            Node.value = newValue
            return Node
            
        raise triesException("key not found")
            
            
        
    #
    # @return the inserted node
    # @exception triesException if insertion failed
    #  
    def insert(self,key, value):
        
        if value == None:
            raise triesException("the inserted value can't be none")
        
        def exact(Node,key):
            if Node.value != None : #is it a value node?
                raise triesException("the inserted key already exists")

            return Node
            
        def partial(Node,key,count,totalCount):
            tempTries        = tries(Node.key[count:], Node, Node.value)
            tempTries.childs = Node.childs
            
            for child in tempTries.childs:
                child.parent = tempTries
            
            tempTries.value  = Node.value
            
            Node.key    = Node.key[:count]

            #le noeud courant recupere la nouvelle valeur
            #Node.value  = value
            Node.childs = [tempTries]
            
            return Node

            
        def noMatchChild(Node,key,totalCount):
            newNode = tries(key[totalCount:],Node)
            Node.childs.append(newNode)
            return newNode
            
        def false(Node,key,count,totalCount):
            tempTries        = tries(Node.key[count:], Node, Node.value)
            tempTries.childs = Node.childs
            
            for child in tempTries.childs:
                child.parent = tempTries
            
            tempTries.value  = Node.value
            
            Node.key         = Node.key[:count]
            
            #creation du nouveau noeud
            newTries         = tries(key[totalCount:], Node)
        
            #mise a jour du noeud courant, non value node, devient un noeud pivot
            Node.childs      = [tempTries,newTries]
            Node.value       = None
            
            return newTries
            
        Node = self.searchNode(key,exact,partial,noMatchChild,false)
        Node.value = value
        return Node
    
    #
    # @return any kind of node
    #                
    def search(self,key):
        def exact(Node,key):
            return Node
            
        return self.searchNode(key,exact)
    
    #
    # @return a value node
    #    
    def searchUniqueFromPrefix(self,prefix):
        def exact(Node,prefix):
            if Node.value != None:
                return Node
            
            #if the current node has a None value, it's an intermediate node with at most two children
            raise triesException("the prefix <"+str(prefix)+"> corresponds to multiple node")
        
        def partial(Node,prefix,count,totalCount):
            return exact(Node,prefix)
        
        return self.searchNode(prefix,exact,partial)
        
        
    #
    # @return a dictionnary with all the key/value or None if there is no result
    #
    def getKeyListFromPrefix(self,prefix):
        def exact(Node,prefix):
            return Node.getAllPossibilities()
            
        def partial(Node,prefix,count,totalCount):
            return Node.getAllPossibilities()
            
        return self.searchNode(prefix,exact,partial)
    
    #
    #
    #
    def searchNode(self,prefix,exactResult,partialResult = noneFunc, noMatchChild = noneFunc, falseResult = noneFunc):
        #must be a valid string
        if prefix == None or type(prefix) != str or len(prefix) == 0:
            raise triesException("the searched key must be a string with a length bigger than zero")
        
        currentNode   = self
        currentPrefix = prefix
        totalCount    = 0
        while True:
            #count the common char with this node key   
            count       = charInCommons(currentNode.key, currentPrefix) 
            totalCount += count

            #the current key node is completly used
            if count == len(currentNode.key):
                #valide string and end node
                if len(currentPrefix) == count:
                    return exactResult(currentNode,prefix) # bear = bear #perfect concordance, prefix is equal to a prefix in the tree
                    
                #else count < len(self.key):
                        
                currentPrefix = currentPrefix[len(currentNode.key):]
                for child in currentNode.childs:
                    if child.canPropagate(currentPrefix):
                        currentNode = child
                        break
                else:        
                    return noMatchChild(currentNode,prefix,totalCount) # bearor > bear
                
            else: #count < len(self.key)
            
                if len(currentPrefix) == count:
                    return partialResult(currentNode,prefix,count,totalCount) # be < bear #partial match, prefix is a part of a prefix in the tree
                
                return falseResult(currentNode,prefix,count,totalCount) # bee != bear
            
                
    
    #
    # build a dictionnary (key + value) with all the combinatories possible from this node
    #
    # TODO convert en non recursif
    #
    # @return a set of string
    #
    def getAllPossibilities(self, dico = {}):
        dico[self.getCompleteName()] = self.value
        
        for child in self.childs:
            child.getAllPossibilities(dico)
            
        return dico
    
    #
    # this methode compute the bigger number of child of all the current node childs 
    #
    # @return an integer bigger or equal to zero
    #
    def getMaxChildCount(self):
        m = len(self.childs)
        
        if self.value != None:
            m += 1
        
        for child in self.childs:
            m = max(m,child.getMaxChildCount)

        return m
    
    #    
    # this methode identify if the current node is an end node or not
    #
    # @return True if the current node is an end node, return False otherwise 
    #        
    def isFinalNode(self):
        return len(self.child) == 0  
        
    #
    #
    #
    def canPropagate(self, key):
        return len(self.key) == 0 or len(key) == 0 or self.key[0] == key[0]

    #
    # TODO convert en non recursif
    #
    def traversal(self,level = 0):
        s = ""
        for i in range(0,level):
            s+= " "

        s = s+"{"+self.key+"}"
        s += repr(self)

        for child in self.childs :
            s += "\n" + child.traversal(level+1)

        return s
        
                
            

    #
    #
    #
    def __repr__(self):
        
        if self.value == None:
            if self.parent == None:
                return "none node (key = \""+self.key+"\", completeName = "+self.getCompleteName()+", parent = None, child count = "+str(len(self.childs))+")"
            else:
                return "none node (key = \""+self.key+"\", completeName = "+self.getCompleteName()+", parent = \""+self.parent.key+"\", child count = "+str(len(self.childs))+")"
        else:
            if self.parent == None:
                return "tries node (key = \""+self.key+"\", value = \""+str(self.value)+"\", completeName = "+self.getCompleteName()+", parent = None, child count = "+str(len(self.childs))+")"
            else:
                return "tries node (key = \""+self.key+"\", value = \""+str(self.value)+"\", completeName = "+self.getCompleteName()+", parent = \""+self.parent.key+"\", child count = "+str(len(self.childs))+")"

    #
    #
    #
    def getCompleteName(self):
        node = self
        s = ""

        while node != None:            
            s = node.key + s
            node = node.parent

        return s
        
    #
    #
    #
    def isEmptyTries(self):
        return len(self.childs) == 0 and self.value == None
    
    def countValue(self):
        if self.value != None:
            count = 1
        else:
            count = 0
        
        for c in self.childs:
            count += c.countValue()
            
        return count
    
    #TODO faire les equals, hash, etc..
        
        
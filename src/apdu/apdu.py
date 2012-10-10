#!/usr/bin/python2.6
from smartcard.util import toHexString

#
# this class is an abstract prototype to all apdu sent to any card reader/writer
#
class Apdu(object):
    "apdu abstract class"
    def __init__(self):
        pass
        
    def getSize(self):
        "return the length of the command"
        pass
        
    def toHexArray(self):
        "return the command into a byte array"
        pass
        
class ApduDefault(Apdu):
    "apdu abstract class"
    def __init__(self,cla,ins,p1,p2,data=[],expected_answer=0):
        self.table = [cla,ins,p1,p2]
        
        if len(data) > 0:
            self.table.append(len(data))
            self.table.extend(data)
        
        self.table.append(expected_answer)

    def getSize(self):
        "return the length of the command"
        return len(self.table)

    def toHexArray(self):
        "return the command into a byte array"
        return self.table
        
    def __str__(self):
        return toHexString(self.table)
        
class ApduRaw(Apdu):
    def __init__(self,rawByte):
        self.rawByte = rawByte
    def getSize(self):
        "return the length of the command"
        return len(self.rawByte)

    def toHexArray(self):
        "return the command into a byte array"
        return self.rawByte
        
    def __str__(self):
        return toHexString(self.table)
        
class ApduPn53x(object):
    def __init__(self,ins,data = []):
        self.table = [0xD4,ins]
        if len(data) > 0:
            self.table.extend(data)
            
    def getSize(self):
        "return the length of the command"
        return len(self.table)

    def toHexArray(self):
        "return the command into a byte array"
        return self.table

    def __str__(self):
        return toHexString(self.table)
        

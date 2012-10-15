#!/usr/bin/python2.6
from string import rstrip

PACK = 1
HEX = 2
UPPERCASE = 4
COMMA = 8

def toHexString(bytes=[], format=0):
    for byte in tuple(bytes): 
        pass 

    if not isinstance(bytes,list): 
        raise TypeError, 'not a list of bytes' 

    if bytes == None or bytes == []: 
        return "" 
    else: 
        pformat = "%-0.2X" 
        if COMMA & format: 
            pformat = pformat + "," 
        pformat = pformat + " " 
        if PACK & format: 
            pformat = rstrip(pformat) 
        if HEX & format: 
            if UPPERCASE & format: 
                pformat = "0X" + pformat 
            else: 
                pformat = "0x" + pformat 
                    
        return rstrip(rstrip(reduce(lambda a, b: a + pformat % ((b + 256) % 256), [""] + bytes)), ',')

#
# this class is an abstract prototype to all apdu sent to any card reader/writer
#
class Apdu(list):
    "apdu abstract class"
    #def __init__(self):
    #    pass
        
    def getSize(self):
        "return the length of the command"
        return len(self)
        
    def toHexArray(self):
        "return the command into a byte array"
        return self
    
    def __str__(self):
        return toHexString(self)
        
class ApduDefault(Apdu):
    "apdu abstract class"
    def __init__(self,cla,ins,p1,p2,data=[],expected_answer=0):
        self.extend([cla,ins,p1,p2])
        
        if len(data) > 0:
            self.append(len(data))
            self.extend(data)
        
        self.append(expected_answer)

    #def getSize(self):
    #    "return the length of the command"
    #    return len(self.table)

    #def toHexArray(self):
    #    "return the command into a byte array"
    #    return self.table
        
class ApduRaw(Apdu):
    def __init__(self,rawByte):
        self.extend(rawByte)
        
    #def getSize(self):
    #    "return the length of the command"
    #    return len(self.rawByte)

    #def toHexArray(self):
    #    "return the command into a byte array"
    #    return self.rawByte
        
    #def __str__(self):
    #    return toHexString(self.table)
        

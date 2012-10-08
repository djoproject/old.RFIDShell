#!/usr/bin/python2.6

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
        self.table = [cla,ins,p1,p2,len(data)]
        self.table.extend(data)
        if len(data) > 0:
            self.table.append(expected_answer)

    def getSize(self):
        "return the length of the command"
        return len(self.table)

    def toHexArray(self):
        "return the command into a byte array"
        return self.table
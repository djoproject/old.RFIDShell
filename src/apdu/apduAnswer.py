#!/usr/bin/python2.6
from apdu import Apdu,toHexString

class ApduAnswer(Apdu):
    def __init__(self,sw1,sw2,data=[]):
        self.sw1 = sw1
        self.sw2 = sw2
        self.extend(data)
        
    def __str__(self):
        return "sw1=%X, sw2=%X, data="%(self.sw1,self.sw2)+toHexString(self)

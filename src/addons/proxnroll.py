#!/usr/bin/python2.6
from arg.args import *
from keyList import keys
from apdu.apdu import ApduDefault

class Proxnroll(object):
    colorOFF   = 0x00
    colorON    = 0x01
    colorSLOW  = 0x02
    colorAUTO  = 0x03
    colorQUICK = 0x04
    colorBEAT  = 0x05
    
    def __init__(self):
        pass
        
    def setLedColorFun(self,red,green,yellow_blue = None):
        #TODO check value
        
        if yellow_blue == None:
            d = [0x1E,red,green]
        else:
            d = [0x1E,red,green,yellow_blue]
        
        return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=0x00,data=d)
        
    def setBuzzerDuration(self,duration):
        #TODO check value
        
        lsb = duration&0xFF
        msb = (duration>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=0x00,data=[0x1C,msb,lsb])
        
    def test(self, expected_answer_size = 0,delay_to_answer=0, datas = []):
        
        if expected_answer_size < 0 or expected_answer_size > 255:
            pass #TODO
            
        if delay_to_answer < 0 or delay_to_answer > 63:
            pass #TODO
            
        if len(datas) < 0 or len(datas) > 255:
            pass #TODO
        
        return ApduDefault(cla=0xFF,ins=0xFD,p1=0x00,p2=0x00,data=[0x1C,msb,lsb])

DefaultProxnroll = Proxnroll()

def setLedColorFun(envi,args):
    
    def convertTokentToCode(a):
        if a == "off":
            return Proxnroll.colorOFF
        elif a == "on":
            return Proxnroll.colorON
        elif a == "slow":
            return Proxnroll.colorSLOW
        #elif a == "auto":
        #    d.append(0x03)
        elif a == "quick":
            return Proxnroll.colorQUICK
        elif a == "beat":
            return Proxnroll.colorBEAT
        else:  
            return Proxnroll.colorAUTO
    
    
    if len(args) > 2:
        apdu = DefaultProxnroll.setLedColorFun(convertTokentToCode(args[0]),convertTokentToCode(args[1]),convertTokentToCode(args[2]))
    else:
        apdu = DefaultProxnroll.setLedColorFun(convertTokentToCode(args[0]),convertTokentToCode(args[1]))
    
    data, sw1, sw2 = envi["connection"].transmit(apdu.toHexArray())
    print "%x %x" % (sw1, sw2)
    
def setBuzzerDuration(envi,args):    
    if len(args) == 0:
        duration = 0
    else:
        duration = args[0]

    apdu = DefaultProxnroll.setBuzzerDuration(duration)
    data, sw1, sw2 = envi["connection"].transmit(apdu.toHexArray())
    print "%x %x" % (sw1, sw2)

def testInstruction():
    pass
    
#TODO faire un erreur manager    

t = tokenValueArgChecker(["off","on","auto","slow","quick","beat"])
Executer.addCommand(["proxnroll","setlight"],"proxnroll setlight","",True,setLedColorFun,MultiArgsChecker([t,t],[t,t,t]))
i0to60000 = IntegerArgChecker(0,60000)
Executer.addCommand(["proxnroll","setbuzzer"],"proxnroll setbuzzer","",True,setBuzzerDuration,MultiArgsChecker([],[i0to60000]))
Executer.addCommand(["proxnroll","test"],"proxnroll test instruction","",True,testInstruction)

#TODO encapsulate instruction pmd841p-ea.pdf page 10/64








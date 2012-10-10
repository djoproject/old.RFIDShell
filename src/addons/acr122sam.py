#!/usr/bin/python2.6
from arg.args import *
from apdu.apduExecuter import Executer
from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.apdu import ApduDefault
from apdu.exception import apduBuilderException

class acr122SamAPDUBuilder(iso7816_4APDUBuilder):        
    def directTransmit(self,datas):
        if len(datas) < 1 or len(datas) > 255:
            raise apduBuilderException("invalid datas size, must be a list from 1 to 255 item, got "+str(len(datas)))
        
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x00,p2=0x00,data=datas)
    
    def getResponse(self,Length):
        
        if Length < 1 or Length > 255:
            raise apduBuilderException("invalid argument Length, must be a value between 1 and 255, got "+str(Length))
            
        return ApduDefault(cla=0xFF,ins=0xC0,p1=0x00,p2=0x00,expected_answer=Length)
    
    LinkToBuzzerOff = 0x00
    LinkToBuzzerDuringT1 = 0x01
    LinkToBuzzerDuringT2 = 0x02
    LinkToBuzzerDuringT1AndT2 = 0x03
    
    def ledAndBuzzerControl(self,initialRed,initialGreen,finalRed,finalGreen,T1Duration,T2Duration,Repetition,LinkToBuzzer):
        P2 = 0
        
        if finalRed != None:
            if finalRed:
                P2 |= 0x01
            P2 |= 0x04
        
        if finalGreen != None:
            if finalGreen:
                P2 |= 0x02
            P2 |= 0x08
        
        if initialRed != None:
            if initialRed:
                P2 |= 0x10
            P2 |= 0x40
            
        if initialGreen != None:
            if initialGreen:
                P2 |= 0x20
            P2 |= 0x80    
            
        if T1Duration < 1 or T1Duration > 255:
            raise apduBuilderException("invalid argument T1Duration, must be a value between 1 and 255, got "+str(T1Duration))
        
        if T2Duration < 1 or T2Duration > 255:
            raise apduBuilderException("invalid argument T2Duration, must be a value between 1 and 255, got "+str(T2Duration))
        
        if Repetition < 1 or Repetition > 255:
            raise apduBuilderException("invalid argument Repetition, must be a value between 1 and 255, got "+str(Repetition))
            
        if LinkToBuzzer < 0 or LinkToBuzzer > 3:
            raise apduBuilderException("invalid argument LinkToBuzzer, must be a value between 0 and 4, got "+str(LinkToBuzzer))
            
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x40,p2=P2,data=[T1Duration,T2Duration,Repetition,LinkToBuzzer])
        
    def getFirmwareVersion(self):
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x48,p2=0x01)

defaultACRSam = acr122SamAPDUBuilder()
        

def firmwareVersion(envi,args):
    Executer.executeAPDUAndConvertDataToString(defaultACRSam.getFirmwareVersion())
    
def transmit(envi,args):
    Executer.executeAPDUAndPrintDataAndSW(defaultACRSam.directTransmit(args))

def response(envi,args):
    a = defaultACRSam.getResponse(args[0])
    print a
    Executer.executeAPDUAndPrintDataAndSW(a)
    
def ledAndBuzzer(envi,args):
    
    tab = []
    for i in range(0,4):
        if args[i] == "off":
            tab.append(False)
        elif args[i] == "on":
            tab.append(True)
        else:
            tab.append(None)
    
    if args[7] == "off":
        value = acr122SamAPDUBuilder.LinkToBuzzerOff
    elif args[7] == "t1":
        value = acr122SamAPDUBuilder.LinkToBuzzerDuringT1
    elif args[7] == "t2":
        value = acr122SamAPDUBuilder.LinkToBuzzerDuringT2
    else:
        value = acr122SamAPDUBuilder.LinkToBuzzerDuringT1AndT2
        
    Executer.executeAPDU(defaultACRSam.ledAndBuzzerControl(tab[0],tab[1],tab[2],tab[3],args[4],args[5],args[6],value))
    
    

i = IntegerArgChecker(1,255)
Executer.addCommand(["acr122","firmware"],"acr122 firmware version","",True,firmwareVersion)
Executer.addCommand(["acr122","transmit"],"acr122 transmit data to pn532","",True,transmit,AllTheSameChecker(hexaArgChecker()))
Executer.addCommand(["acr122","response"],"acr122 get response from pn532","",True,response,DefaultArgsChecker([i]))

t = tokenValueArgChecker(["off","on","default"])
t2 = tokenValueArgChecker(["off","t1","t2","both"])
Executer.addCommand(["acr122","ledbuzzer"],"acr122 manage led and buzzer","",True,ledAndBuzzer,DefaultArgsChecker([t,t,t,t,i,i,i,t2]))




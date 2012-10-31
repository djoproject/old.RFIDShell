#!/usr/bin/python2.6
from apdu.apduExecuter import *
from arg.args import *
from arg.argchecker import *

from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.apdu import ApduDefault
from apdu.exception import apduBuilderException
from smartcard.sw.SWExceptions import CheckingErrorException


acr122SW = {
    0x61:(None, 
        {0x00: "Sucess !!!",
         None: "Bytes available : "}),
    0x63:(CheckingErrorException, 
        {0x00: "Operation failed",
         0x01: "Timeout Error : the card does not answer",
         0x27: "The checksum of the Contactless Response is wrong",
         0x7F: "The PN532_Contactless Command is wrong."})
}
#TODO load somewhere

class acr122SamAPDUBuilder(iso7816_4APDUBuilder):
    
    @staticmethod       
    def directTransmit(args):
        "acr122 transmit data to pn532"
        
        if len(args) < 1 or len(args) > 255:
            raise apduBuilderException("invalid args size, must be a list from 1 to 255 item, got "+str(len(datas)))
        
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x00,p2=0x00,data=args)
    
    @staticmethod
    def getResponse(Length):
        "acr122 get response from pn532"
        
        if Length < 1 or Length > 255:
            raise apduBuilderException("invalid argument Length, must be a value between 1 and 255, got "+str(Length))
            
        return ApduDefault(cla=0xFF,ins=0xC0,p1=0x00,p2=0x00,expected_answer=Length)
    
    LinkToBuzzerOff = 0x00
    LinkToBuzzerDuringT1 = 0x01
    LinkToBuzzerDuringT2 = 0x02
    LinkToBuzzerDuringT1AndT2 = 0x03
    
    @staticmethod
    def ledAndBuzzerControl(initialRed,initialGreen,finalRed,finalGreen,T1Duration,T2Duration,Repetition,LinkToBuzzer):
        "acr122 manage led and buzzer"
        
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
    
    @staticmethod
    def getFirmwareVersion():
        "acr122 firmware version"
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x48,p2=0x01)
        
def acr122execute(args):
    apdu = acr122SamAPDUBuilder.directTransmit(args)
    
    apduAnswer = executeAPDU(apdu)
    
    if apduAnswer.sw1 == 0x61:
        apdu = acr122SamAPDUBuilder.getResponse(apduAnswer.sw2)
        return executeAPDU(apdu)
    else:
        pass #TODO
    
i = IntegerArgChecker(1,255)

Executer.addCommand(CommandStrings=["acr122","firmware"],   preProcess=acr122SamAPDUBuilder.getFirmwareVersion ,process=executeAPDU,                                                            postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["acr122","transmit"],   preProcess=acr122SamAPDUBuilder.directTransmit     ,process=executeAPDU,    argChecker=AllTheSameChecker(hexaArgChecker(),"args"))
Executer.addCommand(CommandStrings=["acr122","response"],   preProcess=acr122SamAPDUBuilder.getResponse        ,process=executeAPDU,    argChecker=DefaultArgsChecker([("Length",i)]),          postProcess=resultHandlerAPDUAndPrintDataAndSW)

t = tokenValueArgChecker({"off":False,"on":True,"default":None})
t2 = tokenValueArgChecker({"off":acr122SamAPDUBuilder.LinkToBuzzerOff,"t1":acr122SamAPDUBuilder.LinkToBuzzerDuringT1,"t2":acr122SamAPDUBuilder.LinkToBuzzerDuringT2,"both":acr122SamAPDUBuilder.LinkToBuzzerDuringT1AndT2})

Executer.addCommand(CommandStrings=["acr122","ledbuzzer"],  preProcess=acr122SamAPDUBuilder.ledAndBuzzerControl ,process=executeAPDU,   argChecker=DefaultArgsChecker([("initialRed",t),("initialGreen",t),("finalRed",t),("finalGreen",t),("T1Duration",i),("T2Duration",i),("Repetition",i),("LinkToBuzzer",t2)]))
Executer.addCommand(CommandStrings=["acr122","execute"],    preProcess=acr122execute                            ,process=executeAPDU,   argChecker=AllTheSameChecker(hexaArgChecker(),"args"),  postProcess=printResultHandler)



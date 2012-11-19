#!/usr/bin/python2.6
from arg.args import Executer
from arg.argchecker import *

from apdu.apduExecuter import *

from apdu.apdu import ApduDefault,ApduRaw
from apdu.exception import apduBuilderException,apduAnswserException
from addons.iso7816_4 import iso7816_4APDUBuilder
from arg.resultHandler import printResultHandler

def omnikeyExecute(envi,args):
    #TODO manage when the pyscard wrapper is not patched

    return executeAPDU(envi,ApduRaw(args),"omnikey")

class omnikeyAPDUBuilder(iso7816_4APDUBuilder):
    
    @staticmethod 
    def getDataCardSerialNumber():
        return iso7816_4APDUBuilder.getDataCA(0x00,0x00)
    
    #TODO pas d'ATR ?
    
    @staticmethod
    def mifareIncrement(address,value = 0):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 65535 was expected, got "+str(address))
            
        if value < 0 or value > 0xffffffff:
            raise apduBuilderException("invalid argument value, a value between 0 and "+str(0xffffffff)+" was expected, got "+str(value))
    
        lsb = address&0xFF
        msb = (address>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xD4,p1=msb,p2=lsb,data=[value&0xff , (value>>8)&0xff , (value>>16)&0xff , (value>>24)&0xff])
    
    @staticmethod
    def mifareDecrement(address,value = 0):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 65535 was expected, got "+str(address))
            
        if value < 0 or value > 0xffffffff:
            raise apduBuilderException("invalid argument value, a value between 0 and "+str(0xffffffff)+" was expected, got "+str(value))
    
        lsb = address&0xFF
        msb = (address>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xD8,p1=msb,p2=lsb,data=[value&0xff , (value>>8)&0xff , (value>>16)&0xff , (value>>24)&0xff])
    
    
    @staticmethod
    def openGenericSession():
        return ApduDefault(cla=0xFF,ins=0xA0,p1=0x00,p2=0x07,data=[0x01 , 0x00 , 0x01])
        
    @staticmethod
    def closeGenericSession():
        return ApduDefault(cla=0xFF,ins=0xA0,p1=0x00,p2=0x07,data=[0x01 , 0x00 , 0x02])
        
    @staticmethod
    def sendCommandGenericSession(Cmd):
        if len(Cmd) < 1 or len(Cmd) > 249:
            raise apduBuilderException("invalid Cmd size, must be a list from 1 to 249 item, got "+str(len(Cmd)))
            
        d = [0x01, 0x00,0xF3, 0x00, 0x00, 0x64]
        d.extend(Cmd)
        return ApduDefault(cla=0xFF,ins=0xA0,p1=0x00,p2=0x05,data=[0x01 , 0x00 , 0x02])
    
    #TODO faire un loadkey
    
    
    #ICLASS
    @staticmethod
    def iclassSelectPage():
        pass #TODO
        
    def iclassLoadKey():
        pass #TODO
        
    def iclassGetKeySlotInfo(KeySlot=0,Secured=False):
        
        if KeySlot < 0 or KeySlot > 255:
            raise apduBuilderException("invalid argument KeySlot, a value between 0 and 255 was expected, got "+str(address))
        
        if Secured:
            return ApduDefault(cla=0x84,ins=0xC4,p1=0x00,p2=KeySlot,data=[])
        else:
            return ApduDefault(cla=0x80,ins=0xC4,p1=0x00,p2=KeySlot,data=[])
        
    def iclassAutenticate():
        pass #TODO
        
    def iclassRead():
        pass #TODO
        
    def iclassUpdate():
        pass #TODO
    
    #ICLASS secure part
    def iclassSecureManageSession():
        pass #TODO
        
    def iclassSecureUpdateCardKey():
        pass #TODO
        
    #ISO15693
    def iso15693GetData():
        pass #TODO
        
    def iso15693PutData():
        pass #TODO
        
    def iso15693Lock():
        pass #TODO
        
    def iso15693GetSecurityStatus():
        pass #TODO
        
    def iso15693ReadBinary():
        pass #TODO
        
    def iso15693UpdateBinary():
        pass #TODO
        
    def iso15693UpdateSingleByte():
        pass #TODO
        
    
    
try:
    Executer
except NameError:
    print "  No variable Executer found, this is an addon, it can't be executed alone"
    exit()
        
               
Executer.addCommand(CommandStrings=["omnikey","card","serial"],preProcess=omnikeyAPDUBuilder.getDataCardSerialNumber,       process=executeAPDU,postProcess=resultHandlerAPDUAndPrintData)
#Executer.addCommand(CommandStrings=["proxnroll","read"],       preProcess=omnikeyAPDUBuilder.readBinary,process=executeAPDU,argChecker=DefaultArgsChecker([("address",i)],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["omnikey","apdu"],         process=omnikeyExecute,argChecker=AllTheSameChecker(hexaArgChecker(),"args"),postProcess=printResultHandler)




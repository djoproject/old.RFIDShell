#!/usr/bin/python2.6

from arg.args import *
from arg.argchecker import *

from apdu.apduExecuter import *
from apdu.apdu import Apdu
from apdu.exception import apduBuilderException

class ApduMifareUltralight(Apdu):
    def __init__(self,ins,param,data = []):
        self.extend([ins,param])
        if len(data) > 0:
            self.extend(data)

class MifareUltralightAPDUBuilder(object):
    
    @staticmethod
    def REQA():
        pass #TODO
        
    @staticmethod
    def WUPA():
        pass #TODO
    
    @staticmethod
    def Anticollision_level1():
        pass #TODO

    @staticmethod
    def Select_level1():
        pass #TODO
        
    @staticmethod
    def Anticollision_level2():
        pass #TODO

    @staticmethod
    def Select_level2():
        pass #TODO
    
    @staticmethod
    def Halt():
        return ApduMifareUltralight(ins=0x50,param=0x00)
    
    @staticmethod
    def readSector(address=0):
        if address < 0 or address > 0x0F:
            raise apduBuilderException("invalid argument address, a value between 0 and 15 was expected, got "+str(address))
        
        return ApduMifareUltralight(ins=0x30,param=(address&0xFF))
    
    @staticmethod
    def writeSector(datas, address=0):
        if address < 0 or address > 0x0F:
            raise apduBuilderException("invalid argument address, a value between 0 and 15 was expected, got "+str(address))
        
        if len(datas) != 4:
            raise apduBuilderException("invalid datas size, must be a list with 4 item, got "+str(len(datas)))
        
        return ApduMifareUltralight(ins=0xA2,param=(address&0xFF),data=datas)
    
    @staticmethod
    def CompatibilityWrite(datas, address=0):
        if address < 0 or address > 0x0F:
            raise apduBuilderException("invalid argument address, a value between 0 and 15 was expected, got "+str(address))
        
        if len(datas) != 4:
            raise apduBuilderException("invalid datas size, must be a list with 4 item, got "+str(len(datas)))
        
        datas.extend([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        return ApduMifareUltralight(ins=0xA0,param=(address&0xFF),data=datas)
        
try:
    Executer
except NameError:
    print "  No variable Executer found, this is an addon, it can't be executed alone"
    exit()
    
i = IntegerArgChecker(0,0x0F)
Executer.addCommand(CommandStrings=["mifareultralight","read"],     preProcess=MifareUltralightAPDUBuilder.readSector,  process=executeAPDU,argChecker=DefaultArgsChecker([("address",i)],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["mifareultralight","update"],   preProcess=MifareUltralightAPDUBuilder.writeSector, process=executeAPDU,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("address",i)],exactLimitChecker(0x04)))
Executer.addCommand(CommandStrings=["mifareultralight","compatibility","update"],   preProcess=MifareUltralightAPDUBuilder.writeSector, process=executeAPDU,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("address",i)],exactLimitChecker(0x04)))
Executer.addCommand(CommandStrings=["mifareultralight","halt"],     preProcess=MifareUltralightAPDUBuilder.Halt,  process=executeAPDU)









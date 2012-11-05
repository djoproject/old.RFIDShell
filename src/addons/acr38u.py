#!/usr/bin/python2.6

from arg.args import Executer
from arg.argchecker import *

from apdu.apdu import ApduDefault
from apdu.exception import apduBuilderException

class acr38uAPDUBuilder(iso7816_4APDUBuilder):
    
    TYPE_AUTO           = 0x00
    TYPE_I2C_1KTO16K    = 0x01
    TYPE_I2C_32KTO1024K = 0x02
    TYPE_AT88SC153      = 0x3
    TYPE_AT88SC1608     = 0x4
    TYPE_SLE4418_4428   = 0x5
    TYPE_SLE4432_4442   = 0x6
    TYPE_SLE4406_4436_5536  = 0x7
    TYPE_SLE4404            = 0x8
    TYPE_AT88SC101_102_1003 = 0x9
    #TYPE_ = 0xA
    #TYPE_ = 0xB
    TYPE_MCU_T0 = 0xC
    TYPE_MCU_T1 = 0xD
    
    @staticmethod
    def getReaderInformation():
        return ApduDefault(cla=0xFF,ins=0x09,p1=0x00,p2=0x00,expected_answer=0x10)
    
    @staticmethod
    def selectType(TYPE = 0):
        if TYPE < 0 or TYPE > 0xD:
            raise apduBuilderException("invalid argument TYPE, a value between 0 and 13 was expected, got "+str(TYPE))
        
        return ApduDefault(cla=0xFF,ins=0xA4,p1=0x00,p2=0x00,data=[TYPE])
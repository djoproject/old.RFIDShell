#!/usr/bin/python2.6
from arg.args import *
from arg.argchecker import *

from apdu.apduExecuter import *
from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.apdu import ApduDefault,ApduRaw
from acr122V1 import acr122SamAPDUBuilder,acr122execute

class acr122APDUBuilder(acr122SamAPDUBuilder):
    @staticmethod
    def getDataCardSerialNumber():
        "acr122 card serial"
        return iso7816_4APDUBuilder.getDataCA(0x00,0x00)
    
    @staticmethod
    def getDataCardATS():
        "acr122 card historic byte"
        return iso7816_4APDUBuilder.getDataCA(0x01,0x00)
        
    @staticmethod
    def loadKey(KeyName,KeyIndex=0):
        if KeyName not in keys:
            raise apduBuilderException("the key name doesn't exist "+str(KeyName))
            
        if len(keys[KeyName]) != 6:
            raise apduBuilderException("invalid key length, must be 6, got "+str(len(keys[KeyName])))
        
        if KeyIndex < 0x0 or KeyIndex > 0x1:
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 1 was expected, got "+str(KeyIndex))
    
        #P1 === load into volatile memory
        return ApduDefault(cla=0xFF,ins=0x82,p1=0x00,p2=KeyIndex,data=keys[KeyName])

    @staticmethod
    def authentificationObsolete(blockNumber,KeyIndex=0,isTypeA = True):
        
        if blockNumber < 0x0 or blockNumber > 0xFF:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if KeyIndex < 0x0 or KeyIndex > 0x1:
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 1 was expected, got "+str(KeyIndex))
        
        if isTypeA:
            return ApduRaw([0xFF,0x88,0x00,blockNumber,0x60,KeyIndex])
        else:
            return ApduRaw([0xFF,0x88,0x00,blockNumber,0x61,KeyIndex])
        
    @staticmethod
    def authentification(blockNumber=0,KeyIndex=0,isTypeA = True):
        if blockNumber < 0x0 or blockNumber > 0xFF:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if KeyIndex < 0x0 or KeyIndex > 0x1:
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 1 was expected, got "+str(KeyIndex))
        
        if isTypeA:
            return ApduDefault(cla=0xFF,ins=0x86,p1=0x00,p2=0x00,data=[0x01,0x00,blockNumber,0x60,KeyIndex])
        else:
            return ApduDefault(cla=0xFF,ins=0x86,p1=0x00,p2=0x00,data=[0x01,0x00,blockNumber,0x61,KeyIndex])
        
    @staticmethod
    def readBinary(blockNumber=0,byteToRead=0):
        if byteToRead < 0x0 or byteToRead > 0xFF:
            raise apduBuilderException("invalid argument byteToRead, a value between 0 and 255 was expected, got "+str(byteToRead))
        
        if blockNumber < 0x0 or blockNumber > 0xFF:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        return ApduDefault(cla=0xFF,ins=0xB0,p1=0x00,p2=blockNumber,data=[],expected_answer=byteToRead)
        
    @staticmethod
    def updateBinary(bytes,blockNumber=0):
        if len(bytes) < 1 or len(bytes) > 255:
            raise apduBuilderException("invalid args bytes, must be a list from 1 to 255 item, got "+str(len(bytes)))
        
        if blockNumber < 0x0 or blockNumber > 0xFF:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        return ApduDefault(cla=0xFF,ins=0xD6,p1=0x00,p2=blockNumber,data=bytes)
    
    #0x00 = set, 0x01 = inc, 0x02 = dec
    #value is signed
    @staticmethod
    def valueBlockOperationDec(operation,value=0,blockNumber=0):
        if blockNumber < 0x0 or blockNumber > 0xFF:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if operation < 0x0 or operation > 0x03:
            raise apduBuilderException("invalid argument operation, a value between 0 and 255 was expected, got "+str(operation))

        if value < -0x10000000 or value > 0xEFFFFFFF:
            raise apduBuilderException("invalid argument value, a value between -2147483648 and 2147483647 was expected, got "+str(value))

        if value < 0:
            value = 0xFFFFFFFF + (value + 1)

        B4 = value&0xFF
        B3 = (value>>8)&0xFF
        B2 = (value>>16)&0xFF
        B1 = (value>>24)&0xFF

        return ApduDefault(cla=0xFF,ins=0xD7,p1=0x00,p2=blockNumber,data=[B1,B2,B3,B4])
    
    @staticmethod
    def valueBlockOperationSet(value=0,blockNumber=0):
        return valueBlockOperationDec(0x00,value,blockNumber)
        
    @staticmethod
    def valueBlockOperationInc(value=0,blockNumber=0):
        return valueBlockOperationDec(0x01,value,blockNumber)
            
    @staticmethod
    def valueBlockOperationDec(value=0,blockNumber=0):
        return valueBlockOperationDec(0x02,value,blockNumber)
        
    @staticmethod
    def readValueBlock(blockNumber=0):
        if blockNumber < 0x0 or blockNumber > 0xFF:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
            
        return ApduDefault(cla=0xFF,ins=0xB1,p1=0x00,p2=blockNumber,data=[],expected_answer=0x04)
        
    @staticmethod
    def restoreValueBlock(source,target):
        if source < 0x0 or source > 0xFF:
            raise apduBuilderException("invalid argument source, a value between 0 and 255 was expected, got "+str(source))
        
        if target < 0x0 or target > 0xFF:
            raise apduBuilderException("invalid argument target, a value between 0 and 255 was expected, got "+str(target))
        
        return ApduDefault(cla=0xFF,ins=0xD7,p1=0x00,p2=source,data=[0x03,target])
        
    @staticmethod
    def getPICCOperatingParameter():
        "acr122 get picc parameter"
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x50,p2=0x01)
        
    def setPICCOperatingParameter(param):
        if param < 0x0 or param > 0xFF:
            raise apduBuilderException("invalid argument param, a value between 0 and 255 was expected, got "+str(param))
            
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x51,p2=param)
        
    @staticmethod
    def setTimeoutParameter(value):
        if value < 0x0 or value > 0xFF:
            raise apduBuilderException("invalid argument value, a value between 0 and 255 was expected, got "+str(value))
        
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x41,p2=value)
        
    @staticmethod
    def setBuzzerOutputEnable(enable=True):
        if enable:
            return ApduDefault(cla=0xFF,ins=0x00,p1=0x52,p2=0xFF) 
        else:
            return ApduDefault(cla=0xFF,ins=0x00,p1=0x52,p2=0x00) 


def PICCOperatingParameter(autopolling,autoats,polling,felica424K,felica212K,topaz,iso14443B,iso14443A):
    return acr122APDUBuilder.setPICCOperatingParameter(autopolling|autoats|polling|felica424K|felica212K|topaz|iso14443B|iso14443A)

i = IntegerArgChecker(1,255)

#Executer.addCommand(CommandStrings=["acr122","firmware"],                   preProcess=acr122APDUBuilder.getFirmwareVersion,        process=executeAPDU,postProcess=resultHandlerAPDUAndConvertDataToString)
#Executer.addCommand(CommandStrings=["acr122","transmit"],                   preProcess=acr122APDUBuilder.directTransmit,            process=executeAPDU,argChecker=AllTheSameChecker(hexaArgChecker(),"args"))
#Executer.addCommand(CommandStrings=["acr122","response"],                   preProcess=acr122APDUBuilder.getResponse,               process=executeAPDU,argChecker=DefaultArgsChecker([("Length",i)]),          postProcess=resultHandlerAPDUAndPrintDataAndSW)

#t = tokenValueArgChecker({"off":False,"on":True,"default":None})
#t2 = tokenValueArgChecker({"off":acr122APDUBuilder.LinkToBuzzerOff,"t1":acr122APDUBuilder.LinkToBuzzerDuringT1,"t2":acr122APDUBuilder.LinkToBuzzerDuringT2,"both":acr122APDUBuilder.LinkToBuzzerDuringT1AndT2})

#Executer.addCommand(CommandStrings=["acr122","ledbuzzer"],                  preProcess=acr122APDUBuilder.ledAndBuzzerControl,       process=executeAPDU,argChecker=DefaultArgsChecker([("initialRed",t),("initialGreen",t),("finalRed",t),("finalGreen",t),("T1Duration",i),("T2Duration",i),("Repetition",i),("LinkToBuzzer",t2)]))
#Executer.addCommand(CommandStrings=["acr122","execute"],                    preProcess=acr122execute,             process=executeAPDU,argChecker=AllTheSameChecker(hexaArgChecker(),"args"),  postProcess=printResultHandler)
            
Executer.addCommand(CommandStrings=["acr122","card","serial"],              preProcess=acr122APDUBuilder.getDataCardSerialNumber,   process=executeAPDU,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["acr122","card","ats"],                 preProcess=acr122APDUBuilder.getDataCardATS,            process=executeAPDU,postProcess=resultHandlerAPDUAndPrintData)

Executer.addCommand(CommandStrings=["acr122","mifare","loadkey"],           preProcess=acr122APDUBuilder.loadKey,                   process=executeAPDU,argChecker=DefaultArgsChecker([("KeyIndex",IntegerArgChecker(0,15)),("KeyName",stringArgChecker())]))
typeAB = tokenValueArgChecker({"a":True,"b":False})
Executer.addCommand(CommandStrings=["acr122","mifare","authenticate"],      preProcess=acr122APDUBuilder.authentification,          process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker(0,0xFF)),("KeyIndex",IntegerArgChecker(0,15)),("isTypeA",typeAB)],0))
Executer.addCommand(CommandStrings=["acr122","mifare","authenticateOld"],   preProcess=acr122APDUBuilder.authentificationObsolete,  process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker(0,0xFF)),("KeyIndex",IntegerArgChecker(0,15)),("isTypeA",typeAB)],0))

Executer.addCommand(CommandStrings=["acr122","read"],                       preProcess=acr122APDUBuilder.readBinary,                process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker()),("byteToRead",hexaArgChecker())],2),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["acr122","update"],                     preProcess=acr122APDUBuilder.updateBinary,              process=executeAPDU,argChecker=InfiniteArgsChecker("bytes",hexaArgChecker(),[("blockNumber",hexaArgChecker())],defaultLimitChecker(0xFF)))

Executer.addCommand(CommandStrings=["acr122","block","set"],                preProcess=acr122APDUBuilder.valueBlockOperationSet,    process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker()),("value",IntegerArgChecker(-0x10000000,0x7FFFFFFF))]))
Executer.addCommand(CommandStrings=["acr122","block","incremente"],         preProcess=acr122APDUBuilder.valueBlockOperationInc,    process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker()),("value",IntegerArgChecker(-0x10000000,0x7FFFFFFF))]))
Executer.addCommand(CommandStrings=["acr122","block","decremente"],         preProcess=acr122APDUBuilder.valueBlockOperationDec,    process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker()),("value",IntegerArgChecker(-0x10000000,0x7FFFFFFF))]))    
    
Executer.addCommand(CommandStrings=["acr122","block","read"],               preProcess=acr122APDUBuilder.readValueBlock,            process=executeAPDU,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker())],0),postProcess=resultHandlerAPDUAndPrintData)

Executer.addCommand(CommandStrings=["acr122","block","restore"],            preProcess=acr122APDUBuilder.restoreValueBlock,         process=executeAPDU,argChecker=DefaultArgsChecker([("source",hexaArgChecker()),("target",hexaArgChecker())]))
Executer.addCommand(CommandStrings=["acr122","picc"],                       preProcess=acr122APDUBuilder.getPICCOperatingParameter, process=executeAPDU,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["acr122","set","picc"],                 preProcess=PICCOperatingParameter,       process=executeAPDU,argChecker=DefaultArgsChecker([("autopolling",tokenValueArgChecker({"enable":0x80,"disable":0x0})), ("autoats",tokenValueArgChecker({"enable":0x40,"disable":0x0})), ("polling",tokenValueArgChecker({"250ms":0x20,"500ms":0x0})), ("felica424K",tokenValueArgChecker({"detect":0x10,"skip":0x0})), ("felica212K",tokenValueArgChecker({"detect":0x08,"skip":0x0})), ("topaz",tokenValueArgChecker({"detect":0x04,"skip":0x0})), ("iso14443B",tokenValueArgChecker({"detect":0x02,"skip":0x0})), ("iso14443A",tokenValueArgChecker({"detect":0x01,"skip":0x0}))]))
#Executer.addCommand(CommandStrings=["acr122","set","picc"],                 preProcess=PICCOperatingParameter,       process=executeAPDU,argChecker=DefaultArgsChecker([("autopolling",tokenValueArgChecker({"enable":0x80,"disable":0x0})), ("autoats",tokenValueArgChecker({"enable":0x40,"disable":0x0})), ("polling",tokenValueArgChecker({"250ms":0x20,"500ms":0x0})), ("felica424K",tokenValueArgChecker({"detect":0x10,"skip":0x0})), ("felica212K",tokenValueArgChecker({"detect":0x08,"skip":0x0})), ("topaz",tokenValueArgChecker({"detect":0x04,"skip":0x0})), ("iso14443B",tokenValueArgChecker({"detect":0x02,"skip":0x0})), ("iso14443A",tokenValueArgChecker({"detect":0x01,"skip":0x0}))]))

Executer.addCommand(CommandStrings=["acr122","set","timeout"],              preProcess=acr122APDUBuilder.setTimeoutParameter,       process=executeAPDU,argChecker=DefaultArgsChecker([("value",hexaArgChecker())]))

typeEnable = tokenValueArgChecker({"enable":True,"disable":False})
Executer.addCommand(CommandStrings=["acr122","set","buzzer"],               preProcess=acr122APDUBuilder.setBuzzerOutputEnable,     process=executeAPDU,argChecker=DefaultArgsChecker([("value",typeEnable)],0))



#!/usr/bin/python2.6
from arg.args import Executer
from arg.argchecker import *
from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.apduExecuter import *

try:
    from keyList import keys #TODO manage when key store didn't exist
except ImportError:
    keys = {}
    print "WARNING : proxnroll loading, no permanent key store found"

from apdu.apdu import ApduDefault
from apdu.exception import apduBuilderException,apduAnswserException
from smartcard.sw.SWExceptions import CheckingErrorException
from rfid.util import getPIXSS, getPIXNN
from rfidDefault import printATR

from pcscAddon import pcscAPDUBuilder

proxnrollSW = {
    0x68:(CheckingErrorException, 
        {0x00: "CLA byte is not correct"}),
    0x69:(CheckingErrorException, 
        {0x86: "Volatile memory is not available or key type is not valid",
         0x87: "Non-volatile memory is not available",
         0x88: "Key number is not valid",
         0x89: "Key length is not valid"}),
    0x6C:(CheckingErrorException, 
        {None: "Wrong length (Le is shorter than data length, XX in SW2 gives the correct value)"}),
    0x6F:(CheckingErrorException, 
        {0x00: "Card mute (or removed)",
         0xE7: "SAM didn't answer with 9000 (maybe this is not a Calypso SAM !)",
         None: "Error code returned by the Gemcore"})
    
    #TODO there is a lot of other error code in the doc
    
}
#TODO load somewhere

class ProxnrollAPDUBuilder(pcscAPDUBuilder):
    colorOFF   = 0x00
    colorON    = 0x01
    colorSLOW  = 0x02
    colorAUTO  = 0x03
    colorQUICK = 0x04
    colorBEAT  = 0x05
    
    #def __init__(self):
    #    pass
    
    @staticmethod
    def setLedColorFun(red,green,yellow_blue = None):        
        if red < 0 or red > 5:
            raise apduBuilderException("invalid argument red, a value between 0 and 5 was expected, got "+str(red))
            
        if green < 0 or green > 5:
            raise apduBuilderException("invalid argument green, a value between 0 and 5 was expected, got "+str(green))
        
        if yellow_blue == None:
            d = [0x1E,red,green]
        else:
            if yellow_blue < 0 or yellow_blue > 5:
                raise apduBuilderException("invalid argument yellow_blue, a value between 0 and 5 was expected, got "+str(yellow_blue))
            d = [0x1E,red,green,yellow_blue]
        
        return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=0x00,data=d)
    
    @staticmethod    
    def setBuzzerDuration(duration):
        if duration < 0 or duration > 60000:
            raise apduBuilderException("invalid argument duration, a value between 0 and 60000 was expected, got "+str(duration))
        
        lsb = duration&0xFF
        msb = (duration>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=0x00,data=[0x1C,msb,lsb])
    
    @staticmethod    
    def test(expected_answer_size = 0,delay_to_answer=0, datas = []):
        
        if expected_answer_size < 0 or expected_answer_size > 255:
            raise apduBuilderException("invalid argument expected_answer_size, a value between 0 and 255 was expected, got "+str(expected_answer_size))
            
        if delay_to_answer < 0 or delay_to_answer > 63:
            raise apduBuilderException("invalid argument delay_to_answer, a value between 0 and 63 was expected, got "+str(delay_to_answer))
            
        if len(datas) < 0 or len(datas) > 255:
            raise apduBuilderException("invalid argument datas, a value list of length 0 to 255 was expected, got "+str(len(datas)))
        
        return ApduDefault(cla=0xFF,ins=0xFD,p1=expected_answer_size,p2=delay_to_answer,data=datas)
    
    ###
    protocolType_ISO14443_TCL = 0x00
    protocolType_ISO14443A = 0x01
    protocolType_ISO14443B = 0x02
    protocolType_ISO15693 = 0x04
    protocolType_ISO15693_WithUID = 0x05
    protocolType_ISO14443A_WithoutCRC = 0x09
    protocolType_ISO14443B_WithoutCRC = 0x0A
    protocolType_ISO15693_WithoutCRC = 0x0C
    
    lastByte_Complete_WithoutCRC = 0x0F
    lastByte_With1bits_WithoutCRC = 0x1F
    lastByte_With2bits_WithoutCRC = 0x2F
    lastByte_With3bits_WithoutCRC = 0x3F
    lastByte_With4bits_WithoutCRC = 0x4F
    lastByte_With5bits_WithoutCRC = 0x5F
    lastByte_With6bits_WithoutCRC = 0x6F
    lastByte_With7bits_WithoutCRC = 0x7F
    
    redirectionToMainSlot = 0x80
    redirectionTo1stSlot = 0x81
    redirectionTo2ndSlot = 0x82
    redirectionTo3rdSlot = 0x83
    redirectionTo4stSlot = 0x84
    
    timeoutDefault = 0x00
    timeout1ms = 0x01
    timeout2ms = 0x02
    timeout4ms = 0x03
    timeout8ms = 0x04
    timeout16ms = 0x05
    timeout32ms = 0x06
    timeout65ms = 0x07
    timeout125ms = 0x08
    timeout250ms = 0x09
    timeout500ms = 0x0A
    timeout1s = 0x0B
    timeout2s = 0x0C
    timeout4s = 0x0D
    
    
    #TODO BUG : avec un mauvais protocole, le reader renvoit 0x6f 0x47, code non defini...
    #           et ca renvoit 0x6f 0x01 quand ca reussi avec les ultralight...
    @staticmethod
    def encapsulate(datas,protocolType=0x00,timeoutType=0x00,defaultSW = True):
        
        #TODO limite de 255
        
        if timeoutType < 0 or timeoutType > 0x0D:
            raise apduBuilderException("invalid argument timeoutType, a value between 0 and 13 was expected, got "+str(timeoutType))
            
        if protocolType != 0x00 and protocolType != 0x01 and protocolType != 0x02 and protocolType != 0x04 and protocolType != 0x05 and protocolType != 0x09 and protocolType != 0x0A and protocolType != 0x0C and protocolType != 0x0F and protocolType != 0x1F and protocolType != 0x2F and protocolType != 0x3F and protocolType != 0x4F and protocolType != 0x5F and protocolType != 0x6F and protocolType != 0x7F and protocolType != 0x80 and protocolType != 0x81 and protocolType != 0x82 and protocolType != 0x83 and protocolType != 0x84:
            raise apduBuilderException("invalid argument protocolType, see the documentation")
            
        if not defaultSW:
            timeoutType &= 0x80
            
        return ApduDefault(cla=0xFF,ins=0xFE,p1=protocolType,p2=timeoutType,data=datas)
        
    ###
    @staticmethod
    def getDataCardCompleteIdentifier():
        return iso7816_4APDUBuilder.getDataCA(0xF0,0x00)
    
    @staticmethod
    def getDataCardType():
        return iso7816_4APDUBuilder.getDataCA(0xF1,0x00)

    @staticmethod
    def parseDataCardType(toParse):
        if len(toParse) != 3:
            raise apduAnswserException("(proxnroll) parseDataCardType, 3 bytes waited, got "+str(len(toParse)))
        
        print "Procole : "+getPIXSS(toParse[0]) + ", Type : " +getPIXNN((toParse[1] << 8) + toParse[2])  

    @staticmethod
    def getDataCardShortSerialNumber():
        return iso7816_4APDUBuilder.getDataCA(0xF2,0x00)

    @staticmethod
    def getDataCardATR():
        return iso7816_4APDUBuilder.getDataCA(0xFA,0x00)
    
    @staticmethod
    def getDataProductSerialNumber():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x00)

    @staticmethod
    def getDataHarwareIdentifier():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x01)

    @staticmethod
    def getDataVendorName():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x81)

    @staticmethod
    def getDataProductName():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x82)

    @staticmethod
    def getDataProductSerialNumber():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x83)

    @staticmethod
    def getDataProductUSBIdentifier():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x84)
        
    @staticmethod
    def getDataProductVersion():
        return iso7816_4APDUBuilder.getDataCA(0xFF,0x85)
        
    ###          
    
    @staticmethod
    def loadKey(KeyIndex,KeyName,InVolatile = True ,isTypeA = True):
        if KeyName not in keys:
            raise apduBuilderException("the key name doesn't exist "+str(KeyName))
        
        #only allow mifare key
        if len(keys[KeyName]) != 6:
            raise apduBuilderException("invalid key length, must be 6, got "+str(len(keys[KeyName])))

        #proxnroll specific params
        if InVolatile:
            if KeyIndex < 0 or KeyIndex > 3:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 3 was expected, got "+str(KeyIndex))
        else:
            if KeyIndex < 0 or KeyIndex > 15:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 15 was expected, got "+str(KeyIndex))
        
        #B key special index
        if not isTypeA:
            KeyIndex &= 0x10
            
        return pcscAPDUBuilder.loadKey(KeyIndex,KeyName,InVolatile)
        
    @staticmethod
    def generalAuthenticate(blockNumber,KeyIndex,InVolatile = True ,isTypeA = True):
        if blockNumber < 0 or blockNumber > 255:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if InVolatile:
            if KeyIndex < 0 or KeyIndex > 3:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 3 was expected, got "+str(KeyIndex))
            
            #volatile key special index
            KeyIndex &= 0x20
        else:
            if KeyIndex < 0 or KeyIndex > 15:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 15 was expected, got "+str(KeyIndex))
            
        #if isTypeA:
        #    datas = [0x01,0x00,blockNumber,0x60,KeyIndex]
        #else:
        #    datas = [0x01,0x00,blockNumber,0x61,KeyIndex]
        #    
        ap = pcscAPDUBuilder.generalAuthenticate(blockNumber,KeyIndex,InVolatile,isTypeA)
        
        ap.setIns(0x88)
     
        return ap
        
    @staticmethod
    def mifareClassicRead(blockNumber,KeyName = None):
        if blockNumber < 0 or blockNumber > 255:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if KeyName == None:
            return ApduDefault(cla=0xFF,ins=0xF3,p1=0x00,p2=blockNumber)
        else:
            if KeyName not in keys:
                raise apduBuilderException("the key name doesn't exist "+str(KeyName))

            if len(keys[KeyName]) != 6:
                raise apduBuilderException("invalid key length, must be 6, got "+str(len(keys[KeyName])))
            
            #if len(KeyName) != 6:
            #    raise apduBuilderException("invalid key size, must be 6, got "+str(len(KeyName)))
                
            return ApduDefault(cla=0xFF,ins=0xF3,p1=0x00,p2=blockNumber,data=keys[KeyName])
        
    @staticmethod
    def mifareClassifWrite(blockNumber,datas,KeyName = None):
        if blockNumber < 0 or blockNumber > 255:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))

        if len(datas) < 1 or len(datas) > 255:
            raise apduBuilderException("invalid datas size, must be a list from 1 to 255 item, got "+str(len(datas)))
            
        if (len(datas) % 16) != 0:
            raise apduBuilderException("invalid datas size, must be a multiple of 16")

        if KeyName == None:
            return ApduDefault(cla=0xFF,ins=0xF4,p1=0x00,p2=blockNumber,data=datas)
        else:
            if KeyName not in keys:
                raise apduBuilderException("the key name doesn't exist "+str(KeyName))

            if len(keys[KeyName]) != 6:
                raise apduBuilderException("invalid key length, must be 6, got "+str(len(keys[KeyName])))
            
            #if len(KeyName) != 6:
            #    raise apduBuilderException("invalid key size, must be 6, got "+str(len(KeyName)))
        
            toSend = []
            toSend.extend(datas)
            toSend.extend(keys[KeyName])
            return ApduDefault(cla=0xFF,ins=0xF4,p1=0x00,p2=blockNumber,data=toSend)
        
    
    #### SLOT CONTROL ####
    @staticmethod
    def slotControlResumeCardTracking():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x00,p2=0x00)
    
    @staticmethod
    def slotControlSuspendCardTracking():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x01,p2=0x00)
    
    @staticmethod
    def slotControlStopRFField():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x10,p2=0x00)

    @staticmethod
    def slotControlStartRFField():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x10,p2=0x01)
    
    @staticmethod
    def slotControlResetRFField():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x10,p2=0x02)
        
    @staticmethod
    def slotControlTCLDeactivation():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x00)

    @staticmethod
    def slotControlTCLActivationTypeA():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x01)

    @staticmethod
    def slotControlTCLActivationTypeB():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x02)
    
    @staticmethod
    def slotControlDisableNextTCL():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x04)

    @staticmethod
    def slotControlDisableEveryTCL():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x05)

    @staticmethod
    def slotControlEnableTCLAgain():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x06)

    @staticmethod
    def slotControlResetAfterNextDisconnectAndDisableNextTCL():
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x07)
    
    @staticmethod
    def slotControlStop():
        "stop the slot"
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0xDE,p2=0xAD)
    
    #### CALYPSO METHOD ###
    
    @staticmethod
    def configureCalypsoSamSetSpeed9600():
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x04,p2=0x00)
        
    @staticmethod
    def configureCalypsoSamSetSpeed115200():
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x04,p2=0x01)

    @staticmethod
    def configureCalypsoSamEnableInternalDigestUpdate():
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x08,p2=0x00)
        
    @staticmethod
    def configureCalypsoSamDisableInternalDigestUpdate():
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x08,p2=0x01)
        
def readAllFun(envi):
    ls = []
    for i in range(0,0xffff):
        apdu = ProxnrollAPDUBuilder.readBinary(i)
        apduAnswer = executeAPDU(envi,apdu)
        
        if apduAnswer.sw1 != 0x90 and apduAnswer.sw2 != 0x00:
            print "%x %x" % (apduAnswer.sw1, apduAnswer.sw2)
            break
        
        ls.append(apduAnswer)
    return ls

##############################################################################################################
##############################################################################################################
##############################################################################################################
#(CommandStrings=,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):

try:
    Executer
except NameError:
    print "  No variable Executer found, this is an addon, it can't be executed alone"
    exit()
            
t = tokenValueArgChecker({"off":ProxnrollAPDUBuilder.colorOFF,"on":ProxnrollAPDUBuilder.colorON,"auto":ProxnrollAPDUBuilder.colorAUTO,"slow":ProxnrollAPDUBuilder.colorSLOW,"quick":ProxnrollAPDUBuilder.colorQUICK,"beat":ProxnrollAPDUBuilder.colorBEAT})
i0to60000 = IntegerArgChecker(0,60000)


Executer.addCommand(CommandStrings=["proxnroll","setlight"],                               preProcess=ProxnrollAPDUBuilder.setLedColorFun,process=executeAPDU,argChecker=DefaultArgsChecker([("red",t),("green",t),("yellow_blue",t)],2))
Executer.addCommand(CommandStrings=["proxnroll","setbuzzer"],                              preProcess=ProxnrollAPDUBuilder.setBuzzerDuration,process=executeAPDU,                                  argChecker=DefaultArgsChecker([("duration",i0to60000)],0))
Executer.addCommand(CommandStrings=["proxnroll","calypso","setspeed","9600"],              preProcess=ProxnrollAPDUBuilder.configureCalypsoSamSetSpeed9600,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","calypso","setspeed","115200"],            preProcess=ProxnrollAPDUBuilder.configureCalypsoSamSetSpeed115200,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","calypso","enabledigestupdate"],           preProcess=ProxnrollAPDUBuilder.configureCalypsoSamEnableInternalDigestUpdate,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","calypso","disabledigestupdate"],          preProcess=ProxnrollAPDUBuilder.configureCalypsoSamDisableInternalDigestUpdate,process=executeAPDU)
                
Executer.addCommand(CommandStrings=["proxnroll","vendor"],                   preProcess=ProxnrollAPDUBuilder.getDataVendorName,process=executeAPDU                                   ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","name"],           preProcess=ProxnrollAPDUBuilder.getDataProductName,process=executeAPDU                                  ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","serialString"],   preProcess=ProxnrollAPDUBuilder.getDataProductSerialNumber,process=executeAPDU                          ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","usbidentifiel"],  preProcess=ProxnrollAPDUBuilder.getDataProductUSBIdentifier,process=executeAPDU                         ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","version"],        preProcess=ProxnrollAPDUBuilder.getDataProductVersion,process=executeAPDU                               ,postProcess=resultHandlerAPDUAndConvertDataToString)
Executer.addCommand(CommandStrings=["proxnroll","product","serial"],         preProcess=ProxnrollAPDUBuilder.getDataProductSerialNumber,process=executeAPDU   ,postProcess=resultHandlerAPDUAndPrintData)

Executer.addCommand(CommandStrings=["proxnroll","card","serial"],            preProcess=ProxnrollAPDUBuilder.getDataCardSerialNumber,process=executeAPDU                             ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","ats"],               preProcess=ProxnrollAPDUBuilder.getDataCardATS,process=executeAPDU               ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","completeIdentifier"],preProcess=ProxnrollAPDUBuilder.getDataCardCompleteIdentifier,process=executeAPDU,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","type"],              preProcess=ProxnrollAPDUBuilder.getDataCardType,process=executeAPDU              ,postProcess=ProxnrollAPDUBuilder.parseDataCardType)
Executer.addCommand(CommandStrings=["proxnroll","card","shortSerial"],       preProcess=ProxnrollAPDUBuilder.getDataCardShortSerialNumber,process=executeAPDU ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","card","atr"],               preProcess=ProxnrollAPDUBuilder.getDataCardATR,process=executeAPDU               ,postProcess=printATR) #resultHandlerAPDUAndPrintData
Executer.addCommand(CommandStrings=["proxnroll","hardwareIdentifier"],       preProcess=ProxnrollAPDUBuilder.getDataHarwareIdentifier,process=executeAPDU     ,postProcess=resultHandlerAPDUAndPrintData)

Executer.addCommand(CommandStrings=["proxnroll","control","tracking","resume"],            preProcess=ProxnrollAPDUBuilder.slotControlResumeCardTracking,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","tracking","suspend"],           preProcess=ProxnrollAPDUBuilder.slotControlSuspendCardTracking,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","rffield","stop"],               preProcess=ProxnrollAPDUBuilder.slotControlStopRFField,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","rffield","start"],              preProcess=ProxnrollAPDUBuilder.slotControlStartRFField,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","rffield","reset"],              preProcess=ProxnrollAPDUBuilder.slotControlResetRFField,process=executeAPDU)

Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","deactivation"],          preProcess=ProxnrollAPDUBuilder.slotControlTCLDeactivation,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","activation","a"],        preProcess=ProxnrollAPDUBuilder.slotControlTCLActivationTypeA,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","activation","b"],        preProcess=ProxnrollAPDUBuilder.slotControlTCLActivationTypeB,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","disable","next"],        preProcess=ProxnrollAPDUBuilder.slotControlDisableNextTCL,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","disable","every"],       preProcess=ProxnrollAPDUBuilder.slotControlDisableEveryTCL,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","enable"],                preProcess=ProxnrollAPDUBuilder.slotControlEnableTCLAgain,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","control","t=cl","reset"],                 preProcess=ProxnrollAPDUBuilder.slotControlResetAfterNextDisconnectAndDisableNextTCL,process=executeAPDU)

Executer.addCommand(CommandStrings=["proxnroll","control","stop"],                         preProcess=ProxnrollAPDUBuilder.slotControlStop,process=executeAPDU)
Executer.addCommand(CommandStrings=["proxnroll","test"],                                   preProcess=ProxnrollAPDUBuilder.test,process=executeAPDU
                    ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("expected_answer_size",IntegerArgChecker(0,255)),("delay_to_answer",IntegerArgChecker(0,63))])
                    ,postProcess=resultHandlerAPDUAndPrintDataAndSW)

typeAB = tokenValueArgChecker({"a":True,"b":False})
typeVolatile = tokenValueArgChecker({"volatile":True,"nonvolatile":False})
Executer.addCommand(CommandStrings=["proxnroll","mifare","loadkey"],                       preProcess=ProxnrollAPDUBuilder.loadKey,process=executeAPDU,                 
argChecker=DefaultArgsChecker([("KeyIndex",IntegerArgChecker(0,15)),("KeyName",stringArgChecker()),("isTypeA",typeAB),("InVolatile",typeVolatile)],2))
Executer.addCommand(CommandStrings=["proxnroll","mifare","authenticate"],                  preProcess=ProxnrollAPDUBuilder.generalAuthenticate,process=executeAPDU,     
argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker(0,0xFF)),("KeyIndex",IntegerArgChecker(0,15)),("isTypeA",typeAB),("InVolatile",typeVolatile)],2))

i = IntegerArgChecker()
#TODO add the expected argument to readBinary
Executer.addCommand(CommandStrings=["proxnroll","read"],                                   preProcess=ProxnrollAPDUBuilder.readBinary,process=executeAPDU,                 argChecker=DefaultArgsChecker([("address",i)],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","mifare","read"],                          preProcess=ProxnrollAPDUBuilder.mifareClassicRead,process=executeAPDU,          argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker()),("KeyName",stringArgChecker())],1),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["proxnroll","update"],                                 preProcess=ProxnrollAPDUBuilder.updateBinary,process=executeAPDU,               argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("address",hexaArgChecker(0,0xFFFF))],defaultLimitChecker(0xFF)))

timeoutType = tokenValueArgChecker({"default":ProxnrollAPDUBuilder.timeoutDefault,
                                    "1ms":ProxnrollAPDUBuilder.timeout1ms,
                                    "2ms":ProxnrollAPDUBuilder.timeout2ms,
                                    "4ms":ProxnrollAPDUBuilder.timeout4ms,
                                    "8ms":ProxnrollAPDUBuilder.timeout8ms,
                                    "16ms":ProxnrollAPDUBuilder.timeout16ms,
                                    "32ms":ProxnrollAPDUBuilder.timeout32ms,
                                    "65ms":ProxnrollAPDUBuilder.timeout65ms,
                                    "125ms":ProxnrollAPDUBuilder.timeout125ms,
                                    "250ms":ProxnrollAPDUBuilder.timeout250ms,
                                    "500ms":ProxnrollAPDUBuilder.timeout500ms,
                                    "1s":ProxnrollAPDUBuilder.timeout1s,
                                    "2s":ProxnrollAPDUBuilder.timeout2s,
                                    "4s":ProxnrollAPDUBuilder.timeout4s})
                                    
protocoleType = tokenValueArgChecker({"default":ProxnrollAPDUBuilder.protocolType_ISO14443_TCL,
                                    "ISO14443A":ProxnrollAPDUBuilder.protocolType_ISO14443A,
                                    "ISO14443B":ProxnrollAPDUBuilder.protocolType_ISO14443B,
                                    "ISO15693":ProxnrollAPDUBuilder.protocolType_ISO15693,
                                    "ISO15693UID":ProxnrollAPDUBuilder.protocolType_ISO15693_WithUID,
                                    "ISO14443ANOCRC":ProxnrollAPDUBuilder.protocolType_ISO14443A_WithoutCRC,
                                    "ISO14443BNOCRC":ProxnrollAPDUBuilder.protocolType_ISO14443B_WithoutCRC,
                                    "ISO15693NOCRC":ProxnrollAPDUBuilder.protocolType_ISO15693_WithoutCRC})
                                    
redirectionType = tokenValueArgChecker({"main":ProxnrollAPDUBuilder.redirectionToMainSlot,
                                        "1":ProxnrollAPDUBuilder.redirectionTo1stSlot,
                                        "2":ProxnrollAPDUBuilder.redirectionTo2ndSlot,
                                        "3":ProxnrollAPDUBuilder.redirectionTo3rdSlot,
                                        "4":ProxnrollAPDUBuilder.redirectionTo4stSlot})
                                        
partialType = tokenValueArgChecker({"8":ProxnrollAPDUBuilder.lastByte_Complete_WithoutCRC,
                                        "1":ProxnrollAPDUBuilder.lastByte_With1bits_WithoutCRC,
                                        "2":ProxnrollAPDUBuilder.lastByte_With2bits_WithoutCRC,
                                        "3":ProxnrollAPDUBuilder.lastByte_With3bits_WithoutCRC,
                                        "4":ProxnrollAPDUBuilder.lastByte_With4bits_WithoutCRC,
                                        "5":ProxnrollAPDUBuilder.lastByte_With5bits_WithoutCRC,
                                        "6":ProxnrollAPDUBuilder.lastByte_With6bits_WithoutCRC,
                                        "7":ProxnrollAPDUBuilder.lastByte_With7bits_WithoutCRC})

Executer.addCommand(CommandStrings=["proxnroll","encapsulate","standard"],                 preProcess=ProxnrollAPDUBuilder.encapsulate,process=executeAPDU               ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("protocolType",protocoleType),("timeoutType",timeoutType)],defaultLimitChecker(0xFF)),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["proxnroll","encapsulate","redirection"],              preProcess=ProxnrollAPDUBuilder.encapsulate,process=executeAPDU               ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("protocolType",redirectionType),("timeoutType",timeoutType)],defaultLimitChecker(0xFF)),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["proxnroll","encapsulate","partial"],                  preProcess=ProxnrollAPDUBuilder.encapsulate,process=executeAPDU               ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("protocolType",partialType),("timeoutType",timeoutType)],defaultLimitChecker(0xFF)),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["proxnroll","mifare","update"],                        preProcess=ProxnrollAPDUBuilder.mifareClassifWrite,process=executeAPDU        ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("blockNumber",hexaArgChecker()),("KeyName",stringArgChecker())],defaultLimitChecker(0xFF)))
Executer.addCommand(CommandStrings=["proxnroll","readall"],                                process=readAllFun,                                     postProcess=printByteListList)



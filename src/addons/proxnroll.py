#!/usr/bin/python2.6
from arg.args import *
from apdu.apduExecuter import *

from keyList import keys
from apdu.apdu import ApduDefault
from smartcard.sw.ErrorChecker import ErrorChecker
from apdu.exception import apduBuilderException
from smartcard.sw.SWExceptions import CheckingErrorException
from addons.iso7816_4 import iso7816_4APDUBuilder

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
}
#TODO load somewhere

class PronrollErrorChecker(ErrorChecker):
    def __call__( self, data, sw1, sw2 ):
        if proxnrollSW.has_key(sw1): 
            exception, sw2dir = proxnrollSW[sw1] 
            if type(sw2dir) == type({}): 
                try: 
                    message = sw2dir[sw2] 
                    raise exception(data, sw1, sw2, message) 
                except KeyError: 
                    if None in sw2dir:
                        message = sw2dir[None]+" : "+str(sw2) 
                        raise exception(data, sw1, sw2, message)

class Proxnroll(iso7816_4APDUBuilder):
    colorOFF   = 0x00
    colorON    = 0x01
    colorSLOW  = 0x02
    colorAUTO  = 0x03
    colorQUICK = 0x04
    colorBEAT  = 0x05
    
    #def __init__(self):
    #    pass
        
    def setLedColorFun(self,red,green,yellow_blue = None):        
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
        
    def setBuzzerDuration(self,duration):
        if duration < 0 or duration > 60000:
            raise apduBuilderException("invalid argument duration, a value between 0 and 60000 was expected, got "+str(duration))
        
        lsb = duration&0xFF
        msb = (duration>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=0x00,data=[0x1C,msb,lsb])
        
    def test(self, expected_answer_size = 0,delay_to_answer=0, datas = []):
        
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
    
    def encapsulate(self,datas,protocolType=0x00,timeoutType=0x00,defaultSW = True):
        
        if timeoutType < 0 or timeoutType > 0x0D:
            raise apduBuilderException("invalid argument timeoutType, a value between 0 and 13 was expected, got "+str(timeoutType))
            
        if protocolType != 0x00 and protocolType != 0x01 and protocolType != 0x02 and protocolType != 0x04 and protocolType != 0x05 and protocolType != 0x09 and protocolType != 0x0A and protocolType != 0x0C and protocolType != 0x0F and protocolType != 0x1F and protocolType != 0x2F and protocolType != 0x3F and protocolType != 0x4F and protocolType != 0x5F and protocolType != 0x6F and protocolType != 0x7F and protocolType != 0x80 and protocolType != 0x81 and protocolType != 0x82 and protocolType != 0x83 and protocolType != 0x84:
            raise apduBuilderException("invalid argument protocolType, see the documentation")
            
        if not defaultSW:
            timeoutType &= 0x80
            
        return ApduDefault(cla=0xFF,ins=0xFE,p1=protocolType,p2=timeoutType,data=datas)
        
    ###
        
    def getDataCardSerialNumber(self):
        return self.getDataCA(0x00,0x00)
    
    def getDataCardATS(self):
        return self.getDataCA(0x01,0x00)
        
    def getDataCardCompleteIdentifier(self):
        return self.getDataCA(0xF0,0x00)
      
    def getDataCardType(self):
        return self.getDataCA(0xF1,0x00)

    def getDataCardShortSerialNumber(self):
        return self.getDataCA(0xF2,0x00)

    def getDataCardATR(self):
        return self.getDataCA(0xFA,0x00)
        
    def getDataProductSerialNumber(self):
        return self.getDataCA(0xFF,0x00)

    def getDataHarwareIdentifier(self):
        return self.getDataCA(0xFF,0x01)

    def getDataVendorName(self):
        return self.getDataCA(0xFF,0x81)

    def getDataProductName(self):
        return self.getDataCA(0xFF,0x82)

    def getDataProductSerialNumber(self):
        return self.getDataCA(0xFF,0x83)

    def getDataProductUSBIdentifier(self):
        return self.getDataCA(0xFF,0x84)
        
    def getDataProductVersion(self):
        return self.getDataCA(0xFF,0x85)
        
    ###          
        
    def loadKey(self,KeyIndex,Key,InVolatile = True,isTypeA = True):
        if len(Key) != 6:
            raise apduBuilderException("invalid key size, must be 6, got "+str(len(Key)))
        
        if InVolatile:
            if KeyIndex < 0 or KeyIndex > 3:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 3 was expected, got "+str(KeyIndex))
            
            if not isTypeA:
                KeyIndex &= 0x10
            
            return ApduDefault(cla=0xFF,ins=0x82,p1=0x00,p2=KeyIndex,data=Key)
        else:
            if KeyIndex < 0 or KeyIndex > 15:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 15 was expected, got "+str(KeyIndex))
        
            if not isTypeA:
                KeyIndex &= 0x10
        
            return ApduDefault(cla=0xFF,ins=0x82,p1=0x00,p2=KeyIndex,data=Key)
        
        
    def generalAuthenticate(self,blockNumber,KeyIndex,InVolatile = True,isTypeA = True):
        if blockNumber < 0 or blockNumber > 255:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if InVolatile:
            if KeyIndex < 0 or KeyIndex > 3:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 3 was expected, got "+str(KeyIndex))
                
            KeyIndex &= 0x20
        else:
            if KeyIndex < 0 or KeyIndex > 15:
                raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 15 was expected, got "+str(KeyIndex))
            
        if isTypeA:
            datas = [0x01,0x00,blockNumber,0x60,KeyIndex]
        else:
            datas = [0x01,0x00,blockNumber,0x61,KeyIndex]
     
        return ApduDefault(cla=0xFF,ins=0x88,p1=0x00,p2=0x00,data=datas)
        
    def readBinary(self, address = 0):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 65535 was expected, got "+str(address))
        
        lsb = address&0xFF
        msb = (address>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xB0,p1=msb,p2=lsb)
        
    def mifareClassicRead(self,blockNumber,Key = None):
        if blockNumber < 0 or blockNumber > 255:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))
        
        if Key == None:
            return ApduDefault(cla=0xFF,ins=0xF3,p1=0x00,p2=blockNumber)
        else:
            if len(Key) != 6:
                raise apduBuilderException("invalid key size, must be 6, got "+str(len(Key)))
                
            return ApduDefault(cla=0xFF,ins=0xF3,p1=0x00,p2=blockNumber,data=Key)
            
    def updateBinary(self,datas):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 65535 was expected, got "+str(address))
        
        if len(datas) < 1 or len(datas) > 255:
            raise apduBuilderException("invalid datas size, must be a list from 1 to 255 item, got "+str(len(datas)))
        
        lsb = address&0xFF
        msb = (address>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xD6,p1=msb,p2=lsb,data=datas)
        
    def mifareClassifWrite(self,blockNumber,datas,Key = None):
        if blockNumber < 0 or blockNumber > 255:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 255 was expected, got "+str(blockNumber))

        if len(datas) < 1 or len(datas) > 255:
            raise apduBuilderException("invalid datas size, must be a list from 1 to 255 item, got "+str(len(datas)))
            
        if (len(datas) % 16) != 0:
            raise apduBuilderException("invalid datas size, must be a multiple of 16")

        if Key == None:
            return ApduDefault(cla=0xFF,ins=0xF4,p1=0x00,p2=lsb,data=datas)
        else:
            if len(Key) != 6:
                raise apduBuilderException("invalid key size, must be 6, got "+str(len(Key)))
        
            toSend = []
            toSend.extend(datas)
            toSend.extend(Key)
            return ApduDefault(cla=0xFF,ins=0xF4,p1=0x00,p2=lsb,data=toSend)
        
    
    #### SLOT CONTROL ####
    
    def slotControlResumeCardTracking(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x00,p2=0x00)
    
    def slotControlSuspendCardTracking(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x01,p2=0x00)
    
    def slotControlStopRFField(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x10,p2=0x00)

    def slotControlStartRFField(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x10,p2=0x01)
        
    def slotControlResetRFField(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x10,p2=0x02)

    def slotControlTCLDeactivation(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x00)

    def slotControlTCLActivationTypeA(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x01)

    def slotControlTCLActivationTypeB(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x02)
        
    def slotControlDisableNextTCL(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x04)

    def slotControlDisableEveryTCL(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x05)

    def slotControlEnableTCLAgain(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x06)

    def slotControlResetAfterNextDisconnectAndDisableNextTCL(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0x20,p2=0x07)
        
    def slotControlStop(self):
        return ApduDefault(cla=0xFF,ins=0xFB,p1=0xDE,p2=0xAD)
    
    #### CALYPSO METHOD ###
    
    def configureCalypsoSamSetSpeed9600(self):
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x04,p2=0x00)
        
    def configureCalypsoSamSetSpeed115200(self):
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x04,p2=0x01)

    def configureCalypsoSamEnableInternalDigestUpdate(self):
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x08,p2=0x00)

    def configureCalypsoSamDisableInternalDigestUpdate(self):
        return ApduDefault(cla=0xFF,ins=0xFC,p1=0x08,p2=0x01)

##############################################################################################################
##############################################################################################################
##############################################################################################################


try:
    Executer
except NameError:
    print "  No variable Executer found, this is an addon, it can't be executed alone"
    exit()

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
        Executer.executeAPDU(DefaultProxnroll.setLedColorFun(convertTokentToCode(args[0]),convertTokentToCode(args[1]),convertTokentToCode(args[2])))
    else:
        Executer.executeAPDU(DefaultProxnroll.setLedColorFun(convertTokentToCode(args[0]),convertTokentToCode(args[1])))
    
def setBuzzerDuration(envi,args):    
    if len(args) == 0:
        duration = 0
    else:
        duration = args[0]

    Executer.executeAPDU(DefaultProxnroll.setBuzzerDuration(duration))
    
def calypsoSpeed(envi,args):
    if args[0] == "9600":
        Executer.executeAPDU(DefaultProxnroll.configureCalypsoSamSetSpeed9600())
    else:
        Executer.executeAPDU(DefaultProxnroll.configureCalypsoSamSetSpeed115200())
    
def enableCalypsoDigestUpdate(envi,args):
    Executer.executeAPDU(DefaultProxnroll.configureCalypsoSamEnableInternalDigestUpdate())
def enableCalypsoDigestUpdate(envi,args):
    Executer.executeAPDU(DefaultProxnroll.configureCalypsoSamDisableInternalDigestUpdate())
def vendorName(envi,args):
    Executer.executeAPDUAndConvertDataToString(DefaultProxnroll.getDataVendorName())
def productName(envi,args):
    Executer.executeAPDUAndConvertDataToString(DefaultProxnroll.getDataProductName())     
def productSerial(envi,args):
    Executer.executeAPDUAndConvertDataToString(DefaultProxnroll.getDataProductSerialNumber())
def productUSBIdentifier(envi,args):
    Executer.executeAPDUAndConvertDataToString(DefaultProxnroll.getDataProductUSBIdentifier())
def productVersion(envi,args):
    Executer.executeAPDUAndConvertDataToString(DefaultProxnroll.getDataProductVersion())
def cardSerialNumber(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataCardSerialNumber())
def cardATS(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataCardATS())
def cardCompleteIdentifier(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataCardCompleteIdentifier())
def cardType(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataCardType())    
def cardShortSerialNumber(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataCardShortSerialNumber())
def cardATR(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataCardATR())
def productSerialNumber(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataProductSerialNumber())
def harwareIdentifier(envi,args):
    Executer.executeAPDUAndPrintData(DefaultProxnroll.getDataHarwareIdentifier())      
def controlResumeCardTracking(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlResumeCardTracking())
def controlSuspendCardTracking(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlSuspendCardTracking())
def controlStopRFField(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlStopRFField())
def controlStartRFField(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlStartRFField())
def controlResetRFField(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlResetRFField())
def controlTCLDeactivation(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlTCLDeactivation())
def controlTCLActivationTypeA(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlTCLActivationTypeA())
def controlTCLActivationTypeB(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlTCLActivationTypeB())
def controlDisableNextTCL(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlDisableNextTCL())
def controlDisableEveryTCL(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlDisableEveryTCL())
def controlEnableTCLAgain(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlEnableTCLAgain())
def controlResetAfterNextDisconnectAndDisableNextTCL(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlResetAfterNextDisconnectAndDisableNextTCL())
def controlStop(envi,args):
    Executer.executeAPDU(DefaultProxnroll.slotControlStop())

def testInstruction():
    pass
    
def readInstruction(envi,args):
    if len(args) == 0:
        Executer.executeAPDUAndPrintData(DefaultProxnroll.readBinary())
    else:
        Executer.executeAPDUAndPrintData(DefaultProxnroll.readBinary(args[0]))
        


t = tokenValueArgChecker(["off","on","auto","slow","quick","beat"])
Executer.addCommand(["proxnroll","setlight"],                               "proxnroll setlight",                     "",True,setLedColorFun,MultiArgsChecker([t,t],[t,t,t]))
i0to60000 = IntegerArgChecker(0,60000)
Executer.addCommand(["proxnroll","setbuzzer"],                              "proxnroll setbuzzer",                    "",True,setBuzzerDuration,MultiArgsChecker([],[i0to60000]))

speedToken = tokenValueArgChecker(["9600","115200"])
Executer.addCommand(["proxnroll","calypso","setspeed"],                     "proxnroll calypso set speed",            "",True,calypsoSpeed,DefaultArgsChecker([speedToken]))
Executer.addCommand(["proxnroll","calypso","enabledigestupdate"],           "proxnroll calypso enable digest update", "",True,enableCalypsoDigestUpdate,None)
Executer.addCommand(["proxnroll","calypso","disabledigestupdate"],          "proxnroll calypso disable digest update","",True,enableCalypsoDigestUpdate,None)

Executer.addCommand(["proxnroll","information","vendor"],                   "proxnroll vendor name",                  "",True,vendorName,None)
Executer.addCommand(["proxnroll","information","product","name"],           "proxnroll product name",                 "",True,productName,None)
Executer.addCommand(["proxnroll","information","product","serialString"],   "proxnroll product serial",               "",True,productSerial,None)
Executer.addCommand(["proxnroll","information","product","usbidentifiel"],  "proxnroll product usb identifier",       "",True,productUSBIdentifier,None)
Executer.addCommand(["proxnroll","information","product","version"],        "proxnroll product version",              "",True,productVersion,None)
Executer.addCommand(["proxnroll","information","card","serial"],            "proxnroll product version",              "",True,cardSerialNumber,None)
Executer.addCommand(["proxnroll","information","card","ats"],               "proxnroll product version",              "",True,cardATS,None)
Executer.addCommand(["proxnroll","information","card","completeIdentifier"],"proxnroll product version",              "",True,cardCompleteIdentifier,None)
Executer.addCommand(["proxnroll","information","card","type"],              "proxnroll product version",              "",True,cardType,None)
Executer.addCommand(["proxnroll","information","card","shortSerial"],       "proxnroll product version",              "",True,cardShortSerialNumber,None)
Executer.addCommand(["proxnroll","information","card","atr"],               "proxnroll product version",              "",True,cardATR,None)
Executer.addCommand(["proxnroll","information","product","serial"],         "proxnroll product version",              "",True,productSerialNumber,None)
Executer.addCommand(["proxnroll","information","harwareIdentifier"],        "proxnroll product version",              "",True,harwareIdentifier,None)

Executer.addCommand(["proxnroll","control","tracking","resume"],            "proxnroll control ",                     "",True,controlResumeCardTracking,None)
Executer.addCommand(["proxnroll","control","tracking","suspend"],           "proxnroll control ",                     "",True,controlSuspendCardTracking,None)
Executer.addCommand(["proxnroll","control","rffield","stop"],               "proxnroll control ",                     "",True,controlStopRFField,None)
Executer.addCommand(["proxnroll","control","rffield","start"],              "proxnroll control ",                     "",True,controlStartRFField,None)
Executer.addCommand(["proxnroll","control","rffield","reset"],              "proxnroll control ",                     "",True,controlResetRFField,None)

Executer.addCommand(["proxnroll","control","t=cl","deactivation"],          "proxnroll control ",                     "",True,controlTCLDeactivation,None)
Executer.addCommand(["proxnroll","control","t=cl","activation","a"],        "proxnroll control ",                     "",True,controlTCLActivationTypeA,None)
Executer.addCommand(["proxnroll","control","t=cl","activation","b"],        "proxnroll control ",                     "",True,controlTCLActivationTypeB,None)
Executer.addCommand(["proxnroll","control","t=cl","disable","next"],        "proxnroll control ",                     "",True,controlDisableNextTCL,None)
Executer.addCommand(["proxnroll","control","t=cl","disable","every"],       "proxnroll control ",                     "",True,controlDisableEveryTCL,None)
Executer.addCommand(["proxnroll","control","t=cl","enable"],                "proxnroll control ",                     "",True,controlEnableTCLAgain,None)
Executer.addCommand(["proxnroll","control","t=cl","reset"],                 "proxnroll control ",                     "",True,controlResetAfterNextDisconnectAndDisableNextTCL,None)

Executer.addCommand(["proxnroll","control","stop"],                         "proxnroll control ",                     "",True,controlStop,None,resultHandlerAPDU)

#TODO
Executer.addCommand(["proxnroll","test"],                                   "proxnroll test instruction",             "",True,testInstruction,None)

#TODO def encapsulate(self,datas,protocolType=0x00,timeoutType=0x00,defaultSW = True):

#TODO def loadKey(self,KeyIndex,Key,InVolatile = True,isTypeA = True):

    #TODO def generalAuthenticate(self,blockNumber,KeyIndex,InVolatile = True,isTypeA = True):

    #TODO def readBinary(self, address = 0):
i = IntegerArgChecker()
Executer.addCommand(["proxnroll","read"],                                   "proxnroll test instruction",             "",True,readInstruction,MultiArgsChecker([],[i]))

    #TODO def mifareClassicRead(self,blockNumber,Key = None):

    #TODO def updateBinary(self,datas):

    #TODO def mifareClassifWrite(self,blockNumber,datas,Key = None):








#!/usr/bin/python2.6
from arg.args import *
from apdu.apduExecuter import Executer
from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.apdu import ApduDefault

class acr122APDUBuilder(iso7816_4APDUBuilder):
    def getDataCardSerialNumber(self):
        return self.getDataCA(0x00,0x00)
    
    def getDataCardATS(self):
        return self.getDataCA(0x01,0x00)
        
    def loadKey(self,KeyIndex,Key):
        if len(Key) != 6:
            raise apduBuilderException("invalid key size, must be 6, got "+str(len(Key)))
        
        if KeyIndex < 0 or KeyIndex > 1:
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 15 was expected, got "+str(KeyIndex))
    
        return ApduDefault(cla=0xFF,ins=0x82,p1=0x00,p2=KeyIndex,data=Key)

    def authentificationObsolete(self):
        pass #TODO
        
    def authentification(self):
        pass #TODO
        
    def readBinary(self):
        pass #TODO
        
    def updateBinary(self):
        pass #TODO
        
    def valueBlockOperation(self):
        pass #TODO
        
    def readValueBlock(self):
        pass #TODO
        
    def restoreValueBlock(self):
        pass #TODO
        
    def directTransmit(self):
        pass #TODO
        
    def ledAndBuzzerControl(self):
        pass #TODO
        
    def getFirmwareVersion(self):
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x48,p2=0x01)
        
    def getPICCOperatingParameter(self):
        return ApduDefault(cla=0xFF,ins=0x00,p1=0x50,p2=0x01)
        
    def setPICCOperatingParameter(self):
        pass #TODO
        
    def setTimeoutParameter(self):
        pass #TODO
        
    def setBuzzerOutputEnable(self):
        pass #TODO

defaultACR = acr122APDUBuilder()
        
def cardSerialNumber(envi,args):
    Executer.executeAPDUAndPrintData(defaultACR.getDataCardSerialNumber())
def cardATS(envi,args):
    Executer.executeAPDUAndPrintData(defaultACR.getDataCardATS())
def firmwareVersion(envi,args):
    Executer.executeAPDUAndConvertDataToString(defaultACR.getFirmwareVersion())
def PICCOperatingParameter(envi,args):
    Executer.executeAPDUAndPrintData(defaultACR.getPICCOperatingParameter())    
    
Executer.addCommand(["acr122","information","card","serial"],"acr122 card serial","",True,cardSerialNumber)
Executer.addCommand(["acr122","information","card","ats"],"acr122 card historic byte","",True,cardATS)
Executer.addCommand(["acr122","information","firmware"],"acr122 firmware version","",True,firmwareVersion)
Executer.addCommand(["acr122","information","piccparameter"],"acr122 picc parameter","",True,PICCOperatingParameter)

#TODO loadKey

#!/usr/bin/python2.6

from apdu.apdu import ApduDefault
from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.exception import apduBuilderException

from arg.args import *
from apdu.apduExecuter import *


class scl3711APDUBuilder(iso7816_4APDUBuilder):
    
    @staticmethod 
    def getDataCardSerialNumber():
        return iso7816_4APDUBuilder.getDataCA(0x00,0x00)
        
    @staticmethod
    def getDataCardATS():
        return iso7816_4APDUBuilder.getDataCA(0x01,0x00)
            
    @staticmethod
    def encapsulate(datas):
        #TODO limite de 255
        
        return ApduDefault(cla=0xFF,ins=0xFE,p1=0x00,p2=0x00,data=datas)
        
    @staticmethod
    def sendDataPassThrough(datas):
        #TODO limite de 255
        
        return ApduDefault(cla=0xFF,ins=0xFE,p1=0x00,p2=0x00,data=datas)
        
    @staticmethod
    def readBinary(address = 0):
        if address < 0 or address > 255:
            raise apduBuilderException("invalid argument address, a value between 0 and 255 was expected, got "+str(address))

        return ApduDefault(cla=0xFF,ins=0xB0,p1=0x00,p2=address&0xFF)
        
    @staticmethod
    def updateBinary(datas,address=0):
        if address < 0 or address > 255:
            raise apduBuilderException("invalid argument address, a value between 0 and 255 was expected, got "+str(address))

        if len(datas) < 1 or len(datas) > 255:
            raise apduBuilderException("invalid datas size, must be a list from 1 to 255 item, got "+str(len(datas)))

        return ApduDefault(cla=0xFF,ins=0xD6,p1=0x00,p2=address&0xFF,data=datas)
    
    @staticmethod
    def loadKey(KeyName,isTypeA = True):
        #TODO KeyName
        
        if len(Key) != 6:
            raise apduBuilderException("invalid key size, must be 6, got "+str(len(Key)))

        if isTypeA:
            P2 = 0x60
        else:
            P2 = 0x61
            
        return ApduDefault(cla=0xFF,ins=0x82,p1=0x00,p2=P2,data=Key)
        
    @staticmethod
    def generalAuthenticate(blockNumber,isTypeA = True,KeyIndex = 0):
        if blockNumber < 0 or blockNumber > 65535:
            raise apduBuilderException("invalid argument blockNumber, a value between 0 and 65535 was expected, got "+str(blockNumber))

        lsb = address&0xFF
        msb = (address>>8)&0xFF

        if KeyIndex < 0 or KeyIndex > 255: #verification hasardeuse, le nombre de cle dans la doc n'est pas dis
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 255 was expected, got "+str(KeyIndex))

        if isTypeA:
            datas = [0x01,msb,lsb,0x60,KeyIndex]
        else:
            datas = [0x01,msb,lsb,0x61,KeyIndex]

        return ApduDefault(cla=0xFF,ins=0x88,p1=0x00,p2=0x00,data=datas)
            
    @staticmethod
    def increment(address=0,value=0x01,increment=True):
        if address < 0 or address > 255:
            raise apduBuilderException("invalid argument address, a value between 0 and 255 was expected, got "+str(address))

        if value < 0 or value > 0xFFFFFFFF:
            raise apduBuilderException("invalid argument value, a value between 0 and 4294967295 was expected, got "+str(value))
            
        if increment:
            return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=address,data=[0xC0,address,value&0xFF,(value>>8)&0xFF,(value>>16)&0xFF,(value>>24)&0xFF])
        else:
            return ApduDefault(cla=0xFF,ins=0xF0,p1=0x00,p2=address,data=[0xC1,address,value&0xFF,(value>>8)&0xFF,(value>>16)&0xFF,(value>>24)&0xFF])
            
            
    @staticmethod
    def userToken():
        pass #TODO doc officiel incomplete...
        
    #@staticmethod
    #def desfireApdu(apdu):
    #    return apdu
    
    @staticmethod
    def nfcType1ReadIdentification():
        return ApduDefault(cla=0xFF,ins=0x50)

    @staticmethod
    def nfcType1ReadAll():
        return ApduDefault(cla=0xFF,ins=0x52)
        
    @staticmethod
    def nfcType1ReadByte(byteNumber=0,blockNumber=0):
        if byteNumber < 0 or byteNumber > 7:
            raise apduBuilderException("invalid argument byteNumber, a value between 0 and 7 was expected, got "+str(byteNumber))
        
        if blockNumber < 0 or blockNumber > 0xE:
            raise apduBuilderException("invalid argument byteNumber, a value between 0 and 14 was expected, got "+str(byteNumber))
        
        P2 = (byteNumber&0x7) | ((blockNumber&0x0f)<<3)
        
        return ApduDefault(cla=0xFF,ins=0x54,p1=0x00,p2=P2)
    
    @staticmethod
    def nfcType1WriteByte(byteValue,byteNumber=0,blockNumber=0,erase=True):
        if byteValue < 0 or byteValue > 255:
            raise apduBuilderException("invalid argument byteValue, a value between 0 and 255 was expected, got "+str(byteValue))
        
        if byteNumber < 0 or byteNumber > 7:
            raise apduBuilderException("invalid argument byteNumber, a value between 0 and 7 was expected, got "+str(byteNumber))
        
        if blockNumber < 0 or blockNumber > 0xE:
            raise apduBuilderException("invalid argument byteNumber, a value between 0 and 14 was expected, got "+str(byteNumber))
        
        P2 = (byteNumber&0x7) | ((blockNumber&0x0f)<<3)
        
        if erase:
            return ApduDefault(cla=0xFF,ins=0x56,p1=0x00,p2=P2,data=[byteValue])
        else:
            return ApduDefault(cla=0xFF,ins=0x58,p1=0x00,p2=P2,data=[byteValue])
    
    @staticmethod
    def nfcType1ReadSegment(address=0):
        if address < 0 or address > 0xF:
            raise apduBuilderException("invalid argument address, a value between 0 and 15 was expected, got "+str(address))
    
        return ApduDefault(cla=0xFF,ins=0x5A,p1=0x00,p2=((address&0xF)<<4))
    
    @staticmethod
    def nfcType1Read8bytes(address=0):
        if address < 0 or address > 0xFF:
            raise apduBuilderException("invalid argument address, a value between 0 and 255 was expected, got "+str(address))

        return ApduDefault(cla=0xFF,ins=0x5C,p1=0x00,p2=address)
    
    @staticmethod
    def nfcType1Write8Bytes(bytes,address=0,erase=True):
        if address < 0 or address > 0xFF:
            raise apduBuilderException("invalid argument address, a value between 0 and 255 was expected, got "+str(address))
            
        if len(bytes) != 8:
            raise apduBuilderException("invalid bytes size, must be a list of 8 item, got "+str(len(bytes)))
        
        if erase:
            return ApduDefault(cla=0xFF,ins=0x5E,p1=0x00,p2=address,data=bytes)
        else:
            return ApduDefault(cla=0xFF,ins=0x60,p1=0x00,p2=address,data=bytes)
        
    @staticmethod
    def nfcType3REQC(serviceCode,RFU,TSN):
        if serviceCode < 0 or serviceCode > 0xFFFF:
            raise apduBuilderException("invalid argument serviceCode, a value between 0 and 65535 was expected, got "+str(serviceCode))
        
        if RFU < 0 or RFU > 0xFF:
            raise apduBuilderException("invalid argument RFU, a value between 0 and 255 was expected, got "+str(RFU))
        
        if TSN < 0 or TSN > 0xFF:
            raise apduBuilderException("invalid argument TSN, a value between 0 and 255 was expected, got "+str(TSN))
            
        return ApduDefault(cla=0xFF,ins=0x40,p1=0x00,p2=0x00,data=[(serviceCode>>8)&0xFF,serviceCode&0xFF,RFU,TSN])
        
    @staticmethod
    def nfcType3RequestService(ServiceCodeList):
        
        Data = []
        for s in ServiceCodeList:
            if s < 0 or s > 0xFFFF:
                raise apduBuilderException("invalid argument in service code list, a value between 0 and 65535 was expected, got "+str(s))
                
            lsb = s&0xFF
            msb = (s>>8)&0xFF
            
            Data.extend([msb,lsb])
        
        return ApduDefault(cla=0xFF,ins=0x42,p1=len(ServiceCodes),p2=0x00,data=Data)
        
    @staticmethod
    def nfcType3RequestRespons():
        return ApduDefault(cla=0xFF,ins=0x44)
        
    @staticmethod
    def nfcType3Read(ServiceCodeList,BlockCodeList):
        Data = []
        for s in ServiceCodeList:
            if s < 0 or s > 0xFFFF:
                raise apduBuilderException("invalid argument in service code list, a value between 0 and 65535 was expected, got "+str(s))
                
            lsb = s&0xFF
            msb = (s>>8)&0xFF
            
            Data.extend([msb,lsb])
            
        for s in BlockCodeList:
            if s < 0 or s > 0xFFFF:
                raise apduBuilderException("invalid argument in block code list, a value between 0 and 65535 was expected, got "+str(s))

            lsb = s&0xFF
            msb = (s>>8)&0xFF

            Data.extend([msb,lsb])
        
        return ApduDefault(cla=0xFF,ins=0x46,p1=len(ServiceCodes),p2=len(BlockCodes),data=Data)
        
    @staticmethod
    def nfcType3Write(ServiceCodeList,BlockCodeList,DataList):
        #check len(BlockCodeList) vs len(DataList)
        if len(BlockCodeList) * 16 != len(DataList):
            raise apduBuilderException("invalid DataList size, must be a list equals to "+str(len(BlockCodeList) * 16)+" bytes, got "+str(len(DataList)))
        
        Data = []
        for s in ServiceCodeList:
            if s < 0 or s > 0xFFFF:
                raise apduBuilderException("invalid argument in service code list, a value between 0 and 65535 was expected, got "+str(s))
                
            lsb = s&0xFF
            msb = (s>>8)&0xFF
            
            Data.extend([msb,lsb])
            
        for s in BlockCodeList:
            if s < 0 or s > 0xFFFF:
                raise apduBuilderException("invalid argument in block code list, a value between 0 and 65535 was expected, got "+str(s))

            lsb = s&0xFF
            msb = (s>>8)&0xFF

            Data.extend([msb,lsb])
            
        #append DataList
        Data.extend(DataList)
        
        return ApduDefault(cla=0xFF,ins=0x48,p1=len(ServiceCodes),p2=len(BlockCodes),data=Data)
        
    @staticmethod
    def nfcType3RequestSystemCode():
        return ApduDefault(cla=0xFF,ins=0x4A)
        

try:
    Executer
except NameError:
    print "  No variable Executer found, this is an addon, it can't be executed alone"
    exit()
        
i = IntegerArgChecker()   
Executer.addCommand(CommandStrings=["scl3711","card","serial"],             preProcess=scl3711APDUBuilder.getDataCardSerialNumber,      process=executeAPDU             ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","card","ats"],                preProcess=scl3711APDUBuilder.getDataCardATS,               process=executeAPDU             ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","encapsulate"],               preProcess=scl3711APDUBuilder.encapsulate,                  process=executeAPDU             ,argChecker=AllTheSameChecker(hexaArgChecker(),"datas",0xFF),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["scl3711","senddata"],                  preProcess=scl3711APDUBuilder.sendDataPassThrough,          process=executeAPDU             ,argChecker=AllTheSameChecker(hexaArgChecker(),"datas",0xFF),postProcess=resultHandlerAPDUAndPrintDataAndSW)
Executer.addCommand(CommandStrings=["scl3711","read"],                      preProcess=scl3711APDUBuilder.readBinary,                   process=executeAPDU             ,argChecker=DefaultArgsChecker([("address",i)],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","update"],                    preProcess=scl3711APDUBuilder.updateBinary,                 process=executeAPDU             ,argChecker=InfiniteArgsChecker("datas",hexaArgChecker(),[("address",hexaArgChecker(0,0xFF))],defaultLimitChecker(0xFF)))
                
typeAB = tokenValueArgChecker({"a":True,"b":False})
Executer.addCommand(CommandStrings=["scl3711","mifare","loadkey"],          preProcess=scl3711APDUBuilder.loadKey,                      process=executeAPDU             ,argChecker=DefaultArgsChecker([("KeyName",stringArgChecker()),("isTypeA",typeAB)],1))
Executer.addCommand(CommandStrings=["scl3711","mifare","authenticate"],     preProcess=scl3711APDUBuilder.generalAuthenticate,          process=executeAPDU             ,argChecker=DefaultArgsChecker([("blockNumber",hexaArgChecker(0,0xFF)),("KeyIndex",IntegerArgChecker(0,15)),("isTypeA",typeAB)],2))

typeDec = tokenValueArgChecker({"inc":True,"dec":False})
Executer.addCommand(CommandStrings=["scl3711","mifare","increment"],        preProcess=scl3711APDUBuilder.increment,                    process=executeAPDU             ,argChecker=DefaultArgsChecker([("address",hexaArgChecker(0,0xFF)),("value",hexaArgChecker(0,0xFFFFFFFF)),("increment",typeDec)],2))

#TODO  userToken, doc officiel incomplete...
        
#NFC
Executer.addCommand(CommandStrings=["scl3711","nfc1","identification"],     preProcess=scl3711APDUBuilder.nfcType1ReadIdentification,   process=executeAPDU             ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","nfc1","readall"],            preProcess=scl3711APDUBuilder.nfcType1ReadAll,              process=executeAPDU             ,postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","nfc1","read","segment"],     preProcess=scl3711APDUBuilder.nfcType1ReadSegment,          process=executeAPDU             ,argChecker=DefaultArgsChecker([("address",hexaArgChecker(0,0xF))],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","nfc1","read","8bytes"],      preProcess=scl3711APDUBuilder.nfcType1Read8bytes,           process=executeAPDU             ,argChecker=DefaultArgsChecker([("address",hexaArgChecker(0,0xFF))],0),postProcess=resultHandlerAPDUAndPrintData)
Executer.addCommand(CommandStrings=["scl3711","nfc1","read","byte"],        preProcess=scl3711APDUBuilder.nfcType1ReadByte,             process=executeAPDU             ,argChecker=DefaultArgsChecker([("byteNumber",hexaArgChecker(0,0x7)),("blockNumber",hexaArgChecker(0,0xE))],0),postProcess=resultHandlerAPDUAndPrintData)

eraseToken = tokenValueArgChecker({"erase":True,"noerase":False})
Executer.addCommand(CommandStrings=["scl3711","nfc1","write","byte"],       preProcess=scl3711APDUBuilder.nfcType1WriteByte,            process=executeAPDU             ,argChecker=DefaultArgsChecker([("byteValue",hexaArgChecker(0,0xFF)),("byteNumber",hexaArgChecker(0,0x7)),("blockNumber",hexaArgChecker(0,0xE)),("erase",eraseToken)],1))
Executer.addCommand(CommandStrings=["scl3711","nfc1","write","8byte"],       preProcess=scl3711APDUBuilder.nfcType1Write8Bytes,         process=executeAPDU             ,argChecker=InfiniteArgsChecker("bytes",hexaArgChecker(),[("address",hexaArgChecker(0,0xFF)),("erase",eraseToken)],defaultLimitChecker(0xFF)))


#TODO def nfcType3REQC(serviceCode,RFU,TSN):
#TODO def nfcType3RequestService(ServiceCodeList):
Executer.addCommand(CommandStrings=["scl3711","nfc3","request","response"], preProcess=scl3711APDUBuilder.nfcType3RequestRespons,       process=executeAPDU             ,postProcess=resultHandlerAPDUAndPrintData)
    
#TODO def nfcType3Read(ServiceCodeList,BlockCodeList):
#TODO def nfcType3Write(ServiceCodeList,BlockCodeList,DataList):
Executer.addCommand(CommandStrings=["scl3711","nfc3","request","systemcode"],preProcess=scl3711APDUBuilder.nfcType3RequestSystemCode,   process=executeAPDU             ,postProcess=resultHandlerAPDUAndPrintData)

        
        
        
        
        
        
        
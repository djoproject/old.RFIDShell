from addons.iso7816_4 import iso7816_4APDUBuilder
from apdu.apdu import ApduDefault

class pcscAPDUBuilder(iso7816_4APDUBuilder):
    @staticmethod 
    def getDataCardSerialNumber():
        "build a pcsc apdu to get the uid"
        return iso7816_4APDUBuilder.getDataCA(0x00,0x00)
    
    @staticmethod
    def getDataCardATS():
        "build a pcsc apdu to get the historical bytes"
        return iso7816_4APDUBuilder.getDataCA(0x01,0x00)
        
    @staticmethod
    def loadKey(KeyIndex,KeyName,InVolatile = True,isCardKey=True,ReaderKey = None):
        if KeyName not in keys:
            raise apduBuilderException("the key name doesn't exist "+str(KeyName))
            
        if len(keys[KeyName]) < 1 or len(keys[KeyName]) > 255:
            raise apduBuilderException("invalid key size, must be a list from 1 to 255 item, got "+str(len(pin)))
            
        if KeyIndex < 0 or KeyIndex > 255:
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 255 was expected, got "+str(KeyIndex))
            
        P1 = 0x00
        
        if not InVolatile:
            P1 |= 0x20
            
        if not isCardKey:
            P1 |= 0x80
        
        if ReaderKey != None:
            if ReaderKey < 0 or ReaderKey > 15:
                raise apduBuilderException("invalid argument ReaderKey, a value between 0 and 15 was expected, got "+str(ReaderKey))
            
            P1 |= 0x40
            P1 |= (ReaderKey&0x0f)
            
        #the 0x10 bit is Reserved Future Use
        
        return ApduDefault(cla=0xFF,ins=0x82,p1=P1,p2=KeyIndex,data=keys[KeyName])
    @staticmethod
    def getAuthenticateData(address,KeyIndex,InVolatile = True ,isTypeA = True):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 255 was expected, got "+str(address))
        
        if KeyIndex < 0 or KeyIndex > 255:
            raise apduBuilderException("invalid argument KeyIndex, a value between 0 and 255 was expected, got "+str(KeyIndex))
        
        lsb = address&0xFF
        msb = (address>>8)&0xFF
          
        if isTypeA:
            datas = [msb,lsb,0x60,KeyIndex]
        else:
            datas = [msb,lsb,0x61,KeyIndex]
            
    @staticmethod
    def generalAuthenticate(blockNumber,KeyIndex,InVolatile = True ,isTypeA = True):
        data = [0x01] #Auth version
        
        data.extend(pcscAPDUBuilder.getAuthenticateData(blockNumber,KeyIndex,InVolatile,isTypeA))
     
        return ApduDefault(cla=0xFF,ins=0x86,p1=0x00,p2=0x00,data=datas)
    
    def obsoleteAuthenticate(blockNumber,KeyIndex,InVolatile = True ,isTypeA = True):
        ret = ApduRaw([0xFF,0x88])
        ret.extend(pcscAPDUBuilder.getAuthenticateData(blockNumber,KeyIndex,InVolatile,isTypeA))
        return ret
        
    @staticmethod
    def readBinary(address = 0,expected=0):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 65535 was expected, got "+str(address))
        
        lsb = address&0xFF
        msb = (address>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xB0,p1=msb,p2=lsb,expected_answer=expected)
        
    @staticmethod
    def updateBinary(datas,address=0):
        if address < 0 or address > 65535:
            raise apduBuilderException("invalid argument address, a value between 0 and 65535 was expected, got "+str(address))
        
        if len(datas) < 1 or len(datas) > 255:
            raise apduBuilderException("invalid datas size, must be a list from 1 to 255 item, got "+str(len(datas)))
        
        lsb = address&0xFF
        msb = (address>>8)&0xFF
        
        return ApduDefault(cla=0xFF,ins=0xD6,p1=msb,p2=lsb,data=datas)
        
    @staticmethod
    def verifyCommand(pin,reference=0,ReaderKey=None):
        if len(pin) < 1 or len(pin) > 255:
            raise apduBuilderException("invalid pin size, must be a list from 1 to 255 item, got "+str(len(pin)))
            
        if reference < 0 or reference > 255:
            raise apduBuilderException("invalid argument reference, a value between 0 and 255 was expected, got "+str(reference))
            
        structure = 0
        if ReaderKey != None:
            structure |= 0x40
            if ReaderKey < 0 or ReaderKey > 15:
                raise apduBuilderException("invalid argument ReaderKey, a value between 0 and 255 was expected, got "+str(ReaderKey))
        
            structure |= (ReaderKey&0xf)
        
        return ApduDefault(cla=0xFF,ins=0x20,p1=structure,p2=reference,data=pin)
        
        
        

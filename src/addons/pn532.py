from apdu.apdu import ApduPn53x
from apdu.exception import apduBuilderException

class pn532APDUBuilder(object):
    
    #Miscellaneous
    
    def Diagnose():
        pass#TODO
        
    def GetFirmwareVersion():
        return ApduPn53x(0x02)
        
    def GetGeneralStatus():
        return ApduPn53x(0x04)
    
    def ReadRegister():
        pass#TODO
    
    def WriteRegister():
        pass#TODO
    
    def ReadGPIO():
        return ApduPn53x(0x0c)
    
    def WriteGPIO():
        pass#TODO
    
    def SetSerialBaudRate():
        pass#TODO
    
    def SetParameters():
        pass#TODO
    
    def SAMConfiguration():
        pass#TODO
    
    def PowerDown():
        pass#TODO
    
    #RF communication
    
    def RFConfiguration():
        pass#TODO
    
    def RFRegulationTest():
        pass#TODO
    
    #Initiator
    
    def InJumpForDEP():
        pass#TODO
    
    def InJumpForPSL():
        pass#TODO
    
    def InListPassiveTarget():
        pass#TODO
    
    def InATR():
        pass#TODO
    
    def InPSL():
        pass#TODO
    
    def InDataExchange():
        pass#TODO
    
    def InCommunicateThru():
        pass#TODO
    
    AllTarget = 0x00
    Target1 = 0x01
    Target2 = 0x02
    def InDeselect(target = 0):
        if target < 0 or target > 2:
            raise apduBuilderException("invalid argument target, a value between 0 and 2 was expected, got "+str(target))
            
        return ApduPn53x(0x44,[target])
    
    def InRelease(target = 0):
        if target < 0 or target > 2:
            raise apduBuilderException("invalid argument target, a value between 0 and 2 was expected, got "+str(target))
            
        return ApduPn53x(0x52,[target])
    
    def InSelect():
        if target < 0 or target > 2:
            raise apduBuilderException("invalid argument target, a value between 0 and 2 was expected, got "+str(target))
            
        return ApduPn53x(0x52,[target])
    
    def InAutoPoll():
        pass#TODO
    
    #Target
    
    def TgInitAsTarget():
        pass#TODO
    
    def TgSetGeneralBytes():
        pass#TODO
    
    def TgGetData():
        return ApduPn53x(0x86)
    
    def TgSetData():
        pass#TODO
    
    def TgSetMetaData():
        pass#TODO
    
    def TgGetInitiatorCommand():
        return ApduPn53x(0x88)
    
    def TgResponseToInitiator():
        pass#TODO
    
    def TgGetTargetStatus():
        return ApduPn53x(0x8A)

def pn532StatusToString(Status):
    if Status == 0x00:
        return "success"
    elif Status == 0x01:
        return "Time Out, the target has not answered"
    elif Status == 0x02:
        return "A CRC error has been detected by the CIU"
    elif Status == 0x03:
        return "A Parity error has been detected by the CIU"
    elif Status == 0x04:
        return "During an anticollision/select operation (ISO/IEC14443-3 Type A and ISO/IEC18092 106 kbps passive mode), an erroneous Bit Count has been detected"
    elif Status == 0x05:    
        return "Framing error during mifare operation"
    elif Status == 0x06:
        return "An abnormal bit-collision has been detected during bit wise anticollision at 106 kbps"
    elif Status == 0x07:
        return "Communication buffer size insufficient"
    elif Status == 0x09:
        return "RF Buffer overflow has been detected by the CIU (bit BufferOvfl of the register CIU_ERROR)"
    elif Status == 0x0A:
        return "In active communication mode, the RF field has not been switched on in time by the counterpart (as defined in NFCIP-1 standard)"
    elif Status == 0x0B:
        return "RF Protocol error (cf. [4], description of the CIU_ERROR register)"
    elif Status == 0x0D:
        return "Temperature error: the internal temperature sensor has detected overheating, and therefore has automatically switched off the antenna drivers"
    elif Status == 0x0E:
        return "Internal buffer overflow"
    elif Status == 0x10:
        return "Invalid parameter (range, format, ...)"
    elif Status == 0x12:
        return "DEP Protocol: The PN532 configured in target mode does not support the command received from the initiator (the command received is not one of the following: ATR_REQ, WUP_REQ, PSL_REQ, DEP_REQ, DSL_REQ, RLS_REQ [1])."
    elif Status == 0x13:
        return "DEP Protocol, mifare or ISO/IEC14443-4: The data format does not match to the specification. Depending on the RF protocol used, it can be: BadlengthofRFreceivedframe,Incorrect value of PCB or PFB,InvalidorunexpectedRFreceivedframe, NADorDIDincoherence."
    elif Status == 0x14:
        return "mifare: Authentication error"
    elif Status == 0x23:
        return "ISO/IEC14443-3: UID Check byte is wrong"
    elif Status == 0x25:
        return "DEP Protocol: Invalid device state, the system is in a state which does not allow the operation"
    elif Status == 0x26:
        return "Operation not allowed in this configuration (host controller interface)"
    elif Status == 0x27:
        return "This command is not acceptable due to the current context of the PN532 (Initiator vs. Target, unknown target number, Target not in the good state, ...)"
    elif Status == 0x29:
        return "The PN532 configured as target has been released by its initiator"
    elif Status == 0x2A:
        return "PN5321 and ISO/IEC14443-3B only: the ID of the card does not match, meaning that the expected card has been exchanged with another one."
    elif Status == 0x2B:
        return "PN5321 and ISO/IEC14443-3B only: the card previously activated has disappeared."
    elif Status == 0x2C:
        return "Mismatch between the NFCID3 initiator and the NFCID3 target in DEP 212/424 kbps passive."
    elif Status == 0x2D:
        return "An over-current event has been detected"
    elif Status == 0x2E:
        return "NAD missing in DEP frame"
    else:
        return "unknwon status"


def pn532ParseAnswer(Answer):
    if len(Answer) < 2:
        return "empty answer"
        
    if Answer[0] != 0xD5:
        return "invalid answer header"
    
    if Answer[1] == 0x03
        if len(Answer) != 6:
            return "invalid answer"
        
        return "IC = %x, Ver = %x, Rev = %x,"%(Answer[2],Answer[3],Answer[4])+" ISO18092 initiator support = "+str(Answer[5]&0x08)+" ISO18092 target support = "+str(Answer[5]&0x04)+" ISO/IEC 14443 TypeB = "+str(Answer[5]&0x02)+" ISO/IEC 14443 TypeA = "+str(Answer[5]&0x01)
        
        
    
    
    
    
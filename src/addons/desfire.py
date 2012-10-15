#!/usr/bin/python2.6

from apdu.apdu import Apdu

class ApduDesfire(Apdu):
    def __init__(self,ins,data = []):
        self.append(ins)
        if len(data) > 0:
            self.extend(data)

class DesfireFileParameter():
    COMSET_PLAINTEXT = 0x00
    COMSET_MAC_DES_3DES = 0x01
    COMSET_FULLY_DES_3DES = 0x03

    FILETYPE_STANDARD = 0x00
    FILETYPE_BACKUP = 0x01
    FILETYPE_VALUE = 0X02
    FILETYPE_LINEAR = 0X03
    FILETYPE_CYCLIC = 0x04

    def __init__(self,init = [0x00, 0x00,0x00,0x00,0x00,0x00,0x00,0x00]):
        self.fileType = init[0]
        if self.fileType == DesfireFileParameter.FILETYPE_STANDARD:
            self.comSet = init[1]
            self.accRight = init[2:4] #on stocke directement en lsb to msb, donc on a RW-S-R-W
            self.size = init[4:7]

    #
    # this method define the communication mode with the file
    #
    def setComset(self, value):
        if value != DesfireFileParameter.COMSET_PLAINTEXT and value != DesfireFileParameter.COMSET_MAC_DES_3DES and value != DesfireFileParameter.COMSET_FULLY_DES_3DES:
            raise ParamException("(DesfireApplicationParameter) setComset, not a valable value")

        self.comSet = value

    #
    # this method define the size of the file
    #    
    def setSize(self, size):
        if size < 0 or size > 0xffffff:
            raise ParamException("(DesfireApplicationParameter) setSize, value must be between 0 and "+str(0xffffff))

        self.size[0] = int(size%256 & 0xff)
        size /= 256
        self.size[1] = int(size%256 & 0xff)
        size /= 256
        self.size[2] = int(size%256 & 0xff)

    #
    # this method set the write key
    #   
    def setWriteKey(self, value):
        if value < 0x00 or value > 0x0f:
            raise ParamException("(DesfireApplicationParameter) setWriteKey, value must be between 0 and 15")

        self.accRight[1] &= 0xf0
        self.accRight[1] |= value

    #
    # this method set the read key
    #    
    def setReadKey(self, value):
        if value < 0x00 or value > 0x0f:
            raise ParamException("(DesfireApplicationParameter) setReadKey, value must be between 0 and 15")

        self.accRight[1] &= 0x0f
        self.accRight[1] |= (value << 4)

    #
    # this method set the read/write key
    #        
    def setReadWriteKey(self, value):
        if value < 0x00 or value > 0x0f:
            raise ParamException("(DesfireApplicationParameter) setReadWriteKey, value must be between 0 and 15") 

        self.accRight[0] &= 0x0f
        self.accRight[0] |= (value << 4)

    #
    # this method set the Setting key
    #    
    def setSettingKey(self, value):
        if value < 0x00 or value > 0x0f:
            raise ParamException("(DesfireApplicationParameter) setSettingKey, value must be between 0 and 15")

        self.accRight[0] &= 0xf0
        self.accRight[0] |= value

    #
    # override of toString method
    #
    def __str__(self):
        if self.fileType == DesfireFileParameter.FILETYPE_STANDARD or self.fileType == DesfireFileParameter.FILETYPE_BACKUP:
            if self.fileType == DesfireFileParameter.FILETYPE_STANDARD:
                ret = "Standard file "
            else:
                ret = "Back-up file "

            #size 
            size = self.size[2]
            size *= 256
            size += self.size[1]
            size *= 256
            size += self.size[0]   
            ret += ", size = "+str(size)

            #com set
            if (self.comSet & 0x01) == DesfireFileParameter.COMSET_PLAINTEXT:
                ret += ", Plain communication"
            elif (self.comSet & 0x03) == DesfireFileParameter.COMSET_FULLY_DES_3DES:
                ret += ", Fully DES/3DES enciphered communication"
            elif (self.comSet & 0x03) == DesfireFileParameter.COMSET_MAC_DES_3DES:
                ret += ", Plain communication secured by DES/3DES MACing"
            else:
                ret += ", Unknwon communication mode"

            #right
            ret += ", read Key = "+str( (self.accRight[1] >> 4) & 0xf )
            ret += ", write Key = "+str( self.accRight[1] & 0xf )
            ret += ", read/write Key = "+str( (self.accRight[0] >> 4) & 0xf )
            ret += ", change Key = "+str( self.accRight[0] & 0xf )

            return ret
        elif self.fileType == DesfireFileParameter.FILETYPE_VALUE:
            return "Value file : not supported"
        elif self.fileType == DesfireFileParameter.FILETYPE_LINEAR:
            return "Linear record : not supported"
        elif self.fileType == DesfireFileParameter.FILETYPE_CYCLIC:
            return "Cyclic record : not supported"
        else:
            return "Unknown file type"


#
# this class extend the Function class to manage a mifare desfire card
# 
#
class DesfireAPDUBuilder():  
    #def __init__(self, connection):
    #    Function.__init__(self, connection)
    #    self.numDir = 0 #we remember in which Application we are
    #    self.sessionkey = None #session key for the cryptographic exchange

    #
    # override of the polling function
    #
    #def polling(self):
    #    self.numDir = 0
    #    self.sessionkey = None
    #    Function.polling(self)
    #    self.selectApplication(0)

    #
    # this method is a generic call to the desfire card, all the action on the desfire will used this method
    # @Exception CommandException, if an error occur in the APDU answer
    #
    #def desCommand(self, cmd, args):
    #    if cmd < 0 or cmd > 0xff:
    #        raise ParamException("(DesfireFunction) desCommand, invalid command, must be between 0 and 255, get : "+str(cmd))

    #    apdu = DirectTransmission(InDataExchange(0x01,Desfire(cmd, 0x00, 0x00, args)))
    #    data, sw1, sw2 = self.connection.transmit( apdu.toHexArray() )
    #    apdu_response = Answer_DirectTransmission(sw1, sw2, data)
    #    checkErrorInCommand(apdu_response)

    #    apdu = GetResponse(apdu_response.getAvailableData())
    #    data, sw1, sw2 = self.connection.transmit( apdu.toHexArray() )
    #    apdu_response = Answer_GetResponse(sw1, sw2, data, "desfire")
    #    checkErrorInCommand(apdu_response)

    #    return apdu_response


###################################################################################################
# APPLICATION MANAGEMENT ##########################################################################
###################################################################################################

    #
    # this method create a new application if doesn't exist
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if dir_id is invalid
    #
    #TODO parameter
    def createApplication(self, dir_id, parameter):  
        #0x0b, parametre d'utilisation de la cle, pour les key settings, createFile, deleteFile
            #pas besoin de cle pour getFileID, getFileSetting, getKeySetting
        if dir_id < 0 or dir_id > 0xffffff:
            raise ParamException("(DesfireFunction) createApplication, invalid directory number")

        return ApduDesfire(0xca,[dir_id & 0xff, int(dir_id/0x100 & 0xff), int(dir_id/0x10000 & 0xff), parameter.keySettings, parameter.keyCount])
    #
    # this method select an application if exists
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if dir_id is invalid
    #    
    def selectApplication(self, dir_id):   
        if dir_id < 0 or dir_id > 0xffffff:
            raise ParamException("(DesfireFunction) selectApplication, invalid directory number")
    
        #self.sessionkey = None
        return ApduDesfire(0x5a,[dir_id & 0xff, int(dir_id/0x100 & 0xff), int(dir_id/0x10000 & 0xff)])
        #self.numDir = dir_id
    
    #
    # this method delete an application if exists
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if dir_id is invalid
    #  
    def deleteApplication(self, dir_id): 
        if dir_id < 0 or dir_id > 0xffffff:
            raise ParamException("(DesfireFunction) deleteApplication, invalid directory number")
        
        return ApduDesfire(0xda,[dir_id & 0xff, int(dir_id/0x100 & 0xff), int(dir_id/0x10000 & 0xff)])

    #
    # this method list all existing application
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ExtractDataException, if no data avaible
    #
    def listApplications(self):
        FunctionException.function = "listApplications"
        try:     
            desresp = getThirdLevel(self.desCommand(0x6A,[]))
        
            ret = [[0x00, 0x00, 0x00]]

            if not desresp.hasData():
                return ret
                #raise ExtractDataException("(listApplications) desfire/mifare answer has no data available")
        
            data = desresp.getData()
            status1, status2 = desresp.getStatus()
        
            if len(data) % 3 != 0:
                raise ExtractDataException("listApplications, invalid data count, must be divisible by 3")
        
            for i in range(0,len(data)/3):
                tmp = data[(i*3):(i*3)+3]
                tmp.reverse()
                ret.append(tmp)
        
            #no possibility to test the following piece of code
            #a classical desfire allow only creation of 28 Application
            #The command 0x6A allow us to retrieve all 28 AID
            #But the documentation indicate we must normaly retrieve only 19 aid
            while status2 == Answer_Desfire.ADDITIONAL_FRAME:
                desresp = getThirdLevel(self.desCommand(0xAF,[]))

                if not desresp.hasData():
                    raise ExtractDataException("(listApplications) desfire/mifare answer has no data available")

                data = desresp.getData()
                status1, status2 = desresp.getStatus()
            
                if len(data) % 3 != 0:
                    raise ExtractDataException("listApplications, invalid data count, must be divisible by 3")

                for i in range(0,len(data)/3):
                    tmp = data[(i*3):(i*3)+3]
                    tmp.reverse()
                    ret.append(tmp)
            
            return ret
        finally:
            FunctionException.function = None
    #
    # this method return the parameter of the current AID, or master AID if no aid selected
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ExtractDataException, if no data avaible
    #
    def getApplicationSetting(self):
        return ApduDesfire(0x45,[])
###################################################################################################
# FILES MANAGEMENT ################################################################################
###################################################################################################

    #
    # this method return the parameter of a file fileID
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if fileID is invalid
    #
    def getFileSetting(self, fileID):
        if fileID < 0 or fileID > 0xff:
            raise ParamException("(DesfireFunction) getFileSetting, invalid file number")
        
        return ApduDesfire(0xF5,[fileID & 0xff])

    #
    # this method create a new file if doesn't exist
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if fileID is invalid
    #
    def createFile(self, fileID, parameter):
        #0x03 : communication fully des/3des
            #0x00 : plain text
            #0x01 : mac access
        #0x00 E0 : free read, key 0 for rest
            #voir page 17 pour d'autre mode
        if fileID < 0 or fileID > 0xff:
            raise ParamException("(DesfireFunction) createFile, invalid file number")
        
        return ApduDesfire(0xcd,[fileID & 0xff, parameter.comSet, parameter.accRight[0], parameter.accRight[1], parameter.size[0], parameter.size[1], parameter.size[2]])

    #
    # this method create a new file if doesn't exist
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ExtractDataException, if no data avaible
    #  
    def listFiles(self): 
        return ApduDesfire(0x6F,[])
    
    #
    # this method read a cyphered file
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ExtractDataException, if no data avaible
    # @Exception ParamException, if invalid fileID or invalid sizeToRead or invalid offset
    # @Exception CypherException, if an error occur in cryptography
    #
    def sreadFile(self, fileID, sizeToRead = 0, offset = 0):
        if self.sessionkey == None:
            raise CypherException("(DesfireFunction) sreadFile, session key not defined, must authenticate before")
        
        #read and decypher
        ret = sslDesDecFromReader(self.readFile(fileID, sizeToRead, offset), self.sessionkey)
        
        if sizeToRead == 0:
            indice = len(ret) -1
            
            while (ret[indice] != 0x80 or indice < 0):
                indice -= 1
            
            if indice < 2:
                raise CypherException("(DesfireFunction) sreadFile, invalid padding") 
            
            crc1, crc2 = computeCRC(ret[:indice-2])
            if ret[indice-2] != crc1 or ret[indice-1] != crc2:
                raise CypherException("(DesfireFunction) sreadFile, invalid crc")
                
            return ret[:indice-2]
        else:
            if len(ret) < sizeToRead+2:
                raise CypherException("(DesfireFunction) sreadFile, invalid readed data") 
            
            crc1, crc2 = computeCRC(ret[:sizeToRead])
            if ret[sizeToRead] != crc1 or ret[sizeToRead+1] != crc2:
                raise CypherException("(DesfireFunction) sreadFile, invalid crc") 
            
            return ret[:sizeToRead]

    #
    # this method read a standard file
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ExtractDataException, if no data avaible
    # @Exception ParamException, if invalid fileID or invalid sizeToRead or invalid offset
    #
    def readFile(self, fileID, sizeToRead = 0, offset = 0):  
        FunctionException.function = "readFile fid="+str(fileID)+", offset="+str(offset)
        try:      
            if fileID < 0 or fileID > 0xff:
                raise ParamException("(DesfireFunction) readFile, invalid file number")
            
            if sizeToRead < 0 or sizeToRead > 0xffffff:
                raise ParamException("(DesfireFunction) readFile, invalid size to read")
        
            if offset < 0 or offset > 0xffffff:
                raise ParamException("(DesfireFunction) readFile, invalid offset")
                
            resp = self.desCommand(0xBD,[fileID & 0xFF, offset & 0xff, int(offset/0x100 & 0xff), int(offset/0x10000 & 0xff), sizeToRead & 0xff, int(sizeToRead/0x100 & 0xff), int(sizeToRead/0x10000 & 0xff)])
        
            desresp = getThirdLevel(resp)
        
            if not desresp.hasData():
                raise ExtractDataException("desfire/mifare answer has no data available")

            data = desresp.getData()
            status1, status2 = desresp.getStatus()
            while status2 == Answer_Desfire.ADDITIONAL_FRAME:
                resp = self.desCommand(0xAF,[])
                desresp = getThirdLevel(resp)
            
                if not desresp.hasData():
                    raise ExtractDataException("desfire/mifare answer has no data available")
            
                data.extend(desresp.getData())
                status1, status2 = desresp.getStatus()
            
            return data
        finally:
            FunctionException.function = None
    
    #
    # this method write a cyphered file
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception CypherException, if an error occur in cryptography
    # @Exception ParamException, if invalid offset
    #
    def swriteFile(self, fileID, data, offset = 0):
        #construction des donness a chiffrer
        toCypher = []
        toCypher.extend(data)
        crc1, crc2 = computeCRC(data)
        toCypher.append(crc1)
        toCypher.append(crc2)
        
        if len(toCypher) % 8 != 0:
            padd = 8 - (len(toCypher) % 8)
            while (padd > 0):
                toCypher.append(0x00)
                padd -= 1

        #chiffrage + ecriture
        self.writeFile(fileID, sslDesDecToReader(toCypher, self.sessionkey), offset, len(data))

    #
    # this method write a standard file
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if invalid offset
    #  
    def writeFile(self, fileID, data, offset = 0, dataSize=None): 
        FunctionException.function = "writeFile fid="+str(fileID)+", offset="+str(offset)
        try:       
            if offset < 0 or offset > 0xffffff:
                raise ParamException("(DesfireFunction) writeFile, invalid offset")
        
            length = len(data)
            if dataSize == None:
                dataSize = length
            count = 52
            param = [fileID & 0xFF, offset & 0xff, int(offset/0x100 & 0xff), int(offset/0x10000 & 0xff), dataSize & 0xff, int(dataSize/0x100 & 0xff), int(dataSize/0x10000 & 0xff)]
        
            if length <= count:
                param.extend(data)
            else:
                param.extend(data[:count])
                
            self.desCommand(0x3D,param)
        
            while (count < length):
                if length > count + 59:
                    toSend = data[count:count+59]
                else:
                    toSend = data[count:]
                
                self.desCommand(0xAF,toSend)
                count +=59
        finally:
            FunctionException.function = None
    #
    # this method delete a file if exists
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception ParamException, if fileID is invalid
    #
    def deleteFile(self, fileID):
        if fileID < 0 or fileID > 0xff:
            raise ParamException("(DesfireFunction) deleteFile, invalid file number")    
            
        return ApduDesfire(0xdf,[fileID & 0xff])

###################################################################################################
# CRYPTOGRAPHIC MANAGEMENT ########################################################################
###################################################################################################
    
    #
    # this method allow to change the value of the "Change key"
    #
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception CypherException, if an error occur in cryptography
    #
    def changeKey1(self, keyNo, newKeyName):
        FunctionException.function = "changeKey1 keyNo="+str(keyNo)
        try:
            #verification des arguments              
            if keyNo < 0 or keyNo > 0xD:
                raise ParamException("(DesfireFunction) changeKey1, invalid key number, must be between 0 and 13")
    
            if newKeyName not in keys:
                raise ParamException("(DesfireFunction) changeKey1, unknown new key name : "+str(newKeyName))
        
            if self.sessionkey == None:
                raise CypherException("(DesfireFunction) changeKey1, session key not defined, must authenticate before")
        
            logging.info("methode changeKey1: KEYno = "+str(keyNo)+", new key = "+printHexaTable(keys[newKeyName]))
        
            #get new key
            newKey = []
            newKey.extend(keys[newKeyName])
            if len(newKey) != 16 and len(newKey) != 8:
                raise ParamException("(DesfireFunction) changeKey1, invalid new key, must have 16 or 8 bytes, received : "+str(len(newKey)))
        
            if len(newKey) == 8:
                newKey.extend(keys[newKeyName])
            
            #on genere les parametres + chiffrement
            param = [keyNo & 0xff]
            crcNewKey1, crcNewKey2 = computeCRC(newKey)#crc on new key
            newKey.extend([crcNewKey1, crcNewKey2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                
            param.extend(sslDesDecToReader(newKey, self.sessionkey))
        
            #on envoi la requete de changement de key
            self.desCommand(0xc4, param)
        finally:
            FunctionException.function = None
    #
    # this method allow to change the value of any key different of the "Change key"
    #
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception CypherException, if an error occur in cryptography
    #  
    def changeKey(self, keyNo, oldKeyName, newKeyName): 
        FunctionException.function = "changeKey keyNo="+str(keyNo)
        try:       
            if keyNo < 0 or keyNo > 0xD:
                raise ParamException("(DesfireFunction) changeKey, invalid key number, must be between 0 and 13")
        
            if oldKeyName not in keys:
                raise ParamException("(DesfireFunction) changeKey, unknown old key name : "+str(oldKeyName))
            
            if newKeyName not in keys:
                raise ParamException("(DesfireFunction) changeKey, unknown new key name : "+str(newKeyName))
         
            if self.sessionkey == None:
                raise CypherException("(DesfireFunction) changeKey, session key not defined, must authenticate before")
        
            logging.info("methode changeKey: KEYno = "+str(keyNo)+", old key = "+printHexaTable(keys[oldKeyName])+", new key = "+printHexaTable(keys[newKeyName]))
            
            #get old key
            oldKey = []
            oldKey.extend(keys[oldKeyName])
            if len(oldKey) != 16 and len(oldKey) != 8:
                raise ParamException("(DesfireFunction) changeKey, invalid old key, must have 16 bytes, received : "+str(len(oldKey)))
        
            if len(oldKey) == 8:
                oldKey.extend(keys[oldKeyName])
        
            #get new key
            newKey = []
            newKey.extend(keys[newKeyName])
            if len(newKey) != 16 and len(newKey) != 8:
                raise ParamException("(DesfireFunction) changeKey, invalid new key, must have 16 bytes, received : "+str(len(newKey)))
        
            if len(newKey) == 8:
                newKey.extend(keys[newKeyName])
        
            #prepare param and decypher with session key
            xorKey = xorList(oldKey, newKey)           #xor two key
            crcXor1, crcXor2 = computeCRC(xorKey)      #crc on xor
            crcNewKey1, crcNewKey2 = computeCRC(newKey)#crc on new key
            xorKey.extend([crcXor1, crcXor2, crcNewKey1, crcNewKey2, 0x00, 0x00, 0x00, 0x00 ])#add 4 bytes crc and padding 4 bytes 0x00
        
            param = [keyNo & 0xff]      
            param.extend(sslDesDecToReader(xorKey, self.sessionkey))
    
            #send request to desfire
            self.desCommand(0xc4, param)
        finally:
            FunctionException.function = None
    #
    # this method allow to authenticate with a key
    #
    # @Exception CommandException, if an error occur in the APDU answer
    # @Exception CypherException, if an error occur in cryptography
    #
    def authentication(self, keyNo = 0, keyName = "zero"):
        FunctionException.function = "authentication keyNo="+str(keyNo)
        try:      
            if keyNo < 0 or keyNo > 0xD:
                raise ParamException("(DesfireFunction) authentication, invalid key number, must be between 0 and 13")
        
            if keyName not in keys:
                raise ParamException("(DesfireFunction) authentication, unknown key name : "+str(keyName))
        
            key = keys[keyName]
            if len(key) != 16 and len(key) != 8:
                raise ParamException("(DesfireFunction) authentication, invalid key, must have 16 or 8 bytes, received : "+str(len(key)))
        
            self.sessionkey = None #on invalide la cle de session precedante
        
            #AUTHENTICATION STEP 1
            challenge1 = getThirdLevelData(self.desCommand(0x0a, [keyNo & 0xFF]))
            if len(challenge1) != 8:
                raise ExtractDataException("(functionclass) authentication, challenge (1) must have 8 bytes, received : "+str(len(challenge1)))
                
            #CALCUL ANSWER
            nounce = getNounce()
            NT = sslDesDecToReader(challenge1,key)
            rep = generateD1D2(NT, nounce, key)

            #AUTHENTICATION STEP 2 + VERIFICATION
            challenge = getThirdLevelData(self.desCommand(0xaf,rep))#si la cle est incorrecte, une exception est levee au checkErrorInCommand
            if len(challenge) != 8:
                raise ExtractDataException("(functionclass) authentication, challenge (2) must have 8 bytes, received : "+str(len(challenge)))
        
            nouncePrime = sslDesDecToReader(challenge,key)

            #verification de la concordance entre nounce et nouncePrime
            for i in range(0,8):
                if nounce[(i+1) % 8] != nouncePrime[i]:
                    return False
                
            #calcul de la cle de session avec challenge1(nt) et nounce(nr)
            if len(key) > 8:
                specialCase = True
                for i in range(0,8):
                    if key[i] != key[i+8]:
                        specialCase = False
                        break
            else:
                specialCase = True

            self.sessionkey = []
            if specialCase:#des, cle sur 8 bytes
                self.sessionkey.extend(nounce[:4])
                self.sessionkey.extend(NT[:4])
            else: #3des, cle sur 16 bytes
                self.sessionkey.extend(nounce[:4])
                self.sessionkey.extend(NT[:4])
                self.sessionkey.extend(nounce[4:])
                self.sessionkey.extend(NT[4:])
            
            return True 
        finally:
            FunctionException.function = None
###################################################################################################
# OTHER MANAGEMENT ########################################################################
###################################################################################################
    
    #
    # this method allow to format the card
    #
    # @Exception CommandException, if an error occur in the APDU answer
    #
    def resetCard(self):
        return ApduDesfire(0xFC)
            
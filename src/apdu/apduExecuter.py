#!/usr/bin/python2.6

from arg.args import Executer
from smartcard.sw.SWExceptions import CheckingErrorException,SWException
from smartcard.util import toHexString

def stringListResultHandler(result):
    if result == None or len(result) == 0:
        Executer.printOnShell("no item available")
        return
        
    for i in result:
        Executer.printOnShell(i)

def resultHandlerAPDU(apdu):
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        Executer.printOnShell("no connection available")
        return
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
    except SWException as ex:
        Executer.printOnShell("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
    except Exception as e:
        Executer.printOnShell(str(e))
    
def resultHandlerAPDUAndConvertDataToString(apdu):
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        Executer.printOnShell("no connection available")
        return
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
        s = ""
        for c in data:
            s += chr(c)
        Executer.printOnShell("data = "+s)
    except SWException as ex:
        Executer.printOnShell("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
    except Exception as e:
        Executer.printOnShell(str(e))
    
def resultHandlerAPDUAndPrintData(apdu):
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        Executer.printOnShell("no connection available")
        return
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
        Executer.printOnShell(toHexString(data))
    except SWException as ex:
        Executer.printOnShell( "%x %x : " % (ex.sw1, ex.sw2)+ex.message)
    except Exception as e:
        Executer.printOnShell(str(e))
        
def resultHandlerAPDUAndPrintDataAndSW(apdu):
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        Executer.printOnShell("no connection available")
        return
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
        Executer.printOnShell("%x %x : " % (sw1, sw2)+toHexString(data))
    except SWException as ex:
        Executer.printOnShell( "%x %x : " % (ex.sw1, ex.sw2)+ex.message)
    except Exception as e:
        Executer.printOnShell(str(e))

#def executeAPDU(con,apdu):
    #TODO

        
#def executeAPDUAndConvertDataToString(con,apdu):
    #TODO

#def executeAPDUAndPrintData(con,apdu):
    #TODO

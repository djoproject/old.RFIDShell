#!/usr/bin/python2.6

from smartcard.sw.SWExceptions import CheckingErrorException,SWException
#from smartcard.util import toHexString
from apdu import toHexString
from apduAnswer import ApduAnswer
from arg.exception import argExecutionException


"""def resultHandlerAPDU(apdu):
    "execute an apdu"
    
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        raise argExecutionException("no connection available")
        
    try:
        Executer.envi["connection"].transmit(apdu.toHexArray())
    except SWException as ex:
        raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)"""
    
def resultHandlerAPDUAndConvertDataToString(printer,apduAnswer):
    "convert an apdu hexa result into a human readable string"
    
    if apduAnswer == None:
        return
    
    #if "connection" not in Executer.envi or Executer.envi["connection"] == None:
    #    raise argExecutionException("no connection available")
        
    #try:
        #data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
    s = ""
    for c in apduAnswer:
        s += chr(c)
    printer.printOnShell("data = "+s)
        
    #except SWException as ex:
    #    raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)

def resultHandlerAPDUAndConvertDataAndSWToString(printer,apduAnswer):
    "convert an apdu hexa result into a human readable string"

    if apduAnswer == None:
        return

    s = ""
    for c in apduAnswer:
        s += chr(c)
        
    s += chr(apduAnswer.sw1)
    s += chr(apduAnswer.sw2)
    
    printer.printOnShell("data = "+s)
    
def resultHandlerAPDUAndPrintData(printer,apduAnswer):
    "print an apdu result"
    
    if apduAnswer == None:
        return
    
    #if "connection" not in Executer.envi or Executer.envi["connection"] == None:
    #    raise argExecutionException("no connection available")
        
    #try:
    #    data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
    printer.printOnShell(toHexString(apduAnswer))
    #except SWException as ex:
    #    raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
        
def resultHandlerAPDUAndPrintDataAndSW(printer,apduAnswer):
    "print the apdu result and the status word"
    
    if apduAnswer == None:
        return
    
    #if "connection" not in Executer.envi or Executer.envi["connection"] == None:
    #    raise argExecutionException("no connection available")
        
    #try:
    #    data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
    printer.printOnShell("0x%x 0x%x : " % (apduAnswer.sw1, apduAnswer.sw2)+toHexString(apduAnswer))
    #except SWException as ex:
    #    raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
        
def executeAPDU(envi,apdu):
    "execute an apdu and return an apduAnswer"

    if "connection" not in envi or envi["connection"] == None:
        raise argExecutionException("no connection available")

    try:
        data, sw1, sw2 =  envi["connection"].transmit(apdu.toHexArray())
        return ApduAnswer(sw1,sw2,data)
    except SWException as ex:
        raise argExecutionException("0x%x 0x%x : " % (ex.sw1, ex.sw2)+ex.message)
        
def printByteList(printer,result):
    if result == None or len(result) == 0:
        printer.printOnShell("no item available")
        return

    hexa = ""
    ascii = ""
    intString = ""
    binString = ""
    
    for h in result:
        
        tmp = "%x"%h
        while len(tmp) < 2:
            tmp = "0"+tmp
        
        hexa += tmp+" "
        
        if h < 33 or h > 126:
            ascii += "."
        else:
            ascii += chr(h)
        
        tmp = str(h)
        while len(tmp) < 3:
            tmp = "0"+tmp
        
        intString += tmp+" "
        
        tmp = bin(h)[2:]
        while len(tmp) < 8:
            tmp = "0"+tmp
        binString += tmp+" "
        
    printer.printOnShell(hexa+" | "+ascii+" | "+intString+" | "+binString)

def printByteListList(printer,result):
    if result == None or len(result) == 0:
        printer.printOnShell("no item available")
        return
    
    printer.printOnShell("hex          | ascii| dec              | bin")
    for l in result:
        printByteList(printer,l)
    
    
    
    
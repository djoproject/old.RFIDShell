#!/usr/bin/python2.6

from arg.args import Executer
from smartcard.sw.SWExceptions import CheckingErrorException,SWException
from smartcard.util import toHexString
from apduAnswer import ApduAnswer
from arg.exception import argExecutionException


def resultHandlerAPDU(apdu):
    "execute an apdu"
    
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        raise argExecutionException("no connection available")
        
    try:
        Executer.envi["connection"].transmit(apdu.toHexArray())
    except SWException as ex:
        raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
    
def resultHandlerAPDUAndConvertDataToString(apdu):
    "execute an apdu and convert the hexa result into a human readable string"
    
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        raise argExecutionException("no connection available")
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
        s = ""
        for c in data:
            s += chr(c)
        Executer.printOnShell("data = "+s)
        
    except SWException as ex:
        raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
    
def resultHandlerAPDUAndPrintData(apdu):
    "execute an apdu and print the result"
    
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        raise argExecutionException("no connection available")
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
        Executer.printOnShell(toHexString(data))
    except SWException as ex:
        raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
        
def resultHandlerAPDUAndPrintDataAndSW(apdu):
    "execute an apdu and print the result and the status word"
    
    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        raise argExecutionException("no connection available")
        
    try:
        data, sw1, sw2 = Executer.envi["connection"].transmit(apdu.toHexArray())
        Executer.printOnShell("%x %x : " % (sw1, sw2)+toHexString(data))
    except SWException as ex:
        raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)
        
def resultHandlerAPDUreturnDATAandSW(apdu):
    "execute an apdu and print the result and the status word"

    if "connection" not in Executer.envi or Executer.envi["connection"] == None:
        raise argExecutionException("no connection available")

    try:
        data, sw1, sw2 =  Executer.envi["connection"].transmit(apdu.toHexArray())
        return ApduAnswer(sw1,sw2,data)
    except SWException as ex:
        raise argExecutionException("%x %x : " % (ex.sw1, ex.sw2)+ex.message)

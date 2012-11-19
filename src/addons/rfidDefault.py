#!/usr/bin/python2.6
from arg.args import *
from arg.argchecker import *
from arg.resultHandler import *

from apdu.apduExecuter import *


try:
    print "Key Store loading..."
    from keyList import keys
except ImportError:
    import os
    if not os.path.exists("keyList.py"):
        print "Key Store Creation..."
        try:
            f = open("keyList.py", 'w')
            f.write("#"+os.linesep)
            f.write("#"+os.linesep)
            f.write("# OFFLINE key set"+os.linesep)
            f.write("#"+os.linesep)
            f.write("keys = {}"+os.linesep)
            f.write(os.linesep)
            f.close()
            
        except IOError as ioe:
            print "failed to create the key store : "+str(ioe)
            exit()
        
        keys = {}

import platform

#test smartcard
try:
    from smartcard.System import readers
    from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
    from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
    from smartcard.CardMonitoring import CardMonitor, CardObserver
    from smartcard.CardConnection import CardConnection
    from smartcard.ATR import ATR
    from smartcard.pcsc.PCSCContext import PCSCContext
    from smartcard.pcsc.PCSCExceptions import EstablishContextException

    from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
    from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
    from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
    from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker
except ImportError as ie:
    print "failed to load smartcard : "+str(ie)
    print "maybe the library is not installed"
    print "http://pyscard.sourceforge.net"
    
    import sys
    if(sys.platform == 'darwin'):
        print "HINT : on macos system, try to execute this script with python2.6"
    
from apdu.apdu import toHexString
from apdu.apdu import ApduRaw

#TODO
    #-faire une section critique entre les observeurs et les methods pour proteger : l'envi et la liste de card
    #-lorsqu'on quitte, se deconnecter? ou ca le fait deja tout seul?

########### TEST CONTEXT ###############
try:
    print "context loading... please wait"
    PCSCContext()
    print "context loaded"
except EstablishContextException as e:
    print "   "+str(e)
    
    pf = platform.system()
    if pf == 'Darwin':
        print "   HINT : connect a reader and use a tag/card with it, then retry the command"
    elif pf == 'Linux':
        print "   HINT : check the 'pcscd' daemon, maybe it has not yet started or it crashed"
    elif pf == 'Windows':
        print "   HINT : check the 'scardsvr' service, maybe it has not yet started or it crashed"
    else:
        print "   HINT : check the os process that manage card reader"
    exit()


###############################################################################################
##### Monitor reader ##########################################################################
###############################################################################################
class ReaderManager( ReaderObserver ):
    """A simple reader observer that is notified
    when readers are added/removed from the system and
    prints the list of readers
    """
    
    def __init__(self):
        self.readermonitor = ReaderMonitor()
        self.enable = False
        self.readermonitor.addObserver( self )
        
    def update( self, observable, (addedreaders, removedreaders) ):
        r = ""
        if addedreaders != None and len(addedreaders) > 0:
            r += "Added readers" + str(addedreaders) 
        
        if removedreaders != None and len(removedreaders) > 0:
            
            if len(r) > 0:
                r += "\n"
            
            r += "Removed readers" + str(removedreaders)
            
            if "connectedReader" in Executer.envi:
                for reader in removedreaders:
                    if reader == Executer.envi["connectedReader"]:
                        disconnectReaderFromCardFun(Executer.envi)
                        Executer.printAsynchronousOnShell("WARNING : the reader has been removed, the connection is broken")

        if self.enable and len(r) > 0:
            Executer.printAsynchronousOnShell(r)
        
    def activate(self):
        #if not self.enable:
        #    self.readermonitor.addObserver( self )
        
        self.enable = True
        
    def desactivate(self):
        #if self.enable:
        #    self.readermonitor.deleteObserver(self)
        
        self.enable = False

readerobserver = ReaderManager()
#readerobserver.activate()

###############################################################################################
##### Monitor card ############################################################################
###############################################################################################

class CardManager( CardObserver ):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    
    def __init__(self):
        self.cardmonitor = CardMonitor()
        self.enable = False
        self.cardList = []
        self.cardmonitor.addObserver( self )
        self.autocon = False
    
    def update( self, observable, (addedcards, removedcards) ):
        r = ""
        ac = ""
        if addedcards != None and len(addedcards) > 0:
            r += "Added cards" + str(addedcards) 
            for c in addedcards:
                self.cardList.append(c)
            
            ac = self.autoConnect()
        
        if removedcards != None and len(removedcards) > 0:
            
            if len(r) > 0:
                r += "\n"
            
            r += "Removed cards" + str(removedcards)
            
            for c in removedcards:
                self.cardList.remove(c)

                if hasattr(c,'connection'):
                    disconnectReaderFromCardFun(Executer.envi)
                    Executer.printAsynchronousOnShell("WARNING : the card has been removed, the connection is broken")
            
        if self.enable and len(r) > 0:
            if len(ac) > 0:
                r += ac + "\n"
            
            Executer.printAsynchronousOnShell(r)
        else:
            if len(ac) > 0:
                Executer.printAsynchronousOnShell(ac)
        
    def activate(self):
        #if not self.enable:
        #    self.cardmonitor.addObserver( self )
        
        self.enable = True
        
    def desactivate(self):
        #if self.enable:
        #    self.cardmonitor.deleteObserver(self)
        
        self.enable = False
        
    def enableAutoCon(self):
        self.autocon = True
        Executer.printOnShell(self.autoConnect())
        
    def disableAutoCon(self):
        self.autocon = False
        
    def autoConnect(self):
        if "connection" not in Executer.envi and self.autocon:
            if len(self.cardList) == 1:
                if connectReaderFromCardFun(Executer.envi):
                    return "connected to a card"
            elif len(self.cardList) > 1:
                return "WARNING : autoconnect is enable but there is more than one card available, no connection established"
        
        return None
cardobserver = CardManager()

###############################################################################################
##### Monitor datas ###########################################################################
###############################################################################################

class DataManager():
    def __init__(self):
        self.enable = False
        
    def activate(self):
        
        if "connection" not in Executer.envi:
            Executer.printOnShell("cardservice context is not yet defined")
            return
        
        if not self.enable:
            Executer.envi["connection"].addObserver(self)

        self.enable = True

    def desactivate(self):
        if "connection" not in Executer.envi:
            Executer.printOnShell("cardservice context is not yet defined")
            return
        
        if self.enable:
            Executer.envi["connection"].deleteObserver(self)

        self.enable = False
        
    def available(self):
        return "connection" in Executer.envi
        
    def update( self, cardconnection, ccevent ):
        #TODO parfois l'affichage colle les bytes :/
        
        if "connect" == ccevent.type:
            Executer.printOnShell("connecting to " +str(cardconnection.getReader()))

        elif "disconnect" == ccevent.type:
            Executer.printOnShell("disconnecting from " +str(cardconnection.getReader()))

        elif "command" == ccevent.type:
            Executer.printOnShell("> "+ toHexString( ccevent.args[0] ))

        elif "response" == ccevent.type:
            if []==ccevent.args[0]:
                Executer.printOnShell("< [] " + "%-2X %-2X" % tuple(ccevent.args[-2:]))
            else:
                Executer.printOnShell("< " + toHexString(ccevent.args[0]) + "%-2X %-2X" % tuple(ccevent.args[-2:]))
        
dataobserver = DataManager()

###############################################################################################
##### function declaration ####################################################################
###############################################################################################

def listKeyFun():
    "list the available key name"
    return keys.keys()
    #count = 0
    #for k in keys:
    #    print k
    #    count += 1

    #if count == 0:
    #    Executer.printOnShell("no key available")

def addKeyFun(name,key):
    "set a 6, 8 or 16 bytes key"
    #key = []    
    #for i in args:
    #    key.append(args[i])

    #print key

    keys[name] = key

def listReaderFun():
    "list all the reader available on the system"
    
    #indice = 0
    try:
        r = readers()
    #    for r in readers():
    #        print "\t"+str(indice)+" : "+str(r)
    #        indice += 1
    
    #TODO manage ListReadersException
    
    except Exception as e:
        Executer.printOnShell(str(e))
        return

    if r == None or len(r) == 0:
        #Executer.printOnShell("no reader available on this system")
        Executer.printOnShell("HINT : some reader need to connect a card before to be detected in the system")
        
    return r

def monitorCardFun():
    "enable the card monitoring"
    
    if cardobserver.enable:
        Executer.printOnShell("The cards are already monitored")
    else:
        cardobserver.activate()
        Executer.printOnShell("Monitor cards : enable")

def monitorReaderFun():
    "enable the reader monitoring"
    
    if readerobserver.enable:
        Executer.printOnShell("The readers are already monitored")
    else:
        readerobserver.activate()
        Executer.printOnShell("Monitor readers : enable")

def monitorDataFun():
    "enable the data monitoring"
    
    if not dataobserver.available():
        Executer.printOnShell("the data monitoring is not yet available, connect a reader or insert a card")
        dataobserver.desactivate()
        return

    if dataobserver.enable:
        Executer.printOnShell("The data are already monitored")
    else:
        dataobserver.activate()
        if dataobserver.enable:
            Executer.printOnShell("Monitor data : enable")

def monitorCardAll():
    "enable the global monitoring"
    
    monitorCardFun()
    monitorReaderFun()
    monitorDataFun()
    
def disableMonitorCardFun():
    "disable the card monitoring"
    
    if cardobserver.enable:
        cardobserver.desactivate()
        Executer.printOnShell("Monitor cards : disable")
    else:
        Executer.printOnShell("The cards are not monitored")

def disableMonitorReaderFun():
    "disable the reader monitoring"
    
    if readerobserver.enable:
        readerobserver.desactivate()
        Executer.printOnShell("Monitor readers : disable")
    else:
        Executer.printOnShell("The readers are not monitored")

def disableMonitorDataFun():
    "disable the data monitoring"
    
    if not dataobserver.available():
        Executer.printOnShell("the data monitoring is not yet available, connect a reader or insert a card")
        dataobserver.desactivate()
        return
    
    if dataobserver.enable:
        dataobserver.desactivate()
        Executer.printOnShell("Monitor data : disable")
    else:
        Executer.printOnShell("The data are not monitored")

def disableMonitorCardAll():
    "disable the global monitoring"
    
    disableMonitorCardFun()
    disableMonitorReaderFun()
    disableMonitorDataFun()

def listCardFun():
    "list all the card available on the system"
    
    return cardobserver.cardList
    #i = 1
    #for c in cardobserver.cardList:
    #    Executer.printOnShell("card "+str(i)+" : "+toHexString(c.atr) + " connected on reader <" + str(c.reader)+">")
    #    i += 1
    
    #if i == 1:
    #    Executer.printOnShell("no card available")

def cardListResultHandler(result):
    if result == None or len(result) == 0:
        Executer.printOnShell("no item available")
        return
    
    i = 1
    for c in result:
        Executer.printOnShell("card "+str(i)+" : "+toHexString(c.atr) + " connected on reader <" + str(c.reader)+">")

def cardInfoFun(cardIndex=None):
    "print all the info of the card ATR"
    
    if cardIndex == None:
        indice = 0
        if len(cardobserver.cardList) > 1:
            Executer.printOnShell("Warning : the information comes from the first card available in the list, there are others cards")
            i += 1
    else:
        indice = cardIndex
        
    if len(cardobserver.cardList) == 0:
        Executer.printOnShell("there is no card available")
        return
    
    try:
        card = cardobserver.cardList[indice]
    except IndexError:
        Executer.printOnShell("invalid indice")
        return
    
    return card.atr
    
def printATR(bytes):
    if bytes == None or not isinstance(bytes,list) or len(bytes) < 1:
        Executer.printOnShell("The value is not a valid ATR")
        return
    
    atr = ATR(bytes)
    
    print atr
    print
    atr.dump()
    print 'T15 supported: ', atr.isT15Supported()
    
def connectReaderFromCardFun(envi,cardIndex=None):
    "establish a link between the shell and a card"
    
    if "connection" in envi and envi["connection"] != None:
        print "there is already a connection to reader "+envi["connectedReader"]
        return
    
    if cardIndex == None:
        indice = 0
        if len(cardobserver.cardList) > 1:
            Executer.printOnShell("Warning : the information comes from the first card available in the list, there are others cards")
    else:
        indice = cardIndex
        
    if len(cardobserver.cardList) == 0:
        Executer.printOnShell("there is no card available")
        return
    
    try:
        card = cardobserver.cardList[indice]
    except IndexError:
        Executer.printOnShell("invalid indice")
        return False
    
    try:
        envi["connection"] = card.createConnection() #create a connection on the reader
    except Exception as e:
        Executer.printOnShell(str(e))
        return False
        
    try:
        envi["connection"].connect()#create a connection on the card
    except Exception as e:
        del envi["connection"]
        Executer.printOnShell(str(e))
        return False
    
    card.connection = envi["connection"]
    card.connection.card = card
    envi["connectedReader"] = card.connection.getReader()

    errorchain=[]
    errorchain=[ ErrorCheckingChain( errorchain, ISO7816_8ErrorChecker() ),
                 ErrorCheckingChain( errorchain, ISO7816_9ErrorChecker() ),
                 ErrorCheckingChain( errorchain, ISO7816_4ErrorChecker() ) ]
    envi["connection"].setErrorCheckingChain(errorchain)
    
    return True
    
def disconnectReaderFromCardFun(envi):
    "destroy the link between the current card/reader and the shell"
    
    if dataobserver.enable:
        dataobserver.desactivate()
    
    if "connection" not in envi or envi["connection"] == None:
        print "there is no opened connexion"
        
        if "connection" in envi:
            del envi["connection"]
        
        return
    
    try:
        envi["connection"].disconnect()
    except Exception as e:
        Executer.printOnShell(str(e))
    
    if hasattr(envi["connection"],'card'):
        del envi["connection"].card.connection
        del envi["connection"].card
    
    if "connectedReader" in envi:
        del envi["connectedReader"]
        
    del envi["connection"]
    
def connectReaderFun(envi,readerIndex = None):
    "establish a link between the shell and a card"
    
    if "connection" in envi and envi["connection"] != None:
        print "there is already a connection to reader"
        return False
    
    r = readers()
    if readerIndex == None:
        indice = 0
        if len(r) > 1:
            Executer.printOnShell("Warning : the connection will open on the first available reader but there are others")
    else:
        indice = readerIndex
    
    if len(r) == 0:
        Executer.printOnShell("there is no reader available")
        return False
     
    try:
        reader = r[indice]
    except IndexError:
        Executer.printOnShell("invalid indice")
        return False
        
    try:
        envi["connection"] = reader.createConnection() #create a connection on the reader
    except Exception as e:
        Executer.printOnShell(str(e))
        return False
        
    try:
        envi["connection"].connect()#create a connection on the card
    except Exception as e:
        del envi["connection"]
        Executer.printOnShell(str(e))
        return False
    
    card = None
    for c in cardobserver.cardList:
        if c.atr == envi["connection"].getATR() and c.reader == reader:
            card = c
            card.connection = envi["connection"]
            card.connection.card = card

    if card == None:
        Executer.printOnShell("WARNING : the connected card is not in the card list")
    
    envi["connectedReader"] = reader
    
    return True

def sendAPDU(envi,args):
    "send an apdu to the reader"
    return executeAPDU(envi,ApduRaw(args))

def forge(args):
    "forge an apdu without send it to the reader"
    return ApduRaw(args)
    
def enableAutoCon():
    cardobserver.enableAutoCon()
    
def disableAutoCon():
    cardobserver.disableAutoCon()
    
def setProtocol(envi,protocols):
    if "connection" not in envi or envi["connection"] == None:
        raise argExecutionException("no connection available")
    
    protocol = 0
    
    for p in protocols:
        protocol |= p
    
    envi["connection"].setProtocol(protocol)
    
def getProtocol(envi,printer):
    if "connection" not in envi or envi["connection"] == None:
        raise argExecutionException("no connection available")
        
    p = envi["connection"].getProtocol()
    
    if (p&CardConnection.T0_protocol):
        printer.printOnShell("T0 enable")
        
    if (p&CardConnection.T1_protocol):
        printer.printOnShell("T1 enable")

    if (p&CardConnection.T15_protocol):
        printer.printOnShell("T15 enable")
        
    if (p&CardConnection.RAW_protocol):
        printer.printOnShell("RAW enable")

###############################################################################################
##### add command to shell ####################################################################
###############################################################################################
#(CommandStrings,preProcess=None,process=None,argChecker=None,postProcess=None,showInHelp=True):

#key management        
Executer.addCommand(CommandStrings=["lskey"],                     preProcess=listKeyFun,postProcess=stringListResultHandler)
s = stringArgChecker()
i = IntegerArgChecker()

Executer.addCommand(CommandStrings=["set","key"],                    process=addKeyFun,argChecker=InfiniteArgsChecker("key",hexaArgChecker(),[("name",s)],multiLimitChecker(6,8,16)) )

#reader management
Executer.addCommand(CommandStrings=["list","reader"],             preProcess=listReaderFun,postProcess=stringListResultHandler)
Executer.addCommand(CommandStrings=["connect","reader"],          process=connectReaderFun,argChecker=DefaultArgsChecker([("readerIndex",i)],0))
Executer.addCommand(CommandStrings=["disconnect"],                process=disconnectReaderFromCardFun)

#monitoring management
Executer.addCommand(CommandStrings=["monitor","all"],             process=monitorCardAll)
Executer.addCommand(CommandStrings=["monitor","reader"],          process=monitorReaderFun)
Executer.addCommand(CommandStrings=["monitor","card"],            process=monitorCardFun)
Executer.addCommand(CommandStrings=["monitor","data"],            process=monitorDataFun)

Executer.addCommand(CommandStrings=["disable","monitor","all"],   process=disableMonitorCardAll)
Executer.addCommand(CommandStrings=["disable","monitor","reader"],process=disableMonitorReaderFun)
Executer.addCommand(CommandStrings=["disable","monitor","card"],  process=disableMonitorCardFun)
Executer.addCommand(CommandStrings=["disable","monitor","data"],  process=disableMonitorDataFun)

#card management
Executer.addCommand(CommandStrings=["list","card"],               preProcess=listCardFun,postProcess=cardListResultHandler)

Executer.addCommand(CommandStrings=["atr"],                       preProcess=cardInfoFun,postProcess=printATR,argChecker=DefaultArgsChecker([("cardIndex",i)],0))
Executer.addCommand(CommandStrings=["connect","card"],            process=connectReaderFromCardFun,   argChecker=DefaultArgsChecker([("cardIndex",i)],0))

#apdu
Executer.addCommand(CommandStrings=["apdu"],                      process=sendAPDU,argChecker=AllTheSameChecker(hexaArgChecker(),"args"),postProcess=printResultHandler)
Executer.addCommand(CommandStrings=["forge"],                     preProcess=forge,argChecker=AllTheSameChecker(hexaArgChecker(),"args"),postProcess=printResultHandler)
#TODO make an alias with "execute"

Executer.addCommand(CommandStrings=["auto","connection"],           process=enableAutoCon)
Executer.addCommand(CommandStrings=["disable","auto","connection"], process=disableAutoCon)

protType = tokenValueArgChecker({"T0":CardConnection.T0_protocol,"T1":CardConnection.T1_protocol,"RAW":CardConnection.RAW_protocol,"T15":CardConnection.T15_protocol})
Executer.addCommand(CommandStrings=["set","protocol"],           process=setProtocol, argChecker=AllTheSameChecker(protType,"protocols",1,4,True))
Executer.addCommand(CommandStrings=["get","protocol"],           process=getProtocol)



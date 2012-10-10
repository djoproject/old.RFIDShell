#!/usr/bin/python2.6
from arg.args import *
from apdu.apduExecuter import *

from keyList import keys
import platform

from smartcard.System import readers
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from smartcard.ATR import ATR

from smartcard.pcsc.PCSCContext import PCSCContext
from smartcard.pcsc.PCSCExceptions import EstablishContextException

from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker

from apdu.apdu import ApduRaw

#TODO
    #-faire une section critique entre les observeurs et les methods pour proteger : l'envi et la liste de card
    #-lorsqu'on quitte, se deconnecter? ou ca le fait deja tout seul?

########### TEST CONTEXT ###############
try:
    print "load context... please wait"
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
                        disconnectReaderFromCardFun(Executer.envi,[])
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
    
    def update( self, observable, (addedcards, removedcards) ):
        r = ""
        if addedcards != None and len(addedcards) > 0:
            r += "Added cards" + str(addedcards) 
            for c in addedcards:
                self.cardList.append(c)
        
        if removedcards != None and len(removedcards) > 0:
            
            if len(r) > 0:
                r += "\n"
            
            r += "Removed cards" + str(removedcards)
            
            for c in removedcards:
                self.cardList.remove(c)

                if hasattr(c,'connection'):
                    disconnectReaderFromCardFun(Executer.envi,[])
                    Executer.printAsynchronousOnShell("WARNING : the card has been removed, the connection is broken")
            
        if self.enable and len(r) > 0:
            Executer.printAsynchronousOnShell(r)
        
    def activate(self):
        #if not self.enable:
        #    self.cardmonitor.addObserver( self )
        
        self.enable = True
        
    def desactivate(self):
        #if self.enable:
        #    self.cardmonitor.deleteObserver(self)
        
        self.enable = False

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

def listKeyFun(envi,args):
    return keys.keys()
    #count = 0
    #for k in keys:
    #    print k
    #    count += 1

    #if count == 0:
    #    Executer.printOnShell("no key available")

def addKeyFun(envi,args):
    key = []    
    for i in range(1,len(args)):
        key.append(args[i])

    keys[args[0]] = key

def listReaderFun(envi,args):
    #indice = 0
    try:
        r = readers()
    #    for r in readers():
    #        print "\t"+str(indice)+" : "+str(r)
    #        indice += 1
    except Exception as e:
        Executer.printOnShell(str(e))
        return

    if r == None or len(r) == 0:
        #Executer.printOnShell("no reader available on this system")
        Executer.printOnShell("HINT : some reader need to connect a card before to be detected in the system")
        
    return r

def monitorCardFun(envi,args):
    if cardobserver.enable:
        Executer.printOnShell("The cards are already monitored")
    else:
        cardobserver.activate()
        Executer.printOnShell("Monitor cards : enable")

def monitorReaderFun(envi,args):
    if readerobserver.enable:
        Executer.printOnShell("The readers are already monitored")
    else:
        readerobserver.activate()
        Executer.printOnShell("Monitor readers : enable")

def monitorDataFun(envi,args):
    if not dataobserver.available():
        Executer.printOnShell("the data monitoring is not yet available, connect a reader or insert a card")
        dataobserver.desactivate()

    if dataobserver.enable:
        Executer.printOnShell("The data are already monitored")
    else:
        dataobserver.activate()
        Executer.printOnShell("Monitor data : enable")

def monitorCardAll(envi,args):
    monitorCardFun(envi,args)
    monitorReaderFun(envi,args)
    monitorDataFun(envi,args)
    
def disableMonitorCardFun(envi,args):
    if cardobserver.enable:
        cardobserver.desactivate()
        Executer.printOnShell("Monitor cards : disable")
    else:
        Executer.printOnShell("The cards are not monitored")

def disableMonitorReaderFun(envi,args):
    if readerobserver.enable:
        readerobserver.desactivate()
        Executer.printOnShell("Monitor readers : disable")
    else:
        Executer.printOnShell("The readers are not monitored")

def disableMonitorDataFun(envi,args):
    if not dataobserver.available():
        Executer.printOnShell("the data monitoring is not yet available, connect a reader or insert a card")
        dataobserver.desactivate()
    
    if dataobserver.enable:
        dataobserver.desactivate()
        Executer.printOnShell("Monitor data : disable")
    else:
        Executer.printOnShell("The data are not monitored")

def disableMonitorCardAll(envi,args):
    disableMonitorCardFun(envi,args)
    disableMonitorReaderFun(envi,args)
    disableMonitorDataFun(envi,args)

def listCardFun(envi,args):
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

def cardInfoFun(envi,args):    
    if len(args) == 0:
        indice = 0
        if len(cardobserver.cardList) > 1:
            Executer.printOnShell("Warning : the information comes from the first card available in the list, there are others cards")
            i += 1
    else:
        indice = args[0]
        
    if len(cardobserver.cardList) == 0:
        Executer.printOnShell("there is no card available")
        return
    
    try:
        card = cardobserver.cardList[indice]
    except IndexError:
        Executer.printOnShell("invalid indice")
        return
    
    atr = ATR(card.atr)
    
    print atr
    print
    atr.dump()
    print 'T15 supported: ', atr.isT15Supported()
    
def connectReaderFromCardFun(envi,args):
    if "connection" in envi and envi["connection"] != None:
        print "there is already a connection to reader"
        return
    
    if len(args) == 0:
        indice = 0
        if len(cardobserver.cardList) > 1:
            Executer.printOnShell("Warning : the information comes from the first card available in the list, there are others cards")
    else:
        indice = args[0]
        
    if len(cardobserver.cardList) == 0:
        Executer.printOnShell("there is no card available")
        return
    
    try:
        card = cardobserver.cardList[indice]
    except IndexError:
        Executer.printOnShell("invalid indice")
        return
        
    envi["connection"] = card.createConnection() #create a connection on the reader
    envi["connection"].connect()#create a connection on the card
    card.connection = envi["connection"]
    card.connection.card = card
    envi["connectedReader"] = card.connection.getReader()

    errorchain=[]
    errorchain=[ ErrorCheckingChain( errorchain, ISO7816_8ErrorChecker() ),
                 ErrorCheckingChain( errorchain, ISO7816_9ErrorChecker() ),
                 ErrorCheckingChain( errorchain, ISO7816_4ErrorChecker() ) ]
    envi["connection"].setErrorCheckingChain(errorchain)
    
def disconnectReaderFromCardFun(envi,args):
    if "connection" not in envi or envi["connection"] == None:
        print "there is no opened connexion"
        return
    
    try:
        envi["connection"].disconnect()
    except Exception as e:
        print str(e)
    
    if hasattr(envi["connection"],'card'):
        del envi["connection"].card.connection
        del envi["connection"].card
        
    del envi["connectedReader"]
    del envi["connection"]
    
def connectReaderFun(envi,args):
    if "connection" in envi and envi["connection"] != None:
        print "there is already a connection to reader"
        return
    
    r = readers()
    if len(args) == 0:
        indice = 0
        if len(r) > 1:
            Executer.printOnShell("Warning : the connection will open on the first available reader but there are others")
    else:
        indice = args[0]
    
    if len(r) == 0:
        Executer.printOnShell("there is no reader available")
        return  
     
    try:
        reader = r[indice]
    except IndexError:
        Executer.printOnShell("invalid indice")
        return
        
    envi["connection"] = reader.createConnection()
    envi["connectedReader"] = reader
    
def sendAPDU(envi,args):
    #Executer.executeAPDUAndPrintDataAndSW(ApduRaw(args))
    return args

###############################################################################################
##### add command to shell ####################################################################
###############################################################################################

#key management        
Executer.addCommand(["lskey"],                     "list keys",               "list the available key name",                                   True,listKeyFun,                  None,stringListResultHandler)
s = stringArgChecker()
i = IntegerArgChecker()
keyCmdChecker = MultiArgsChecker([s,i,i,i,i,i,i,i,i],[s,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i]) #manage 8bytes or 16bytes key

Executer.addCommand(["setKey"],                    "set a key",               "set a 8 bytes key or 16 bytes key",                             True,addKeyFun,                   keyCmdChecker)

#reader management
Executer.addCommand(["lsreader"],                  "list reader",             "list all the reader available on the system",                   True,listReaderFun,               None,stringListResultHandler)
Executer.addCommand(["connect","reader"],          "connect a card",          "establish a link between the shell and a card",                 True,connectReaderFun,            MultiArgsChecker([],[s]))
Executer.addCommand(["disconnect"],                "disconnect a card/reader","destroy the link between the current card/reader and the shell",True,disconnectReaderFromCardFun)

#monitoring management
Executer.addCommand(["monitor","all"],             "monitor all",             "enable the global monitoring",                                  True,monitorCardAll)
Executer.addCommand(["monitor","reader"],          "monitor the reader",      "enable the reader monitoring",                                  True,monitorReaderFun)
Executer.addCommand(["monitor","card"],            "monitor card",            "enable the card monitoring",                                    True,monitorCardFun,              None,stringListResultHandler)
Executer.addCommand(["monitor","data"],            "monitor data",            "enable the data monitoring",                                    True,monitorDataFun)

Executer.addCommand(["disable","monitor","all"],   "disable all monitor",     "disable the global monitoring",                                 True,disableMonitorCardAll)
Executer.addCommand(["disable","monitor","reader"],"disable reader monitor",  "disable the reader monitoring",                                 True,disableMonitorReaderFun)
Executer.addCommand(["disable","monitor","card"],  "disable card monitor",    "disable the card monitoring",                                   True,disableMonitorCardFun)
Executer.addCommand(["disable","monitor","data"],  "disable data monitor",    "disable the data monitoring",                                   True,disableMonitorDataFun)

#card management
Executer.addCommand(["lscard"],                    "list card",               "list all the card available on the system",                     True,listCardFun,                None,cardListResultHandler)
Executer.addCommand(["cardinfo"],                  "card info",               "print all the info of the card ATR",                            True,cardInfoFun,                MultiArgsChecker([],[i]))
Executer.addCommand(["connect","card"],            "connect a card",          "establish a link between the shell and a card",                 True,connectReaderFromCardFun,   MultiArgsChecker([],[i]))

#apdu
Executer.addCommand(["apdu"],"","",True,sendAPDU,AllTheSameChecker(hexaArgChecker()),resultHandlerAPDUAndPrintDataAndSW)



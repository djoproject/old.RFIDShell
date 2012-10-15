#!/usr/bin/python2.6

from smartcard.sw.ErrorChecker import ErrorChecker
from arg.args import Executer

class PronrollErrorChecker(ErrorChecker):
    def __call__( self, data, sw1, sw2 ):
        if not proxnrollSW.has_key(sw1): 
            return
        
        exception, sw2dir = proxnrollSW[sw1] 
        if type(sw2dir) != type({}): 
            return
            
        try: 
            message = sw2dir[sw2]
            if isinstance(exception,Exception):
                raise exception(data, sw1, sw2, message)
                
        except KeyError: 
            if None in sw2dir:
                message = sw2dir[None]+" : "+str(sw2) 
                raise exception(data, sw1, sw2, message)
#!/usr/bin/python2.6

class apduBuilderException(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return repr(self.value)
        
class apduAnswserException(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return repr(self.value)
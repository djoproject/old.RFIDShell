

def stringListResultHandler(printer,result):
    #if result == None or len(result) == 0:
    #    Executer.printOnShell("no item available")
    #    return
        
    for i in result:
        printer.printOnShell(i)
        
def printResultHandler(printer,result):
    if result != None:
        printer.printOnShell(str(result))
    
def listResultHandler(printer,result):
    #if result == None or len(result) == 0:
    #    Executer.printOnShell("no item available")
    #    return

    for i in result:
        printer.printOnShell(str(i))
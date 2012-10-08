#!/usr/bin/python2.6
from tries import *

"""t = tries("")
t.insert("all","plop")

t1 = tries("")
t1.insert("monitor",t)

t2 = tries("")
t2.insert("enable",t1)

print repr(t2)"""

"""from triesShell import *

ts = triesShell()

ts.addEntry(["enable","monitor","all"],commandShell())
ts.addEntry(["enable","monitor","cards"],commandShell())
ts.addEntry(["enable","monitor","readers"],commandShell())

print repr(ts)"""

t = tries("be", None,"k")
t.insert("bebear","a")
t.insert("bebe","b")
t.insert("bebearor","c")
t.insert("bebearoraa","d")
t.insert("bebebe","e")
#t.insert("be","z")

t.insert("toto","f")
#t.insert("bebc","c")

print t.traversal()
t.remove("bebe")
print ""
print t.traversal()
t.remove("bebebe")
print ""
print t.traversal()

#print repr(t)
#print t.search("beb")
#t.update("bebe","ghaa")
#print t.traversal()
#print t.searchUniqueFromPrefix("beb")
#print t.getKeyListFromPrefix("bea")
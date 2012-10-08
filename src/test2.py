#!/usr/bin/python2.6
from triesShell import *

t = triesShell()
t.addEntry(["aa","bb", "cc"],"ok")
node, args = t.searchEntryFromMultiplePrefix(["a","b","c"])
print node.value

t.removeEntry(["aa","bb", "cc"])

print repr(t)

node, args = t.searchEntryFromMultiplePrefix(["a","b","c"])
print node.value
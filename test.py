#!/usr/bin/env python
import sys
print sys.argv[1]
print len(sys.argv)

#if sys.argv[1].endswith(".log"):
if not sys.argv[1].endswith(".log") and not sys.argv[1].endswith(".gz"):
    print "this is not a default log file"



#!/usr/bin/env python

"""
Wind2OSSM filename

Translater from any supported format to OSSM format

"""

Usage = """
Wind2OSSM.py infilename [timezone] [timezonename]

Converts various wind file formats to the OSSM format

the second argument, if provided, will shift the timezone. 

For example:
Wind2OSSM.py SomeData.txt 8 PST

Converts the wind data in SameData.txt to an OSSM wind file,
subtracting 8 hours, to shift from UTC to PST

"""

import sys
#import MetData
from weathertools import MetData

try:
    infilename = sys.argv[1]
except IndexError:
    print Usage
    sys.exit()
#print "split name:", infilename.rsplit('.',1)
outfilename = infilename.rsplit('.',1)[0] + ".OSM"

try:
    timeZone = int(sys.argv[2])
except IndexError:
    timeZone = 0

try:
    timeZoneName  = sys.argv[3]
except IndexError:
    timeZoneName = ""


# identify the file type

# Readers = MetData.IdentifyFile(infilename)
# 
# if len(Readerrs) == 0:
#     raise Exception("I don't have a matching reader")
# elif len(Readers) > 1:
#     raise Exception("more than one reader matched")

print "Reading:", infilename
print "Converting to:", outfilename
Data = MetData.MetData(infilename)
if timeZone <> 0:
    Data.ChangeTZ(timeZone, timeZoneName)

Data.SaveAsOSSMWind(outfilename, units='knots')
#Data.SaveAsOSSMWind(outfilename)


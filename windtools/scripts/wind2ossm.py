#!/usr/bin/env python

"""
Wind2OSSM filename

Translate from any supported format to OSSM format

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
from windtools import MetData

try:
    infilename = sys.argv[1]
except IndexError:
    print Usage
    sys.exit()
outfilename = infilename.rsplit('.', 1)[0] + ".OSM"

try:
    timeZone = int(sys.argv[2])
except IndexError:
    timeZone = 0

try:
    timeZoneName = sys.argv[3]
except IndexError:
    timeZoneName = ""


print "Reading:", infilename
data = MetData(infilename)

print "Converting to:", outfilename
if timeZone != 0:
    data.ChangeTZ(timeZone, timeZoneName)

data.SaveAsOSSMWind(outfilename, units='knots')

#Data.SaveAsOSSMWind(outfilename)


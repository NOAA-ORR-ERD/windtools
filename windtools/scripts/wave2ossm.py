#!/usr/bin/env python

"""
Wind2OSSM filename

Translate from any supported format to OSSM format

"""

import sys
from windtools import MetData

# #fixme: "This shifts to Pacific time!!!"
try:
    infilename = sys.argv[1]
except IndexError:
    print "You need to give me a file to process!!"
    sys.exit(1)

print "split name:", infilename.rsplit('.', 1)
outfilename = infilename.rsplit('.', 1)[0] + ".wave.OSM"


data = MetData(infilename)
# check for lat-lon
if data.LatLong == (None, None):
    latlon = raw_input("I need the lat, lon (ex: 28.54, -92.45): > ").strip()
    lat, lon = (float(l) for l in latlon.split(","))
    data.LatLong = (lat, lon)
data.ChangeTZ(8, "PST")

print "Converting to PST!!!!"

#Data.SaveAsOSSMWind(outfilename, units='knots')

data.SaveAsOSSMWave(outfilename)


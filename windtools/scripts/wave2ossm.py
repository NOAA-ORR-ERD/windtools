#!/usr/bin/env python

"""
Wind2OSSM filename

Translater from any supported format to OSSM format

"""

import sys
from weathertools import MetData

##fixme: "This shifts to Pacific time!!!"
infilename = sys.argv[1]
print "split name:", infilename.rsplit('.',1)
outfilename = infilename.rsplit('.',1)[0] + ".wave.OSM"

# identify the file type

# Readers = MetData.IdentifyFile(infilename)
# 
# if len(Readerrs) == 0:
#     raise Exception("I don't have a matching reader")
# elif len(Readers) > 1:
#     raise Exception("more than one reader matched")
    
Data = MetData.MetData(infilename)
Data.ChangeTZ(8, "PST")

print "Converting to PST!!!!"

#Data.SaveAsOSSMWind(outfilename, units='knots')
Data.SaveAsOSSMWave(outfilename)


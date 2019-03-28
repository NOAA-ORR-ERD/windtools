#!/usr/bin/env python

"""
merge_winds.py file1 [file2] ...

(typically filename*.txt)

Should ready any supported format and output OSSM format

"""

Usage = """
merge_winds.py file1 [file2] [...] outfilename

(typically merge_winds.py filename*.txt)

merges multiple files into one.

outputs OSSM format (for now)

"""

import sys
from windtools import MetData

if len(sys.argv) < 4:
    print("You must supply at least two input files and one output file")
    print Usage
    sys.exit()
else:
    infilenames = sys.argv[1:-1]
    outfilename = sys.argv[-1]

if not outfilename.lower().endswith(".osm"):
    outfilename += ".osm"

# try:
#     timeZone = int(sys.argv[2])
# except IndexError:
#     timeZone = 0

# try:
#     timeZoneName = sys.argv[3]
# except IndexError:
#     timeZoneName = ""

print "Reading:", infilenames[0]
data = MetData(infilenames[0])

for infile in infilenames[1:]:
    print "Reading:", infile
    new_data = MetData(infile)
    data += new_data

# print "Converting to:", outfilename
# if timeZone != 0:
#     data.ChangeTZ(timeZone, timeZoneName)

data.SaveAsOSSMWind(outfilename, units='knots')

#Data.SaveAsOSSMWind(outfilename)


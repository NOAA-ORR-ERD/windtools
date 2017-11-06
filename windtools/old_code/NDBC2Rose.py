#!/usr/bin/env python

"""
Translate from NDBC data to roseplot3 format
"""

infilename = "BURL1-Aug-Oct.txt"

infile = file(infilename, 'rU')

data = np.zeros(10, 12)

while True:
    line = infile.readline().strip()
    if not line:
        break
    if line.startswith("3 - PERCENT FREQUENCY OF AVERAGE WIND SPEED"):
        # start reading a table.
        month = infile.readline().strip()
        infile.readline()
        infile.readline()
        # the zero line:
        
    

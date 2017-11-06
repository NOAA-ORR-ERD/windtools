#!/usr/bin/env python

import sys

iw=[3,6,10,15,21,"kts"] #the windspeed bin boundaries, and units (for plot)

num_bins = 16

b=[None]*num_bins #initialize the the two-dimensional array 
for n in range(num_bins): b[n]=[0]*len(iw) #b is a list of lists, all zeros
#[dummy,infilename,outfilename]=sys.argv #get the file names from the command line
month = sys.argv[1]
infilename = sys.argv[2]
outfilename = infilename + "_month_"+month+".bins" 

infile=open(infilename,'rU')
outfile=open(outfilename,'w')

calm=0 # initialize number of events with no windspeed
dirless=0 #initialize number of events with ambiguous direction

# read past the header:
while True:
    line = infile.readline()
    if line.strip() == '0,0,0,0,0,0,0,0':
        print "past the header"
        break

while True:
    aline=infile.readline().strip()
    if not aline: break
#    if aline[0]=='#': continue

    a=aline.split(',')
#    if a[4][0]=='*' or a[5][0]=='*':   #missing data is denoted with "***"
#        print 'skip record with missing data:', aline,
#        continue
    if int(a[1]) <> int(month):
        continue
    wdir = float(a[6]) #data was read as string, convert to float
    speed = float(a[5])
    ndir=int(wdir/(360/num_bins)%num_bins) #the %num_bins means the remainder in the division by num_bins 
    if speed==0:
        calm+=1
    elif wdir==0:
        dirless+=1
    else:
        for n in range(len(iw)-1):
            if speed<=iw[n]:
                nspd=n
                break
            nspd=n+1 #the final, open-ended bin
        b[ndir][nspd]+=1 #ignore direction of windspeed=0
outfile.write(str([calm, dirless])+"\n")
outfile.write(str(iw)+"\n")
for i in range(0,num_bins):
    outfile.write(str([i,b[i][:]])+"\n")
outfile.close()
print outfilename + " was written"

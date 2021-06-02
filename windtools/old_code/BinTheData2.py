#!/usr/bin/env python
#import sys


iw=[3,6,10,15,21,"kts"] #the windspeed bin boundaries, and units (for plot)
b=[None]*36 #initialize the the two-dimensional array 
for n in range(36): b[n]=[0]*len(iw) #b is a list of lists, all zeros
#[dummy,infilename,outfilename]=sys.argv #get the file names from the command line
infilename='sfo1998.dat'
outfilename='rosebin2.dat'

infile=open(infilename,'r')
outfile=open(outfilename,'w')
calm=0 # initialize number of events with no windspeed
dirless=0 #initialize number of events with ambiguous direction

while 1:
	aline=infile.readline()
	if not aline: break
	if aline[0]=='#': continue
	a=aline.split()
	if a[4][0]=='*' or a[5][0]=='*':   #missing data is denoted with "***"
			print('skip record with missing data:', aline, end=' ')
			continue
	wdir=int(a[5]) #data was read as string, convert to integer
	speed=int(a[4])
	ndir=wdir/10%36 #the %36 means the remainder in the division by 36 
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
for i in range(0,36):
	outfile.write(str([i,b[i][:]])+"\n")
outfile.close()
print(outfilename+" was written")

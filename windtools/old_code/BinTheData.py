#!/usr/bin/env python
import sys
b=[0]*36 #initialize the bins with zero
#following does not work with Windows:
#[dummy,infilename,outfilename]=sys.argv
infilename='sfo1998.dat'
outfilename='rosebin.dat'
infile=open(infilename,'r')
outfile=open(outfilename,'w')

calm=0 # initialize nubmer of events with no windspeed
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
		b[ndir]=b[ndir]+1 #ignore direction of windspeed=0
outfile.write("%d %d\n" % (calm, dirless))
for i in range(0,36):
	outfile.write("%d %d\n" % (i,b[i]))
outfile.close()
print(outfilename+" was written")

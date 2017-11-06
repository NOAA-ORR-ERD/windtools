#!/usr/bin/env python
import sys
from simpleSVG import * 
infilename='rosebin.dat'
bindat=open(infilename,'r')
wf=[]
sumb=0.
#read in number of calm and directionless events 
aline=bindat.readline()
calm,dirless=[int(x) for x in aline.split()] 
#read in "binned data", the second column being the number of events 
#in that "angle bin" marked in the first column:
while 1:
	aline=bindat.readline()
	if not aline: break
	if aline[0]=='#': continue
	i,b=[int(x) for x in aline.split()] #convert substrings to integers
	wf.append(b)
	sumb=sumb+b
sumb=sumb+calm+dirless
n=len(wf) #should be 36
mwf=max(wf)
rsize=170 #pt size for maximum "petal" length
sc=float(rsize)/mwf  #scale factor, pts per number
da=360./n
dah=.5*da
a1=90+dah
r1=10 #an integer, so unit is pts
#now plot using simpleSVG:

a=svg_class(fname="windrose1.svg")
a.scale(xmin=-1,xmax=1,ymin=-1,ymax=1)
a.group(stroke_width=".25pt",fill="black",text_anchor='middle')
for i in range(0,n):
	a2=a1
	a1=a2-da
	r2=r1+sc*wf[i]
	a.sector(0.,0.,r1,int(r2),a1,a2,fill='red')
for i in range(1,7):
	rfreq=i*.02
	lab="%5.2f" % (rfreq)
	r=rfreq*sumb*sc+r1
	a.circle(0.,0.,int(r),fill='none',stroke='blue')
	a.text(0.,int(a.jy(0.))+int(r)+11,0,lab,font_size='12pt')
a.text(.5j,.10j,0.,'blue circles are frequency per 10 degrees',font_size='12pt',
stroke='blue',fill='blue')
a.text(.5j,.05j,0.,'SFO 2 m winds, 1998',font_size='18pt')
calmf=float(calm)/sumb
calmfs="   calm freq= %f" % calmf 
a.text(.5j,.95j,0.,calmfs,font_size='12pt')
dirlessf=float(dirless)/sumb
dirlessfs="dirless freq= %f" % dirlessf 
a.text(.5j,.98j,0.,dirlessfs,font_size='12pt')
a.close()

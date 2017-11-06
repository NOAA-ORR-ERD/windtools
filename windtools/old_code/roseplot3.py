#!/usr/bin/env python
# Similar to roseplot2.py, but here the radius of the sectors 
# is adjusted so that the area of the sectors, rather than radius,
# is proportional to the relative frequency.
import sys, math

from simpleSVG import * 

infilename='rosebin2.dat'


bindat=open(infilename,'r')
wf=[] #will be a list of total events if an angle bin
wfs=[] #will be a list of lists of events in windspeed bins
colors=[(0.,.5,0.),(0.,.7,.7),(.5,.6,.6),(.8,.6,.4),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),(0.,1.,1.)]
clrs=[rgbstring(*t) for t in colors]

sumb=0. #this will be the sum of all the bins 

#read in number of calm and directionless incidents:
calm,dirless=eval(bindat.readline())
iw=eval(bindat.readline())

#read in binned data: angle bin number, followed by events in windspeed bins 
while 1:
	aline=bindat.readline()
	if not aline: break
	i,bb=eval(aline) #
	b=reduce(lambda x, y: x+y, bb) #sums the windspeed bins, see "help(reduce)"
	wf.append(b) #list of events in each angle bin 
	wfs.append(bb) #list of lists of windspeed bins
	sumb=sumb+b #total of all windspeed bins
sumb=sumb+calm+dirless #total of all events
n=len(wf) #should be 36
mwf=max(wf)
rsize=170 #pt size for maximum "petal" length
sc=float(rsize)**2/mwf #scale factor, pts per number
da=360./n
dah=.5*da
a1=90+dah #convert meteorology angle to postscript angle
r0=10 #an integer, so unit is pts
r0=int(math.sqrt((calm+dirless)*sc/n))


#now plot using simpleSVG:
a=svg_class(fname="windrose3.svg")

a.scale(xmin=-1,xmax=1,ymin=-1,ymax=1)
a.group(stroke_width=".25pt",fill="black",text_anchor='middle')

for i in range(0,n):
	a2=a1
	a1=a2-da  #notice -da; meteorology is clockwise, svg is anticlockwise
	r2=r0
	for n in range(len(wfs[i])):
		f=wfs[i][n]
		r1=r2 #last outer radius becomes current inner radius of sector
		r2=int(math.sqrt(r1**2+sc*f))
		a.sector(0.,0.,r1,r2,a1,a2,fill=clrs[n])

for i in range(1,7): #make the blue frequency circles
	rfreq=i*.02
	lab="%5.2f" % (rfreq)
	r=math.sqrt(rfreq*sumb*sc+r0**2)
	a.circle(0.,0.,int(r),fill='none',stroke='blue')
	a.text(0.,int(a.jy(0.))+int(r)+11,0,lab,font_size='12pt')

a.text(.5j,.10j,0.,'blue circles are frequency per 10 degrees',font_size='12pt',
           stroke='blue',fill='blue')

a.text(.5j,.05j,0.,'SFO 2 m winds, 1998',font_size='18pt')

a.group(text_anchor="start")
calmf=float(calm)/sumb
calmfs="   calm freq= %f" % calmf 

a.text(.1j,.95j,0.,calmfs,font_size='12pt')
dirlessf=float(dirless)/sumb
dirlessfs="dirless freq= %f" % dirlessf 

a.text(.1j,.98j,0.,dirlessfs,font_size='12pt')
a.group()

x=.5j
y=.98j
dx=.07j
dy=-.07j
a.group(text_anchor="middle")

for n in range(len(iw)):
	a.rect2(x+n*dx,y,x+(n+1)*dx,y+dy,fill=clrs[n])
	a.text(x+(n+1)*dx,y+dy-.01j,0.,str(iw[n]),font_size="12pts")

a.group()
a.close()

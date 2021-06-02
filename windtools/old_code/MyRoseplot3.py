#!/usr/bin/env python
# Similar to roseplot2.py, but here the radius of the sectors 
# is adjusted so that the area of the sectors, rather than radius,
# is proportional to the relative frequency.
import sys, math

import numpy as np

import simpleSVG as SVG

infilename = sys.argv[1]
title = ".".join(infilename.split(".")[:-1])

def ReadBinnedData(filename):
    
    bindat=open(filename,'rU')

    wfs=[] #will be a list of lists of events in windspeed bins
    #read in number of calm and directionless incidents:
    calm, dirless = eval(bindat.readline())
    # velocity bins
    vel_bins = eval(bindat.readline())
    #read in binned data: angle bin number, followed by events in windspeed bins 
    while 1:
        aline=bindat.readline()
        if not aline:
            break
        i, bb=eval(aline) #
        wfs.append(bb) #list of lists of windspeed bins
    wfs = np.array(wfs)
    return calm, dirless, wfs, vel_bins

def GenerateRose(filename, calm, dirless, wfs, vel_bins):

    colors=[(0.,.5,0.),(0.,.7,.7),(.5,.6,.6),(.8,.6,.4),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),(0.,1.,1.)]
    clrs=[SVG.rgbstring(*t) for t in colors]

    wf = wfs.sum(axis=1)
    ## fixme - make calm just the first bins.
    sumb = wfs.sum() + calm + dirless

    n = wfs.shape[0] # number of direction bins
    mwf = wf.max() # max number in a direction bin


    rsize = 170 #pt size for maximum "petal" length
    sc = float(rsize)**2/mwf #scale factor, pts per number
    da = 360./n
    dah = .5*da
    a1 = 90+dah #convert meteorology angle to svg angle

    r0 = int(math.sqrt((calm+dirless)*sc/n)) #an integer, so unit is pts


    #now plot using simpleSVG:
    a = SVG.svg_class(fname=filename)

    a.scale(xmin=-1,xmax=1,ymin=-1,ymax=1)
    a.group(stroke_width=".25pt", fill="black", text_anchor='middle')

    lightVariable = calm+dirless * 100. / sumb
    # put the percent light and variable in the middle:
    a.text(256, 256, 0, "%.2f"%lightVariable, font_size='12pt')
    for i in range(1,7): #make the blue frequency circles
        rfreq=i*.02
        r=math.sqrt(rfreq*sumb*sc+r0**2)
        a.circle(0.,0.,int(r),fill='none',stroke='blue')

    # make the "sectors"
    for i in range(0,n):
        a2 = a1
        a1 = a2-da  #notice -da; meteorology is clockwise, svg is anticlockwise
        r2 = r0
        for n in range(len(wfs[i])):
            f=wfs[i][n]
            r1=r2 #last outer radius becomes current inner radius of sector
            r2=int(math.sqrt(r1**2+sc*f))
            a.sector(0.,0.,r1,r2,a1,a2,fill=clrs[n])

    for i in range(1,7): #make the labels for the frequency circles
        rfreq=i*.02
        lab="%5.1f" % (rfreq*100)
        r=math.sqrt(rfreq*sumb*sc+r0**2)
        a.text(0., int(a.jy(0.))+int(r)+11, 0, lab, font_size='12pt')

    

    a.text(.5j,.10j,0.,'blue circles are percent occurance',font_size='12pt',
               stroke='blue',fill='blue')

    a.text(.5j,.05j,0.,title,font_size='18pt')

    a.group(text_anchor="start")
    calmf=float(calm)/sumb
    calmfs="calm percent= %.1f"%(calmf*100) 

    a.text(.1j,.95j,0.,calmfs,font_size='12pt')
    dirlessf=float(dirless)/sumb
    dirlessfs="dirless percent= %.1f"%(dirlessf*100) 

    a.text(.1j,.98j,0.,dirlessfs,font_size='12pt')


    a.group()

    x=.5j
    y=.98j
    dx=.07j
    dy=-.07j
    a.group(text_anchor="middle")

    for n in range(len(vel_bins)):
            a.rect2(x+n*dx,y,x+(n+1)*dx,y+dy,fill=clrs[n])
            a.text(x+(n+1)*dx,y+dy-.01j,0.,str(vel_bins[n]),font_size="12pts")

    a.group()
    a.close()

def GenerateRose2(filename,  wfs, vel_bins):

    colors=[(0.,.5,0.),(0.,.7,.7),(.5,.6,.6),(.8,.6,.4),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),(0.,1.,1.)]
    clrs=[SVG.rgbstring(*t) for t in colors]
    
    print(wfs)
    sumb = wfs.sum() 
    calm = wfs[:,0].sum()
    dirless = 0
    # remove the calm column
    wfs = wfs [:,1:]
    # remove the extra bins
    vel_bins = vel_bins[1:-1]

    wf = wfs.sum(axis=1)

    n = wfs.shape[0] # number of direction bins
    mwf = wf.max() # max number in all direction bins


    rsize = 170 #pt size for maximum "petal" length
    sc = float(rsize)**2/mwf #scale factor, pts per number
    da = 360./n
    dah = .5*da
    a1 = 90+dah #convert meteorology angle to svg angle

    r0 = int(math.sqrt((calm+dirless)*sc/n)) #an integer, so unit is pts


    #now plot using simpleSVG:
    a = SVG.svg_class(fname=filename)

    a.scale(xmin=-1,xmax=1,ymin=-1,ymax=1)
    a.group(stroke_width=".25pt", fill="black", text_anchor='middle')

    print(calm, dirless, sumb)
    lightVariable = (calm+dirless) * 100. / sumb
    # put the percent light and variable in the middle:
    a.text(256, 256, 0, "%.2f%%"%lightVariable, font_size='12pt')
    for i in range(1,7): #make the blue frequency circles
        rfreq=i*.02
        r=math.sqrt(rfreq*sumb*sc+r0**2)
        a.circle(0.,0.,int(r),fill='none',stroke='blue')

    # make the "sectors"
    for i in range(0,n):
        a2 = a1
        a1 = a2-da  #notice -da; meteorology is clockwise, svg is anticlockwise
        r2 = r0
        for n in range(len(wfs[i])):
            f=wfs[i][n]
            r1=r2 #last outer radius becomes current inner radius of sector
            r2=int(math.sqrt(r1**2+sc*f))
            a.sector(0.,0.,r1,r2,a1,a2,fill=clrs[n])

    for i in range(1,7): #make the labels for the frequency circles
        rfreq=i*.02
        lab="%5.1f" % (rfreq*100)
        r=math.sqrt(rfreq*sumb*sc+r0**2)
        a.text(0., int(a.jy(0.))+int(r)+11, 0, lab, font_size='12pt')

    

    a.text(.5j,.10j,0.,'blue circles are percent occurance',font_size='12pt',
               stroke='blue',fill='blue')

    a.text(.5j,.05j,0.,title,font_size='18pt')

#    a.group(text_anchor="start")
#    calmf=float(calm)/sumb
#    calmfs="calm percent= %.1f"%(calmf*100) 
#
#    a.text(.1j,.95j,0.,calmfs,font_size='12pt')
#    dirlessf=float(dirless)/sumb
#    dirlessfs="dirless percent= %.1f"%(dirlessf*100) 
#
#    a.text(.1j,.98j,0.,dirlessfs,font_size='12pt')


    a.group()

    x=.5j
    y=.98j
    dx=.07j
    dy=-.07j
    a.group(text_anchor="middle")

    for n in range(len(vel_bins)):
            a.rect2(x+n*dx,y,x+(n+1)*dx,y+dy,fill=clrs[n])
            a.text(x+(n+1)*dx, y+dy-.01j, 0., "%i"%vel_bins[n], font_size="12pts")

    a.group()
    a.close()

#calm, dirless, wfs, vel_bins = ReadBinnedData(infilename)
#vel_bins = vel_bins[1:]
fname=infilename+".svg"
#GenerateRose(fname, calm, dirless, wfs, vel_bins)

dirs = np.random.normal(loc=180, scale = 60, size=(5000,) )
spds = np.random.normal(loc=10, scale = 6, size=(5000,) )
spds = np.where((spds<0), 0, spds)
data = np.c_[spds, dirs]
vel_bins = [1, 5, 10, 15, 21,]
import WindRose
binned, spd_bins, dir_bins = WindRose.BinTheData(data, vel_bins, num_dir_bins=16)

GenerateRose2(fname, binned.T, spd_bins)




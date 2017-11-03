#!/usr/bin/env python

import matplotlib
from matplotlib import transforms
from matplotlib.collections import LineCollection
import pylab
import numpy as np


class VectorLineCollection(LineCollection):
    def __init__(self, Points, Angles, fig, axis):

        self.Points = Points
        self.Angles = Angles
        
        self.ArrowLength = 0.3 # should be inches 
        self.ArrowHeadSize = 0.08 # should be inches
        self.ArrowHeadAngle = 45. # degrees

        self.CalcArrowPoints()
        self.CalcArrows()

        LineCollection.__init__(self,
                                self.Arrows,
                                offsets=self.Points,
                                transOffset=axis.transData, # transforms the x,y offsets
                                )
#        trans = transforms.scale_transform(fig.dpi, fig.dpi) 
        trans = transforms.ScaledTranslation(fig.dpi, fig.dpi) 
        self.set_transform(trans)  # the points to pixels transform

        return None
        
    def CalcArrowPoints(self):
        L = self.ArrowLength
        S = self.ArrowHeadSize
        phi = self.ArrowHeadAngle * np.pi / 360
        #print "phi:", phi
        #print "S", S
        self.ArrowPoints = np.array( ( (0, L, L - S*np.cos(phi), L, L - S*np.cos(phi) ),
                                      (0, 0, S*np.sin(phi),     0,    -S*np.sin(phi) ) ),
                                    np.float )
        return None
        
    def CalcArrows(self):
        ArrowPoints = self.ArrowPoints
        self.Arrows = np.zeros((self.Angles.shape[0],5,2), np.float)
        for i, theta in enumerate(self.Angles):
            RotationMatrix = np.array( ( ( np.cos(theta), -np.sin(theta) ),
                                        ( np.sin(theta), np.cos(theta) ) ),
                                      np.float
                                      )
            #Pts = np.transpose(np.matrixmultiply(RotationMatrix, ArrowPoints))
            Pts = np.transpose(np.dot(RotationMatrix, ArrowPoints))
            self.Arrows[i] = Pts 
        return None


if __name__ == "__main__":

    speed = np.array((10.0, 12.0, 8.0, 14.0))
    theta = np.array((15.0, 45.0, 200, 270))# * (np.pi / 180) # in degrees -- is that right?
    time = np.arange(len(speed))
    time.shape = (-1,1)
    speed.shape = (-1,1)
    xy = np.concatenate((time,speed),1)

    print xy
    print theta

    ## Now plot it
    Fig = pylab.figure()
    ax = Fig.add_subplot(111)
    
#    VLC  = VectorLineCollection(xy, theta, Fig, ax)
#    ax.add_collection(VLC)
#    ax.plot(xy[:,0], xy[:,1], 'o')
#    ax.grid(True)
    
    ## with quiver:
    ax.quiver(time, np.zeros_like, theta, angles='array'headlength=0, headwidth=0, headaxislength=0)
    pylab.show()



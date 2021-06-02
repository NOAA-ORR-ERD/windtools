#!/usr/bin/env python

"""
some code to do a stick plot with MPL

This version uses matplotlib's quiver.

Author:
Christopher H. Barker
Chris.Barker@noaa.gov

This code is released into the Public Domain: do with it what you will.

"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import datetime

def reset_directions(directions, dir='from'):
    """
    changes the input directions to match quiver expectations,
    and switches from "from" to "to"
    """
    if dir == 'from':
        # reverse the direction, so it plots "to"
        print("reversing direction")
        directions = (directions + 90) * -1
    elif dir == 'to':
        # don't reverse, so it plots "to"
        directions = (directions - 90) * -1
    else:
        raise ValueError('dir has to be either "from" or "to"')
    return directions
    
def set_date_locator(xaxis):

    locator = mpl.dates.AutoDateLocator()
    xaxis.set_major_locator(locator)

    Formatter = mpl.dates.AutoDateFormatter(locator, tz=None)
    # edit the format strings to remove the TZ spec
    # this only works with my cutom version of AutoDateLocator
#    print Formatter.format_strings
#    Formatter.format_strings[1.0/24.0] = "%H:%M:%S"
#    Formatter.format_strings[1.0/(24*60)] = "%H:%M:%S"
#    Formatter.format_strings[1.0/(24*3600)] = "%H:%M:%S"
#    print Formatter.format_strings

 #   print Formatter.format_strings
                                                      
    xaxis.set_major_formatter(Formatter)

        
def stick(axes, times, speeds, directions, dir="from", ylabel=''):
    """
    Create a stick plot of the given data on the given axes.
   
    Stick plots are commonly used to display time series of
    a vector quantity at a point, such as wind or ocean current observations.
    
    Call signature::
        stick(axes, times, speeds, directions, dir='to', ylabel='')
   
    Arguments: 
       *axes*:  The axes object you want to plot on
       *times*: An array of datetime objects giving the time of the
                observations
       *speeds*: An array of the velocities of the observations
       *directions*: An array of the directions of the observations in
                     degrees from North, where North is up on the plot.
       *dir*:  either "from" or "to" (default "to")- specifies whether the
               direction data supplied is the direction _from which_ the wind
               (or whatever) is blowing (typical of wind data) or _to which_
               the current is moving (typical of currents). If dir is set to
               'from', the directions will be reversed to that the sticks point
                in the to direction. 
       *ylabel*:  A string with the ylabel of the observation (m/s, etc)
    
       *type*:   A string with the plot type -- either "stick" or "vector"
    """
    props = {'units' : "y",
             'width' : 0.001,
             'headwidth': 0,
             'headlength': 0,
             'headaxislength': 0,
             #'scale' : .1,
             }
    directions = reset_directions(directions, dir=dir)

    ##fixme: this could be smarter
    label_scale = np.floor(np.nanmax(speeds) / 10) * 10
    if label_scale == 0:
        label_scale = 5.0
    unit_label = "%3g %s"%(label_scale, ylabel)

    times = mpl.dates.date2num(times)
    y = np.zeros_like(speeds)
    v = np.zeros_like(directions)
    
    Q = axes.quiver(times, y, speeds, v, angles=directions.reshape((-1,1)), **props)
    axes.axhline(y=0, linewidth=1, color='r')
    print("quiverkey", label_scale)
    #axes.quiverkey(Q, X=0.1, Y=0.95, U=label_scale, label=unit_label, coordinates='axes', labelpos='S')

    axes.yaxis.set_major_locator(mpl.ticker.NullLocator())
    #locator = mpl.dates.AutoDateLocator()
    #axes.xaxis.set_major_locator(locator)
    #axes.xaxis.set_major_formatter(mpl.dates.AutoDateFormatter(locator))

def vector(axes, times, speeds, directions, dir="from", ylabel=''):
    """
    Create a "vector" plot of the given data on the given axes.
   
    A vector plot is a way to plot a time series of a vector quantity at a
    point, such as wind or ocean current observations. For antoher option,
    see "stick"
    
    Call signature::
        stick(axes, times, speed, direction, ylabel='m/s')
   
    Arguments: 
       *axes*:  The axes object you want to plot on
       *times*: An array of datetime objects giving the time of the
                observations
       *speeds*: An array of the velocities of the observations
       *directions*: An array of the directions of the observations (in
                     degrees from North, where North is up on the plot)
       *ylabel*:  A string with the ylabel of the observation
    
    """

    props = {'units' : "dots",
             'width' : 2,
             'headwidth': 2,
             'headlength': 4,
             'headaxislength': 4,
             'scale' : .05,
             }
    directions = reset_directions(directions, dir=dir)
    times = mpl.dates.date2num(times)

    dir_rad = directions / 180. * np.pi
    u = np.cos(dir_rad)
    v = np.sin(dir_rad)

    Q = axes.quiver(times, speeds, u, v, **props)
    axes.plot(times, speeds, '--')
    #axes.plot(times, speeds, 'o')

    set_date_locator(axes.xaxis)

    axes.set_ylabel(ylabel, rotation='horizontal')
    axes.set_ylim(ymin=0, ymax=speeds.max()*1.2)
    axes.grid('on')

if __name__ == '__main__':

    ## some sample data:
    directions = np.array([  0.0,  22.5,  45.0,  67.5,  90.0, 112.5, 135.0, 157.5,
                           180.0, 202.5, 225.0, 247.5, 270.0, 292.5, 315.0, 337.5],
                          dtype=np.float)
    speeds  = ( np.sin( np.linspace(0, 2*np.pi, len(directions)) ) + 1.5 ) * 6
    times = list(range(len(speeds)))
    #times = [datetime.datetime(2009, 5, 13, 0) + datetime.timedelta(hours=h*48) for h in times]
    times = [datetime.datetime(2009, 5, 13, 0) + datetime.timedelta(hours=h*2) for h in times]
    
    fig = plt.figure(1)
    fig.clear()

    ax1 = fig.add_subplot(2,1,1)
    stick(ax1, times, speeds, directions, ylabel='m/s', dir='from')

    ax2 = fig.add_subplot(2,1,2)
    vector(ax2, times, speeds, directions, ylabel='$m/s$', dir='from')
    fig.autofmt_xdate(bottom=0.18)

    ax1.set_xlim = ax2.get_xlim

    plt.draw()
    plt.show()


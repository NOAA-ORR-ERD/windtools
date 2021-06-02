#!/usr/bin/env python

"""
WindPlot filename

Simple plotter for any supported format. Generates a matplotlib window with a
stick plot and a vector plot

"""

Usage = """
WindPlot infilename 

Generates a matplotlib window with a stick plot and a vector plot

"""

import sys

import matplotlib as mpl
import matplotlib.pyplot as plt

from weathertools import MetData
from weathertools.Plotting import wind_plots
import importlib
importlib.reload(wind_plots)

try:
    infilename = sys.argv[1]
except IndexError:
    print(Usage)
    sys.exit()

print("Reading:", infilename)
Data = MetData.MetData(infilename)

times = Data.Times

data = Data[('WindSpeed', 'WindDirection')]
speeds = data[:,0]
directions = data[:,1]

for i in zip(times, directions):
    print(i)

units = Data.Units['WindSpeed']

print("Plotting:")

fig = plt.figure(1)
fig.clear()

ax = fig.add_subplot(2,1,1)
wind_plots.stick(ax, times, speeds, directions, ylabel=units)

#ax = fig.add_subplot(1,1,1)
ax = fig.add_subplot(2,1,2)
wind_plots.vector(ax, times, speeds, directions, ylabel=units)

fig.autofmt_xdate(bottom=0.18)

plt.draw()
plt.show()



#!/usr/bin/env python

"""
nose-based tests for WindRose code

"""
#
import nose
import numpy as np

import WindRose as WR

points4 = np.arange(0, 360, 90, dtype=np.float)
points8 = np.arange(0, 360, 45,  dtype=np.float)
points16 = np.arange(0, 360, 22.5, dtype=np.float)
points32 = np.arange(0, 360, 11.25, dtype=np.float)

def check_all_counted(data, spd_bins, num_dir_bins,):
    print "check_all_counted called"
    bins, spd_bins, dir_bins = WR.BinTheData(data, spd_bins, num_dir_bins)
    print "bins", bins
    print "bins.sum():",  bins.sum(), len(data)
    assert bins.sum() == len(data)

def check_all_same(data, spd_bins, num_dir_bins,):
    print "check_all_same called"
    bins, spd_bins, dir_bins = WR.BinTheData(data, spd_bins, num_dir_bins)  
    print "bins[0]:", bins[0]
    print "dir_bins", dir_bins
    print num_dir_bins
    assert np.alltrue(bins[0] == (len(data)/num_dir_bins))

def test_all_counted():
    for dir_data in (points4, points8, points16, points32, ):
        data = np.array([(sp, dir) for sp in (0, 5, 10) for dir in dir_data], dtype=np.float)
        for num_bins in (4, 8, 16):
            spd_bins = (5, 10, 15, 20)
            yield check_all_counted, data, spd_bins, num_bins 

def test_all_same():
    for dir_data in (points4, points8):
        data = np.array([(sp, dir) for sp in (5,) for dir in dir_data], dtype=np.float)
        for num_bins in (4, ):
            spd_bins = (0,10)
            yield check_all_same, data, spd_bins, num_bins
    for dir_data in (points16, points32):
        data = np.array([(sp, dir) for sp in (5,) for dir in dir_data], dtype=np.float)
        for num_bins in (4, 8, 16):
            spd_bins = ( 6, 12)
            yield check_all_same, data, spd_bins, num_bins
            
            
            
            
            
            
            
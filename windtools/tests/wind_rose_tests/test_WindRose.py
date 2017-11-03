#!/usr/bin/env python

"""
nose-based tests for WindRose code

"""
#
import nose
#import numpy as np
#
#import WindRose as WR
#
#points4 = np.arange(0, 360, 90, dtype=np.float)
#points8 = np.arange(0, 360, 45,  dtype=np.float)
#points16 = np.arange(0, 360, 22.5, dtype=np.float)
#points32 = np.arange(0, 360, 11.25, dtype=np.float)
#
#def test_dir_bin(dirs, num_dir_bins):
#    data = np.array([(sp, dir) for sp in (5,) for dir in dirs], dtype=np.float)
#    spd_bins = (0,10)
#    bins, spd_bins, dir_bins = WR.BinTheData(data, spd_bins, num_dir_bins)  
#    assert bins.sum() == len(dirs)
#    assert np.alltrue(bins == (len(dirs)/len()
#
#test_dir_bin(points4)

def test_evens():
    for i in range(0, 5):
        yield check_even, i, i*3

def check_even(n, nn):
    assert n % 2 == 0 or nn % 2 == 0

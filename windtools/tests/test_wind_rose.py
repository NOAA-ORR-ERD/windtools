#!/usr/bin/env python

"""
WindRose.py

Assorted functions for testing WindRose

"""

import numpy as np

from windtools import wind_rose
from windtools import WindRose


# sample data:

# evenly distributed data
# points = np.random.normal(loc=180, scale = 60, size=(100,) )
# points %= 360
# data = np.array([(sp, dir) for sp in (1, 3, 4, 5, 6, 7, 12, 17, 25) for dir in points], dtype=np.float)

bins = [3, 5, 10, 15, 25, 35]

# normal data:
n = 1000
dirs = np.random.normal(loc=180, scale = 60, size=(n,) )
spds = np.random.normal(loc=10, scale = 6, size=(n,) )
# spds_norm = np.where((spds_norm<0), 0, spds_norm)
np.clip(spds, 0, np.inf, spds)
data_norm = np.c_[spds, dirs]
print data_norm

# sample data:
# one in each bin
spds_one = [2, 7, 12, 20]
bins_one = [5, 10, 15]
dirs_one = [0, 90, 180, 270]
data_one = np.array([(s,d) for s in spds_one for d in dirs_one], dtype=np.float64)


def test_one_in_each():
    binned_data = wind_rose.BuildStatTable(data_one, bins_one, num_dir_bins=4)
    assert np.all(binned_data == (1.0 / len(binned_data.flat) * 100))


def test_add_to_100percent():
    binned_data = wind_rose.BuildStatTable(data_norm, bins, num_dir_bins=16)
    print binned_data
    print repr(binned_data.sum())
    assert round(binned_data.sum(), 10)  == 100.0


def test_missing_data():
    data = data_norm[:100].copy()
    # put in some NaNs:
    data[[3, 5, 9, 10], 0] = np.nan
    data[[13, 15, 32, 56], 1] = np.nan
    binned_data = wind_rose.BuildStatTable(data_norm, bins, num_dir_bins=4)
    print binned_data
    print binned_data.sum()
    assert round(binned_data.sum(), 10) == 100.0


def test_dir_avg():
    avg = wind_rose.BuildDirAverages(data_one, num_dir_bins=4)
    assert np.allclose(avg, [10.25, 10.25, 10.25, 10.25])


def test_dir_nan():
    data = data_one.copy()
    data[2, 1] = np.nan
    data[3, 0] = np.nan
    avg = wind_rose.BuildDirAverages(data, num_dir_bins=4)
    assert np.allclose(avg, [13.0, 10.25, 10.25, 13.0])

#!/usr/bin/env python

"""
Tests of MetData functionality aside from reading
"""
import datetime
import numpy as np
import pytest

from windtools import MetData, MetDataError

# fixme -- I should probably load something from a file for this...
DummyData = MetData(TimeZone='PST',
                             Name='A test data set',
                             LatLong=(34.12, -119.32),
                             Fields={"WindSpeed": 0,
                                     "WaterTemp": 1,
                                     "WindDirection": 2,
                                     },
                            Units={"WindSpeed": "knots",   # most often?
                                   "WindDirection": "degrees",
                                   "WaterTemp": "C"
                                   },
                            DataArray = np.array([[14, 17.2, 310],
                                                  [18, 16.2, 300],
                                                  [16, 17.3, 290],
                                                  [18, 18.2, 280],
                                                  [16, 14.6, 260],
                                                  [12, 12.1, 250],
                                                  [18, 12.2, 270],
                                                  [24, 13.2, 300],
                                                  [24, 13.3, 290],
                                                  [22, 15.1, 315],
                                                  [22, 10.4, 315],
                                                  [20,  9.2, 315],
                                                  [20,  9.1, 315],
                                                  [20, 10.2, 315],
                                                  [15, 11.3, 340],
                                                  [15, 12.2, 340],
                                                  [15, 13.4, 340],
                                                  [12, 14.5, 340]],
                                                 dtype=np.float64),
                            Times = [datetime.datetime(*dt) for dt in [(2004, 1, 5, 4, 0),
                                                                       (2004, 1, 6, 5, 0),
                                                                       (2004, 2, 6, 4, 0),
                                                                       (2004, 2, 7, 4, 0),
                                                                       (2004, 3, 5, 4, 0),
                                                                       (2004, 3, 5, 6, 0),
                                                                       (2004, 4, 5, 4, 0),
                                                                       (2004, 4, 5, 5, 0),
                                                                       (2004, 5, 5, 1, 0),
                                                                       (2004, 5, 5, 4, 0),
                                                                       (2004, 6, 5, 4, 0),
                                                                       (2004, 7, 5, 4, 0),
                                                                       (2004, 8, 5, 4, 0),
                                                                       (2004, 9, 5, 4, 0),
                                                                       (2004, 10, 5, 4, 0),
                                                                       (2004, 11, 5, 4, 0),
                                                                       (2004, 12, 5, 4, 0),
                                                                       (2004, 12, 5, 4, 0),]
                                     ],
                            )


def test_check():
    assert DummyData.CheckData()


def test_wrong_length():
    MD = DummyData.Copy()
    del MD.Times[-1]
    with pytest.raises(MetDataError):
        MD.CheckData()


def test_out_of_order():
    MD = DummyData.Copy()
    t = MD.Times[2:0:-1]
    MD.Times[:2] = t
    with pytest.raises(MetDataError):
        MD.CheckData()


def test_months():
    a = DummyData.GetFieldsMonthlyAsArray((2, 5), ("WindSpeed", "WaterTemp"), )
    print(a)
    assert np.array_equal(a, [[16., 17.3],
                              [18., 18.2],
                              [24., 13.3],
                              [22., 15.1],
                              ])


def test_months2():
    a = DummyData.GetFieldsMonthlyAsArray((11,), ("WindSpeed", "WindDirection"), )
    print(a)
    assert np.array_equal(a, [[15, 340],
                              ])

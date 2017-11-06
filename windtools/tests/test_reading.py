#!/usr/bin/env python

"""
tests mostly of metdata reading
"""

import os
import numpy as np
# import datetime
from datetime import datetime as dt

# import unittest
import pytest

from windtools import MetData, NoFileTypeMatchError

TestDataDir = os.path.join(os.path.split(__file__)[0], "data")


class Undefined:  # it's a singleton, it could be anything!
    pass


# placeholder!
def assert_equal(a, b):
    assert a == b


class ReaderTester:
    """
    a base class for a set of tests on a file reader
    """
    filename = Undefined
    start_time = Undefined
    end_time = Undefined
    time_zone = Undefined
    name = Undefined
    lat_long = Undefined
    fields = Undefined
    units = Undefined
    sample_data = Undefined

    # def __init__(self):
    #     print "\n TESTING:", self.filename
    #     if self.filename is Undefined:
    #         raise nose.SkipTest
    #     self.MD = MetData(os.path.join(TestDataDir, self.filename))


    def test_start_time(self):
        ## fixme: could I use a decorator to do this?
        #print "Times", self.MD.Times
        #if self.start_time is Undefined:
        #    raise nose.SkipTest
        assert_equal(self.MD.Times[0], self.start_time)

    def test_end_time(self):
        if self.end_time is not Undefined:
            assert_equal(self.MD.Times[-1], self.end_time)

    def test_fields(self):
        if self.fields is not Undefined:
            assert_equal(set(self.MD.Fields.keys()), set(self.fields))

    def test_units(self):
        if self.units is not Undefined:
            for key, value in self.units.items():
                assert_equal(self.MD.Units[key], value)

    def test_time_zone(self):
        if self.time_zone is not Undefined:
            assert_equal(self.MD.TimeZone, self.time_zone)

    def test_name(self):
        if self.name is not Undefined:
            assert_equal(self.MD.Name, self.name)

    def test_lat_long(self):
        if self.lat_long is not Undefined:
            assert_equal(self.MD.LatLong, self.lat_long)

# The specific readers:

#class Test_Dummy(ReaderTester):
#    """
#    Class with nothing defined, to test if the test skipping is working
#    """
#    pass

class Test_RawPorts(ReaderTester):
    filename = "RawPortsSample.txt"
    MD = MetData(os.path.join(TestDataDir, filename))
    start_time = dt(2006, 4, 24, 1)
    end_time = dt(2006, 4, 25, 15)
    time_zone = 'UTC'
    name = ''
    lat_long = (None, None)
    fields = ['AirTemp',
              'PredictedWaterLevel',
              'AirPressure',
              'WindGusts',
              'ObservedWaterLevel',
              'WindSpeed',
              'WaterTemp',
              'Salinity',
              'WindDirection',
              'SpecificGravity']

    units = {'AirTemp': 'degreesF',
             'PredictedWaterLevel': 'feet',
             'AirPressure': 'millibars',
             'WindGusts': 'knots',
             'ObservedWaterLevel': 'feet',
             'WindSpeed': 'knots',
             'WaterTemp': 'degreesF',
             'Salinity': 'PSU',
             'WindDirection': 'degrees',
             'SpecificGravity': 'SG'}


class Test_RawPorts_html(Test_RawPorts):
    filename = "RawPortsSample.html"
    MD = MetData(os.path.join(TestDataDir, filename))

class Test_NDBC_Historical(ReaderTester):
    filename = "42035h2000-sept.txt"
    MD = MetData(os.path.join(TestDataDir, filename))
    start_time = dt(2000, 9, 1, 00)
    end_time = dt(2000, 10, 27, 07)
    time_zone = 'UTC'
    name = '42035h2000-sept'
    lat_long = (None, None)
    fields = ['AirTemp',
              'DominantWavePeriod',
              'WindGusts',
              'WaveHeight',
              'WindDirection',
              'AverageWavePeriod',
              'WindSpeed',
              'Visibility',
              'AirPressure',
              'MeanWaveDirection',
              'WaterTemp',
              'DewPoint',
              'TideHeight',
              'AirTemp',
              'Year',
              'Month',
              'Hour',
              'Day',
              ]

    units = {'AirTemp': 'degreesC',
             'AirPressure': 'hPa',
             'DewPoint': 'degreesC',
             'WindGusts': 'm/s',
             'WindSpeed': 'm/s',
             'WaterTemp': 'degreesC',
             'WindDirection': 'degrees',
             'DominantWavePeriod': 'seconds',
             'WaveHeight': 'meters',
             'AverageWavePeriod': 'seconds',
             'MeanWaveDirection': 'degrees',
             'Visibility': 'nauticalmiles',
             'TideHeight': 'feet',
             }

class Test_NDBC_RealTime(ReaderTester):
    filename = "46086_5day.txt"
    MD = MetData(os.path.join(TestDataDir, filename))

    start_time = dt(2007, 8, 18, 17, 50)
    end_time = dt(2007, 8, 23, 16, 50)
    time_zone = 'UTC'
    name = '46086_5day'
    lat_long = (None, None)
    fields = ['AirTemp',
               'DominantWavePeriod',
               'Hour',
               'WindGusts',
               'WaveHeight',
               'WindDirection',
               'AverageWavePeriod',
               'WindSpeed',
               'Visibility',
               'Month',
               'AirPressure',
               'MeanWaveDirection',
               'Year',
               'WaterTemp',
               'PressureTendency',
               'DewPoint',
               'Day',
               'Minute',
               'TideHeight',
              ]

    units = {'AirTemp': 'degreesC',
             'AirPressure': 'hPa',
             'DewPoint': 'degreesC',
             'WindGusts': 'm/s',
             'WindSpeed': 'm/s',
             'WaterTemp': 'degreesC',
             'WindDirection': 'degrees',
             'DominantWavePeriod': 'seconds',
             'WaveHeight': 'meters',
             'AverageWavePeriod': 'seconds',
             'MeanWaveDirection': 'degrees',
             'Visibility': 'nauticalmiles',
             'TideHeight': 'feet',
             }

class Test_NDBC_ContinuousWind(ReaderTester):
    filename = "46047_5day.cwind"
    MD = MetData(os.path.join(TestDataDir, filename))
    start_time = dt(2007, 8, 23, 14, 0)
    end_time = dt(2007, 8, 23, 16, 50)
    time_zone = 'UTC'
    name = '46047_5day'
    lat_long = (None, None)
    fields = ['Hour',
              'WindGusts',
              'WindGustDirection',
              'Month',
              'WindSpeed',
              'Year',
              'WindGustTime',
              'WindDirection',
              'Day',
              'Minute',
              ]


    units = {'WindGusts': 'm/s',
             'WindSpeed': 'm/s',
             'WindDirection': 'degrees',
             'WindGustDirection':'degrees',
             'WindGustTime': None
             }

class Test_NDBC_RealTime_Missing_Dir(ReaderTester):
    filename = "NDBC_with_MM_dir.txt"
    MD = MetData(os.path.join(TestDataDir, filename))
    start_time = dt(2014, 7, 31, 15, 35)
    end_time = dt(2014, 7, 31, 21, 35)
    # time_zone = 'UTC'
    # name = '46086_5day'
    # lat_long = (None, None)
    # fields = ['AirTemp',
    #            'DominantWavePeriod',
    #            'Hour',
    #            'WindGusts',
    #            'WaveHeight',
    #            'WindDirection',
    #            'AverageWavePeriod',
    #            'WindSpeed',
    #            'Visibility',
    #            'Month',
    #            'AirPressure',
    #            'MeanWaveDirection',
    #            'Year',
    #            'WaterTemp',
    #            'PressureTendency',
    #            'DewPoint',
    #            'Day',
    #            'Minute',
    #            'TideHeight',
    #           ]

    # units = {'AirTemp': 'degreesC',
    #          'AirPressure': 'hPa',
    #          'DewPoint': 'degreesC',
    #          'WindGusts': 'm/s',
    #          'WindSpeed': 'm/s',
    #          'WaterTemp': 'degreesC',
    #          'WindDirection': 'degrees',
    #          'DominantWavePeriod': 'seconds',
    #          'WaveHeight': 'meters',
    #          'AverageWavePeriod': 'seconds',
    #          'MeanWaveDirection': 'degrees',
    #          'Visibility': 'nauticalmiles',
    #          'TideHeight': 'feet',
    #          }
    def test_missing_wind_dir(self):
        print self.MD.GetFieldsAsArray(['WindDirection', 'WindSpeed'])
        wind = self.MD.GetFieldsAsArray(['WindDirection', 'WindSpeed'])
        # make sure NaNs are in the right place:
        assert np.isnan(wind[3, 0])
        assert np.isnan(wind[12, 0])
        assert np.isnan(wind[13, 0])
        assert np.isnan(wind[14, 0])
        assert np.isnan(wind[15, 0])
        assert np.isnan(wind[16, 0])
        assert np.isnan(wind[18, 0])


class Test_NCDC_LCD(ReaderTester):
    filename = "NCDC-LCD.txt"
    MD = MetData(os.path.join(TestDataDir, filename))
    start_time = dt(2008, 10, 1, 0, 15)
    end_time = dt(2008, 10, 27, 3, 56)
    time_zone = 'LST'  # is that correct??
    name = 'GROTON-NEW LONDON AIRPORT (14707)'
    lat_long = (41.328, -72.049)
    fields = ['AirTemp',  # that's all it reads now!
              'WindSpeed',
              'WindDirection',
              ]
    units = {'AirTemp': 'celsius',
             'WindSpeed': 'mph',
             'WindDirection': 'degrees',
             }


class Test_NGDCXX(ReaderTester):
    filename = "NGDC_test.txt"
    MD = MetData(os.path.join(TestDataDir, filename))
    start_time = dt(1974, 9, 24, 0, 0)
    end_time = dt(1974, 10, 16, 6, 0)
    time_zone = 'UTC'  # is that correct??
    name = 'USAF: 488260, NCDC WBAN NUMBER: 99999'
    lat_long = (None, None)
    fields = ['AirTemp',  # that's all it reads now!
              'WindSpeed',
              'WindDirection',
              'WindGusts'
              ]

    units = {'AirTemp': 'degreesF',
             'WindSpeed': 'mph',
             'WindDirection': 'degrees',
             'WindGusts': 'mph',
             }


# a few tests of files that shouldn't be read
def test_BrokenPorts():
    filename = "DummyFile.txt"
    with pytest.raises(NoFileTypeMatchError):
        MetData(os.path.join(TestDataDir, filename))


##These are the test files that should work!
#TestFiles = [["RawPorts" , "RawPortsSample.txt"],
#             ["RawPorts" , "RawPortsSample.html"],
#             ["Dummy" , "DummyFile.txt"],
#             ["NDBC-Historical", "42035h2000-sept.txt"],
#             ["NDBC-Real-Time", "46086_5day.txt"],
#             ["NDBC-Continuous-Wind", "46047_5day.cwind"],
#             ["NCDC_LCD", "NCDC-LCD.txt"],
#             ["NGDCXX", "NGDC_test.txt"],
#             ]
#
#for file in TestFiles:
#    file[1] = os.path.join(TestDataDir, file[1])
#    #print file
#
#
##create instance of the Readers
#RawPortsReader = MetData.RawPortsReaderClass()
#NDBCReader = MetData.NDBCReaderClass()
### A list of all the available met file readers.
#FileReaders = [RawPortsReader, NDBCReader]
#
## fixme -- is any of this working????
#class TestTypeDetector(unittest.TestCase):
#
#    def testDetector(self):
#        self.assertRaises(MetData.NoFileTypeMatchError,
#                          MetData,
#                          os.path.join(TestDataDir, "DummyFile.txt")
#                         )
#
#class TestReaders(unittest.TestCase):
#
#    def testTypeCheck(self):
#        for TestFile in TestFiles:
#            print "Testing:", TestFile[1]
#            for Reader in FileReaders:
#                if Reader.Type == TestFile[0]:
#                    # It should return True
#                    self.failUnless(Reader.IsType(TestFile[1]),
#                        "%s did not recognise the file: %s"%(Reader.Type,  TestFile[1])
#                       )
#                else:
#                    self.failIf(Reader.IsType(TestFile[1]),
#                        "%s thinks %s is its type."%(Reader.Type,  TestFile[1])
#                       )
#
#class TestRawPorts(unittest.TestCase):
#    Reader = MetData.RawPortsReaderClass()
#
###    I don't know why this is failing -- it should be fixed
###    def testNoStation(self):
###        self.assertRaises(MetData.BadFileTypeError,
###                          self.Reader.LoadData,
###                          os.path.join(TestDataDir, "NoStationLine.txt"))
#
#    def testWrongHeader(self):
#        self.assertRaises(MetData.BadFileTypeError,
#                          self.Reader.LoadData,
#                          os.path.join(TestDataDir, "BadHeader.txt"))
#
#    ##fixme: these need more tests!
#    def testRead(self):
#        self.Reader.LoadData(os.path.join(TestDataDir,"RawPortsSample.txt"))
#        self.assertEquals(self.Reader.DataArray.shape, (381, 10))
#
#class TestNDBCHistorical(unittest.TestCase):
#    Reader = MetData.NDBCReaderClass()
#    Reader.LoadData(os.path.join(TestDataDir,"42035h2000-sept.txt"))
###    def testWrongHeader(self):
###        self.assertRaises(MetData.BadFileTypeError,
###                          self.Reader.LoadData,
###                          os.path.join(TestDataDir, "BadHeader.txt"))
#
#    #fixme: this needs more tests!
#    def testRead1(self):
#        self.assertEquals(self.Reader.DataArray.shape, (1352, 13))
#
#
###["NDBC-Real-Time", "46086_5day.txt"]
#class TestNDBC_RT_Reader(unittest.TestCase):
#
#    Reader = MetData.NDBC_RT_ReaderClass()
#    Reader.LoadData(os.path.join(TestDataDir,"46086_5day.txt"))
#
#    #fixme: this needs more tests!
#    def testRead1(self):
#        self.assertEquals(self.Reader.DataArray.shape, (120, 14))
#
#    def testRead2(self):
#        a = np.array([240., 2., 3., 1.3, 10., np.nan, np.nan, 1008.1, 16.8, 20.4, np.nan, np.nan, -0.5, np.nan])
#        b =  self.Reader.DataArray[-5]
#        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
### ["NDBC-Continuous-Wind", "46047_5day.cwind"]
##class TestNDBC_Cont_Wind_Reader(unittest.TestCase):
##
##    Reader = MetData.NDBC_Cont_Wind_ReaderClass()
##    Reader.LoadData(os.path.join(TestDataDir,"46047_5day.cwind"))
##
##    #fixme: this needs more tests!
##    def testRead1(self):
##        print  self.Reader.DataArray.shape
##        self.assertEquals(self.Reader.DataArray.shape, (18, 4))
##
##    def testRead2(self):
##        a = np.array([326, 6.6, np.nan, np.nan])
##        b =  self.Reader.DataArray[2]
##        print b
##        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
#class TestNCDC_LCD_Reader(unittest.TestCase):
#
#    Filename = os.path.join(TestDataDir,"NCDC-LCD.txt")
#    Reader = MetData.NCDC_LCD_ReaderClass()
#    Reader.LoadData(Filename)
#
#    def testIsType(self):
#        self.assertTrue(self.Reader.IsType(self.Filename))
#
#    def testRead1(self):
#        self.assertEquals(self.Reader.DataArray.shape, (752, 3))
#
#    def testRead2(self):
#        a = np.array([7.0, 210.0, 17.2])
#        b =  self.Reader.DataArray[2]
#        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
#    def testRead3(self):
#        a = np.array([7.0, np.nan, 13.3])
#        b =  self.Reader.DataArray[180]
#        print b
#        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
#    def testRead4(self):
#        self.assertTrue(self.Reader.TimeZone == "LST")
#
#    def testRead4(self):
#        self.assertTrue(self.Reader.LatLong == (41.328, -72.049))
#
#    def testRead5(self):
#        self.assertTrue(self.Reader.Times[0] == datetime.datetime(2008, 10, 1, 0, 15))
#
#    def testRead5(self):
#        self.assertTrue(self.Reader.Times[-1] == datetime.datetime(2008, 10, 27, 3, 56))
#
#class TestNGDC_Reader(unittest.TestCase):
#
#    Filename = os.path.join(TestDataDir,"NGDC_test.txt")
#    Reader = MetData.NGDC_ReaderClass()
#    Reader.LoadData(Filename)
#
#    def testIsType(self):
#        self.assertTrue(self.Reader.IsType(self.Filename))
#
#    def testRead1(self):
#        self.assertEquals(self.Reader.DataArray.shape, (99, 4))
#
#    def testRead2(self):
#        a = np.array([70, 3, np.nan, 81])
#        b =  self.Reader.DataArray[2]
#        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
#    def testRead3(self):
#        a = np.array([20, 2, np.nan, 84])
#        b =  self.Reader.DataArray[-1]
#        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
#    def testRead4(self):
#        self.assertTrue(self.Reader.TimeZone == "UTC")
#
#    def testRead4(self):
#        self.assertTrue(self.Reader.LatLong == (None, None))
#
#    def testRead5(self):
#        self.assertTrue(self.Reader.Times[0] == datetime.datetime(1974, 9, 24, 0, 0))
#
##    def testRead5(self):
##        self.assertTrue(self.Reader.Times[-1] == datetime.datetime(2008, 10, 27, 3, 56))
#
#class TestOSSM_Hyd_Reader(unittest.TestCase):
#
#    Filename = os.path.join(TestDataDir,"OSSM_Hydr.osm")
#    Reader = MetData.OSSM_Hyd_Reader()
#    Reader.LoadData(Filename)
#
#    def testIsType(self):
#        self.assertTrue(self.Reader.IsType(self.Filename))
#
#    def testName(self):
#        self.assertTrue(self.Reader.Name == "HILLSBOURGH STATION")
#
#    def testArraySize(self):
#        self.assertEquals(self.Reader.DataArray.shape, (10, 1))
#
#    def testRead3(self):
#        a = np.array((177.0,))
#        b =  self.Reader.DataArray[-1]
#        self.assertTrue(np.alltrue(a[~np.isnan(a)] == b[~np.isnan(b)]))
#
#    def testRead4(self):
#        print "lat-long:", self.Reader.LatLong
#        self.assertTrue(self.Reader.LatLong == (28.029534,-82.688080))
#
#    def testRead5(self):
#        self.assertTrue(self.Reader.Times[0] == datetime.datetime(2002, 10, 01, 0, 0))
#
#
#if __name__ == "__main__":
#    unittest.main()


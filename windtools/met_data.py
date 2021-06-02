#!/usr/bin/env python

"""
This needs a lot of re-factoring!!!

What is a MetData object, vs a DataReader Object???

A module that provides classes for handling various met data formats

Standard Field names used so far:
 "PredictedWaterLevel"
 "ObservedWaterLevel"
 "WindSpeed"
 "WindDirection"
 "WindGusts"
 "WindGustDirection"
 "WindGustTime"
 "AirTemp"
 "WaterTemp"
 "Salinity"
 "AirPressure"
 "PressureTendency"
 "WaveHeight" : Significant Wave Height
 "DominantWavePeriod"
 "AverageWavePeriod"
 "MeanWaveDirection"
 "DewPoint"
 "Visibility"
 "TideHeight"
 "Unknown" : if it's not clear -- there should be a way to reset this...
 "BAR" : Used on NDBC data -- don't know what it means (atm. pressure?)


"""
import os
import datetime
import copy

import numpy as np

import unit_conversion as UC

## Special Exceptions:
class MetDataError(Exception):
    pass

class NoFileTypeMatchError(MetDataError):
    pass

class MultipleFileTypeMatchError(MetDataError):
    def __init__(self, TypeList):
        self.TypeList = TypeList
    pass

class BadFileTypeError(MetDataError):
    pass

class MetData:
    """
    A class that holds various met data

    After Loading the data, it will have a DataArray attribute that is a
    numpy array of Floats (doubles). Missing values are replaced by NaN.

    fixme: Use masked arrays instead?

    """

    def __init__(self,
                 FileName=None,
                 FileReader=None,
                 DataArray=None,
                 Fields=None,
                 Units=None,
                 Times=None,
                 TimeZone=None,
                 Name=None,
                 LatLong=(None, None),
                 ):

        self.DataArray = DataArray
        self.Fields = Fields
        self.Units = Units
        self.Times = Times
        self.TimeZone = TimeZone
        self.Name = Name
        self.LatLong = LatLong

        if FileName is not None:
            self.FileName = FileName
            if FileReader is None:
                PossibleTypes = self.DetectFileType()
                if len(PossibleTypes) == 0:
                    raise NoFileTypeMatchError("%s does not match any of the known file types"%FileName)
                elif len(PossibleTypes) > 1:
                    print(PossibleTypes)
                    print([r.Type for r in PossibleTypes])
                    raise MultipleFileTypeMatchError([r.Type for r in PossibleTypes])
                else:
                    FileReader = PossibleTypes[0]
            #print 'Using filereader: ', FileReader
            self.FileReader = FileReader
            self.LoadData()

    def __getitem__(self, index):
       if ( type(index) == type("") or type(index) == type("") ):
           index = (index,)
       return self.GetFieldsAsArray(index)

    def DetectFileType(self):
        PossibleTypes = []

        for ReaderClass in FileReaderClasses:
            Reader = ReaderClass()
            if Reader.IsType(self.FileName):
                PossibleTypes.append(Reader)

        return PossibleTypes

    def LoadData(self):
        # fixme: Shouldn't this be handled with subclassing or something?
        # or reall, the FileReader should poopulate the MetDAta object..
        self.FileReader.LoadData(self.FileName)
        self.DataArray = self.FileReader.DataArray
        self.Fields = self.FileReader.Fields
        self.Units = self.FileReader.Units
        self.Times = self.FileReader.Times
        self.TimeZone = self.FileReader.TimeZone
        self.Name = self.FileReader.Name
        self.LatLong = self.FileReader.LatLong

    def ChangeTZ(self, shift, name):
        # fixme -- this should be smarter about timezones and their names
        self.TimeZone = name
        shift = datetime.timedelta(hours=shift)
        self.Times = [t - shift for t in self.Times]

    def ChangeUnits(self, shift, name):
        pass

    def TruncateTimeSeries(self, sdate=None, edate=None):
        if sdate is not None:
            sidx = [id for id,date in enumerate(self.Times) if date>=sdate][0]
        else:
            sidx = 0
        if edate is not None:
            eidx = [id for id,date in enumerate(self.Times) if date<=edate][0]
        else:
            eidx = len(self.Times)

        self.Times = self.Times[sidx:eidx]
        self.DataArray = self.DataArray[sidx:eidx,:]



    def SaveAsOSSMWind(self, filename, name=None, units='mps'):
        print("writing:", filename)
        SpeedUnits = self.Units["WindSpeed"]
        spd_idx = self.Fields["WindSpeed"]
        dir_idx = self.Fields["WindDirection"]
        data = self.DataArray[:, (spd_idx, dir_idx)]
        # write the file:
        outfile = open(filename, 'w', encoding='utf-8')
        outfile.write("%s\n"%self.Name)
        if self.LatLong[0] is not None and self.LatLong[1] is not None:
            print("writting lat-lon:", self.LatLong)
            outfile.write("%f, %f\n"%tuple(self.LatLong)) ## this needs to be fixed!
        else:
            outfile.write("\n")
        outfile.write("%s\n"%units)
        outfile.write("%s\n"%self.TimeZone)
        outfile.write("0,0,0,0,0,0,0,0\n")
        for t, (speed, dir) in zip(self.Times, data):
            if np.isnan(speed):
                continue
            if np.isnan(dir):
                if speed == 0.0: # we can still use it if speed is zero
                    dir = 0 # arbitrary
                else:
                    continue
            outfile.write("%i, %i, %i, %i, %i, "%(t.day, t.month, t.year, t.hour, t.minute) )
            # convert speed
            speed = UC.Convert("Velocity", SpeedUnits, units, speed)
            outfile.write("%.2f, %i\n"%(speed, dir))

    def SaveAsOSSMWave(self, filename, name=None, units='mps'):
        print("writing:", filename)
        SpeedUnits = self.Units["WindSpeed"]
        spd_idx = self.Fields["WaveHeight"]
        data = self.DataArray[:, (spd_idx, )]
        # write the file:
        outfile = open(filename, 'w', encoding='utf-8')
        outfile.write("%s\n" % self.Name)
        outfile.write("%f, %f\n" % self.LatLong)  # this needs to be fixed!

        outfile.write("%s\n" % units)
        outfile.write("%s\n" % self.TimeZone)
        outfile.write("0,0,0,0,0,0,0,0\n")
        for t, (speed) in zip(self.Times, data):
            if np.isnan(speed):
                continue
            outfile.write("%i, %i, %i, %i, %i, "%(t.day, t.month, t.year, t.hour, t.minute) )
            # convert speed
            speed = UC.Convert("Velocity", SpeedUnits, units, speed)
            outfile.write("%.2f\n"%(speed,))

    def GetFieldsAsArray(self, fields):
        """
        returns a numpy array with just the fields specified in fields
        """
        outdata = np.empty((self.DataArray.shape[0], len(fields)), dtype=np.float64)
        #fixme: this should be do-able with fancy indexing!
        for i, f in enumerate(fields):
            outdata[:,i] = self.DataArray[:,self.Fields[f]]
        return outdata

    def GetFieldsMonthlyAsArray(self, months, fields, ):
        """
        Returns a numpy array with just the fields specified in fields, and only for the months specified.

        months should be a sequence of month indexes, ie: (1,2) for January and February
        """
        field_ind = []
        for f in fields:
            field_ind.append(self.Fields[f])
        outdata = [] # don't know how big it will be yet.
        #fixme: this should be do-able with fancy indexing!
        for i, dt in enumerate(self.Times):
            if dt.month in months:
                outdata.append(self.DataArray[i,field_ind])
        return np.array(outdata, dtype=np.float64)

    def CheckData(self):
        """
        Does assorted data integrity checks
        """
        if len(self.Times) != self.DataArray.shape[0]:
            raise MetDataError("Length of Times list does not match size of DataArray")

        # check for dates in order:
        prev_time = self.Times[0]
        for i, time in enumerate(self.Times[1:]):
            if time - prev_time <= datetime.timedelta(0):
                raise MetDataError("Times are out of sequence at: %s" % time)
        return True

    def Copy(self):
        """
        returns a MetData object that is a copy of this one
        """
        # fixme: should this be the __copy__ or __deepcopy__ method?
        MD = MetData(DataArray=copy.copy(self.DataArray),
                     Fields=copy.copy(self.Fields),
                     Units=copy.copy(self.Units),
                     Times=copy.copy(self.Times),
                     TimeZone=copy.copy(self.TimeZone),
                     Name=copy.copy(self.Name),
                     LatLong=copy.copy(self.LatLong),
                     )
        return MD

    def merge(self, other):
        """
        adds the passed in data to this data set.

        # ToDo: make this the __iadd__ method!
        """
        # check the time periods of the two:
        start1 = self.Times[0]
        end1 = self.Times[-1]
        start2 = other.Times[0]
        end2 = other.Times[-1]

        if start1 < start2:
            first = self
            second = other
        else:
            first = other
            second = self

        # check for overlap:
        if second.Times[0] < first.Times[-1]:
            msg = ("cannot merge two overlapping datasets:\n"
                   "first is from {} to {}\n"
                   "second is from {} to {}\n".format(first.Times[0],
                                                      first.Times[-1],
                                                      second.Times[0],
                                                      second.Times[-1],
                                                      ))

            raise ValueError(msg)

        # check for matching fields:
        print("self fields:", self.Fields)
        print("other fields:", other.Fields)

        if first.Fields != second.Fields:
            print(list(first.Fields.keys()))
            print(list(second.Fields.keys()))
            raise ValueError("dataset Fields don't match")
        if first.TimeZone != second.TimeZone:
            raise ValueError("Timezone doesn't match")
        if first.Units != second.Units:
            raise ValueError("Units doesn't match")
        if first.LatLong != self.LatLong:
            raise ValueError("LatLong doesn't match")

        # Merge them:
        self.Times = first.Times + second.Times
        print(first.DataArray.shape)
        print(second.DataArray.shape)
        self.DataArray = np.concatenate((first.DataArray,
                                         second.DataArray))
        print(self.DataArray.shape)
        return None  # This is a mutating method -- so it returns None

    def __iadd__(self, other):
        self.merge(other)
        return self


class MetFileReader:
    """
    Base class for all Met File readers

    """
    def __init__(self):
        self.TimeZone = 'UTC' # this can be changed by individual reader, if need be
        self.Name = ""
        self.LatLong = (None, None)
        self.DataArray = None
        self.Times = None

class OSSM_ReaderClass(MetFileReader):
    """
    Class for reading data from OSSM format files.

    This is subclassed for the different types...

    The trick here is that OSSM format files often don't have any info about
    what the data is, or units, or...

    Not all that well tested!

    """

    Type = "OSSM"
    TimeZone = 'local' # is this usually the case?
    Fields = { "WindSpeed": 0,
               "WindDirection": 1,  # but not always!
               }
    Units = {"WindSpeed": "knots",   # most often?
             "WindDirection": "degrees",
             }

    def IsType(self, FileName):
        """
        How to do this???

        The data should be 7 comma separated values
        """
        ## I think the fifth line should be all zeros
        infile = open(FileName, 'r', encoding='utf-8')
        for i in range(4):
            infile.readline()
        line = infile.readline()

    def CheckDataLine(self, line):
        """
        Check if a line of data fits the OSSM format.
        """
        data = line.strip().split(',')
        # should be 7 fields
        if len(data) != 7:
            return False
        # first 5 should be integers
        try:
            list(map(int, data[:5]))
        except ValueError:
            return False
        # last two should be floats
        try:
            list(map(float, data[5:]))
        except ValueError:
            return False
        # fixme: Should I check data fields, etc?
        return True

    def CheckHeader(self, FileName, num_rows=0):
        """
        Checks if the Header is the right length
        Sixth row should be OSSM-style data, and first five should not be.
          NOTE:  are there other OOSM formats where that is true?
        """
        infile = open(FileName, 'r', encoding='utf-8')
        for i in range(num_rows):
            line = infile.readline()
            if self.CheckDataLine( line ):
                return False
        return self.CheckDataLine(infile.readline() )

    def ReadData(self, infile):
        """
        reads the actual data.

        infile should be an open text file, already at the top of the data
        """
        DataArray = []
        Times = []
        for line in infile:
            line = line.strip()
            if not line: continue
            data = line.split(",")
            if data:
                DataArray.append( (float(data[5]), float(data[6]) ) )
                #process date:
                dt = list(map(int, data[:5]))
                Times.append( datetime.datetime(dt[2],dt[1],dt[0],dt[3],dt[4]) )
        DataArray = np.array(DataArray, dtype=np.float64)
        self.DataArray = DataArray
        self.Times = Times

class OSSM_Raw_ReaderClass(OSSM_ReaderClass):
    """
    Reader for old-style OSSM wind files with no header at all
    """
    Type = "OSSM_Raw"
    TimeZone = None # should this be None?
    Fields = { "WindSpeed": 0,
               "WindDirection": 1,
               }
    Units = {"WindSpeed": "knots",   # most often? wuld it be better to put None?
             "WindDirection": "degrees",
             }


class OSSM_Wind_ReaderClass(OSSM_ReaderClass):
    Type = "OSSM_Wind"
    TimeZone = 'local' # is this usually the case?
    Fields = { "WindSpeed": 0,
               "WindDirection": 1,  # but not always!
               }
    Units = {"WindSpeed": "knots",   # most often?
             "WindDirection": "degrees",
             }

    def IsType(self, FileName):
        """
        Sixth row should be OSSM-style data, and first five should not be.
          NOTE:  are there other OOSM formats where that is true?
        """
        return self.CheckHeader(FileName, 5)

    def LoadData(self, FileName):
        infile = open(FileName, 'r', encoding='utf-8')

        # read the header
        self.Name = infile.readline().strip()
        # lat-long
        line = infile.readline().strip()
        if not line: #no lat-long line
            self.LatLong = (None, None)
        else:
            LatLong = [ float(i) for i in line.strip().split(',') ]
            if len(LatLong) == 4: # degrees-minutes form
                self.LatLong =  ( LatLong[0] + LatLong[1] / 60,
                                  LatLong[2] + LatLong[3] / 60
                                  )
            elif len(LatLong) == 2:
                self.LatLong = tuple(LatLong)
            else:
                raise ValueError( 'Lat-Lon line bad in header: "%s"'%line)
        # units
        self.Units["WindSpeed"] = infile.readline().strip()
        # time zone:
        self.TimeZone = infile.readline().strip()
        # skip the line of zeros:
        infile.readline()

        self.ReadData(infile)

class OSSM_Hyd_Reader(OSSM_ReaderClass):
    """
    Reader for the OSSM "Hydrology" format -- usually used for river flow data
    """
    Type = "OSSM_Hyd"
    TimeZone = None # No info in the file...
    Fields = { "Discharge": 0,
               }
    Units = {} # will be set from header

    def IsType(self, FileName):
        """
        Sixth row should be OSSM-style data, and first five should not be.
          NOTE:  are there other OOSM formats where that is true?
        """
        return self.CheckHeader(FileName, 3)

    def LoadData(self, FileName):
        infile = open(FileName, 'r', encoding='utf-8')

        # read the header
        self.Name = infile.readline().strip()
        line = infile.readline()
        self.LatLong = tuple( map(float, line.strip().split(',')) )
        self.Units["Discharge"] = infile.readline().strip()

        self.ReadData(infile)
        self.DataArray = self.DataArray[:, 0:1].copy() # remove the empty direction column


class NGDC_ReaderClass(MetFileReader):
    """
    class for reading data from NGDC:
    SURFACE HOURLY ABBREVIATED FORMAT

    This is a fixed field format, described in 3505doc.txt

    """
    Type = "NGDC"
    TimeZone = 'UTC'
    # This maps the fields to the column number in the data array
    # NOTE: there are a lot more....
    Fields = {"WindDirection": 0,
              "WindSpeed": 1,
              "WindGusts": 2,
              "AirTemp": 3,
              }

    #This maps the field names to units.
    Units = {"WindSpeed": "mph",
             "WindDirection": "degrees", # 990 is "variable", "***" is calm
             "WindGusts": "mph",
             "AirTemp": "degreesF",
             }

    ## These are all possible numbers indicating missing values!
    MissingValues = ("*","**", "***", "*****", "******")

    HeaderLine = 'USAF  WBAN YR--MODAHRMN DIR SPD GUS CLG SKC L M H  VSB WW WW WW W TEMP DEWP    SLP   ALT    STP MAX MIN PCP01 PCP06 PCP24 PCPXX SD'
    #HeaderLine = ['YR', 'JD', 'PW', 'OW', 'WS', 'WD', 'WG', 'AT', 'WT', 'SA', 'SG', 'TZ', 'AP', 'CD', 'T']

    def IsType(self, FileName):
        """
        Detects whether the given file is this type of met file

        I'm sure this could be much improved -- why not just use LoadData?

        """
        infile = open(FileName, 'r', encoding='utf-8')
        for i, line in enumerate(infile):
            if line.strip() == self.HeaderLine:
                return True
            if i > 4: #if it's not in the first 4 lines, it's probably not one of these.
                return False

    def LoadData(self, FileName):
        infile = open(FileName, 'r', encoding='utf-8')
        # skip the header
        infile.readline()
        ## load the data
        DataArray = []
        Times = []
        self.Name = ""
        for line in infile:
            if not self.Name:
                # pull the station number from the first data line
                # fixme: could there be multiple stations in one file?
                self.Name = "USAF: %s, NCDC WBAN NUMBER: %s"%(line[0:6], line[7:12])
            data = line[13:73].split()# only the first part -- all we're parsing

            #process date:
            dt = data[0]
            y  = int(dt[0:4])
            mo = int(dt[4:6])
            d  = int(dt[6:8])
            h  = int(dt[8:10])
            mi = int(dt[10:12])
            dt = datetime.datetime(y, mo, d, h, mi)

            #now the values:
            try:
                dir = float(data[1])
            except ValueError:
                dir = np.nan
            try:
                spd = float(data[2])
            except ValueError:
                spd = np.nan
            try:
                gust = float(data[3])
            except ValueError:
                gust = np.nan
            try:
                temp = float(data[14])
            except ValueError:
                spd = np.nan
            Times.append(dt)
            DataArray.append((dir, spd, gust, temp))
        DataArray = np.array(DataArray)

        self.DataArray = DataArray
        self.Times = Times


class RawPortsReaderClass(MetFileReader):
    """
    Class for reading data from the raw real time PORTS data
    """
    Type = "RawPorts"

    #This maps the fields to the column number in the data array
    Fields = {"PredictedWaterLevel": 0,
              "ObservedWaterLevel" : 1,
              "WindSpeed": 2,
              "WindDirection": 3,
              "WindGusts": 4,
              "AirTemp": 5,
              "WaterTemp": 6,
              "Salinity": 7,
              "SpecificGravity": 8,
              "AirPressure": 9,
              }

    #This maps the field names to units.
    Units = {"PredictedWaterLevel": "feet",
             "ObservedWaterLevel": "feet",
             "WindSpeed": "knots",
             "WindDirection": "degrees",
             "WindGusts": "knots",
             "AirTemp": "degreesF",
             "WaterTemp":"degreesF",
             "Salinity": "PSU", # Practical Salinity Units
             "SpecificGravity": "SG",
             "AirPressure": "millibars",
             }

    ## These are all possible numbers indicating missing values!
    MissingValues = (99.99, -999, -999.900, -999.99 )

    HeaderLine = ['YR', 'JD', 'PW', 'OW', 'WS', 'WD', 'WG', 'AT', 'WT', 'SA', 'SG', 'TZ', 'AP', 'CD', 'T']

    def IsType(self, FileName):
        """
        Detects whether the given file is this type of met file

        I'm sure this could be much improved -- why not just use LoadData and see if you get an exception?

        """
        Yes = 0
        infile = open(FileName, 'r', encoding='utf-8')
        for i, line in enumerate(infile):
            if line.split() == self.HeaderLine:
                return True
            if i > 40:
                return False

    def LoadData(self, FileName):
        self.StationName = None
        print("loading:", FileName)
        infile = open(FileName, 'r', encoding='utf-8')
        # look for the Header
        for i in range(40):
            line = infile.readline()
            if not line:
                break
            if "STATION NAME" in line:
                self.StationName = line.split(':')[1].strip()
                print(infile.readline())
                break
        if self.StationName is None:
            raise BadFileTypeError("This does not appear to be a %s file\n It does not have a 'STATION NAME' line"%self.Type)

        line = infile.readline()
        if line.split() != self.HeaderLine:
            raise BadFileTypeError("This does not appear to be a %s file\nIt does not have the right Header line after the 'STATION NAME'"%self.Type)
        infile.readline()
        infile.readline()

        ## load the data
        DataArray = []
        Times = []
        for line in infile:
            if not line:
                break
            line = line.strip().split()
            if not line:
                break
            values = line[2:11]
            TZ = line[11]
            values.append(line[12])
            mo, d, y = line[13].split('/')
            h, mi, s = line[14].split(':')
            dt = datetime.datetime(*[int(x) for x in (y, mo, d, h, mi, s)])
            values = [float(v) for v in values]
            # print dt, values[:4]
            Times.append(dt)
            DataArray.append(values)
        DataArray = np.array(DataArray)

        ## Replace the missing values with NaN:
        for val in self.MissingValues:
            DataArray[DataArray == val] =  np.NaN

        self.DataArray = DataArray
        self.Times = Times


class NDBCReaderClass(MetFileReader):
    """
    Class for reading data from the NDBC historical archives or Real time data

    Amy 11/09: Included year,month,day,hour,min column in field mapping -- since there are so many variations

    """
    ##fixme -- this is going to have to be much smarter -- reading the header to figure out what fields are there. ARRGG!!
    ## Amy 11/09 made it a litte bit smarter -- it handles all NDBC archives formats, real-time and continuous winds formats

    Type = "NDBC"

    # this maps the short versions in the header with the longer ones:
    FieldNames = { "YY": "Year",
                   "YYYY": "Year",
                   "#YY":  "Year",
                   "MM": "Month",
                   "DD": "Day",
                   "hh": "Hour",
                   "mm":  "Minute",
                   "WDIR": "WindDirection",
                   "WD":  "WindDirection",
                   "WSPD": "WindSpeed",
                   "GST": "WindGusts",
                   "GDR": "WindGustDirection",
                   "GTIME": "WindGustTime",
                   "WVHT": "WaveHeight",
                   "DPD": "DominantWavePeriod",
                   "APD": "AverageWavePeriod",
                   "MWD": "MeanWaveDirection",
                   "BAR":  "AirPressure",
                   "PRES": "AirPressure",
                   "ATMP": "AirTemp",
                   "WTMP": "WaterTemp",
                   "DEWP": "DewPoint",
                   "VIS": "Visibility",
                   "TIDE": "TideHeight",
                   "PTDY": "PressureTendency",
                   }

    #This maps the field names to units.
    Units = {"WindDirection":"degrees",
             "WindSpeed": "m/s",
             "WindGusts": "m/s",
             "WindGustDirection":"degrees",
             "WindGustTime": None,
             "WaveHeight": "meters",
             "DominantWavePeriod": "seconds",
             "AverageWavePeriod": "seconds",
             "MeanWaveDirection": "degrees",
             "AirPressure": "hPa",
             "AirTemp": "degreesC",
             "WaterTemp": "degreesC",
             "DewPoint": "degreesC",
             "Visibility": "nauticalmiles",
             "PressureTendency": "hPa",
             "TideHeight": "feet",
             }

    ## these are in the DateTime -- no need to have them in the data
    FieldsToIgnore = ["Year", "Month", "Day", "Hour", "Minute"]
    ##FieldsToIgnore = []
    ## These are all possible numbers indicating missing values!
    MissingValues = (-999999, 99.00, 999, 999.0)# not really -999999, but "MM" is converted to this
    HeaderLine = ['MM','DD','hh']

    def MapFields(self, Header):
        """
        Maps the field names to the column number in the data array
        """
        Fields = {}
        for i, abrv in enumerate(Header):
            Fields[self.FieldNames[abrv]] = i
        self.Fields = Fields

    def IsType(self, FileName):
        """
        Detects whether the given file is this type of met file

        I'm sure this could be much improved

        """
        line = open(FileName, 'r', encoding='utf-8').readline()

        if line.split()[1:4] == self.HeaderLine:
            return True
        else:
            return False

    def LoadData(self, FileName, Name = None, LatLong = None):
        if Name is None:
            self.Name = os.path.split(FileName)[-1].rsplit(".")[0]
        infile = open(FileName, 'r', encoding='utf-8')
        if not self.IsType(FileName):
            raise BadFileTypeError("This does not appear to be a %s file\n It does not have the correct header line"%self.Type)

        ## load the data
        Header = infile.readline().split()
        Header_len = len(Header)
        self.MapFields(Header)
        self.DataArray = []
        Times = []
        msg = None
        for line in infile:
            line = line.replace("MM", "-999999")
            line = line.split()
            try: #sometimes there is a second headerline
                values = [float(v) for v in line]
                if len(values) == Header_len: #sometimes the number of data columns abruptly changes!
                    self.DataArray.append(values)
                elif len(values) > Header_len:
                    self.DataArray.append(values[:Header_len])
                    msg = 'Number of data values > number of headers (removed extra values)'
                elif len(values) < Header_len:
                    m = Header_len - len(values)
                    for ii in range(m):
                        values.extend([-999999])
                    self.DataArray.append(values)
                    msg = 'Number of data values < number of headers (added extra "Missing" values)'
                y = int(values[self.Fields['Year']])
                if y<100: #two digit years before 2000
                    y += 1900
                mo = int(values[self.Fields['Month']])
                d = int(values[self.Fields['Day']])
                h = int(values[self.Fields['Hour']])
                try:
                    min = int(values[self.Fields['Minute']])
                except:
                    min = 0
                dt = datetime.datetime(y,mo,d,h,min)
                Times.append(dt)
            except ValueError:
                pass
        if msg:
            print(msg)
        self.DataArray = np.array(self.DataArray, np.float64)
        ## Replace the missing values with NaN:
        for val in self.MissingValues:
            self.DataArray[self.DataArray == val] =  np.NaN

        ## this data is usually in reverse order
        if Times[1] < Times[0]: # the times appear to be in reverse order
            Times.reverse()
            self.DataArray = np.flipud(self.DataArray)
        self.Times = Times

class NCDC_LCD_ReaderClass(MetFileReader):
    """
    Class for reading data from NCDC

    NOTE: this doesn't read everything!
          there are "flags" on a lot of the fields that are ignored
    """
    Type = "NCDC_LCD"

    #This maps the fields to the column number in the data array
    Fields = {"WindSpeed": 0,
              "WindDirection": 1,
              "AirTemp": 2,
              }

    #This maps the field names to units.
    Units = {"WindSpeed": "mph",
             "WindDirection": "degrees",
             "AirTemp": "celsius",
             }

    ## These are all possible numbers indicating missing values!
    MissingValues = (-99999, )

    HeaderLine = "WBAN,Date,Time,StationType,SkyCondition,SkyConditionFlag,Visibility,VisibilityFlag,WeatherType,WeatherTypeFlag,DryBulbFarenheit,DryBulbFarenheitFlag,DryBulbCelsius,DryBulbCelsiusFlag,WetBulbFarenheit,WetBulbFarenheitFlag,WetBulbCelsius,WetBulbCelsiusFlag,DewPointFarenheit,DewPointFarenheitFlag,DewPointCelsius,DewPointCelsiusFlag,RelativeHumidity,RelativeHumidityFlag,WindSpeed,WindSpeedFlag,WindDirection,WindDirectionFlag,ValueForWindCharacter,ValueForWindCharacterFlag,StationPressure,StationPressureFlag,PressureTendency,PressureTendencyFlag,PressureChange,PressureChangeFlag,SeaLevelPressure,SeaLevelPressureFlag,RecordType,RecordTypeFlag,HourlyPrecip,HourlyPrecipFlag,Altimeter,AltimeterFlag".split(',')

    def IsType(self, FileName):
        """
        Detects whether the given file is this type of met file

        I'm sure this could be much improved -- why not just use LoadData?

        """
        Yes = 0
        infile = open(FileName, 'r', encoding='utf-8')
        for i, line in enumerate(infile):
            if line.strip().split(",") == self.HeaderLine:
                return True
            if i > 10:
                return False

    def LoadData(self, FileName):
        infile = open(FileName, 'r', encoding='utf-8')
        count = 0
        while count < 10:
            line = infile.readline().strip()
            if not line:
                break
            if line.split(':')[0] == "Station Location":
                self.Name = line.split(':')[1].strip()
            if line.split(':')[0] == "Lat":
                Lat = float(line.split(':')[1].strip())
            if line.split(':')[0] == "Lon":
                Long = float(line.split(':')[1].strip())
            if line.split(',') == self.HeaderLine:
                break
            count += 1
        else:
            raise BadFileTypeError("This does not appear to be a %s file\n It does not have a the right header line."%self.Type)

        ## load the data
        DataArray = []
        Times = []
        for line in infile:
            line = line.split(',')
            date = line[1]
            time = line[2]
            speed = line[24]
            if 'M' in speed:
                speed = np.NaN
            dir = line[26]
            if 'VR' in dir:
                dir = np.NaN
            temp = line[12]
            if 'M' in temp:
                temp = np.NaN
            y, mo, d = date[0:4], date[4:6], date[6:8]
            h, mi, s = time[0:2], time[2:4], 0
            dt = datetime.datetime(*[int(x) for x in (y, mo, d, h, mi, s)])
            Times.append(dt)
            DataArray.append( (float(speed), float(dir), float(temp)) )
        DataArray = np.array(DataArray)

        ## Replace the missing values with NaN:
        for val in self.MissingValues:
            DataArray[DataArray == val] =  np.NaN

        self.DataArray = DataArray
        self.Times = Times
        self.TimeZone = "LST"
        self.LatLong = (Lat, Long)


FileReaderClasses = [RawPortsReaderClass,
                     NDBCReaderClass,
                     NCDC_LCD_ReaderClass,
                     NGDC_ReaderClass,
                     OSSM_Wind_ReaderClass,
                     ]




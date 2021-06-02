#!/usr/bin/env python

"""
WindRose.py

Assorted functions for computing wind roses

"""

import numpy as np

class WindRose():
    """
    class that hold a wind rose object

    data is a set of data -- a MetData object

    vel_bins is an array defining the bins, for example:
        [3,6,10,15,21,]
        In this case, less than 3 goes into the "zero" bin, and everything greater
        than 21 is in the "large" bin, resulting in 6 total bins

    num_dir_bins is the number of direction bins to use
    -- a power of two is usually used: 4, 8, 16 or 32
    """
    def __init__(self,
                 data=None,
                 vel_bins=((1, 5, 10, 15, 20, 25)),
                 num_dir_bins=16,
                 units="",
                 title="",
                 ):
        self.data = data
        self.vel_bins = np.asarray(vel_bins)
        self.units = units
        self.num_dir_bins = num_dir_bins
        self.title=title

        self.binned_data = None

        if data is not None:
            self.BinTheData()
        return None

    def BinTheData(self):
        """
        Creates an array of binned data from the speed and velocity data provided.

        data is a (N,2) array, with data[:,0] the speed and data[:,1] the direction.
        direction is in degrees.


        if the monthly flag is True, then a set wind roses will be created, one for each month
        """
        data = self.data
        if data is None:
            return None

        velocity_bins = self.vel_bins
        num_dir_bins = self.num_dir_bins

        # add Inf to vel bins, if required:
        velocity_bins = np.asarray(velocity_bins, dtype=np.float64)
        if not( velocity_bins[-1] == np.Inf):
            velocity_bins = np.r_[velocity_bins, np.Inf]
        # add a zero at the beginning, if required
        if not( velocity_bins[0] == 0.0):
            velocity_bins = np.r_[0.0, velocity_bins]
        self.dir_bins = np.linspace(0, 360, num_dir_bins+1)
        bin_width = 360. / num_dir_bins
        ##shift data so that it is centered on the bins
        ##  (i.e. 0 degrees is the middle of the North bin)
        data[:,1] += (bin_width/2.0)
        # so that > 360 is in the zeroth bin
        data[:,1] %= 360

        binned, _, _ = np.histogram2d(data[:,0], data[:,1], bins=(velocity_bins, self.dir_bins) )
        #convert to percent
        binned /= binned.sum()#len(data)
        binned *= 100
        self.binned_data = binned
        return None

    def SaveBinTable(self, filename):
        outfile = file(filename, 'wt')
        binned = self.binned_data

        spd_bins = self.vel_bins
        dir_bins = self.dir_bins

        if len(dir_bins) == 5:
            dirs = ['N', 'E', 'S', 'W']
        elif len(dir_bins) == 9:
            dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        elif len(dir_bins) == 17:
            dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        else:
            raise ValueError("I can't do other numbers of bins -- "
                             "only 5, 9, or 17, this has %i" % len(dir_bins))

        outfile.write(self.title)
        outfile.write("\n")
        outfile.write("%10s\t" % self.units)
        line = "\t".join(["%10s" % d for d in dirs])
        outfile.write(line)
        outfile.write("\n")
        for i, s in enumerate(spd_bins):
            outfile.write("%10s\t" % s)
            line = '\t'.join(["%10.2f" % v for v in binned[i]])
            outfile.write("%s\n" % line)



    def WriteOldFormat(self, filename):
        """
        I think this writes the format used by a postscript Wind Rose tool I once used
        """
        outfile = file(filename, 'wt')

        binned = self.binned_data
        spd_bins = self.vel_bins
        dir_bins = self.dir_bins
        # first the no-wind and no-dir data:
        # I just use the entire low-speed bin (the first row):
        num_light = binned[0,:].sum()
        outfile.write("[%i, 0]\n"%num_light)
        # now the speed bins:
        bins = list(spd_bins[1:-1].astype(np.int))
        bins.append('kts')
        outfile.write(str(bins) + "\n")
        # now the data table:
        for i in range(binned.shape[1]):
            row = [i]
            row.append(list(binned[1:, i]))
            outfile.write(str(row) + "\n")


# ###################
# Are these functions still used???
#  They seem to duplicate the functionality in the class above
# ##################
def BuildStatTable(data, vel_bins, num_dir_bins=16):
    """
    Creates an array of binned data from the speed and velocity data provided.

    data is a (N,2) array, with data[:,0] the speed and data[:,1] the direction.
    direction is in degrees.

    vel_bins is an array defining the bins, for example:
        [3,6,10,15,21,]
    In this case, less than 3 goes into the "zero" bin, and everything greater
    than 21 is in the "large" bin, resulting in 6 total bins

    num_dir_bins is the number of direction bins to use -- a power of two is usually used: 8, 16 or 32

    """
    # add Inf to vel bins, if required:
    vel_bins = np.asarray(vel_bins, dtype=np.float64)
    if not( vel_bins[-1] == np.Inf):
        vel_bins = np.r_[vel_bins, np.Inf]

    # add a zero at the beginning, if required
    if not( vel_bins[0] == 0.0):
        vel_bins = np.r_[0.0, vel_bins]

    dir_bins = np.linspace(0, 360, num_dir_bins+1)
    bin_width = 360. / num_dir_bins

    ##shift data so that it is centered on the bins
    ##  (i.e. 0 degrees is the middle of the North bin)
    data[:,1] += (bin_width/2.0)
    # so that > 360 is in the zeroth bin
    data[:,1] %= 360

    binned, _1, _2 = np.histogram2d(data[:,0], data[:,1], bins=(vel_bins, dir_bins) )
    # scale to percent:
    binned /= binned.sum() # not using len(data), as there could be NaNs
    binned *= 100

    return binned


def BuildDirAverages(data, num_dir_bins=16):
    """
    computes the average velocity in each direction bin
    """
    dir_bins = np.linspace(0, 360, num_dir_bins + 1)
    bin_width = 360. / num_dir_bins

    # shift data so that it is centered on the bins
    #   (i.e. 0 degrees is the middle of the North bin)
    data[:, 1] += (bin_width / 2.0)
    # so that > 360 is in the zeroth bin
    data[:, 1] %= 360
    avg = np.zeros(num_dir_bins,)

    # strip the NaNs out in either speed or direction
    good_ind = np.isfinite(data[:, 0]) & np.isfinite(data[:, 1])
    data = data[good_ind, :]
    for i in range(num_dir_bins):
        ind = (data[:, 1] >= dir_bins[i]) & (data[:, 1] < dir_bins[i + 1])
        in_bin = data[ind, 0]
        avg[i] = np.average(in_bin)
    return avg


def MakeOSSMTable(data):
    """
    Return a OSSM-style met stats table from a MetData Object
    """
    # this is the OSSM standard
    vel_bins = np.array([1, 3.5, 6.5, 10.5, 16.5, 21.5, 27.5, 33.5, 40.5, 47.5, 55.5 ])

    binned_data = BuildStatTable(data, vel_bins, num_dir_bins=16).transpose()
    # print binned_data.shape
    table = []
    table.append("      |                                   SPEED (KNOTS)                            | TOTAL|MEAN\n"
                 "16 PT.| 1 - 3| 4 - 6|  7-10| 11-16| 17-21| 22-27| 28-33| 34-40| 41-47| 48-55|  >=56|PERCNT|WIND \n"
                 " DIR. |      |      |      |      |      |      |      |      |      |      |      |      |SPEED\n\n")
    for i, dir in enumerate(['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']):
        line = []
        line.append("%5s"%dir)
        for val in binned_data[i][1:]:
            line.append("%7.1f"%val)
        line.append("%7.1f"%binned_data[i][1:].sum())
        line.append("\n")
        table.append("".join(line))
    table.append(" CALM                                                                             %7.1f\n"%binned_data[:,0].sum())
    line = ["  ALL"]
    for val in binned_data.sum(axis=0):
        line.append("%7.1f"%val)
    line.append('\n')
    table.append("".join(line))
    return "".join(table)


if __name__ == "__main__":
    #points = np.arange(0, 360, 11.25, dtype=np.float64)
    #points = np.random.normal(loc=180, scale = 60, size=(100,) )
    #points %= 360
    #data = np.array([(sp, dir) for sp in (1, 3, 4, 5, 6, 7, 12, 17, 25) for dir in points], dtype=np.float64)
    dirs = np.random.normal(loc=180, scale = 60, size=(1000,) )
    spds = np.random.normal(loc=10, scale = 6, size=(1000,) )
    spds = np.where((spds<0), 0, spds)
    data = np.c_[spds, dirs]
    #vel_bins = [1, 5, 10, 15, 21,]
    #Rose = WindRose(data, vel_bins, units='knots', num_dir_bins=16)
    #print Rose.binned_data
    print(MakeOSSMTable(data))


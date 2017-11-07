#!/usr/bin/env python

"""
script to download historical data from NDBC
"""

import sys
import requests

USAGE = """download_ndbc.py station_name [startyear=2000] [endyear=2018]

Downloads the historical data files from teh NDBC web site:

http://www.ndbc.noaa.gov/

The station name is the short alphanumerric ID of the station.

The script will look for data starting in startyear, ending in endyear.

If you don't specify, it will look for 2000 -- 2018

example:

download_ndbc.py 41052 2011 2017
"""


def download_data(station, start_year, end_year):
    base_url = "http://www.ndbc.noaa.gov/view_text_file.php?filename={station}h{year:4d}.txt.gz&dir=data/historical/stdmet/"

    for year in range(start_year, end_year+1):
        url = base_url.format(station=station, year=year)
        filename = "{station}-{year}.txt".format(station=station, year=year)
        print "downloading station: {station} for {year}".format(station=station, year=year)
        req = requests.get(url)
        if req.status_code != 200:
            print "No data for: %i -- got a %s status code" % (year, req.status_code)
        else:
            open(filename, 'w').write(req.text)


if __name__ == "__main__":

    try:
        station_name = sys.argv[1]
    except IndexError:
        print USAGE
        sys.exit(1)
    try:
        endyear = int(sys.argv[3])
    except IndexError:
        endyear = 2018
    try:
        startyear = int(sys.argv[2])
    except IndexError:
        startyear = 2000

    download_data(station_name, startyear, endyear)

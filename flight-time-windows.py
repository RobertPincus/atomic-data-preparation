import xarray as xr
import numpy  as np
import datetime
import time
import pathlib

dataDir = pathlib.Path("Fairall-summary-data/flight-level-summary")
for f in sorted(dataDir.glob("2020*_A*.nc")):
    aoc = xr.open_dataset(f, decode_times = False)
    hours = aoc.HH.where(xr.ufuncs.logical_not(xr.ufuncs.isnan(aoc.HH)), drop = True)
    # Is the last hour larger than the first hour? This means all UTC hours are in the same day
    print("Start hour: ", "{:02d}".format(int(hours[0].values)), ", End hour: ", "{:02d}".format(int(hours[-1].values)), (hours[-1] - hours[0]).values >= 0)
    aoc.close()

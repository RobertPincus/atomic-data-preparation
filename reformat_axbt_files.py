#
# Chris Fairall assembled Matlib files containing QC'd profiles from the AXBTs dropped by the P3 during ATOMIC
# Gijs de Boer translated these into netcdf
# This script reformats the data in Level-2 and Level-3A following the treatment of the dropsondes (JOANNE)
#   Level-2 files contain one profile of temperature vs depth with no missing values
#   Level-3A file contains all AXBTs from the project interpolated onto a uniform vertical grid
# Contact: Robert Pincus <Robert.Pincus@colorado.edu>
#
import xarray as xr
import numpy  as np
import glob
import os
import time
import pathlib

campaign = "EUREC4A"
activity = "ATOMIC"
platform = "P3"
instrument = "AXBT"
data_version = "0.5.2"

filePrefix = "{}_{}".format(platform, instrument)
dataDir = pathlib.Path("Fairall-summary-data/AXBT")
files = sorted(dataDir.glob("*.cdf"))

#
# A little more compliance with CF: names of lat/lon units, temperature C -> K
#
ds = xr.open_mfdataset(files, combine='by_coords').rename({"T":"temperature"}).drop(["base_time", "time_offset"])
ds.lon.attrs["units"] = "deg_east"
ds.lat.attrs["units"] = "deg_north"
ds.time.attrs["description"] = "AXBT launch time and date"
ds.temperature.attrs["standard_name"] = "sea_water_temperature"
if ds.temperature.attrs["units"] is "C":
    ds.temperature.attrs["units"] = "K"
    ds["temperature"] += 273.15

#
# Level 2:Each profile has its own length, stripping out missing values
#
L2 = []
for i in range(ds.time.size):
    out = ds.isel(time=i).swap_dims({"sample":"depth"}).reset_coords().dropna(dim="depth", subset=["temperature", "depth"], how="any")
    L2.append(out)

#
# Write out Level-2 files
#
L2_dir = dataDir.joinpath("Level_2")
L2_dir.mkdir(parents=True, exist_ok=True)
for out in L2:
    datetime = out.time.dt
    fileName = filePrefix + "_{:04d}{:02d}{:02d}".format(datetime.year.values, datetime.month.values,  datetime.day.values)
    fileName += "_{:02d}{:02d}{:02d}.nc".format(datetime.hour.values, datetime.minute.values, datetime.second.values)
    print(fileName)
    out.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                 "campaign":campaign,
                 "activity":activity,
                 "platform":platform,
                 "instrument":instrument,
                 "contact":"Chris Fairall <Chris.Fairall@noaa.gov>",
                 "version":data_version}
    out.to_netcdf(L2_dir.joinpath(fileName), encoding={"time":{"units":"seconds since 2020-01-01"}}) # Encoding?
    out.close()

#
# Level 3A:
# Interpolate onto .1 m depth spacing to 1 km.
#
L3 = xr.concat([i.interp(depth=np.arange(0, 1000., .1)) for i in L2], dim="time")
L3["depth"].attrs = L2[0].depth.attrs
#
# Level 3A file
#
L3_dir = dataDir.joinpath("Level_3")
L3_dir.mkdir(parents=True, exist_ok=True)
L3.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
             "campaign":campaign,
             "activity":activity,
             "platform":platform,
             "instrument":instrument,
             "contact":"Chris Fairall <Chris.Fairall@noaa.gov>",
             "version":data_version}
fileName = filePrefix + "_Level_3.nc"
L3.to_netcdf(L3_dir.joinpath(fileName), encoding={"time":{"units":"seconds since 1970-01-01"}}) # Encoding?
L3.close()

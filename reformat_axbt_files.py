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
data_version = "v0.7"

filePrefix = "{}_{}".format(platform, instrument)
dataDir = pathlib.Path("data/AXBT")
files = sorted(dataDir.joinpath("Fairall_Level_1").glob("*.cdf"))

#
# A little more compliance with CF: lat/lon names, units, temperature C -> K
#
ds = xr.open_mfdataset(files, combine='by_coords').rename({"T":"temperature","lat":"lat", "lon":"lon"}).drop(["base_time", "time_offset"])
ds.lon.attrs["units"] = "degrees_east"
ds.lon.attrs        ["standard_name"] = "longitude"
ds.lat.attrs ["units"]  = "degrees_north"
ds.lat.attrs        ["standard_name"] = "latitude"
ds.time.attrs       ["standard_name"] = "time"
ds.time.attrs["description"] = "AXBT launch time and date"
ds.depth.attrs      ["standard_name"] = "depth"
ds.temperature.attrs["standard_name"] = "sea_water_temperature"

if ds.temperature.attrs["units"] is "C":
    ds.temperature.attrs["units"] = "K"
    ds["temperature"] += 273.15
#
# Add a unique AXBT ID of the form P3-
#
ds["axbt_id"] = xr.DataArray(["P3-{:02d}{:02d}_a{:03d}".format(ds.time[i].dt.month.values, ds.time[i].dt.day.values, i+1)
                              for i in range(len(ds.time))], dims = ["time"])
#
# Level 2:Each profile has its own length, stripping out missing values
#
L2 = []
for i in range(ds.time.size):
    out = ds.isel(time=i).swap_dims({"sample":"depth"}).reset_coords().dropna(dim="depth", subset=["temperature", "depth"], how="any")
    for v in ["depth", "time"] :
        out[v].attrs = ds[v].attrs
    out["time"].attrs["standard_name"] = "time"
    L2.append(out)

#
# Write out Level-2 files
#
L2_dir = dataDir.joinpath("Level_2")
L2_dir.mkdir(parents=True, exist_ok=True)
print("Level 2 files:")
for out in L2:
    datetime = out.time.dt
    fileName  = filePrefix + "_{:04d}{:02d}{:02d}".format(datetime.year.values, datetime.month.values,  datetime.day.values)
    fileName += "_{:02d}{:02d}{:02d}.nc".format(datetime.hour.values, datetime.minute.values, datetime.second.values)
    print("  " + fileName)
    out.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                 "Conventions":"CF-1.7",
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
for v in ["depth", "time"] :
    L3[v].attrs = ds[v].attrs
L3["time"].attrs["standard_name"] = "time"

#
# Level 3A file
#
L3_dir = dataDir.joinpath("Level_3")
L3_dir.mkdir(parents=True, exist_ok=True)
L3.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
             "Conventions":"CF-1.7",
             "campaign":campaign,
             "activity":activity,
             "platform":platform,
             "instrument":instrument,
             "contact":"Chris Fairall <Chris.Fairall@noaa.gov>",
             "version":data_version}
fileName = filePrefix + "_Level_3.nc"
print("Level 3 file:", fileName)
L3.to_netcdf(L3_dir.joinpath(fileName), encoding={"time":{"units":"seconds since 1970-01-01"}}) # Encoding?
L3.close()

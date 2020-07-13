#
# Chris Fairall assembled Matlib files containing cloud parameters, radar parameters, and windspeed estimates
#    as measureed by the P3 during ATOMIC
# Gijs de Boer translated these into netcdf
# This script reformats the data into archive compatible Level-3 files
# Contact: Robert Pincus <Robert.Pincus@colorado.edu>
#
import xarray as xr
import numpy  as np
import glob
import time
import pathlib

campaign = "EUREC4A"
activity = "ATOMIC"
platform = "P3"
product = "Clouds"
data_version = "0.5"

filePrefix = "{}_{}".format(platform, product)
dataDir = pathlib.Path("Fairall-summary-data/P3_Cloud_NetCDF_rainrate")
files = sorted(dataDir.glob("*.cdf"))

sfmr_vars = ["U10_SMFR", "U10_SMFR_Corr"]
nrcs_vars = ["CS_Radar", "CS_Radar_Corr"]

cloud_L3_dir = dataDir.joinpath("Level_3")
cloud_L3_dir.mkdir(parents=True, exist_ok=True)

for f in files:
    ds = xr.open_dataset(f).drop(["base_time", "time_offset"])
    out = ds

    #
    # A little more compliance with CF: names of lat/lon units, temperature C -> K
    #
    out.lon.attrs["units"] = "deg_east"
    out.lat.attrs["units"] = "deg_north"
    for v in ["sst_raw", "sst_IR", "T_IR_CT", "T_Air_CT"]:
        out[v].attrs["units"] = "K"
        out[v] += 273.15
    for v in ["cind_radar", "cind_IR"]:
        out[v].attrs["units"] = ""

    datetime = out.time[0].dt
    fileName = filePrefix + "_{:04d}{:02d}{:02d}".format(datetime.year.values, datetime.month.values,  datetime.day.values)
    fileName += "_{:02d}{:02d}{:02d}.nc".format(datetime.hour.values, datetime.minute.values, datetime.second.values)
    print(fileName)
    out.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                 "campaign":campaign,
                 "activity":activity,
                 "platform":platform,
                 "product":product,
                 "contact":"Chris Fairall <Chris.Fairall@noaa.gov>",
                 "version":data_version}
    out.to_netcdf(cloud_L3_dir.joinpath(fileName), encoding={"time":{"units":"seconds since 2020-01-01"}}) # Encoding?

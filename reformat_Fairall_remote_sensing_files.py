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
project = "ATOMIC"
platform = "P3"
product = "Remote-sensing"
data_version = "v1.0"

filePrefix = "{}_{}".format(platform, product)
dataDir = pathlib.Path("data/remote-sensing")
files = sorted(dataDir.joinpath("Level_3pre").glob("*.cdf"))
name_mapping = {
    "time":"time",
    "lon":"longitude",
    "lat":"latitude"}

cloud_L3_dir = dataDir.joinpath("Level_3")
cloud_L3_dir.mkdir(parents=True, exist_ok=True)

for f in files:
    ds = xr.open_dataset(f).drop(["base_time", "time_offset"]).rename({"p":"press"})
    out = ds

    #
    # A little more compliance with CF: names of lat/lon units, temperature C -> K
    #
    for key, value in name_mapping.items():
        out[key].attrs["standard_name"] = value
    out.lon.attrs["units"] = "degrees_east"
    out.lat.attrs["units"] = "degrees_north"
    for v in ["sst_raw", "sst_IR", "T_IR_CT", "T_Air_CT"]:
        out[v].attrs["units"] = "K"
        out[v] += 273.15
    for v in ["cind_radar", "cind_IR", "MSS_Radar"]:
        out[v].attrs["units"] = "1"
    for v in ["pitch", "roll"]:
        out[v].attrs["units"] = "degrees"
    del out.time.attrs["description"]

    datetime = out.time[0].dt
    fileName = filePrefix + "_{:04d}{:02d}{:02d}".format(datetime.year.values, datetime.month.values,  datetime.day.values)
    # fileName += "_{:02d}{:02d}{:02d}.nc".format(datetime.hour.values, datetime.minute.values, datetime.second.values)
    fileName += "_" + data_version + ".nc"
    print(fileName)
    out.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                 "Conventions":"CF-1.7",
                 "campaign":campaign,
                 "project":project,
                 "platform":platform,
                 "product":product,
                 "contact":"Chris Fairall <Chris.Fairall@noaa.gov>",
                 "version":data_version}
    out.to_netcdf(cloud_L3_dir.joinpath(fileName), encoding={"time":{"units":"seconds since 2020-01-01"}}) # Encoding?
    out.close()
    ds.close()

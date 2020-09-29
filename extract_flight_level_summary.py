#
# Extract selected data sets from the large file with flight level data provided by NOAA/AOC
#   Reproduce calculations done by Chris Fairall <Chris.Fairall@noaa.gov> for the ATOMIC
#   field program
#
# Contact: Robert Pincus <Robert.Pincus@colorado.edu>
#
import xarray as xr
import numpy  as np
import datetime
import time
import pathlib

# Mixing ratio calculation from Chris Fairall <Chris.Fairall@noaa.gov>
# p (mb), x = temperature (C), h = relative humidity (%)
def qair3(p, x, h):
    es=6.112*xr.ufuncs.exp(17.502*x/(x+241.0))*(1.0007+3.46e-6*p)*h/100.
    return(es*622./(p-.378*es))

campaign = "EUREC4A"
project = "ATOMIC"
platform = "P3"
product = "Flight-Level"
data_version = "v1.0"
filePrefix = "{}_{}_{}_{}".format(campaign, project, platform, product)
dataDir = pathlib.Path("data/flight-level-summary")

#
# Mapping between variables in the summary and the file provided by AOC
#
var_mapping = {
    "lat":"LATref", # Also in Fairall/de Boer summary file
    "lon":"LONref", #
    "alt":"ALTref", #
    "pitch":"PITCHref", #
    "roll":"ROLLref", #
    "cog":"TRK.d",
    "ws":"WS.d",
    "wd":"WD.d",
    "sfmrU":"SfmrWS.1",
    "sfmrR":"SfmrRainRate.1",
#    "sst":"TRadD.1",
    "gs":"GS.d",
    "hed":"THDGref",
    "tas":"TAS.d", #
    "press":"PS.c", #
    "Td":"TD.c",
    "Ta":"TA.d",
    "RH":"HUM_REL.d",
    "TradD":"TRadD.1",
    "TradS":"TRadS.1",
    "cab":"PCAB.1",
    "wvel":"UWZ.d",
    "uvel":"UWX.d",
    "vvel":"UWY.d"
}

#
# CF standard names, where sensible
#
name_mapping = {
    "time":"time",
    "lon":"longitude",
    "lat":"latitude",
    "ws":"wind_speed",
    "wd":"wind_to_direction",
    "Td":"dew_point_temperature",
    "Ta":"air_temperature",
    "RH":"relative_humidity"}

for input_file in sorted(dataDir.joinpath("Level_1").glob("2020*_A*.nc")):
    aoc_file_name = input_file.name
    print ("Opening " + aoc_file_name)
    full = xr.open_dataset(input_file, decode_times = False)
    #
    # Construct a time index
    #
    # Mask is false where there are NAs
    timeMask =xr.ufuncs.logical_not(np.logical_or(np.logical_or(xr.ufuncs.isnan(full.HH),
                                                                xr.ufuncs.isnan(full.MM)), xr.ufuncs.isnan(full.SS)))
    hours = full.HH.where(timeMask, drop=True)
    mins  = full.MM.where(timeMask, drop=True)
    secs  = full.SS.where(timeMask, drop=True)
    # Don't see year/month/day in the file data or metadata so we'll decode from file name...
    year  = int(aoc_file_name[0:4])
    month = int(aoc_file_name[4:6])
    day   = int(aoc_file_name[6:8])
    #   Hours, mins, secs are in UTC time
    #   File names are consistent with this - night flight were 8/9, 9/10, 10/11 local time
    #   I ensured that all flights begin and end on the same UTC day, and all night flights were in the same month
    #
    # Create a new dataset with time coordinates
    #
    subset = xr.Dataset(coords = {'time':[datetime.datetime(year, month, day, hours[i], mins[i], secs[i]) for i in range(hours.size)]})
    #
    # Should we also remove time on the ground?
    #

    for key, value in var_mapping.items():
        atts = full[value].attrs
        atts["AOC_name"] = value
        subset[key] = xr.DataArray(full[value].where(timeMask, drop=True).values,
                                   dims={"time"},
                                   coords={"time":subset.time},
                                   attrs = atts)
    #
    # Water vapor mixing ratio - Chris originally included this derived parameter but I'm not going to,
    #   leaving it instead for users to compute themselves
    #
    if False:
        subset["q"] = qair3(subset.press,  subset.Ta, subset.RH)
        subset.q.attrs = {"units":"g/kg", "Description":"Water vapor mixing ratio (computed from press, Ta, RH)", "standard_name":"humidity_mixing_ratio"}

    #
    # CF compliance
    #
    for v in ["pitch", "roll", "cog", "wd", "hed"]:
        subset[v].attrs["units"] = "degrees"
    for v in ["Td", "Ta"]:
        subset[v].attrs["units"] = "K"
        subset[v] += 273.15
    subset.lat.attrs["units"] = "degrees_north"
    subset.lon.attrs["units"] = "degrees_east"
    # This doesn't seem to work - it would be best to replace the units to be consistent with
    #   remote sensing files which use hPa
    if subset.press.attrs["units"] is "mb":
         subset.press.attrs["units"] = "hPa"

    for key, value in name_mapping.items():
        subset[key].attrs["standard_name"] = value

    #
    # Pitch used for radar calculations
    #
    subset["pitchradar"]      = subset.pitch
    subset.pitchradar.values -= 1.1
    subset.pitchradar.assign_attrs({"details":"1.1 degrees subtracted from pitch to align with W-band radar"})

    L2_dir = dataDir.joinpath("Level_2")
    L2_dir.mkdir(parents=True, exist_ok=True)
    fileName  = filePrefix + "_{:04d}{:02d}{:02d}".format(year,month,day)
    # fileName += "_{:02d}{:02d}{:02d}".format(int(hours[0].values), int(mins[0].values), int(secs[0].values)) + ".nc"
    fileName += "_" + data_version + ".nc"
    print("Writing " + fileName)
    subset.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "Conventions":"CF-1.7",
                    "campaign":campaign,
                    "project":project,
                    "platform":platform,
                    "product":product,
                    "contact":"Chris Fairall <Chris.Fairall@noaa.gov>",
                    "version":data_version}
    subset.to_netcdf(L2_dir.joinpath(fileName), encoding={"time":{"units":"seconds since 2020-01-01","dtype":"double"}})
    subset.close()
    full.close()


#
# Would have been great to do this over OpenDAP
#  Even better to have gotten the names of the file automatically but that's fussy
#
#flight_dates = ["0117", "0119", "0123", "0124", "0131", "0203", "0204", "0205", "0209", "0210", "0211"]
#server_root = "http://psl.noaa.gov/thredds/dodsC/Datasets/ATOMIC/data/p3/flight_level/Level_1/"
#for fd in flight_dates:
#    aoc_file_name = "2020" + fd + "I1_"
#    if fd is "0131" or fd is "0211":
#        aoc_file_name += "AXC.nc"
#    else:
#        aoc_file_name += "AC.nc"
#    print ("Opening " + aoc_file_name)

#    full = xr.open_dataset(server_root + aoc_file_name, decode_times = False)

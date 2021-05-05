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
data_version = "v1.1"
filePrefix = "{}_{}_{}_{}".format(campaign, project, platform, product)
dataDir = pathlib.Path("data/flight-level-summary")

flight_dates = [datetime.date(2020, 1, 17),
                datetime.date(2020, 1, 19),
                datetime.date(2020, 1, 23),
                datetime.date(2020, 1, 24),
                datetime.date(2020, 1, 31),
                datetime.date(2020, 2,  3),
                datetime.date(2020, 2,  4),
                datetime.date(2020, 2,  5),
                datetime.date(2020, 2,  9),
                datetime.date(2020, 2, 10),
                datetime.date(2020, 2, 11)]

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
    "U10_sfmr":"SfmrWS.1",
    "RainRate_sfmr":"SfmrRainRate.1",
    "gs":"GS.d",
    "hed":"THDGref",
    "tas":"TAS.d", #
    "press":"PS.c", #
    "Td":"TD.c",
    "Ta":"TA.d",
    "RH":"HUM_REL.d",
    "TIR_down":"TRadD.1",
    "TIR_side":"TRadS.1",
    "TIR_up"  :"TRadU.1",
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

#
# Would have been great to do this over OpenDAP but some variables (e.g. TRK.d) can't be read??
#  Even better to have gotten the names of the file automatically but that's fussy
#

for d in flight_dates:
    aoc_file_name = dataDir.joinpath("Level_1").joinpath(f"{d:%Y%m%d}" + "I1_")
    try:
        full = xr.open_dataset(aoc_file_name.as_posix() + "AC.nc",  decode_times = False)
    except:
        full = xr.open_dataset(aoc_file_name.as_posix() + "AXC.nc", decode_times = False)

    #
    # Construct a time index
    #
    # Mask is false where there are NAs
    timeMask =xr.ufuncs.logical_not(np.logical_or(np.logical_or(xr.ufuncs.isnan(full.HH),
                                                                xr.ufuncs.isnan(full.MM)),
                                                                xr.ufuncs.isnan(full.SS)))
    hours = full.HH.where(timeMask, drop=True)
    mins  = full.MM.where(timeMask, drop=True)
    secs  = full.SS.where(timeMask, drop=True)
    #   Hours, mins, secs are in UTC time
    #   File names are consistent with this - night flight were 8/9, 9/10, 10/11 local time
    #   I ensured that all flights begin and end on the same UTC day, and all night flights were in the same month
    #
    # Create a new dataset with time coordinates
    #
    subset = xr.Dataset(coords = {'time':[datetime.datetime(d.year, d.month, d.day,
                                                            hours[i], mins[i], secs[i])
                                                            for i in range(hours.size)]})
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
    fileName  = filePrefix + f"{d:_%Y%m%d}"
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
    subset.to_netcdf(L2_dir.joinpath(fileName),
                     encoding={"time":{"units":"seconds since 2020-01-01","dtype":"double"}})
    subset.close()
    full.close()

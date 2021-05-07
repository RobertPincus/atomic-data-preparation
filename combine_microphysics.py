#!/usr/env/python

#
# Combine five microphysics files from Mason Leandro at UCSD,
#   two containing best-estimate size distributions and three
#   containing measurements from individual instruments, to
#   produce a single file
#

import xarray as xr
import numpy  as np
import pathlib
import time
import datetime

campaign = "EUREC4A"
project = "ATOMIC"
platform = "P3"
product = "microphysics"
data_version = "v1.0"
filePrefix = "{}_{}_{}_{}".format(campaign, project, platform, product)

dates = [datetime.date(2020, 1, 31),
         datetime.date(2020, 2,  3),
         datetime.date(2020, 2,  4),
         datetime.date(2020, 2,  5),
         datetime.date(2020, 2,  9),
         datetime.date(2020, 2, 10)]

dataDir = pathlib.Path("data/ATOMIC_microphysics_nc_files")
for d in dates:
    suffix = f"{d:_%Y%m%d}" + ".nc"
    #
    # Two synthesized/merged  datasets
    #
    synth = xr.merge([xr.open_dataset(dataDir.joinpath(l + suffix)).rename({
                        v:l + "_" + v for v in ["number_concentration", "effective_radius"]})
                        for l in ["hydrometeor", "aerosol"]])
    #
    # Three files for individual instruments
    #
    inst = xr.merge([xr.open_dataset(dataDir.joinpath(l + suffix)).rename({
                        v:l + "_" + v for v in ["number_concentration", "size", "size_bnds"]})
                        for l in ["CAS", "CIP", "PIP"]])
    for l in ["CAS", "CIP", "PIP"]:
        inst[l + "_size"                ].attrs["description"] = "Bin-mean sizes measured by "                     + l + " instrument"
        inst[l + "_size_bnds"           ].attrs["description"] = "Bin size boundaries measured by "                + l + " instrument"
        inst[l + "_number_concentration"].attrs["description"] = "Size-resolved number concentration measured by " + l + " instrument"
    combo = xr.merge([synth, inst])
    combo.attrs = {"creation_date":time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                   "Conventions":"CF-1.7",
                   "campaign":campaign,
                   "project" :project,
                   "platform":platform,
                   "product" :product,
                   "contact" :"Mason Leandro <masonleandro@ucsc.edu>",
                   "version" :data_version}
    combo.to_netcdf(dataDir.joinpath("{}_{}_{}.nc".format(filePrefix, f"{d:%Y%m%d}", data_version)))
    inst.close()
    synth.close()
    combo.close()

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

dates = [datetime.date(2020, 2,  5)]

for d in dates:
    dataDir = pathlib.Path("ATOMIC_microphysics_processed"+ f"{d:_%Y%m%d}")
    suffix = f"{d:_%Y%m%d}" + ".nc"
    synth = xr.merge([xr.open_dataset(dataDir.joinpath(l + suffix)).rename({
                        v:l + "_" + v for v in ["number_concentration", "effective_radius"]})
                        for l in ["hydrometeor", "aerosol"]])
    inst = xr.merge([xr.open_dataset(dataDir.joinpath(l + suffix)).rename({
                        v:l + "_" + v for v in ["number_concentration", "size", "size_bnds"]})
                        for l in ["CAS", "CIP", "PIP"]])
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

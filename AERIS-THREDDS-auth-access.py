import xarray as xr
import requests
import docopt

session = requests.Session()
session.auth = ('eurec4a', 'barbados')

a = xr.open_dataset(xr.backends.PydapDataStore.open("https://observations.ipsl.fr/thredds/dodsC/EUREC4A/SATELLITES/GOES-E/2km_01min/2020/2020_02_13/clavrx_goes16_2020_044_2359_BARBADOS-2KM-FD.level2.nc",
                                        session=session))

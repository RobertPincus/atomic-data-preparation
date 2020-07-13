import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pathlib

fl_files = sorted(pathlib.Path("flight-level-summary/Level_2").glob("*.nc"))
cl_files = sorted(pathlib.Path("cloud-summary").glob("*.cdf"))

# Create the PdfPages object to which we will save the pages:
# The with statement makes sure that the PdfPages object is closed properly at
# the end of the block, even if an Exception occurs.
with PdfPages('flight-level-and-clouds.pdf') as pdf:
    for i in range(len(cl_files)):
        fl = xr.open_dataset(fl_files[i])
        cl = xr.open_dataset(cl_files[i])
        plt.figure()
        plt.plot(fl.time, fl.P3_altref)
        plt.plot(cl.time, cl.alt)
        cl.close()
        fl.close()
        #plt.title(fl.time[0].strftime("%m-%d"))
        pdf.savefig()  # saves the current figure into a pdf page
        plt.close()

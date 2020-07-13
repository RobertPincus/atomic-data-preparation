import xarray as xr
import pathlib
import matplotlib.pyplot as plt

dataDir = pathlib.Path("Fairall-summary-data/AXBT")
L2_dir = dataDir.joinpath("Level_2")
L3_dir = dataDir.joinpath("Level_3")

L3 = xr.open_dataset(L3_dir.joinpath("P3_AXBT_Level_3.nc"))
L2 = [xr.open_dataset(f) for f in sorted(L2_dir.glob("*.nc"))]

for i in range(L3.time.size):
  plt.plot(L3.temperature[i,], L3.depth)
plt.xlabel("Temperature (K)")
plt.ylabel("Depth (m)")
plt.gca().invert_yaxis()
plt.title("ATOMIC AXBT profiles: Level 3")
plt.savefig("AXBT_Level_3.pdf")
plt.clf()

for i in L2:
  plt.plot(i.temperature,i.depth)
plt.xlabel("Temperature (K)")
plt.ylabel("Depth (m)")
plt.gca().invert_yaxis()
plt.title("ATOMIC AXBT profiles: Level 2")
plt.savefig("AXBT_Level_2.pdf")

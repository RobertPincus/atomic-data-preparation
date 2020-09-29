#
# commands run with zsh to update attributes (version, activity -> project) and rename files
#
autoload zmv
for file in AXBT/Level_2/*.nc; ncatted -O -h -a version,global,o,c,v1.0 -a project,global,o,c,ATOMIC -a activity,global,d,c,ATOMIC $file
zmv 'AXBT/Level_2/(*)_v(*).nc' 'AXBT/Level_2/EUREC4A_ATOMIC_$1_v1.0.nc'
for file in AXBT/Level_3/*.nc; ncatted -O -h -a version,global,o,c,v1.0 -a project,global,o,c,ATOMIC -a activity,global,d,c,ATOMIC $file
zmv 'AXBT/Level_3/(*)_v(*).nc' 'AXBT/Level_3/EUREC4A_ATOMIC_$1_v1.0.nc'

for file in Flight-Level/Level_2/*.nc; ncatted -O -h -a version,global,o,c,v1.0 -a project,global,o,c,ATOMIC -a activity,global,d,c,ATOMIC $file
zmv 'Flight-Level/Level_2/P3_Flight-Level_(*)_v(*).nc' 'Flight-Level/Level_2/EUREC4A_ATOMIC_P3_Flight-level_$1_v1.0.nc'
mv Flight-Level Flight-level

for file in Remote-sensing/*.nc; ncatted -O -h -a version,global,o,c,v1.0 -a project,global,o,c,ATOMIC -a activity,global,d,c,ATOMIC $file
zmv 'Remote-sensing/(*)_v(*).nc' 'Remote-sensing/$1_v1.0.nc'

for file in W-band-radar/*.nc; ncatted -O -h -a version,global,o,c,v1.0 -a project,global,o,c,ATOMIC -a activity,global,d,c,ATOMIC $file
zmv 'W-band-radar/(*)_v(*).nc' 'W-band-radar/EUREC4A_$1_v1.0.nc'

for file in WSRA/*.nc; ncatted -O -h -a version,global,o,c,v1.0 -a project,global,o,c,ATOMIC -a activity,global,d,c,ATOMIC $file
zmv 'WSRA/(*)_v(*).nc' 'WSRA/EUREC4A_ATOMIC_$1_v1.0.nc'

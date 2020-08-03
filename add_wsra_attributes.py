# commands run with zsh to add attributes to WSRA Level-4 files provided by Prosensing.
export wsra_version='v0.9'
for file in data/WSRA/*.nc; do ncatted -O -h -a platform,global,o,c,P3 -a campaign,global,o,c,EUREC4A -a activitiy,global,o,c,ATOMIC -a contact,global,o,c,"Ivan Popstefanija <popstefanija@prosensing.com>" -a instrument,global,o,c,WSRA -a version,global,o,c,${wsra_version} $file; done
autoload zmv
zmv -n 'data/WSRA/WSRA-L4-(*)I.nc' 'data/WSRA/P3_WSRA_$1_${wsra_version}.nc'

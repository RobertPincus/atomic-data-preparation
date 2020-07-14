# commands run with zsh to add attributes to WSRA Level-4 files provided by Prosensing. 
for file in *.nc; do ncatted -O -h -a platform,global,o,c,P3 -a campaign,global,o,c,EUREC4A -a activitiy,global,o,c,ATOMIC -a contact,global,o,c,"Ivan Popstefanija <popstefanija@prosensing.com>" -a instrument,global,o,c,WSRA -a version,global,o,c,0.9 $file; done


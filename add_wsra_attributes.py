# commands run with zsh to add attributes to WSRA Level-4 files provided by Prosensing.
export wsra_version='v0.9'
for file in data/WSRA/*.nc; do ncatted -O -h -a platform,global,o,c,P3 -a campaign,global,o,c,EUREC4A -a activitiy,global,o,c,ATOMIC -a contact,global,o,c,"Ivan Popstefanija <popstefanija@prosensing.com>" -a instrument,global,o,c,WSRA -a version,global,o,c,${wsra_version} $file; done
autoload zmv
zmv -n 'data/WSRA/WSRA-L4-(*)I.nc' 'data/WSRA/P3_WSRA_$1_${wsra_version}.nc'
#
# OpenDAP compliance - fill values the same type as the variables themselves
#
for file in data/WSRA/*_${wsra_version}.nc;
    do echo $file;
    for var in dominant_to_secondary_partition_angle \
            dominant_wave_direction \
    		dominant_wave_height \
    		dominant_wave_wavelength \
    		peak_spectral_variance \
    		wsra_computed_roll \
    		rainfall_rate \
    		rainfall_rate_median \
    		sea_surface_mean_square_slope \
    		sea_surface_mean_square_slope_median \
    		sea_surface_wave_significant_height \
    		secondary_wave_direction \
    		secondary_wave_height \
    		secondary_wave_wavelength \
    		swh_correction_ratio ;
        do ncatted -O -h -a missing_value,$var,o,f,-999. $file; done;
    done; done
#
# OpenDAP - no unsinged ints
#
for file in data/WSRA/*_${wsra_version}.nc;
    do echo $file; ncap2 -O -s "time=int(time)" -s "trajectory=int(trajectory)" $file $file; done

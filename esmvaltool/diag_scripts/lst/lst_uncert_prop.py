"""
ESMValTool diagnostic for ESA CCI LST V3 data - Uncertainity Propagation
"""

# Expected keys for OBS LST data in loaded_data:
# ts_day
# ts_night
# lst_unc_loc_sfc_day
# lst_unc_loc_sfc_night
# lst_unc_loc_atm_day
# lst_unc_loc_atm_night
# lst_unc_sys_day
# lst_unc_sys_night
# lst_unc_ran_day
# lst_unc_ran_night

import logging
import iris
import iris.plot as iplt
import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from esmvaltool.diag_scripts.shared import (
    ProvenanceLogger,
    get_plot_filename,
    group_metadata,
    run_diagnostic,
)

# Colour scheme for plots
# blue cyan green yellow
# red purple grey
colour_list = ['#4477aa', '#66ccee', '#228833', '#ccbb44',
               '#ee6677', '#aa3377', '#bbbbbb']

# This gives a colour list for the Land Cover type plots
lc_colour_list = sorted(list(mcolors.CSS4_COLORS.keys()))
lc_colour_list.reverse()

plot_params = {'linewidth': 4,
               'ticksize': 24,
               'labelsize': 28,
               'legendsize': 20,}

line_labels = {
    'lst_unc_loc_atm_day': 'Locally Correlated (Atm)',
    'lst_unc_loc_sfc_day': 'Locally Correlated (Sfc)',
    'lst_unc_sys_day': 'Systematic',
    'lst_unc_ran_day': 'Random',
    'lst_sampling_day': 'Sampling',
    'lst_total_unc_day': 'Total',
    'lst_unc_loc_atm_night': 'Locally Correlated (Atm)',
    'lst_unc_loc_sfc_night': 'Locally Correlated (Sfc)',
    'lst_unc_sys_night': 'Systematic',
    'lst_unc_ran_night': 'Random',
    'lst_sampling_night': 'Sampling',
    'lst_total_unc_night': 'Total',
    }

logger = logging.getLogger(__name__)


def _get_input_cubes(metadata):
    """Load the data files into cubes.

    Based on the hydrology diagnostic originally.

    Inputs:
    metadata = List of dictionaries made from the preprocessor config

    Outputs:
    inputs = Dictionary of cubes
    ancestors = Dictionary of filename information
    """
    inputs = {}
    ancestors = {}
    for attributes in metadata:

        short_name = attributes['short_name']
        filename = attributes['filename']
        logger.info("Loading variable %s", short_name)
        cube = iris.load_cube(filename)
        cube.attributes.clear()
        inputs[short_name] = cube
        ancestors[short_name] = [filename]

    return inputs, ancestors


def _get_provenance_record(attributes, ancestor_files):
    """Create the provenance record dictionary.

    Inputs:
    attributes = dictionary of ensembles/models used, the region bounds
                 and years of data used.
    ancestor_files = list of data files used by the diagnostic.

    Outputs:
    record = dictionary of provenance records.
    """
    caption = "This needs a new caption.".format(**attributes)

    record = {
        'caption': caption,
        'statistics': ['mean'],
        'domains': ['reg'],
        'plot_types': ['times'],
        'authors': ['king_robert'],
        # 'references': [],
        'ancestors': ancestor_files
    }

    return record


def _diagnostic(config):
    """Perform the control for the ESA CCI LST diagnostic.

    Parameters
    ----------
    config: dict
        the preprocessor nested dictionary holding
        all the needed information.

    Returns
    -------

    """
    # this loading function is based on the hydrology diagnostic
    input_metadata = config['input_data'].values()
    loaded_data = {}
    ancestor_list = []

    for dataset, metadata in group_metadata(input_metadata, 'dataset').items():
        cubes, ancestors = _get_input_cubes(metadata)
        loaded_data[dataset] = cubes

    # Methodolgy:
    # calcualte for day and night seperately
    # calls to propagation equations for each compoent
    # ts eq 1 eq_arithmetic_mean
    # lst_unc_loc_atm eq 7 eq_weighted_sqrt_mean
    # lst_unc_sys eq 5 = eq 1 eq_arithmetic_mean, no spatial propagation here
    # lst_unc_loc_sfc follows the worked example in the E3UB
    # use the worked example method in the E3UB document.
    # lst_unc_ran eq 4 eq_propagate_random_with_sampling
    #
    # Then combine to get a total day and night value
    # total uncert  eq 9 eq_sum_in_quadrature
    # a total all day uncertainty can then be obtained using
    # eq 9 eq_sum_in_quadrature
    # Day and night time values kept seperate

    lst_unc_variables = ['lst_unc_loc_atm', 'lst_unc_sys',
                         'lst_unc_loc_sfc', 'lst_unc_ran']

    # This will be a dictionary of variables and cubes
    # of their propagated values
    propagated_values = {}

    # These define the total number of points in the data
    lat_len = len(loaded_data['ESACCI-LST']['ts_day'].coord('latitude').points)
    lon_len = len(loaded_data['ESACCI-LST']['ts_day'].coord('longitude').points)

    # n_fill and n_use ad dictionaries with keys 'day' and 'night'
    # the item for each key is an array
    # These give the cloud/don't use pixel numbers,
    # and the number of useable pixels for each timestep
    n_fill = {}
    n_use = {}
    for time in ['day', 'night']:
        if isinstance(loaded_data['ESACCI-LST'][f'ts_{time}'].data.mask,
                      np.ndarray):
            # mask is an array so there are masked values
            # do counting
            n_fill[time] = np.array([np.sum(loaded_data['ESACCI-LST'][f'ts_{time}'][date].data.mask) for date in range(len(loaded_data['ESACCI-LST']['ts_day'].coord('time').points))])
        elif loaded_data['ESACCI-LST'][f'ts_{time}'].data.mask:
            # mask is single value of True so all masked values
            # make a array of m*n
            n_fill[time] = np.array([lat_len*lon_len for i in loaded_data['ESACCI-LST']['ts_day'].coord('time').points])
        else:
            # mask is a single value of False so no masked values
            # make an array of zeros
            n_fill[time] = np.zeros_like(loaded_data['ESACCI-LST']['ts_day'].coord('time').points)

    n_use['day'] = (lat_len * lon_len) - n_fill['day']
    n_use['night'] = (lat_len * lon_len) - n_fill['night']

    # This loop call the propagation equations, once for 'day' and 'night'
    for time in ['day', 'night']:

        propagated_values[f'ts_{time}'] = \
        eq_arithmetic_mean(loaded_data['ESACCI-LST'][f'ts_{time}'])

        propagated_values[f'lst_unc_loc_atm_{time}'] = \
        eq_weighted_sqrt_mean(loaded_data['ESACCI-LST'][f'lst_unc_loc_atm_{time}'],
        n_use[f'{time}'])
        # no spatial propagation of the systamatic uncertainity
        propagated_values[f'lst_unc_sys_{time}'] = \
        loaded_data['ESACCI-LST'][f'lst_unc_sys_{time}']

        propagated_values[f'lst_unc_loc_sfc_{time}'] = \
        eq_correlation_with_biome(loaded_data['ESACCI-LST'][f'lst_unc_loc_sfc_{time}'],
                                  loaded_data['ESACCI-LST'][f'lcc_{time}'])
        
        propagated_values[f'lst_unc_ran_{time}'], \
        propagated_values[f'lst_sampling_{time}'] = \
        eq_propagate_random_with_sampling(loaded_data['ESACCI-LST'][f'lst_unc_ran_{time}'],
                                          loaded_data['ESACCI-LST'][f'ts_{time}'],
                                          n_use[f'{time}'],
                                          n_fill[f'{time}'])

    # Combines all uncertainty types to get total uncertainty
    # for 'day' and 'night'
    for time in ['day', 'night']:
        time_cubelist = iris.cube.CubeList([propagated_values[f'{variable}_{time}']
                                            for variable in lst_unc_variables])

        propagated_values[f'lst_total_unc_{time}'] = \
                            eq_sum_in_quadrature(time_cubelist)
    
    
    # iplt did not want to work with 360 day calendar of UKESM
    # and demote appears to work on the standard_name
    loaded_data['UKESM1-0-LL']['ts'].coord('time').var_name = 'time2'
    loaded_data['UKESM1-0-LL']['ts'].coord('time').long_name = 'time2'
    loaded_data['UKESM1-0-LL']['ts'].coord('time').standard_name = 'height'
    iris.util.demote_dim_coord_to_aux_coord(loaded_data['UKESM1-0-LL']['ts'],
                                            'height')
    loaded_data['UKESM1-0-LL']['ts'].add_aux_coord(propagated_values['ts_day'].coord('time'),0)
    iris.util.promote_aux_coord_to_dim_coord(loaded_data['UKESM1-0-LL']['ts'],
                                             'time')
   
    plot_lc(loaded_data)
 
    test_plot(propagated_values)
    plot_with_cmip(propagated_values, loaded_data)
   
def plot_lc(loaded_data):
    """Plot to show land cover and correlations
    """

    lc_types = np.unique(loaded_data['ESACCI-LST']['lcc_day'][0].data,
                         return_counts=True)
    
    class_list = lc_types[0]
    bound_list = np.append(class_list - 0.5, 256)
    
    colours = lc_colour_list[0:len(lc_types[0])]
    
    cmap = matplotlib.colors.ListedColormap(colours)
    norm = matplotlib.colors.BoundaryNorm(bound_list, cmap.N)
    
    fig = plt.figure(figsize=(25, 15))
    ax1 = plt.subplot(111)
    
    iplt.pcolormesh(loaded_data['ESACCI-LST']['lcc_day'][0],
                    cmap=cmap, norm=norm)
    x_ticks = [loaded_data['ESACCI-LST']['lcc_day'][0].coord('longitude').points[0],
               loaded_data['ESACCI-LST']['lcc_day'][0].coord('longitude').points[-1]]
    y_ticks = [loaded_data['ESACCI-LST']['lcc_day'][0].coord('latitude').points[0],
               loaded_data['ESACCI-LST']['lcc_day'][0].coord('latitude').points[-1]]
    
    x_ticks = [item for item in loaded_data['ESACCI-LST']['lcc_day'][0].coord('longitude').points[::5]]
    x_tick_labels = ['' for item in x_ticks]
    x_tick_labels[0] = f"{loaded_data['ESACCI-LST']['lcc_day'][0].coord('longitude').points[0]:.2f}"
    x_tick_labels[-1] = f"{loaded_data['ESACCI-LST']['lcc_day'][0].coord('longitude').points[-1]:.2f}"
    plt.xticks(x_ticks, x_tick_labels, fontsize=plot_params['ticksize'])
    
    y_ticks = [item for item in loaded_data['ESACCI-LST']['lcc_day'][0].coord('latitude').points[::5]]
    y_tick_labels = ['' for item in y_ticks]
    y_tick_labels[0] = f"{loaded_data['ESACCI-LST']['lcc_day'][0].coord('latitude').points[0]:.2f}"
    y_tick_labels[-1] = f"{loaded_data['ESACCI-LST']['lcc_day'][0].coord('latitude').points[-1]:.2f}"
    plt.yticks(y_ticks, y_tick_labels, fontsize=plot_params['ticksize'])
    
    plt.grid(c='k', linewidth=1)
    
    plt.xlabel('Longitude', fontsize=plot_params['labelsize'])
    plt.ylabel('Latitude', fontsize=plot_params['labelsize'])
    
    cbar = plt.colorbar()
    
    Z = [(bound_list[i]+bound_list[i+1])/2 for i in range(len(bound_list)-1)]
    labels = [int(item) for item in class_list]
    cbar.set_ticks(Z, labels=labels)
    cbar.ax.tick_params(labelsize=plot_params['ticksize'])
    cbar.set_label('Land Cover Types', fontsize=plot_params['labelsize'])
    
    plt.tight_layout()
    plt.savefig(f'LC_map.png')
    
    fig2 = plt.figure(figsize=(20,25))
    
    ax1 = plt.subplot(111)
    plt.bar(range(len(class_list)), lc_types[1],
            label = labels,
            color=colours,
            linewidth=2, edgecolor='black',
            tick_label = labels)

    ax1.tick_params(labelsize=plot_params['ticksize'])
    
    plt.xlabel('Land Cover Type', fontsize=plot_params['labelsize'])
    plt.ylabel('Count', fontsize=plot_params['labelsize'])
    
    plt.tight_layout()
    plt.savefig(f'LC_bar.png')
    
        
def plot_with_cmip(propagated_values, loaded_data):
    """A plot for comparing OBS+uncertainity with CMIP value
    """
    
    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsfmt = mdates.DateFormatter('%Y')

    for time in ['day', 'night']:
        # one plot for day and night seperately
        fig = plt.figure(figsize=(25,15))

        ax1 = plt.subplot(111)
        iplt.plot(propagated_values[f'ts_{time}'],
                  c=colour_list[0],
                  linewidth=plot_params['linewidth'],
                  label=f'LST {time} (CCI)')
        iplt.fill_between(propagated_values[f'ts_{time}'].coord('time'),
                          propagated_values[f'ts_{time}'] + propagated_values[f'lst_total_unc_{time}'],
                          propagated_values[f'ts_{time}'] - propagated_values[f'lst_total_unc_{time}'],
                          color=colour_list[0],
                          alpha=0.5,
                          label=f'Uncertainty {time} (CCI)'
                          )
        
        iplt.plot(loaded_data['UKESM1-0-LL']['ts'],
                  c=colour_list[4],
                  linewidth=plot_params['linewidth'],
                  label='LST (CMIP6)')
        
        ax1.xaxis.set_major_locator(years)
        ax1.xaxis.set_major_formatter(yearsfmt)
        ax1.xaxis.set_minor_locator(months)
                
        plt.grid(which='major', color='k', linestyle='solid')
        plt.grid(which='minor', color='k', linestyle='dotted', alpha=0.5)
        
        plt.xlabel('Date', fontsize=plot_params['labelsize'])
        plt.ylabel('LST (K)', fontsize=plot_params['labelsize'])

        plt.legend(loc='lower left',
                   bbox_to_anchor=(1.05, 0),
                   fontsize=plot_params['legendsize'])
        
        ax1.tick_params(labelsize=plot_params['ticksize'])
         
        plt.tight_layout()
        plt.savefig(f'cmip_{time}.png')
        
    # make a version with day and night both on same plot
    fig = plt.figure(figsize=(25,15))

    ax1 = plt.subplot(111)
    colour_id = 0
    for time in ['day', 'night']:
        iplt.plot(propagated_values[f'ts_{time}'],
                  c=colour_list[colour_id],
                  linewidth=plot_params['linewidth'],
                  label=f'LST {time} (CCI)')
        iplt.fill_between(propagated_values[f'ts_{time}'].coord('time'),
                          propagated_values[f'ts_{time}'] + propagated_values[f'lst_total_unc_{time}'],
                          propagated_values[f'ts_{time}'] - propagated_values[f'lst_total_unc_{time}'],
                          color=colour_list[colour_id],
                          alpha=0.5,
                          label=f'Uncertainty {time}'
                )
        colour_id =- 1
        
    iplt.plot(loaded_data['UKESM1-0-LL']['ts'],
              c=colour_list[4],
              linewidth=plot_params['linewidth'],
              label='LST (CMIP6)')
        
    ax1.xaxis.set_major_locator(years)
    ax1.xaxis.set_major_formatter(yearsfmt)
    ax1.xaxis.set_minor_locator(months)
        
    plt.grid(which='major', color='k', linestyle='solid')
    plt.grid(which='minor', color='k', linestyle='dotted', alpha=0.5)

    plt.xlabel('Date', fontsize=plot_params['labelsize'])     
    plt.ylabel('LST (K)', fontsize=plot_params['labelsize'])

    plt.legend(loc='lower left',
               bbox_to_anchor=(1.05, 0),
               fontsize=plot_params['legendsize'])
        
    ax1.tick_params(labelsize=plot_params['ticksize'])
         
    plt.tight_layout()
    plt.savefig('cmip_both.png')
        
        
def test_plot(propagated_values):
    """This is a very simple plot to just test the method
    """

    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsfmt = mdates.DateFormatter('%Y')

    for time in ['day', 'night']:
        # one plot for day and night seperately
        fig = plt.figure(figsize=(25,15))

        ax1 = plt.subplot(211)
        iplt.plot(propagated_values[f'ts_{time}'],
                  c=colour_list[0],
                  linewidth=plot_params['linewidth'],
                  label='LST')
        iplt.fill_between(propagated_values[f'ts_{time}'].coord('time'),
                          propagated_values[f'ts_{time}'] + propagated_values[f'lst_total_unc_{time}'],
                          propagated_values[f'ts_{time}'] - propagated_values[f'lst_total_unc_{time}'],
                          color=colour_list[0],
                          alpha=0.5,
                          label='Uncertainty'
        )
        
        ax1.xaxis.set_major_locator(years)
        ax1.xaxis.set_major_formatter(yearsfmt)
        ax1.xaxis.set_minor_locator(months)
        
        plt.grid(which='major', color='k', linestyle='solid')
        plt.grid(which='minor', color='k', linestyle='dotted', alpha=0.5)
        
        plt.ylabel('LST (K)', fontsize=plot_params['labelsize'])

        plt.legend(loc='lower left',
                   bbox_to_anchor=(1.05, 0),
                   fontsize=plot_params['legendsize'])

        ax2 = plt.subplot(212, sharex=ax1)
        iplt.plot(propagated_values[f'lst_unc_loc_atm_{time}'],
                  c=colour_list[2],
                  linewidth=plot_params['linewidth'],
                  label=line_labels[f'lst_unc_loc_atm_{time}'])
        iplt.plot(propagated_values[f'lst_unc_loc_sfc_{time}'],
                  c=colour_list[3],
                  linewidth=plot_params['linewidth'],
                  label=line_labels[f'lst_unc_loc_sfc_{time}'])
        iplt.plot(propagated_values[f'lst_unc_sys_{time}'],
                  c=colour_list[4],
                  linewidth=plot_params['linewidth'],
                  label=line_labels[f'lst_unc_sys_{time}'])
        iplt.plot(propagated_values[f'lst_unc_ran_{time}'],
                  c=colour_list[5],
                  linewidth=plot_params['linewidth'],
                  label=line_labels[f'lst_unc_ran_{time}'])

        iplt.plot(propagated_values[f'lst_sampling_{time}'],
                  '--', 
                  c=colour_list[1],
                  linewidth=plot_params['linewidth'],
                  label=line_labels[f'lst_sampling_{time}'])
        iplt.plot(propagated_values[f'lst_total_unc_{time}'],
                  c=colour_list[6],
                  linewidth=plot_params['linewidth'],
                  label=line_labels[f'lst_total_unc_{time}'])

        plt.grid(which='major', color='k', linestyle='solid')
        plt.grid(which='minor', color='k', linestyle='dotted', alpha=0.5)
        
        plt.xlabel('Date', fontsize=plot_params['labelsize'])
        plt.ylabel('Uncertainty (K)', fontsize=plot_params['labelsize'])

        plt.legend(loc='upper left',
                   bbox_to_anchor=(1.05, 1),
                   fontsize=plot_params['legendsize'])

        ax1.tick_params(labelsize=plot_params['ticksize'])
        ax2.tick_params(labelsize=plot_params['ticksize'])
 
        plt.tight_layout()
        plt.savefig(f'test_A_{time}.png')


# These are the propagation equations

def eq_correlation_with_biome(cube_loc_sfc, lcc):
    """
    Propagate using the land cover/biome information.
    Used for the locally correlated surface uncertainity.
    Method:
        Make a 0.05 degree grid of data
        Find the matching biome matrix
        Calc uncert for each correlated biome
        Calc 0.05 box total uncert
        With all of these, find the total uncert (0.05 -> arbitary)
    """
    
    lat_len = len(cube_loc_sfc.coord('latitude').points)
    lon_len = len(cube_loc_sfc.coord('longitude').points)
    time_len = len(cube_loc_sfc.coord('time').points)
    
    final_values = [] # this is for each overal main area value
    lc_grid = [] # this is for each 5*5 block
    for time_index in range(time_len):
        
        grid_means = [] # this is for the 5*5 block means
        # all cci lst v3 data is 0.05 resolution
        # so use blocks of 5 to get 0.01 degree resolution
        for i in range(0,lat_len,5):
            for j in range(0,lon_len,5):
                this_region = lcc[time_index,i:i+5,j:j+5]
                lc_grid.append(this_region)
                uniques = np.unique(this_region.data.round(decimals=0),
                                    return_index=True,
                                    return_inverse=True)
                # note order of uniques will depends on both options = True
                num_of_biomes = len(uniques[0])
            
                this_uncerts = cube_loc_sfc[time_index,i:i+5,j:j+5].data.flatten()

                uncert_by_biome = [[] for i in range(num_of_biomes)]
                for k, item in enumerate(this_uncerts):
                    uncert_by_biome[uniques[2][k]].append(this_uncerts[k])
            
                # E3UB gives two methods
                # method 1 = eq 5.31 and worked example eq 5.32
                # method 2 is used by CCI at moment and is eq 5.34
                # here use method 2
                
                # np.ma.mean allows masked boxes to be ignored
                mean_list = [np.ma.mean(item) for item in uncert_by_biome]
                this_mean = np.ma.mean(mean_list)
                grid_means.append(this_mean)
    
        # final_values is the value to make a timeseries out of
        this_times_mean = np.mean(grid_means)
        final_values.append(this_times_mean)
    
    # need to make a cube to return
    results_cube = iris.cube.Cube(np.array(final_values),
                                dim_coords_and_dims = [(lcc.coord('time'),0)],
                                units = 'Kelvin',
                                var_name = cube_loc_sfc.var_name,
                                long_name = cube_loc_sfc.long_name,
                                )
    
    return results_cube


def eq_propagate_random_with_sampling(cube_unc_ran, cube_ts, n_fill, n_use):
    """Propagate radom uncertatinty using the sampling uncertainty
    ATBD eq 4

    the sum in quadrature of the arithmetic mean of lst_unc_ran and
    the sampling uncertainty

    Sampling uncertainty is
    n_cloudy * Variance of LST / n_total-1

    see ATBD section 3.13.3

    Inputs:
    cube_unc_ran: The cube with the lst_unc_ran day/night data
    cube_ts:      The lst use for day/night as appropriate
    """

    # total number of pixed
    n_total = n_fill + n_use

    # the mean of the random uncertainty
    unc_ran_mean = eq_weighted_sqrt_mean(cube_unc_ran, n_total)

    # calculate the sampling error
    # variance of the lst * n_fill/n_total-1
    lst_variance = cube_ts.collapsed(['latitude', 'longitude'],
                                     iris.analysis.VARIANCE)
    factor = n_fill/(n_total - 1)
    unc_sampling = iris.analysis.maths.multiply(lst_variance,
                                                factor)

    # apply the ATBD equation
    # note the square of random uncertainty is needed
    output = eq_sum_in_quadrature(iris.cube.CubeList([unc_ran_mean**2,
                                                      unc_sampling]))
    output = iris.analysis.maths.exponentiate(output, 0.5)

    return output, unc_sampling


def eq_arithmetic_mean(cube):
    """Arithmetic mean of cube, across latitude and longitude
    ATBD eq 1
    """

    out_cube = cube.collapsed(['latitude', 'longitude'], iris.analysis.MEAN)

    return out_cube


def eq_sum_in_quadrature(cubelist):
    """Sum in quadrature
    ATBD eq 9

    Input:
    cubelist : A cubelist of 1D cubes
    """

    # dont want to in-place replace the input
    newlist = cubelist.copy()
    for cube in newlist:
        iris.analysis.maths.exponentiate(cube, 2, in_place=True)

    cubes_sum = 0
    for cube in newlist:
        cubes_sum = cubes_sum + cube
    output = iris.analysis.maths.exponentiate(cubes_sum, 0.5,
                                              in_place=False)

    return output


def eq_weighted_sqrt_mean(cube, n_use):
    """Mean with square root of n factor
    ATBD eq 7

    Inputs:
    cube:
    n_use: the number of useable pixels
    NEED TO IMPLIMENT A CHECK ON MASKS BEING THE SAME?
    """
    output = iris.analysis.maths.multiply(cube.collapsed(['latitude',
                                                          'longitude'],
                                                         iris.analysis.MEAN),
                                          1/np.sqrt(n_use))
    return output


if __name__ == '__main__':
    # always use run_diagnostic() to get the config (the preprocessor
    # nested dictionary holding all the needed information)
    with run_diagnostic() as config:
        _diagnostic(config)

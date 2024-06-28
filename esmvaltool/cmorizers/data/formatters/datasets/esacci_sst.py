"""ESMValTool CMORizer for ESACCI-SST data.

Tier
   Tier 3: need to register at CEDA

Source
   https://catalogue.ceda.ac.uk/uuid/4a9654136a7148e39b7feb56f8bb02d2

Last access
   20240628

Download and processing instructions
   A donwnloader is provided by ESMValTool. First you need
   to register.
   Go to https://services.ceda.ac.uk/cedasite/register/info/
   and create an account at CEDA if needed.
  
?       Exclude data above sea ice threshold: True
?         (Threshold: 100 %)
?       Include post-hoc SST bias adjustments: True
?       Output Absolute or Anomaly SST: absolute
?       Generate Sea Ice Fraction: True
?       Error Correlation in Time (Days): 7
?       Error Correlation In Space (Degrees): 3.0

Modification history
   20240618-bock_lisa: update for v3.0
   20201204-roberts_charles: written.
   20201214-predoi_valeriu: approved.
   20201214-lauer_axel: approved.
"""

import glob
import logging
import os

import iris
from esmvalcore.cmor.fixes import get_time_bounds
from esmvaltool.cmorizers.data import utilities as utils
from esmvalcore.preprocessor import concatenate
from esmvalcore.preprocessor import regrid, monthly_statistics

from ...utilities import (
    convert_timeunits,
    fix_coords,
    fix_var_metadata,
    save_variable,
    set_global_atts,
)

logger = logging.getLogger(__name__)


def extract_variable(var_info, raw_info, attrs, year):
    """Extract to all vars."""
    rawvar = raw_info['name']
    constraint = iris.NameConstraint(var_name=rawvar)
    try:
        cube = iris.load_cube(raw_info['file'], constraint)
    except iris.exceptions.ConstraintMismatchError as constraint_error:
        raise ValueError(f"No data available for variable {rawvar}"
                         f"and year {year}") from constraint_error

    # regridding from 0.05x0.05 to 0.5x0.5
    cube = regrid(cube, target_grid='0.5x0.5', scheme='area_weighted')
    #Fix dtype
    utils.fix_dtype(cube)
    # Fix cube
    fix_var_metadata(cube, var_info)
    convert_timeunits(cube, year)
    fix_coords(cube, overwrite_time_bounds=False)
    set_global_atts(cube, attrs)
    return cube


def cmorization(in_dir, out_dir, cfg, cfg_user, start_date, end_date):
    """Cmorization func call."""
    cmor_table = cfg['cmor_table']
    glob_attrs = cfg['attributes']

    # run the cmorization
    for var_name, vals in cfg['variables'].items():
        var = vals['short_name']
        var_info = cmor_table.get_variable(vals['mip'], var)
        glob_attrs['mip'] = vals['mip']
        raw_info = {'name': vals['raw']}
        inpfile_pattern = os.path.join(in_dir, '{year}*'+vals['filename'])
        logger.info("CMORizing var %s from file type %s", var, inpfile_pattern)
        for year in range(vals['start_year'], vals['end_year'] + 1):
            logger.info("Processing year %s", year)
            mon_cubes = []
            #for month in range(1,13):
            for month in range(1,4):
                data_cubes = []
                month_inpfile_pattern = inpfile_pattern.format(year=str(year)+"{:02}".format(month))
                logger.info("Pattern: %s", month_inpfile_pattern)
                inpfiles = sorted(glob.glob(month_inpfile_pattern))
                logger.info("Found input files: %s", inpfiles)
                for inpfile in inpfiles:
                    raw_info['file'] = inpfile
                    logger.info("CMORizing var %s from file type %s", var,
                                raw_info['file'])
                    data_cubes.append(
                        extract_variable(var_info, raw_info, glob_attrs, year))
                monthly_cube = concatenate(data_cubes)
                # Fix monthly time bounds
                time = monthly_cube.coord('time')
                time.bounds = get_time_bounds(time, vals['frequency'])
                mon_cubes.append(monthly_cube)
                #mon_cubes.append(monthly_cube.collapsed('time', iris.analysis.MEAN))
                save_variable(monthly_cube,
                              var,
                              out_dir,
                              glob_attrs,
                              unlimited_dimensions=['time'])
            yearly_cube = monthly_statistics(concatenate(mon_cubes), operator='mean')
            #yearly_cube = concatenate(mon_cubes)
            glob_attrs['mip'] = 'Omon'
            save_variable(yearly_cube,
                          var,
                          out_dir,
                          glob_attrs,
                          unlimited_dimensions=['time'])

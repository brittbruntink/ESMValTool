"""Plot multimodel variable stats at Global Warming Level exceedance years."""
import logging
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import iris 

import esmvaltool.diag_scripts.shared.iris_helpers as ih

from esmvalcore.preprocessor import extract_time, multi_model_statistics
from iris.util import new_axis

from iris.cube import CubeList
from iris.util import equalise_attributes

from esmvaltool.diag_scripts.shared import (
    ProvenanceLogger,
    get_diagnostic_filename,
    get_plot_filename,
    group_metadata,
    io,
    run_diagnostic,
    select_metadata,
    sorted_metadata
)

logger = logging.getLogger(Path(__file__).stem)


def log_provenance(filename, ancestors, caption, cfg):
    """Create a provenance record for the output file."""
    provenance = {
        'caption': caption,
        'domains': ['global'],
        'authors': ['swaminathan_ranjini'],
        'projects': ['ukesm'],
        'ancestors': ancestors,
    }
    with ProvenanceLogger(cfg) as provenance_logger:
        provenance_logger.log(filename, provenance)


def calculate_gwl_mm_stats(project_data, gwl_subset_df, window_size, mean_file, stdev_file):
    """Extract window_size year means at specific GWLs from each model and calculate mean and standard deviation"""
    cubes = iris.cube.CubeList()
    
    datasets = gwl_subset_df['Model'].unique()
    for dataset in  datasets:
        #get every exp for which the data is available for
        all_exps_in_dataset = select_metadata(project_data, dataset = dataset)
        for el in all_exps_in_dataset:
            exp = el['exp']            
            path = el['filename']
            cube = iris.load_cube(path)            
            ih.prepare_cube_for_merging(cube, path)            
            #extract window period
            year_of_exceedance = gwl_subset_df[(gwl_subset_df['Model'] == dataset ) &( gwl_subset_df['Exp'] == exp)]['Exceedance_Year'].values[0]
            if(np.isnan(year_of_exceedance)):
                continue
            start_year = int(year_of_exceedance - ((window_size - 1)/2))
            end_year = int(year_of_exceedance + ((window_size - 1)/2))
            logger.info('Model: %s, Exp : %s start year: %s, endyear: %s', dataset, exp, str(start_year), str(end_year)) 
            #Start year Jan 1st (1, 1) and end_year Dec 31st (12, 31)
            cube = extract_time(cube, start_year, 1, 1, end_year, 12, 31)   
            cube = cube.collapsed('time', iris.analysis.MEAN)        
            cubes.append(cube)
    
   # find index of time coord so this can be unified across data sets
   # before merging as the time data points are different across models/scenarios
    index = 0
    for coord in cubes[0].aux_coords:
        if(coord.standard_name == 'time'):
            break
        else:
            index = index + 1
    for c in cubes[1:]:        
        c.remove_coord('time')
        c.add_aux_coord(cubes[0].aux_coords[index])
        

    if(len(cubes) == 0):
        logger.info("No model instances exceed this GWL.")
    elif (len(cubes) == 1):
        iris.save(cubes[0], mean_file)         
        logger.info("No standard deviation calculated for a single instance.")
    else:
        mm_cube = cubes.merge_cube()
        mm_mean_cube =  mm_cube.collapsed(['cube_label'], iris.analysis.MEAN)
        mm_stdev_cube =  mm_cube.collapsed(['cube_label'], iris.analysis.STD_DEV)    
        iris.save(mm_mean_cube, mean_file) 
        iris.save(mm_stdev_cube, stdev_file) 
                
    return 


def main(cfg):

    input_data = cfg['input_data'].values()
    window_size  = cfg['window_size']
    gwls = cfg['gwls']
    pattern = cfg['pattern']

    gwl_filename = io.get_ancestor_file(cfg, pattern)
    logger.info('GWL exceedance years file is %s', gwl_filename)
    gwl_df = pd.read_csv(gwl_filename)
    sep = '_'
    
    projects = []
    for data in input_data:
        #select by by project
        if(data['project'] not in projects):
            projects.append(data['project'])
    
    logger.info('List of Projects: %s', projects)

    for project in projects:
        #get all data sets for project across experiments
        project_data = select_metadata(input_data, project = project)
        for gwl in gwls:
            gwl_subset_df = gwl_df[gwl_df['GWL'] == gwl]
            if(gwl_subset_df.shape[0] > 0):
                logger.info("Calculating means and standard deviations for GWL: %s", str(gwl))
                filename = sep.join([project, 'mm_mean', str(gwl)]) + '.nc'
                mean_file = os.path.join(cfg['work_dir'],filename )
                filename = sep.join([project, 'mm_stdev', str(gwl)]) + '.nc'
                stdev_file = os.path.join(cfg['work_dir'],filename )

                calculate_gwl_mm_stats(project_data, gwl_subset_df, window_size, mean_file, stdev_file)
                

    
    

if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)

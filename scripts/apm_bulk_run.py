#!/usr/bin/env python3
########################################################################
#
# !!! IMPORTANT NOTES: !!!
#
# 1. You should look at the source code in  __BulkRun__.py to
#    have at least general understanding of the internal workflow
# 2. This script will not change the current units in use.
# 3. Inputs that are suppose to be lists needs to be in a list even if it is a single value
# 4. The program limits itself to 90% of the maximum supplied RAM because each
#     simulation requires slightly more than the method I use to estimate
#     the RAM required.
#
# INSTRUCTIONS ON SETTING UP THE INPUTS
#
# Inputs to the bulk run are set up to allow the user the greatest flexibiltiy
# in setting up a run. Input parameters can be defined for a single map or mulitple maps
# or a combination of the two. The format the preprocessing routine expects is a
# list of tuples in this format:
#
# ( [aperture_maps, ..., ...], {params_to_vary_dict}, {file_name_format_dict} )
#
# The list of aperture maps is the list of maps you want to apply the given
# params and filename formats to.
#
# params_to_vary_dict stores lists of values to use for each input parameter,
# i.e. ROUGHNESS: [0.0, 0.1, 0.2] where the key is the first "field" on an
# input line. A field qualifies as a continuous string of characters not separated by a delimiter.
# Input file delimeters are one or more spaces. For example on the input line
# 'OUTLET-SIDE: TOP', 'OUTLET-SIDE' is the key and 'TOP' is the value.
# To vary the outlet side you would use, 'OUTLET-SIDE': ['TOP', 'LEFT', 'RIGHT', 'BOTTOM']
#
# file_name_format_dict follows similar logic as above in respect to keys.
# Filename formats have form of './STATIC_PORTION_OF_NAME-%param_key%-STUFF.EXT'
# The '%param_key%' portion of the name is replaced by the value of that parameter.
# This allows the user to vary a range of parameters and ensure no files are over written.
#
# For convenience a global_run_params and global_file_formats dict
# can be an input to the preprocessing routine. This is used to apply a set
# of params to the entire bulk simulation run. An empty dict can be used in the input
# tuple if only global params are required. Any params specified in an
# input tuple will take precedence over the values in the global params dict.
#
# The user can use any method in the python world to create the list of input
# tuples. I personally use a combination of string formatting, list and dict generation.
#
# A small example of setting up a set of input tuples is show below:
#
########################################################################
#
from ApertureMapModelTools.RunModel import BulkRun

#
# Input tuple setup demo
dir_8 = 'SHEARING_FRAC_TEST7-8'
prefix_8 = ['IS-8_0', 'IS-8_1', 'IS-8_2', 'IS-8_3', 'IS-8_4']
map_format_str = r'.\{0}\{1}_ApertureMapCropped.txt'
test_8_maps = [map_format_str.format(dir_8, pf) for pf in prefix_8]
#
global_file_formats = {
    'SUMMARY-FILE': r'.\{0}\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-LOG.TXT',
    'STAT-FILE': r'.\{0}\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-STAT.CSV',
    'APER-FILE': r'.\{0}\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-APER.CSV',
    'FLOW-FILE': r'.\{0}\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-FLOW.CSV',
    'PRESS-FILE': r'.\{0}\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-PRES.CSV',
    'VTK-FILE': r'.\{0}\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-VTK.vtk',
    'input_file': r'.\{0}\FULL_MAPS\INP_FILES\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-INIT.INP'
}
#
global_run_params = {
    'FRAC-PRESS': ['1000'],
    'MAP': ['1'],
    'ROUGHNESS': ['2.50'],
    'OUTPUT-UNITS': ['PSI, MM, MM^3/MIN'],
    'VOXEL': ['26.8']
}
#
test_8_file_fmts = [
    {k: global_file_formats[k].format(dir_8, prefix_8[0]) for k in global_file_formats},
    {k: global_file_formats[k].format(dir_8, prefix_8[1]) for k in global_file_formats},
    {k: global_file_formats[k].format(dir_8, prefix_8[2]) for k in global_file_formats},
    {k: global_file_formats[k].format(dir_8, prefix_8[3]) for k in global_file_formats},
    {k: global_file_formats[k].format(dir_8, prefix_8[4]) for k in global_file_formats}
]
#
test_8_run_params = [
    {'OUTLET-PRESS': ['995.13', '993.02', '989.04', '977.78', '966.20', '960.53']},
    {'OUTLET-PRESS': ['995.32', '979.55', '945.06', '772.90']},
    {'OUTLET-PRESS': ['997.84', '993.04', '982.18', '957.69', '929.59']},
    {'OUTLET-PRESS': ['997.70', '999.58', '999.40', '998.95', '997.83', '996.50', '994.36']},
    {'OUTLET-PRESS': ['999.70', '999.63', '999.49', '999.22', '998.44', '997.53', '996.82']}
]
#
input_params = [
    #
    # slices are used because a list is expected
    (test_8_maps[0:1], test_8_run_params[0], test_8_file_fmts[0]),
    (test_8_maps[1:2], test_8_run_params[1], test_8_file_fmts[1]),
    (test_8_maps[2:3], test_8_run_params[2], test_8_file_fmts[2]),
    (test_8_maps[3:4], test_8_run_params[3], test_8_file_fmts[3]),
    (test_8_maps[4:5], test_8_run_params[4], test_8_file_fmts[4])
]
# unsetting demo values
del dir_8
del prefix_8
del map_format_str
del test_8_maps
del test_8_file_fmts
del test_8_run_params
del global_file_formats
del global_run_params
del input_params
#
########################################################################
########################################################################
########################################################################
#

# Run Parameters
args = {
    'start_delay': 20.0,
    'spawn_delay': 5.0,
    'retest_delay': 5.0,
    'sys_RAM': 8.0,
    'num_CPUs': 4
    }
base_inp_file = 'FRACTURE_INITIALIZATION.INP'

# Input Parameters
global_file_formats = {}
global_run_params = {}
input_params = []


#
########################################################################
#

# Creating class with given parameters
bulk_run = BulkRun(base_inp_file, **args)

# pre processing the input parameters tuples
bulk_run.process_input_tuples(input_params,
                              default_params=global_run_params,
                              default_name_format=global_file_formats)

# testing simulations (replace 'dry_run' with 'bulk_run' to actually run sims)
bulk_run.dry_run()

# the start() method actually begins the simulations
# bulk_run.start()














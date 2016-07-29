#!/usr/bin/env python3
########################################################################
#
# !!! IMPORTANT NOTES: !!!
#
# 1. You should look at the source code in  __BulkRun__.py to
#    have at least general understanding of the internal workflow
# 2. This script will not change the current units in use.
# 3. Inputs that are suppose to be lists needs to be in a list even
#       if it is a single value
# 4. The program limits itself to 90% of the maximum supplied RAM because each
#     simulation requires slightly more than the method I use to estimate
#     the RAM required.
#
# INSTRUCTIONS ON SETTING UP THE INPUTS
#
# Inputs to the bulk run are set up to allow the user the greatest flexibiltiy
# in setting up a run. Input parameters can be defined for a single map or
# mulitple maps or a combination of the two. The format the preprocessing
# routine expects is a list of tuples in the following format:
#
# ( [aperture_maps, ..., ...], {params_to_vary_dict}, {file_name_format_dict} )
#
# The list of aperture maps is the list of maps you want to apply the given
# params and filename formats to.
#
# params_to_vary_dict stores lists of values to use for each input parameter,
# i.e. ROUGHNESS: [0.0, 0.1, 0.2] where the key is the first "field" on an
# input line. A field qualifies as a continuous string of characters not
# separated by a delimiter. Input file delimeters are one or more spaces.
# For example on the input line 'OUTLET-SIDE: TOP', 'OUTLET-SIDE' is the key
# and 'TOP' is the value. To vary the outlet side you would use,
# 'OUTLET-SIDE': ['TOP', 'LEFT', 'RIGHT', 'BOTTOM']
# You can vary any number of parameters globally or per map.
#
# file_name_format_dict follows similar logic as above in respect to keys.
# Filename formats have form of:
#  './STATIC_PORTION_OF_NAME-%param_keyword%-STATIC-PORTION.EXT'
# The '%param_keyword%' portion of the name is replaced by the value
# of that parameter. This allows the user to vary a range of parameters
# and have names automatically generated to prevent overwrites or ambiguity.
# Extra non-input parameters can be added to use in filename formatting.
# These should be specified on a per map(s) basis and as a list with a
# single value to prevent the non-input parameters creating duplicate runs.
# For example to run an averaged version of a map along with the full
# resolution maps you might add %map_type% somewhere the name format and
# then map_type: ['AVG'] and map_type: ['FULL'] to the parameter dicts of
# each type of map respectively. Because it is a single value when the
# combination of all possible inputs is created the overall total number
# of simulations is not affected. Take care to not accidently
# use an input file keyword when adding formatting params.
#
# For convenience a run_params and file_formats dict can be an input to the
# preprocessing routine as 'defaults'. This is used to apply a set of params
# to the entire run. An empty dict can be used in the input tuple if
# only default params are required. Any parameters or formats specified
# inside an input tuple will take precedence over the values passed in as
# defaults.
#
# The user can use any method in the python world to create the list of input
# tuples. I personally use a combination of string formatting, list
# and dict generation.
#
# A small example of setting up a set of input tuples is show below:
#
########################################################################
#
from ApertureMapModelTools.RunModel import BulkRun

#
# Input tuple setup demo
prefix = ['IS-8_0', 'IS-8_1', 'IS-8_2', 'IS-8_3', 'IS-8_4']
map_format_str = r'./{0}/{1}_ApertureMap.txt'
maps = [map_format_str.format('SHEARING_TEST7-8', pf) for pf in prefix]
#
dir_fmt = './%dir%/%map_type%/'
file_formats = {
    'SUMMARY-FILE': dir_fmt+'{}/{}-OUTLET_PRESS_%OUTLET-PRESS%-LOG.TXT',
    'STAT-FILE': dir_fmt+'{}/{}-OUTLET_PRESS_%OUTLET-PRESS%-STAT.CSV',
    'APER-FILE': dir_fmt+'{}/{}-OUTLET_PRESS_%OUTLET-PRESS%-APER.CSV',
    'FLOW-FILE': dir_fmt+'{}/{}-OUTLET_PRESS_%OUTLET-PRESS%-FLOW.CSV',
    'PRESS-FILE': dir_fmt+'{}/{}-OUTLET_PRESS_%OUTLET-PRESS%-PRES.CSV',
    'VTK-FILE': dir_fmt+'{}/{}-OUTLET_PRESS_%OUTLET-PRESS%.vtk',
    'input_file': dir_fmt+'INP_FILES/{}-OUTLET_PRESS_%OUTLET-PRESS%.INP'
}
#
run_dict = {
    'INLET-PRESS': ['1000'],
    'MAP': ['1'],
    'ROUGHNESS': ['2.50'],
    'OUTPUT-UNITS': ['PSI,MM,MM^3/MIN'],
    'VOXEL': ['26.8'],
    'dir': ['SHEARING_TEST7-8']
}
#
map_file_fmts = [
    {k: file_formats[k].format(prefix[0]) for k in file_formats},
    {k: file_formats[k].format(prefix[1]) for k in file_formats},
    {k: file_formats[k].format(prefix[2]) for k in file_formats},
    {k: file_formats[k].format(prefix[3]) for k in file_formats},
    {k: file_formats[k].format(prefix[4]) for k in file_formats}
]
#
map_run_params = [
    {'OUTLET-PRESS': ['995.13', '993.02', '989.04'], 'map_type':['FULL']},
    {'OUTLET-PRESS': ['995.32', '979.55', '945.06'], 'map_type':['FULL']},
    {'OUTLET-PRESS': ['997.84', '993.04', '982.18'], 'map_type':['FULL']},
    {'OUTLET-PRESS': ['997.70', '999.58', '999.40'], 'map_type':['FULL']},
    {'OUTLET-PRESS': ['999.70', '999.63', '999.49'], 'map_type':['FULL']}
]
#
input_params = [
    # slices are used because a list of maps is expected
    (maps[0:1], map_run_params[0], map_file_fmts[0]),
    (maps[1:2], map_run_params[1], map_file_fmts[1]),
    (maps[2:3], map_run_params[2], map_file_fmts[2]),
    (maps[3:4], map_run_params[3], map_file_fmts[3]),
    (maps[4:5], map_run_params[4], map_file_fmts[4])
]
# unsetting demo values
del prefix
del map_format_str
del maps
del map_file_fmts
del map_run_params
del file_formats
del run_dict
del input_params
#
########################################################################
########################################################################
########################################################################
#

# Run Parameters
args = {
    'start_delay': 20.0,  # initial delay in starting bulk run
    'spawn_delay': 5.0,  # delay in starting new individual simulations
    'retest_delay': 5.0,  # time to wait between checks for completed sims
    'sys_RAM': 8.0,
    'num_CPUs': 4
    }
base_inp_file = 'FRACTURE_INITIALIZATION.INP'

# Input Parameters
file_formats = {}
run_dict = {}
input_params = []


#
########################################################################
#

# Creating class with given parameters
bulk_run = BulkRun(base_inp_file, **args)

# pre processing the input parameters tuples
bulk_run.process_input_tuples(input_params,
                              default_params=run_dict,
                              default_name_format=file_formats)

# testing simulations (replace 'dry_run' with 'bulk_run' to actually run sims)
bulk_run.dry_run()

# the start() method actually begins the simulations
# bulk_run.start()

#
# This script allows the user to set input parameters for the aperture map
# bulk parallel run program. The user updates the parameters and sets up 
# the creation of the inital input list for the requirements of thier bulk run.
#
import re
from ApertureMapModelTools.BulkRun.__base__ import process_input_tuples,bulk_run
#
#
# Parameters
max_CPUs_to_use = 8
max_RAM_to_use = 16.0 #program limits itself to only use 90% of this value
base_inp_file = 'FRACTURE_INITIALIZATION.INP'
aperture_map_delimiter = 'auto'
#
# Setting up inputs
dir_5 = 'SHEARING_FRAC_TEST5'
prefix_5 = ['IS-5_2','IS-5_3','IS-5_4','IS-5_5','IS-5_6','IS-5_7','IS-5_8']
format_str = r'.\{0}\{1}_ApertureMap.txt'
test_5_maps = [format_str.format(dir_5,pf) for pf in prefix_5]
#
dir_6rb = 'SHEARING_FRAC_TEST6-ROLLING_BALL'
prefix_6rb = ['IS-6_0','IS-6_1','IS-6_2','IS-6_3','IS-6_4']
format_str = r'.\{0}\{1}_ApertureMapRB.csv'
test_6rb_maps = [format_str.format(dir_6rb,pf) for pf in prefix_6rb]

#
dir_6v = 'SHEARING_FRAC_TEST6-VERTICAL'
prefix_6v = ['IS-6_0','IS-6_1','IS-6_2','IS-6_3','IS-6_4']
format_str = r'.\{0}\{1}_ApertureMapV.csv'
test_6v_maps = [format_str.format(dir_6v,pf) for pf in prefix_6v]

#
dir_8 = 'SHEARING_FRAC_TEST7-8'
prefix_8 = ['IS-8_0','IS-8_1','IS-8_2','IS-8_3','IS-8_4']
format_str = r'.\{0}\{1}_ApertureMapCropped.txt'
test_8_maps = [format_str.format(dir_8,pf) for pf in prefix_8]
#
global_file_formats = {
    'SUMMARY-PATH' : r'.\TESTING\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-LOG.TXT',
    'STAT-FILE' : r'.\TESTING\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-STAT.CSV',
    'APER-FILE' : r'.\TESTING\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-APER.CSV',
    'FLOW-FILE' : r'.\TESTING\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-FLOW.CSV',
    'PRESS-FILE' : r'.\TESTING\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-PRES.CSV',
    'VTK-FILE' : r'.\TESTING\FULL_MAPS\{1}\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-VTK.vtk',
    'input_file' : r'.\TESTING\FULL_MAPS\INP_FILES\{1}-FULL-OUTLET_PRESS_%OUTLET-PRESS%-INIT.INP',
}
#
global_run_params = {
    'FRAC-PRESS' : ['1000'],
    'MAP' : ['1'],
    'ROUGHNESS' : ['2.50'],
    'OUTPUT-UNITS' : ['PSI,MM,MM^3/MIN'],
    'VOXEL' : ['26.8']
}
#
input_params = [
    #([test_5_maps[0]], {'OUTLET-PRESS' : ['999.90','999.80','999.60','999.40']}, {k : global_file_formats[k].format(dir_5,prefix_5[0]) for k in global_file_formats}),
    #([test_5_maps[1]], {'OUTLET-PRESS' : ['999.90','999.80','999.60','999.40']}, {k : global_file_formats[k].format(dir_5,prefix_5[1]) for k in global_file_formats}),
    #([test_5_maps[2]], {'OUTLET-PRESS' : ['999.95','999.90','999.70','999.50']}, {k : global_file_formats[k].format(dir_5,prefix_5[2]) for k in global_file_formats}),
    #([test_5_maps[3]], {'OUTLET-PRESS' : ['999.95','999.80','999.60','999.30']}, {k : global_file_formats[k].format(dir_5,prefix_5[3]) for k in global_file_formats}),
    #([test_5_maps[4]], {'OUTLET-PRESS' : ['999.95','999.90','999.70','999.50']}, {k : global_file_formats[k].format(dir_5,prefix_5[4]) for k in global_file_formats}),
    #([test_5_maps[5]], {'OUTLET-PRESS' : ['999.95','999.90','999.70','999.50']}, {k : global_file_formats[k].format(dir_5,prefix_5[5]) for k in global_file_formats}),
    #([test_5_maps[6]], {'OUTLET-PRESS' : ['999.95','999.90','999.70','999.50']}, {k : global_file_formats[k].format(dir_5,prefix_5[6]) for k in global_file_formats}),
    #
    #([test_6rb_maps[0]], {'OUTLET-PRESS' : ['974.20','975.91','936.82','906.71']}, {k : global_file_formats[k].format(dir_6rb,prefix_6rb[0]) for k in global_file_formats}),
    #([test_6rb_maps[1]], {'OUTLET-PRESS' : ['997.35','996.82','995.96','995.01']}, {k : global_file_formats[k].format(dir_6rb,prefix_6rb[1]) for k in global_file_formats}),
    #([test_6rb_maps[2]], {'OUTLET-PRESS' : ['998.68','998.47','998.39','998.29','997.79']}, {k : global_file_formats[k].format(dir_6rb,prefix_6rb[2]) for k in global_file_formats}),
    #
    #([test_6v_maps[0]], {'OUTLET-PRESS' : ['974.20','975.91','936.82','906.71']}, {k : global_file_formats[k].format(dir_6v,prefix_6v[0]) for k in global_file_formats}),
    #([test_6v_maps[1]], {'OUTLET-PRESS' : ['997.35','996.82','995.96','995.01']}, {k : global_file_formats[k].format(dir_6v,prefix_6v[1]) for k in global_file_formats}),
    #([test_6v_maps[2]], {'OUTLET-PRESS' : ['998.68','998.47','998.39','998.29','997.79']}, {k : global_file_formats[k].format(dir_6v,prefix_6v[2]) for k in global_file_formats}),
    #
    ([test_8_maps[0]], {'OUTLET-PRESS' : ['995.13','993.02','989.04','977.78','966.20','960.53']}, {k : global_file_formats[k].format(dir_8,prefix_8[0]) for k in global_file_formats}),
    ([test_8_maps[1]], {'OUTLET-PRESS' : ['995.32','979.55','945.06','772.90']}, {k : global_file_formats[k].format(dir_8,prefix_8[1]) for k in global_file_formats}),
    ([test_8_maps[2]], {'OUTLET-PRESS' : ['997.84','993.04','982.18','957.69','929.59']}, {k : global_file_formats[k].format(dir_8,prefix_8[2]) for k in global_file_formats}),
    ([test_8_maps[3]], {'OUTLET-PRESS' : ['997.70','999.58','999.40','998.95','997.83','996.50','994.36']}, {k : global_file_formats[k].format(dir_8,prefix_8[3]) for k in global_file_formats}),
    ([test_8_maps[4]], {'OUTLET-PRESS' : ['999.70','999.63','999.49','999.22','998.44','997.53','996.82']}, {k : global_file_formats[k].format(dir_8,prefix_8[4]) for k in global_file_formats})
]
#
########################################################################
#######################################################################
# 
#
# pre processing the input params list of tuples
simulation_inputs = process_input_tuples(input_params,global_run_params)
#
# beginning simulations
bulk_run(num_CPUs = max_CPUs_to_use,
         sys_RAM = max_RAM_to_use,
         sim_inputs = simulation_inputs,
         delim = aperture_map_delimiter,
         init_infile = base_inp_file)















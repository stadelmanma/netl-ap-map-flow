#!/usr/bin/env python3
import argparse
from argparse import RawDescriptionHelpFormatter
import logging
import os
from subprocess import call as subp_call
from sys import argv
from ApertureMapModelTools import DataField, files_from_directory
from ApertureMapModelTools.OpenFoamExport import OpenFoamExport, OpenFoamFile
from ApertureMapModelTools.OpenFoamExport import BlockMeshDict, OpenFoamDict
from ApertureMapModelTools.RunModel import InputFile
from ApertureMapModelTools.UnitConversion import get_conversion_factor
#
#
########################################################################
#
desc_str = r"""
Description: Generates a complete OpenFoam simulation from an APM-MODEL
input file and existing OpenFoam files which are used as templates.

Written By: Matthew stadelman
Date Written: 2015/07/25
Last Modfied: 2016/07/25
"""

interactive_message = r"""
-------------------------------------------------------------------------------
apm_open_foam_export script has been run in interactive mode

The following global variables have been defined:
    raw_files - list of file names in searched directories
    block_mesh - BlockMeshDict object generated if input file was passed in
    foam_files - dictionary of OpenFoam files generated
    apm_input_file - InputFile object if an input file was passed in
    map_data_field - DataField object storing aperture map from apm_input_file
    namespace - argparse namespace object of command line args used
-------------------------------------------------------------------------------
"""
#
# creating arg parser
parser = argparse.ArgumentParser(description=desc_str,
                                 formatter_class=RawDescriptionHelpFormatter)

parser.add_argument('-f', '--force', action='store_true',
                    help='''"force/overwrite mode",
                    allows program to overwrite existing files''')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='''"verbose mode", extra messages are printed to
                    the screen''')

parser.add_argument('-i', '--interactive', action='store_true',
                    help='''"interactive mode", processes commandline arguments
                    inside the spawned python intepreter''')

parser.add_argument('--no-interactive', action='store_true',
                    help='''Internal arg used to prevent run_interactive
                         from looping''')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''"output to", outputs all files to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('-r', '--read-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''"read from", reads existing OpenFoam files from
                    the supplied directory. If not specfied will read files
                    from current directory.''')

parser.add_argument('input_file', nargs='?', type=os.path.realpath,
                    help='APM-MODEL input file to read in')
#
# globals defined for easier interactive use
raw_files = None
block_mesh = None
foam_files = {}
apm_input_file = None
map_data_field = None
namespace = None
#
########################################################################


def apm_open_foam_export():
    r"""
    Handles processing of commandline args and generation of open foam files
    """
    global namespace
    namespace = parser.parse_args()
    carg_list = argv
    #
    if namespace.verbose:
        fmt = "[%(filename)s:%(levelname)s:%(lineno)s - %(funcName)s] %(message)s"
        logging.basicConfig(format=fmt, level=logging.DEBUG)
    #
    if namespace.interactive and not namespace.no_interactive:
        run_interactive(carg_list)
        return
    #
    load_foam_files()
    if namespace.input_file:
        load_inp_file()
    #
    if namespace.interactive:
        print(interactive_message)


def run_interactive(carg_list):
    r"""
    Creates an interactive session to manually update files
    """
    cmd = ['python3', '-i'] + carg_list + ['--no-interactive']
    subp_call(cmd)


def load_foam_files():
    r"""
    Loads any existing files from the supplied directory path. Only checks for
    local files and any files in constant/ system if the directories exist.
    """
    global namespace, raw_files, foam_files
    #
    # checking specific directories as well as current one
    con_path = os.path.join(namespace.read_dir, 'constant')
    sys_path = os.path.join(namespace.read_dir, 'system')
    zero_path = os.path.join(namespace.read_dir, '0')
    #
    # non-recursively loading files
    #
    raw_files = []
    for path in [namespace.read_dir, con_path, sys_path, zero_path]:
        path = os.path.realpath(path)
        if os.path.exists(path):
            raw_files += files_from_directory(path, '*', deep=False)
    #
    # processing valid OpenFoamFiles
    for file in raw_files:
        of_file = None
        try:
            of_file = OpenFoamFile.init_from_file(file)
            key = '{location}.{object}'.format(**of_file.head_dict)
            key = key.replace('"', '')
            foam_files[key] = of_file
        except Exception as err:
            msg = 'Skipping file: {} - Encountered {}: {}'
            msg = msg.format(file, err.__class__.__name__, str(err))
            logging.debug(msg)


def load_inp_file():
    r"""
    Loads in an APM-MODEL input file if it was supplied and pulls out
    required information.
    """
    global namespace, apm_input_file, map_data_field, block_mesh
    apm_input_file = InputFile(namespace.input_file)
    #
    # building actual path to map file based on input file location
    file_path = os.path.realpath(namespace.input_file)
    map_path = apm_input_file['APER-MAP'].value
    map_path = os.path.join(os.path.split(file_path)[0], map_path)
    map_path = os.path.realpath(map_path)
    #
    try:
        map_data_field = DataField(map_path)
    except FileNotFoundError:
        logging.warn('Aperture map file was not found at path: '+map_path)
        return
    #
    # applying any geometric changes needed to the fracture data
    if 'MAP' in apm_input_file:
        avg_fact = float(apm_input_file['MAP'].value)
    #
    if 'ROUGHNESS' in apm_input_file:
        value = float(apm_input_file['ROUGHNESS'].value)
        map_data_field.data_map = map_data_field.data_map - value
    #
    if 'HIGH-MASK' in apm_input_file:
        value = float(apm_input_file['HIGH-MASK'].value)
        map_data_field.data_map[map_data_field.data_map > value] = value
    #
    if 'LOW-MASK' in apm_input_file:
        value = float(apm_input_file['LOW-MASK'].value)
        map_data_field.data_map[map_data_field.data_map < value] = value
    #
    # setting transport and bc params from file
    input_params = [
        ('INLET-PRESS', 'inlet_p', None),
        ('OUTLET-PRESS', 'outlet_p', None),
        ('INLET-RATE', 'inlet_rate', None),
        ('OUTLET-RATE', 'outlet_rate', None),
        ('FLUID-VISCOSITY', 'fluid_visc', 0.001),
        ('FLUID-DENSITY', 'fluid_dens', 1000)
    ]
    sim_params = {}
    for keyword, key, default in input_params:
        sim_params[key] = default
        #
        if keyword in apm_input_file:
            if apm_input_file[keyword].commented_out:
                continue
            try:
                value = float(apm_input_file[keyword].value)
                unit = apm_input_file[keyword].unit
                sim_params[key] = value * get_conversion_factor(unit)
            except (KeyError, ValueError) as err:
                msg = 'Could not process input line: {} - Encountered {}: {}'
                msg = msg.format(apm_input_file[keyword].line,
                                 err.__class__.__name__,
                                 str(err))
                logging.warn(msg)

    #
    # getting inlet/outlet sides
    sides = {'left': 'right', 'right': 'left', 'top': 'bottom', 'bottom': 'top'}
    sim_params['inlet'] = sides[apm_input_file['OUTLET-SIDE'].value.lower()]
    sim_params['outlet'] = apm_input_file['OUTLET-SIDE'].value.lower()
    namespace.sim_params = sim_params
    #
    # setting mesh parameters
    mesh_params = {
        'numbersOfCells': '(5 5 5)',
        'boundary.'+sim_params['inlet']+'.type': 'patch',
        'boundary.'+sim_params['outlet']+'.type': 'patch'
    }
    #
    value = float(apm_input_file['VOXEL'].value)
    unit = apm_input_file['VOXEL'].unit
    mesh_params['convertToMeters'] = value * get_conversion_factor(unit)
    #
    # creating blockMeshDict file
    block_mesh = BlockMeshDict(map_data_field, avg_fact, mesh_params)


def generate_p_file():
    r"""
    Handles creation of the p file in the zero directory
    """
    #
    # fetching or creating p file
    if '0.p' in foam_files:
        p_file = foam_files['0.p']
    else:
        p_file = OpenFoamFile('0', 'p', class_name='volScalarField')
        p_file['dimensions'] = '[0 2 -2 0 0 0 0]'
        p_file['internalField'] = 'uniform 0'
        foam_files['0.p'] = p_file
    #
    # creating boundaryField dict and registering it with the p_file
    bound_field = OpenFoamDict('boundaryField')
    p_file[bound_field.name] = bound_field
    #
    # setting initial values to zeroGradient for all sides
    for side in ['left', 'right', 'front', 'back', 'top', 'bottom']:
        side_dict = OpenFoamDict(side)
        side_dict['type'] = 'zeroGradient'
#
########################################################################
#
# Runs the function if being invoked directly, acts as a module otherwise.
if __name__ == '__main__':
    apm_open_foam_export()

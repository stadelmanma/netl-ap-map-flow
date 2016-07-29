#!/usr/bin/env python3
import argparse
from argparse import RawDescriptionHelpFormatter
import logging
import os
from subprocess import call as subp_call
from sys import argv
import scipy as sp
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
    export - OpenFoamExport class holding all of the data
    raw_files - list of file names in searched directories
    block_mesh - BlockMeshDict object generated if input file was passed in
    foam_files - dictionary of OpenFoam files generated
    apm_input_file - InputFile object if an input file was passed in
    map_data_field - DataField object storing aperture map from apm_input_file
    namespace - argparse namespace object of command line args used

Files are not automatically written in interactive mode use
write_all_files() to properly generate them in the output directory
specified by the -o flag.

Alternatively call the .write_foam_file method on the individual files
you wish to write out setting the paths as you need.
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
export = None
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
    global namespace, export
    export = OpenFoamExport()
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
    # loading existing files and generating files based on inputs
    load_foam_files()
    if namespace.input_file:
        load_inp_file()
        generate_trans_props()
        generate_p_file()
        if map_data_field is None:
            msg = 'Cannot calculate flow velocities without an aperture map'
            logging.warn(msg)
        else:
            generate_U_file()
    #
    if namespace.interactive:
        print(interactive_message)
        return
    #
    write_all_files()


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
    global namespace, export, raw_files, foam_files
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
            name = os.path.basename(file)
            location = os.path.split(os.path.dirname(file))[1]
            key = '{0}.{1}'.format(location, name)
            key = key.replace('"', '')
            foam_files[key] = of_file
        except Exception as err:
            msg = 'Skipping file: {} - {}: {}'
            msg = msg.format(os.path.relpath(file),
                             err.__class__.__name__,
                             str(err))
            logging.debug(msg)
    export.foam_files = foam_files


def load_inp_file():
    r"""
    Loads in an APM-MODEL input file if it was supplied and pulls out
    required information.
    """
    global namespace, export, apm_input_file, map_data_field, block_mesh
    #
    # loading fiel and getting all uncommented lines
    apm_input_file = InputFile(namespace.input_file)
    input_args = apm_input_file.get_uncommented_values()
    #
    # building actual path to map file based on input file location
    file_path = os.path.realpath(namespace.input_file)
    map_path = input_args['APER-MAP'].value
    map_path = os.path.join(os.path.split(file_path)[0], map_path)
    map_path = os.path.realpath(map_path)
    #
    try:
        map_data_field = DataField(map_path)
    except FileNotFoundError:
        logging.warn('Aperture map file was not found at path: '+map_path)
    #
    # setting transport and bc params from file
    input_params = [
        ('MAP', 'avg_fact', 1.0),
        ('HIGH-MASK', 'high_mask', 1.0E6),
        ('LOW-MASK', 'low_mask', 0.0),
        ('ROUGHNESS', 'roughness', 0.0),
        ('VOXEL', 'voxel_size', 1.0),
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
        # checking if keyword exists
        if keyword not in input_args:
            continue
        # setting value of keywork
        value = float(input_args[keyword].value)
        unit = input_args[keyword].unit
        sim_params[key] = value
        if not unit:
            continue
        # converting unit of value if needed
        try:
            sim_params[key] = value * get_conversion_factor(unit)
        except (KeyError, ValueError) as err:
            del sim_params[key]
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
    if map_data_field is None:
        return
    #
    # applying any geometric changes needed to the fracture data
    value = sim_params['roughness']
    map_data_field.data_map = map_data_field.data_map - value
    map_data_field.data_vector = map_data_field.data_vector - value
    #
    value = sim_params['high_mask']
    map_data_field.data_map[map_data_field.data_map > value] = value
    map_data_field.data_vector[map_data_field.data_vector > value] = value
    #
    value = sim_params['low_mask']
    map_data_field.data_map[map_data_field.data_map < value] = value
    map_data_field.data_vector[map_data_field.data_vector < value] = value
    #
    # setting mesh parameters
    mesh_params = {
        'convertToMeters': sim_params['voxel_size'],
        'numbersOfCells': '(5 5 5)',
        'boundary.'+sim_params['inlet']+'.type': 'patch',
        'boundary.'+sim_params['outlet']+'.type': 'patch'
    }
    #
    # creating blockMeshDict file
    block_mesh = BlockMeshDict(map_data_field,
                               sim_params['avg_fact'],
                               mesh_params)
    export.block_mesh_dict = block_mesh


def generate_trans_props():
    r"""
    Handles updating the transport properties file with a density and
    viscosity used in the apm model input file
    """
    #
    global namespace
    #
    # fetching or creating transportProperties file
    try:
        trans_file = foam_files['constant.transportProperties']
    except KeyError:
        trans_file = OpenFoamFile('constant', 'transportProperties')
        foam_files['constant.transportProperties'] = trans_file
    #
    dens = namespace.sim_params['fluid_dens']
    visc = namespace.sim_params['fluid_visc']
    #
    trans_file['nu'] = 'nu  [ 0  2 -1 0 0 0 0 ] {}'.format(visc/dens)
    trans_file['rho'] = 'rho  [ 1  -3 0 0 0 0 0 ] {}'.format(dens)


def generate_p_file():
    r"""
    Handles creation of the p file in the zero directory
    """
    #
    global namespace
    #
    # fetching or creating p file
    try:
        p_file = foam_files['0.p']
    except KeyError:
        p_file = OpenFoamFile('0', 'p', class_name='volScalarField')
        p_file['dimensions'] = '[0 2 -2 0 0 0 0]'
        p_file['internalField'] = 'uniform 0'
        foam_files['0.p'] = p_file
    #
    # fetching boundary field dict
    try:
        bound_field = p_file['boundaryField']
    except KeyError:
        bound_field = OpenFoamDict('boundaryField')
        p_file[bound_field.name] = bound_field
    #
    # setting initial values to zeroGradient for all sides
    for side in ['left', 'right', 'front', 'back', 'top', 'bottom']:
        side_dict = OpenFoamDict(side)
        side_dict['type'] = 'zeroGradient'
        bound_field[side] = side_dict
    #
    # adding any BCs
    if namespace.sim_params['inlet_p'] is not None:
        value = namespace.sim_params['inlet_p']
        value = 'uniform {}'.format(value/namespace.sim_params['fluid_dens'])
        side = namespace.sim_params['inlet']
        bound_field[side]['type'] = 'fixedValue'
        bound_field[side]['value'] = value
    #
    if namespace.sim_params['outlet_p'] is not None:
        value = namespace.sim_params['outlet_p']
        value = 'uniform {}'.format(value/namespace.sim_params['fluid_dens'])
        side = namespace.sim_params['outlet']
        bound_field[side]['type'] = 'fixedValue'
        bound_field[side]['value'] = value


def generate_U_file():
    r"""
    Handles creation of the U file in the zero directory
    """
    #
    global namespace, map_data_field

    def calc_velocity(vol_flow, side):
        r"""Calculates the velocity field for a rate BC"""
        #
        x_vel = 0.0
        z_vel = 0.0
        avg_fact = namespace.sim_params['avg_fact']
        #
        if side == 'top':
            avg_b = sp.average(map_data_field.data_map[-1, :])
            axis_len = avg_fact * len(map_data_field.data_map[-1, :])
            z_vel = vol_flow/(avg_b * axis_len)
        elif side == 'bottom':
            vol_flow = -vol_flow
            avg_b = sp.average(map_data_field.data_map[0, :])
            axis_len = avg_fact * len(map_data_field.data_map[0, :])
            z_vel = vol_flow/(avg_b * axis_len)
        elif side == 'left':
            vol_flow = -vol_flow
            avg_b = sp.average(map_data_field.data_map[:, 0])
            axis_len = avg_fact * len(map_data_field.data_map[:, 0])
            x_vel = vol_flow/(avg_b * axis_len)
        elif side == 'right':
            avg_b = sp.average(map_data_field.data_map[:, -1])
            axis_len = avg_fact * len(map_data_field.data_map[:, -1])
            x_vel = vol_flow/(avg_b * axis_len)
        else:
            raise ValueError('Invalid side given: '+side)
        #
        return 'uniform ({} 0.0 {})'.format(x_vel, z_vel)
    #
    # fetching or creating U file
    try:
        u_file = foam_files['0.U']
    except KeyError:
        u_file = OpenFoamFile('0', 'U', class_name='volVectorField')
        u_file['dimensions'] = '[0 1 -1 0 0 0 0]'
        u_file['internalField'] = 'uniform (0 0 0)'
        foam_files['0.U'] = u_file
    #
    # fetching boundaryField dict
    try:
        bound_field = u_file['boundaryField']
    except KeyError:
        bound_field = OpenFoamDict('boundaryField')
        u_file[bound_field.name] = bound_field
    #
    # setting up default values for all sides as no-slip bounds
    for side in ['left', 'right', 'front', 'back', 'top', 'bottom']:
        side_dict = OpenFoamDict(side)
        side_dict['type'] = 'fixedValue'
        side_dict['value'] = 'uniform (0 0 0)'
        bound_field[side] = side_dict
    #
    # adding any BCs
    if namespace.sim_params['inlet_p'] is not None:
        side = namespace.sim_params['inlet']
        bound_field[side]['type'] = 'zeroGradient'
        del bound_field[side]['value']
    #
    if namespace.sim_params['outlet_p'] is not None:
        side = namespace.sim_params['outlet']
        bound_field[side]['type'] = 'zeroGradient'
        del bound_field[side]['value']
    #
    if namespace.sim_params['inlet_rate'] is not None:
        value = namespace.sim_params['inlet_rate']
        side = namespace.sim_params['inlet']
        bound_field[side]['type'] = 'fixedValue'
        bound_field[side]['value'] = calc_velocity(value, side)
    #
    if namespace.sim_params['outlet_rate'] is not None:
        value = namespace.sim_params['outlet_rate']
        side = namespace.sim_params['outlet']
        bound_field[side]['type'] = 'fixedValue'
        bound_field[side]['value'] = calc_velocity(value, side)


def write_all_files(overwrite=False):
    r"""
    Writes all of the existing input files generated and the blockMeshDict
    file to the proper directory given by the namespace object
    """
    #
    global namespace, export, block_mesh
    overwrite = overwrite or namespace.force
    #
    try:
        if block_mesh is not None:
            block_mesh.write_mesh_file(path=namespace.output_dir,
                                       create_dirs=True,
                                       overwrite=overwrite)
        export.write_foam_files(path=namespace.output_dir, overwrite=overwrite)
    except FileExistsError as err:
        logging.fatal('Specify the "-f" flag to automatically overwrite files')
        raise err
#
########################################################################
#
# Runs the function if being invoked directly, acts as a module otherwise.
if __name__ == '__main__':
    apm_open_foam_export()

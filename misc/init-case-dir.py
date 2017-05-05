#!/usr/bin/env python3
r"""
Description: Automatically sets up an OpenFoam case based on the chosen
template case and command line args. This script was designed to generate
a full case and run_script for use on the NETL Joule Supercomputer. The
run_script is assumed to be inside the directory being used as a template case

| Written By: Matthew stadelman
| Date Written: 2016/10/11
| Last Modfied: 2016/10/20
"""
#
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
from shutil import rmtree
import os
from apmapflow import _get_logger, set_main_logger_level, DataField
from apmapflow.openfoam import OpenFoamFile
from apmapflow.unit_conversion import convert_value


usage_str = '%(prog)s [-hvf] job_dir aper_map [job_name] [options]'

#
# fetching logger
logger = _get_logger('apmapflow.Scripts')
#
# setting up the argument parser
parser = argparse.ArgumentParser(description=__doc__,
                                 usage=usage_str,
                                 formatter_class=RawDesc)
#
# defining argument groups
map_group = parser.add_argument_group(title='Aperture Map Params')
bc_group = parser.add_argument_group(title='Boundary Conditions')
sys_group = parser.add_argument_group(title='System Settings')
trans_group = parser.add_argument_group(title='Transport Properties')

# adding non-grouped args
parser.add_argument('job_dir', type=os.path.realpath,
                    help="directory to output case to")
parser.add_argument('job_name', nargs='?', default=None,
                    help="name of job in run script")
parser.add_argument('-v', '--verbose', action='store_true',
                    help="prints debug messages (default: %(default)s)")
parser.add_argument('-f', '--force', action='store_true',
                    help="removes existing case directory (default: %(default)s)")
parser.add_argument('--no-hpcee', action='store_true',
                    help="allow any number of cores and doesn't format run_script")
parser.add_argument('--template', type=os.path.realpath,
                    default=os.path.realpath('template-case'),
                    help="template case directory (default: ./template-case)")
parser.add_argument('--script-name', default='run_openfoam',
                    help="hpcee run script (default: %(default)s)")
#
map_group.add_argument('aper_map', type=os.path.realpath,
                       help="aperture map to use with case")
map_group.add_argument('--avg-fact', type=int, default=1,
                       help="horizontal averaging factor (default: %(default)s)")
map_group.add_argument('--voxel-size', type=float, default=2.680E-5,
                       help="voxel size in meters (default: %(default)s)")
#
bc_group.add_argument('--inlet-side', default='bottom',
                      help="(default: %(default)s)")
bc_group.add_argument('--outlet-side', default='top',
                      help="(default: %(default)s)")
bc_group.add_argument('--inlet-q', default=None, nargs=4,
                      metavar=('    qx', 'qy', 'qz', '[units]'))
bc_group.add_argument('--outlet-q', default=None, nargs=4,
                      metavar=('    qx', 'qy', 'qz', '[units]'))
bc_group.add_argument('--inlet-p', default=None, nargs=2,
                      metavar=('    value', '[units]'))
bc_group.add_argument('--outlet-p', default=None, nargs=2,
                      metavar=('    value', '[units]'))
#
sys_group.add_argument('--end-time', default=750, type=int,
                       help="number of iterations to perform (default: %(default)s)")
sys_group.add_argument('--num-cores', default=64, type=int,
                       help="number of cpus to utilize (default: %(default)s)")
#
trans_group.add_argument('--viscosity', default=[0.001, 'pa*s'], nargs=2,
                         metavar=('    value', '[units]'),
                         help='(default: 0.001 pa*s)')
trans_group.add_argument('--density', default=[1000, 'kg/m^3'], nargs=2,
                         metavar=('    value', '[units]'),
                         help='(default: 1000 kg/m^3)')
#
###############################################################################


def init_case_dir():
    r"""
    Parses command line arguments and delegates tasks to helper functions
    """
    arg_dict = args.__dict__

    # checking args
    if args.verbose:
        set_main_logger_level('debug')
    check_args()

    # creating job directory
    try:
        os.makedirs(args.job_dir)
    except FileExistsError as err:
        if args.force:
            rmtree(args.job_dir)
            os.makedirs(args.job_dir)
        else:
            raise err

    # copying contents of template directory to job_dir
    os.system('cp -r {}/* {}'.format(args.template, args.job_dir))

    # copying over the aperture map and updating args
    os.system('cp {} {}'.format(args.aper_map, args.job_dir))
    args.aper_map = os.path.join(args.job_dir, os.path.basename(args.aper_map))

    #
    update_system_files(**arg_dict)
    update_transport_props(**arg_dict)
    update_u_file(**arg_dict)
    update_p_file(**arg_dict)

    #
    # updating run script
    if args.no_hpcee is False:
        with open(os.path.join(args.job_dir, args.script_name), 'r+') as run:
            content = run.read()
            content = content.format(**arg_dict)
            run.seek(0)
            run.truncate()
            run.write(content)


def check_args():
    r"""
    Ensures a valid combination of arguments was supplied.
    """
    #
    if args.num_cores % 16 > 0 and args.no_hpcee is False:
        msg = 'num-cores must be a multiple of 16 unless using --no-hpcee flag'
        parser.error(msg)
    #
    if args.job_name is None:
        args.job_name = os.path.basename(args.job_dir)
    if not os.path.isfile(args.aper_map):
        parser.error('No such file: '+args.aper_map)
    args.scr_job_dir = os.path.basename(args.job_dir)

    # checking if any exclusive args were doubled up on
    msg = 'only "--{}" or "--{}" can be specified, not both.'
    if args.inlet_p and args.inlet_q:
        parser.error(msg.format('inlet-p', 'inlet-q'))
    if args.outlet_p and args.outlet_q:
        parser.error(msg.format('outlet-p', 'outlet-q'))
    if args.inlet_q and args.outlet_q:
        parser.error(msg.format('inlet-q', 'outlet-q'))

    # checking that at least one inlet and outlet BC was supplied
    msg = ' "--{}" or "--{}" boundary condition needs to be specified.'
    if args.inlet_p is None and args.inlet_q is None:
        parser.error(msg.format('inlet-p', 'inlet-q'))
    if args.outlet_p is None and args.outlet_q is None:
        parser.error(msg.format('outlet-p', 'outlet-q'))


def update_system_files(job_dir, **kwargs):
    r"""
    Updates the controlDict and decomposeParDict
    """
    #
    foam_file = OpenFoamFile(os.path.join(job_dir, 'system', 'controlDict'))
    foam_file['endTime'] = kwargs['end_time']
    foam_file.write_foam_file(path=job_dir, overwrite=True)
    #
    foam_file = os.path.join(job_dir, 'system', 'decomposeParDict')
    foam_file = OpenFoamFile(foam_file)
    foam_file['numberOfSubdomains'] = kwargs['num_cores']
    foam_file.write_foam_file(path=job_dir, overwrite=True)


def update_transport_props(job_dir, **kwargs):
    r"""
    Updates the constant/transportProperties file. Updates the args object
    to have SI values for density and viscosity.
    """
    # loading file
    foam_file = os.path.join(job_dir, 'constant', 'transportProperties')
    foam_file = OpenFoamFile(foam_file)

    # converting values to SI
    density = kwargs['density']
    density = [convert_value(float(density[0]), density[1]), 'kg/m^3']
    #
    viscosity = kwargs['viscosity']
    viscosity = [convert_value(float(viscosity[0]), viscosity[1]), 'pa*s']

    # ouputting SI values to global args object
    args.density = density
    args.viscosity = viscosity
    viscosity = viscosity[0]/density[0]

    # setting kinematic viscosity values
    fmt = 'nu  [ 0  2 -1 0 0 0 0 ] {:0.6e};'
    foam_file['nu'] = fmt.format(viscosity)
    #
    fmt = 'nu0 [ 0 2 -1 0 0 0 0 ] {:0.6e}'
    foam_file['CrossPowerLawCoeffs']['nu0'] = fmt.format(viscosity)
    foam_file['BirdCarreauCoeffs']['nu0'] = fmt.format(viscosity)
    #
    fmt = 'nuInf [ 0 2 -1 0 0 0 0 ] {:0.6e}'
    foam_file['CrossPowerLawCoeffs']['nuInf'] = fmt.format(viscosity)
    foam_file['BirdCarreauCoeffs']['nuInf'] = fmt.format(viscosity)

    # setting density value
    fmt = 'rho  [ 1  -3 0 0 0 0 0 ] {:0.6e}'
    foam_file['rho'] = fmt.format(density[0])
    foam_file.write_foam_file(path=job_dir, overwrite=True)


def update_u_file(job_dir, **kwargs):
    r"""
    Updates the 0/U file
    """
    aper_map = DataField(kwargs['aper_map'])
    p_file = OpenFoamFile(os.path.join(job_dir, '0', 'p'))
    u_file = OpenFoamFile(os.path.join(job_dir, '0', 'U'))
    inlet_side = kwargs['inlet_side']
    outlet_side = kwargs['outlet_side']
    vox = kwargs['voxel_size']
    avg = kwargs['avg_fact']
    #
    area_dict = {
        'left': sum(aper_map.data_map[:, 0] * vox**2 * avg),
        'right': sum(aper_map.data_map[:, -1] * vox**2 * avg),
        'top': sum(aper_map.data_map[-1, :] * vox**2 * avg),
        'bottom': sum(aper_map.data_map[0, :] * vox**2 * avg)
    }

    # calculating SI velocities
    if kwargs['inlet_q']:
        vel = kwargs['inlet_q'][0:3]
        vel = [convert_value(float(v), kwargs['inlet_q'][3]) for v in vel]
        vel = vel/area_dict[inlet_side]
        vel = 'uniform ({} {} {})'.format(*vel)
        #
        u_file['boundaryField'][inlet_side]['type'] = 'fixedValue'
        u_file['boundaryField'][inlet_side]['value'] = vel
        #
        p_file['boundaryField'][inlet_side]['type'] = 'zeroGradient'
        p_file['boundaryField'][inlet_side].pop('value', None)
    #
    if kwargs['outlet_q']:
        vel = kwargs['outlet_q'][0:3]
        vel = [convert_value(float(v), kwargs['outlet_q'][3]) for v in vel]
        vel = vel/area_dict[outlet_side]
        vel = 'uniform ({} {} {})'.format(*vel)
        #
        u_file['boundaryField'][outlet_side]['type'] = 'fixedValue'
        u_file['boundaryField'][outlet_side]['value'] = vel
        p_file['boundaryField'][outlet_side]['type'] = 'zeroGradient'
        p_file['boundaryField'][outlet_side].pop('value', None)
    #
    p_file.write_foam_file(path=job_dir, overwrite=True)
    u_file.write_foam_file(path=job_dir, overwrite=True)


def update_p_file(job_dir, inlet_side=None, outlet_side=None, **kwargs):
    r"""
    Updates the 0/p file
    """
    # loading files
    p_file = OpenFoamFile(os.path.join(job_dir, '0', 'p'))
    u_file = OpenFoamFile(os.path.join(job_dir, '0', 'U'))

    # setting pressure BCs and modifying velocity BCs
    if kwargs['inlet_p']:
        p_val = convert_value(float(kwargs['inlet_p'][0]), kwargs['inlet_p'][1])
        p_val = p_val/kwargs['density'][0]
        p_val = 'uniform {}'.format(p_val)
        #
        p_file['boundaryField'][inlet_side]['type'] = 'fixedValue'
        p_file['boundaryField'][inlet_side]['value'] = p_val
        #
        u_file['boundaryField'][inlet_side]['type'] = 'zeroGradient'
        u_file['boundaryField'][inlet_side].pop('value', None)

    #
    if kwargs['outlet_p']:
        p_val = convert_value(float(kwargs['outlet_p'][0]), kwargs['outlet_p'][1])
        p_val = p_val/kwargs['density'][0]
        p_val = 'uniform {}'.format(p_val)
        #
        p_file['boundaryField'][outlet_side]['type'] = 'fixedValue'
        p_file['boundaryField'][outlet_side]['value'] = p_val
        #
        u_file['boundaryField'][outlet_side]['type'] = 'zeroGradient'
        u_file['boundaryField'][outlet_side].pop('value', None)

    #
    p_file.write_foam_file(path=job_dir, overwrite=True)
    u_file.write_foam_file(path=job_dir, overwrite=True)


if __name__ == '__main__':
    args = parser.parse_args()
    init_case_dir()

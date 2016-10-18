#!/usr/bin/env python3
#
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
from ApertureMapModelTools import _get_logger, set_main_logger_level, DataField
from ApertureMapModelTools.OpenFoam import OpenFoamFile
from ApertureMapModelTools.UnitConversion import convert_value
#
#
desc_str = r"""
Description: Automatically sets up an OpenFoam case based on the chosen
template case and command line args. If a run_script is present it will
attempt to update it to match parameters

Written By: Matthew stadelman
Date Written: 2016/10/11
Last Modfied: 2016/10/18
"""
usage_str = '%(prog)s [-hv] job_dir aper_map [job_name] [options]'

#
# fetching logger
logger = _get_logger('ApertureMapModelTools.Scripts')
#
# setting up the argument parser
parser = argparse.ArgumentParser(description=desc_str,
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
parser.add_argument('--template', type=os.path.realpath,
                    default=os.path.realpath('template-case'),
                    help="template case directory (default ./template-case)")
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
                      metavar=('    u', 'v',  'w', '[units]'))
bc_group.add_argument('--outlet-q', default=None, nargs=4,
                      metavar=('    u', 'v',  'w', '[units]'))
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
trans_group.add_argument('--viscosity',default=[0.001, 'pa*s'], nargs=2,
                         metavar=('    value', '[units]'),
                         help='(default: 0.001 pa*s)')
trans_group.add_argument('--density',default=[1000, 'kg/m^3'], nargs=2,
                         metavar=('    value', '[units]'),
                         help='(default: 1000 kg/m^3)')
#
###############################################################################


def init_case_dir():
    r"""
    Parses command line arguments and delegates tasks to helper functions
    """
    global args
    args = parser.parse_args()
    arg_dict = args.__dict__

    # checking some args
    if args.verbose:
        set_main_logger_level('debug')
    #
    if args.num_cores % 16 > 0:
        parser.error('num-cores must be a multiple of 16')
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

    # creating job directory
    try:
        os.makedirs(args.job_dir)
    except FileExistsError:
        print('remove this except block later on')

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
    # updating job script
    with open(os.path.join(args.job_dir, 'run_openfoam'), 'r+') as f:
        content = f.read()
        content = content.format(**arg_dict)
        f.seek(0)
        f.truncate()
        f.write(content)


def update_system_files(job_dir, end_time=None, num_cores=None, **kwargs):
    r"""
    Updates the controlDict and decomposeParDict
    """
    #
    foam_file = OpenFoamFile(os.path.join(job_dir, 'system', 'controlDict'))
    foam_file['endTime'] = end_time
    foam_file.write_foam_file(path=job_dir, overwrite=True)
    #
    foam_file = OpenFoamFile(os.path.join(job_dir, 'system', 'decomposeParDict'))
    foam_file['numberOfSubdomains'] = num_cores
    foam_file.write_foam_file(path=job_dir, overwrite=True)

def update_transport_props(job_dir, viscosity=None, density=None, **kwargs):
    r"""
    Updates the constant/transportProperties file. Updates the args object to have
    SI values for density and viscosity.
    """
    global args

    # loading file and converting values to SI
    foam_file = OpenFoamFile(os.path.join(job_dir, 'constant', 'transportProperties'))
    density = [convert_value(float(density[0]), density[1]), 'kg/m^3']
    viscosity = [convert_value(float(viscosity[0]), viscosity[1]), 'pa*s']
    args.density = density
    args.viscosity = viscosity
    viscosity = viscosity[0]/density[0]
    density = density[0]

    # setting kinematic viscosity values
    fmt = 'nu  [ 0  2 -1 0 0 0 0 ] {:0.6e};'
    foam_file['nu'] = fmt.format(viscosity)
    foam_file['CrossPowerLawCoeffs']['nu0'] = 'nu0 [ 0 2 -1 0 0 0 0 ] {:0.6e}'.format(viscosity)
    foam_file['CrossPowerLawCoeffs']['nuInf'] = 'nuInf [ 0 2 -1 0 0 0 0 ] {:0.6e}'.format(viscosity)
    foam_file['BirdCarreauCoeffs']['nu0'] = 'nu0 [ 0 2 -1 0 0 0 0 ] {:0.6e}'.format(viscosity)
    foam_file['BirdCarreauCoeffs']['nuInf'] = 'nuInf [ 0 2 -1 0 0 0 0 ] {:0.6e}'.format(viscosity)

    # setting density value
    fmt = 'rho  [ 1  -3 0 0 0 0 0 ] {:0.6e}'
    foam_file['rho'] = fmt.format(density)
    foam_file.write_foam_file(path=job_dir, overwrite=True)


def update_u_file(job_dir, aper_map, inlet_side=None, outlet_side=None, **kwargs):
    r"""
    Updates the 0/U file
    """
    aper_map = DataField(aper_map)
    p_file = OpenFoamFile(os.path.join(job_dir, '0', 'p'))
    u_file = OpenFoamFile(os.path.join(job_dir, '0', 'U'))
    #
    area_dict = {
        'left': sum(aper_map.data_map[:, 0] * kwargs['voxel_size']**2 * kwargs['avg_fact']),
        'right': sum(aper_map.data_map[:, -1] * kwargs['voxel_size']**2 * kwargs['avg_fact']),
        'top': sum(aper_map.data_map[-1, :] * kwargs['voxel_size']**2 * kwargs['avg_fact']),
        'bottom': sum(aper_map.data_map[0, :] * kwargs['voxel_size']**2 * kwargs['avg_fact'])
    }

    # calculating SI velocities
    if kwargs['inlet_q']:
        vel = kwargs['inlet_q'][0:3]
        vel = [convert_value(float(v), kwargs['inlet_q'][3]) for v in vel]
        vel = vel/area_dict[inlet_side]
        #
        u_file['boundaryField'][inlet_side]['type'] = 'fixedValue'
        u_file['boundaryField'][inlet_side]['value'] = 'uniform ({} {} {})'.format(*vel)
        p_file['boundaryField'][inlet_side]['type'] = 'zeroGradient'
        p_file['boundaryField'][inlet_side].pop('value', None)
    #
    if kwargs['outlet_q']:
        vel = kwargs['outlet_q'][0:3]
        vel = [convert_value(float(v), kwargs['outlet_q'][3]) for v in vel]
        vel = vel/area_dict[outlet_side]
        #
        u_file['boundaryField'][outlet_side]['type'] = 'fixedValue'
        u_file['boundaryField'][outlet_side]['value'] = 'uniform ({} {} {})'.format(*vel)
        p_file['boundaryField'][outlet_side]['type'] = 'zeroGradient'
        p_file['boundaryField'][outlet_side].pop('value', None)
    #
    p_file.write_foam_file(path=job_dir, overwrite=True)
    u_file.write_foam_file(path=job_dir, overwrite=True)



def update_p_file(job_dir, aper_map, inlet_side=None, outlet_side=None, **kwargs):
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
        p_file['boundaryField'][inlet_side]['type'] = 'fixedValue'
        p_file['boundaryField'][inlet_side]['value'] = 'uniform {}'.format(p_val)
        u_file['boundaryField'][inlet_side]['type'] = 'zeroGradient'
        u_file['boundaryField'][inlet_side].pop('value', None)

    #
    if kwargs['outlet_p']:
        p_val = convert_value(float(kwargs['outlet_p'][0]), kwargs['outlet_p'][1])
        p_val = p_val/kwargs['density'][0]
        p_file['boundaryField'][outlet_side]['type'] = 'fixedValue'
        p_file['boundaryField'][outlet_side]['value'] = 'uniform {}'.format(p_val)
        u_file['boundaryField'][outlet_side]['type'] = 'zeroGradient'
        u_file['boundaryField'][outlet_side].pop('value', None)

    #
    p_file.write_foam_file(path=job_dir, overwrite=True)
    u_file.write_foam_file(path=job_dir, overwrite=True)


if __name__ == '__main__':
    args = None
    init_case_dir()

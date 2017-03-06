"""
Handles unit conversions utilizing the pint module.
#
Written By: Matthew Stadelman
Date Written: 2017/03/05
Last Modifed: 2017/03/05
#
"""
from pint import UnitRegistry

def register_voxel_unit(voxel_size, unit):
    r"""
    Registers the 'voxel' unit with the unit_registry. voxel_size is the length
    of an edge of the voxel in the specified units.
    """
    pass

def convert_value(value, unit_in, unit_out='SI'):
    r"""
    Returns a converted value.
    """
    pass

def get_conversion_factor(unit_in, unit_out='SI'):
    r"""
    Returns a conversion factor.
    """
    pass

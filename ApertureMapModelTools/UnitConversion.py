"""
Handles unit conversions utilizing the pint module.
#
Written By: Matthew Stadelman
Date Written: 2017/03/05
Last Modifed: 2017/03/05
#
"""
from pint import UnitRegistry as __UnitRegistry

# instantiate the registry and add the 'micron' unit
unit_registry = __UnitRegistry()
unit_registry.define('micron = um')

def register_voxel_unit(voxel_size, unit):
    r"""
    Registers the 'voxel' unit with the unit_registry. voxel_size is the length
    of an edge of the voxel in the specified units.
    """
    unit_registry.define('voxel = {} * {} = vox'.format(voxel_size, unit))

def convert_value(value, unit_in, unit_out='SI'):
    r"""
    Returns a converted value.
    """
    quant = unit_registry.Quantity(value, unit_in)
    #
    if unit_out.upper() == 'SI':
        value = quant.to_base_units().magnitude
    else:
        value = quant.to(unit_out).magnitude
    #
    return value

def get_conversion_factor(unit_in, unit_out='SI'):
    r"""
    Returns a conversion factor.
    """
    if unit_out.upper() == 'SI':
        factor = unit_registry(unit_in).to_base_units().magnitude
    else:
        factor = unit_registry(unit_in).to(unit_out).magnitude
    #
    return factor

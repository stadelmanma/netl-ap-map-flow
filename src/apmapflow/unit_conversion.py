"""
================================================================================
Unit Conversion
================================================================================
| Handles unit conversions utilizing the pint module.

| Written By: Matthew Stadelman
| Date Written: 2017/03/05
| Last Modifed: 2017/04/30

|

"""
from pint import UnitRegistry as __UnitRegistry

# instantiate the registry and add the 'micron' unit
unit_registry = __UnitRegistry()
unit_registry.define('micron = um')


def register_voxel_unit(voxel_size, unit):
    r"""
    Registers the 'voxel' unit with the unit_registry. voxel_size is the length
    of an edge of the voxel in the specified units.

    Parameters
    ----------
    voxel_size : float
        edge length of a voxel cube.
    unit : string
        units the voxel size is defined in.

    Examples
    --------
    >>> import apmapflow.unit_conversion as uc
    >>> uc.register_voxel_unit(26.8, 'um')
    >>> print(uc.unit_registry('voxel').to('m').magnitude)
    """
    unit_registry.define('voxel = {} * {} = vox'.format(voxel_size, unit))


def convert_value(value, unit_in, unit_out='SI'):
    r"""
    Returns a converted value, in the specified output units or SI.

    Parameters
    ----------
    value : float
        edge length of a voxel cube.
    unit_in : string
        the current units of the value
    unit_out : string, optional
        the desired output units, if omitted they are converted to SI

    Returns
    -------
    A floating point value converted to the desired units.

    Examples
    --------
    >>> import apmapflow.unit_conversion as uc
    >>> print(uc.convert_value(26.8, 'um'))
    >>> print(uc.convert_value(26.8, 'um', 'cm'))
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
    Returns a conversion factor between the input unit and output unit or to SI
    if no output unit is provided.

    Parameters
    ----------
    unit_in : string
        the desired input units
    unit_out : string, optional
        the desired output units, if omitted the SI value is used

    Returns
    -------
    A floating point value that can be used to convert between the two units.

    Examples
    --------
    >>> import apmapflow.unit_conversion as uc
    >>> print(uc.get_conversion_factor('micron'))
    >>> print(uc.get_conversion_factor('um', 'mm'))
    """
    if unit_out.upper() == 'SI':
        factor = unit_registry(unit_in).to_base_units().magnitude
    else:
        factor = unit_registry(unit_in).to(unit_out).magnitude
    #
    return factor

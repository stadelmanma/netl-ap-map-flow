"""
Holds the core functions use to convert units.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/24
#
"""
from .__ConversionClasses__ import Temperature
from .__UnitDecomposition__ import UnitDecomposition


def convert_value(value, unit_str_in, unit_str_out='SI'):
    r"""
    This returns a converted value.
    """
    #
    temp_units = list(Temperature.temp_abbrev.keys())
    temp_units += list(Temperature.temp_abbrev.values())
    #
    #
    if (unit_str_in in temp_units):
        value = convert_temperature(value, unit_str_in, unit_str_out)
    else:
        unit_list, init_factor = UnitDecomposition.parse_unit_string(unit_str_in)
        unit_in_factor = init_factor * process_unit_list(unit_list)
        if (unit_str_out.upper() == 'SI'):
            return value * unit_in_factor
        #
        unit_list, init_factor = UnitDecomposition.parse_unit_string(unit_str_out)
        unit_out_factor = init_factor * process_unit_list(unit_list)
        #
        value = value * unit_in_factor/unit_out_factor
    #
    return value


def get_conversion_factor(unit_str_in, unit_str_out='SI'):
    r"""
    This returns a conversion factor, invalid for Fahrenheit and Celcius
    temperature conversions.
    """
    #
    # processing input unit to SI conversion factor
    unit_list, init_factor = UnitDecomposition.parse_unit_string(unit_str_in)
    unit_in_factor = init_factor * process_unit_list(unit_list)
    if (unit_str_out.upper() == 'SI'):
        return(unit_in_factor)
    #
    # processing ouput unit to SI conversion factor
    unit_list, init_factor = UnitDecomposition.parse_unit_string(unit_str_out)
    unit_out_factor = init_factor * process_unit_list(unit_list)
    #
    return unit_in_factor/unit_out_factor


def process_unit_list(unit_list):
    r"""
    Processes a list of unit dictionaries to generate a final overall
    conversion factor.
    """
    factor = 1.0
    #
    for unit in unit_list:
        kind = unit.kind
        name = unit.name
        expn = unit.exponent
        factor = factor * (kind.convert_to_si(name))**expn
    #
    return factor


def convert_temperature(value, unit_in='kelvin', unit_out='kelvin'):
    r"""
    Public wrapper method to handle temperature conversions
    """
    #
    return Temperature.convert_temperature(value, unit_in, unit_out)

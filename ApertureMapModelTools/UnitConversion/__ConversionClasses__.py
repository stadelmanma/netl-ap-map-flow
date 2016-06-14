"""
Handles unit conversions.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/06/12
#
"""
#
import re
from .__SI__ import SI


class Distance(SI):
    r"""
    Handles distance unit conversions to Meters
    """
    #
    unit_to_si = {
        'foot': 0.3048,
        'inch': 0.0254,
        'meter': 1.0,
        'micron': 1.0E-6,
        'yard': 0.9144
    }

    @classmethod
    def convert_to_si(cls, unit_string):
        r"""
        Finds and returns the proper unit conversion factor. Subclassed
        from SI to add special logic for the 'micron' unit
        """
        #
        if (unit_string == 'micron'):
            unit_string = 'micrometer'
        #
        try:
            root_unit, factor = cls.check_prefix(unit_string)
            factor = factor * cls.unit_to_si[root_unit]
        except KeyError:
            raise ValueError('Error - No conversion factor for unit: '+unit_string)
        #
        return(factor)


class Mass(SI):
    r"""
    Handles mass unit conversions to Kilograms
    """
    #
    unit_to_si = {
        'gram': 1.0E-3,
        'kilogram': 1.0,
        'ounce': 0.028349523,
        'pound-mass': 0.4535924,
        'slug': 14.59390
    }
    #
    # adjusting si_prefixes to reflect kilogram as the base unit
    si_prefixes = {pf: fact/1000.0 for pf, fact in SI.si_prefixes.items()}

    @classmethod
    def check_prefix(cls, unit_string):
        r"""
        Tests unit against a pattern for any SI prefixes, subclassed from
        SI to add special logic for kilogram being base unit.
        """
        pattern = ['^(?:'+p+')' for p in cls.si_prefixes.keys()]
        pattern = '|'.join(pattern)
        pattern = re.compile('('+pattern+')?(.+)', re.I)
        #
        try:
            m = pattern.search(unit_string)
            prefix = m.group(1)
            root_unit = m.group(2)
            factor = cls.si_prefixes[prefix]
        except (AttributeError, KeyError):
            factor = 1.0
            root_unit = unit_string
        #
        # handling issue with kilogram being SI unit instead of grams
        if (root_unit == 'gram'):
            factor = (1E-3 if unit_string == 'gram' else factor)
            root_unit = 'kilogram'
        #
        return(root_unit, factor)


class Pressure(SI):
    r"""
    Handles pressure conversions when units aren't a simple Force / Area
    """
    unit_to_si = {
        'atmosphere': 101325.0,
        'bar': 100000.0,
        'pascal': 1.0
    }


class Temperature(SI):
    r"""
    Handles temperure unit conversions
    """
    #
    unit_to_si = {
        'kelvin': 1.0,
        'rankine': 9.0/5.0
    }
    #
    temp_abbrev = {
        'C': 'celsius',
        'F': 'fahrenheit',
        'K': 'kelvin',
        'SI': 'kelvin',
        'R': 'rankine'
    }

    @classmethod
    def convert_temperature(cls, value, unit_in='kelvin', unit_out='kelvin'):
        r"""
        Handles the non-standard coversion method to get Fahrenheit and Celcius
        into and from Kelvin
        """
        #
        if (unit_in in cls.temp_abbrev.keys()):
            unit_in = cls.temp_abbrev[unit_in]
        if (unit_out in cls.temp_abbrev.keys()):
            unit_out = cls.temp_abbrev[unit_out]
        #
        # converting to Kelvin
        if (unit_in == 'fahrenheit'):
            temp = (value + 459.67)*(5.0/9.0)
        elif (unit_in == 'rankine'):
            temp = value * 5.0/9.0
        elif (unit_in == 'celsius'):
            temp = value + 273.15
        elif (unit_in == 'kelvin'):
            temp = value
        else:
            raise ValueError('Error - Invalid input unit: '+unit_in)
        #
        # converting from Kelvin to unit out
        if (unit_out == 'fahrenheit'):
            temp = temp*(9.0/5.0) - 459.67
        elif (unit_out == 'rankine'):
            temp = temp * 9.0/5.0
        elif (unit_out == 'celsius'):
            temp = temp - 273.15
        elif (unit_out == 'kelvin'):
            temp = temp
        else:
            raise ValueError('Error - Invalid ouput unit: '+unit_out)
        #
        return(temp)


class Temporal(SI):
    r"""
    Handles time unit conversions to Seconds, oddly named beacuse of 'time'
    builtin module even though these aren't meant to be imported directly
    into the main namespace
    """
    #
    unit_to_si = {
        'day': 86400.0,
        'hour': 3600.0,
        'minute': 60.0,
        'second': 1.0
    }


class Volume(SI):
    r"""
    Handles volume unit conversions when unit isn't a (distanc unit)^3
    """
    #
    unit_to_si = {
        'cubic-meter': 1.0,
        'fluid-ounce': 29.573529956E-6,
        'gallon': 0.003785412,
        'liter': 1.0E-3
    }

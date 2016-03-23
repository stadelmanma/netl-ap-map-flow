"""
Handles unit conversions.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/22
#
"""
#
from .__SI__ import SI
#
class ConvertDistance(SI):
    r"""
    Handles distance unit conversions to Meters
    """
    #
    unit_to_si = {
        'inch' : 0.0254,
        'feet' : 0.3048,
        'yard' : 0.9144,
        'micron' : 1.0E-6
    }
#
#
class ConvertMass(SI):
    r"""
    Handles distance unit conversions to Kilograms
    """
    #
    unit_to_si = {
        'pound' : 0.4535924,
        'slug' : 14.59390,
        'ounce' : 0.028349523,
        'kilogram' : 1.0
    }
    #
    # adjusting si_prefixes to reflect kilogram as the base unit
    si_prefixes = { pf : fact/1000.0 for pf,fact in SI.si_prefixes.items()}
    #
    # make sure the fact check_prefixes returns grams won't mess things up
    #
#
#
class ConvertTemperature(SI):
    r"""
    Handles distance unit conversions to Kelivin
    """
    #
    unit_to_si = {
        'rankine' : 9.0/5.0,
        'kelvin' : 1.0
    }
    #
    @classmethod
    def convert_temperature(cls,value,unit_in='kelvin',unit_out='kevin'):
        r"""
        Handles the non-standard coversion method to get Fahrenheit and Celcius 
        into and from Kelvin
        """
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
            raise(Exception('Error - Invalid input unit: '+unit_in))
        #
        # converting from Kelvin to unit out
        if (unit_in == 'fahrenheit'):
            temp = temp*(9.0/5.0) - 459.67
        elif (unit_in == 'rankine'):
            temp = temp * 9.0/5.0
        elif (unit_in == 'celsius'):
            temp = temp - 273.15
        elif (unit_in == 'kelvin'):
            temp = temp
        else:
            raise(Exception('Error - Invalid ouput unit: '+unit_out))
        #
        return(temp)
#
#
class ConvertTime(SI):
    r"""
    Handles distance unit conversions to Seconds
    """
    #
    unit_to_si = {
        'day' : 86400.0,
        'hour' : 3600.0,
        'minute' : 60.0,
        'second' : 1.0
    }
#
#
class ConvertVolume(SI):
    r"""
    Handles volume unit conversions, nested in this namespace because volume is
    directly related to a length scale. Converts to Meters^3
    """
    #
    unit_to_si = {
        'liter' : 28.31684659,
        'gallon' : 0.003785412,
        'fluid-ounce' : 29.573529956E-6
    }
    #
    
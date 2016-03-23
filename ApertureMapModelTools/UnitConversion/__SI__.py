"""
Stores basic implementation as well as SI prefixes.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/22
#
"""
#
import re
#
# 
class SI:
    r"""
    Holds basic sub class implementation as well as SI prefixes.
    """
    #
    si_prefixes = {
        'giga'  :	1.0E09,
        'mega'  :	1.0E06,
        'kilo'  :	1.0E03,
        'hecto' :	1.0E02,
        'deca'  :	1.0E01,
        'deci'  :	1.0E-1,
        'centi' :	1.0E-2,
        'milli' :	1.0E-3,
        'micro' :	1.0E-6,
        'nano'  :	1.0E-9
    }
    #
    unit_to_si = {
    }
    #
    @classmethod
    def check_prefix(cls,unit_string):
        pattern = ['^(?:'+p+')' for p in cls.si_prefixes.keys()]
        pattern = '|'.join(pattern)
        pattern = re.compile('('+pattern+')?(.+)',re.I)
        #
        try:
            m = pattern.search(unit_string)
            prefix = m.group(1)
            root_unit = m.group(2)
            factor = cls.si_prefixes[prefix]
        except (AttributeError,KeyError):
            factor = 1.0
            root_unit = unit_string
        #
        # may add the swap gram for kilogram logic here 
        #
        return(root_unit,factor)
    #
    @classmethod
    def convert_to_si(cls,unit):
        r"""
        Finds and returns the proper unit conversion factor.
        """
        try:
            factor = cls.unit_to_si[unit]
        except KeyError:
            raise(Exception('Error - No conversion factor for unit: '+unit))
        #
        return(factor)
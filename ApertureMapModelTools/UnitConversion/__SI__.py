"""
Stores basic implementation as well as SI prefixes.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/24
#
"""
#
import re
#
# 
class SI:
    r"""
    Holds basic sub class implementation as well as SI prefixes. Meant to
    serve as an abstract class for the other conversion classes. test23456
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
    si_abbreviations = {
        'G'  : 'giga',
        'M'  : 'mega',
        'k'  : 'kilo',
        'h'  : 'hecto',
        'da' : 'deca',
        'd'  : 'deci',
        'c'  : 'centi',
        'm'  : 'milli',
        'u'  : 'micro',
        'n'  : 'nano'
    }
    #
    unit_to_si = {
    }
    #
    @classmethod
    def check_prefix(cls,unit_string):
        r"""
        Tests unit against a pattern for any SI prefixes
        """
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
        return(root_unit,factor)
    @classmethod
    def check_abbreviation(cls,unit_string):
        r"""
        Tests unit against a pattern for any SI prefixes
        """
        pattern = ['^(?:'+p+')' for p in cls.si_abbreviations.keys()]
        pattern = '|'.join(pattern)
        pattern = re.compile('('+pattern+')?(.+)')
        #
        try:
            m = pattern.search(unit_string)
            prefix = cls.si_abbreviations[m.group(1)]
            root_unit = m.group(2)
        except (AttributeError,KeyError):
            prefix = ''
            root_unit = unit_string
        #
        return(root_unit,prefix)
    #
    @classmethod
    def convert_to_si(cls,unit_string):
        r"""
        Finds and returns the proper unit conversion factor.
        """
        try:
            root_unit,factor = cls.check_prefix(unit_string)
            factor = factor * cls.unit_to_si[root_unit]
        except KeyError:
            raise(Exception('Error - No conversion factor for unit: '+unit_string))
        #
        return(factor)
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
    @classmethod
    def check_prefix(cls,unit_string):
        pattern = ['^(?:'+p+')' for p in cls.si_prefixes.keys()]
        pattern = '|'.join(pattern)
        pattern = re.compile('('+pattern+')?(.+)',re.I)
        #
        try:
            m = pattern.search(unit_string)
            print(m.groups())
            prefix = m.group(1)
            factor = cls.si_prefixes[prefix]
            print(prefix,factor)
        except AttributeError:
            factor = 1.0
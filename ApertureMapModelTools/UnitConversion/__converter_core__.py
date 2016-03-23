"""
Holds the core functions use to convert units.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/23
#
"""
#
from collections import namedtuple
import re
from . import __ConversionClasses__ as convert
from .__SI__ import SI
#
#
class UnitDecomposition(SI):
    r"""
    Acts as a storage class to parse and build unit lists from strings to
    use as the input for conversion routines. 
    
    'compound_units' store units that are broken down to consist of
    values that are obtainable in the above classes, i.e. storing a pascal
    as (kg*/m/s^2) instead of (Newton/m^2). Any unit that can have a 
    prefix applied needs to be stored as a compound_units unit or
    in a specific unit class above. 
    
    Units are stored in a namedtuple class called 'unit'
    that holds the kind of unit, the unit string and the exponent to
    apply to the conversion factor.
    
    When doing the inital parsing of a unit string, the formatted dict
    will be checked first. If that fails then the progam will attempt to 
    parse the string based on the common_unit_abbrev dic and the SI prefix
    abbrevations.
    """
    #
    unit = namedtuple('unit',['kind','name','exponent'])
    #
    compound_units = {
      'dyne' : (unit(Mass,'gram',1),unit(Distance,'centimeter',1),
                unit(Temporal,'second',-2)),
      'newton' : (unit(Mass,'kilogram',1),unit(Distance,'meter',1),
                  unit(Temporal,'second',-2)),
      'pascal' : (unit(Mass,'kilogram',1),unit(Distance,'meter',-1),
                  unit(Temporal,'second',-2)),
      'poise' : (unit(Mass,'gram',1),unit(Distance,'centimeter',-1),
                 unit(Temporal,'second',-1)),
      'pound-force' : (unit(Mass,'slug',1),unit(Distance,'feet',1),
                       unit(Temporal,'second',-2)),
    }
    #
    # making a list of all the units available
    all_units = {}
    for kind in convert.__dict__.values():
        try:
            for unit in kind.unit_to_si.keys():
                all_units[unit] = tuple([convert.DecomposedUnits.unit(kind,unit,1)])
        except AttributeError:
            pass
    #
    for unit,unit_list in convert.DecomposedUnits.compound_units.items():
        all_units[unit] = unit_list
    #  
    common_unit_abrev = {
        'atm' : 'atmosphere',
        'C' : 'celsius',
        'cc' : 'milliliter',
        'dyn' : 'dyne',
        'ft' : 'feet',
        'fl-oz' : 'fluid-ounce',
        'F' : 'fahrenheit',
        'gal' : 'gallon',
        'hr' : 'hour',
        'in' : 'inch',
        'K' : 'kelvin',
        'kg' : 'kilogram',
        'l' : 'liter',
        'lbs' : 'pound-mass',
        'm' : 'meter',
        'min' : 'minute',
        'N' : 'netwon',
        'oz' : 'ounce',
        'p' : 'poise',
        'pa' : 'pascal',
        'R' : 'rankine',
        's' : 'second',
        'sec' : 'second',
        'yd' : 'yard'
    }
    #
    formatted_unit_strings = {
        'gpm' : '[gallon^1][minute^-1]', 
        #'kg/m^3' : '[kilogram^1][meter^-3]', #most of these might be 
        #'lbs/ft^3' : '[pounds-mass^1][feet^-3]', #able to be removed
        #'m^3/sec' : '[meter^3][second^1]', #if I make my unit parsing 
        #'m^3/s' : '[meter^3][second^1]', #reliable enough
        #'ml/min' : '[milliliter^1][minute^-1]',
        #'mm^3/min' : '[millimeter^3][minute^-1]',
        #'pa*sec' : '[pascal^1][second^1]',
        'psi' : '[pounds-force^1][inch^-2]',

    }
    #
    #
    @classmethod
    def parse_unit_string(cls,unit_string):
        r"""
        Returns a  strcutured unit format for build_unit_list to read.
        Outputs a string in the format [unit1^exp][unit2^exp] etc. 
        
        Initial adjustements to the conversion factor are applied here for
        compound units such as 'centipoise'.
        
        Unit strings must have an operator (* or /) between every unit and
        for sake of sanity the divison operator will only affect the unit 
        that follows it. For example the behavoir of kg/(m*s^2) has to be constructed
        kg/m/s^2. The same logic follows for exponents, as they only affect the
        preceding unit. Any grouping operators '(),{},[]' in the string will not 
        be handled and cause an error or no match at all. 
        """
        #
        initial_factor = 1.0
        formatted_string = ''
        unit_string = re.sub(r'\s','',unit_string)
        # I'll need to adjust the factor for compound unit prefixes here 
        #
        # checking for a pre-formatted unit string
        if (unit_string.lower() in cls.formatted_unit_strings.keys()):
            formatted_string = cls.formatted_unit_strings[unit_string.lower()]
            return(initial_factor,formatted_string)
        #
        #
        # locating all * and / in the unit string
        matches = re.finditer('([*/])',unit_string)
        components = []
        st = 0
        for m in matches:
            components.append(unit_string[st:m.start()])
            st = m.start()
        components.append(unit_string[st:])
        print(components)
        #
        # processing the unit components
        for comp in components:
            expn = 1.0
            comp = (comp[1:] if comp[0] =='*' else comp)
            m = re.search(r'^(?P<bksl>/)?(?P<unit>.+?)(?:[\^](?P<expn>-?\d+))?$',comp)
            unit_str = m.group('unit')
            if m.group('bksl'):
                expn = expn * -1
            if m.group('expn'):
                expn = expn * int(m.group('expn'))
            #
            # need to add some additional processing of unit_str still,
            # the unit_str needs to be converted to the full word version 
            # in common_unit_abrev dict. If a direct value can not be found
            # in the abbrevation dict or the 'all_units' dict then I will have
            # try and find a matching SI prefix abbrev on the unit. i.e. 
            # 'mm' fails but 'm' = milli and then 'm' is the key for 'meter'
            # so I output millimeter to the formatted string
            #
            # If a prefix is found then I'll need to do an additional check
            # to see if it is a compound unit. If the unit is not compound 
            # I can just add the prefix to the string, however if it is a 
            # compound unit then I will have to adjust the factor here 
            # to match the scaling change and use the root unit in the output.
            #
            # All this work kind of phases out the need for the 'build_unit_list'
            # function with the exception of handling a user supplied pre-formatted 
            # string. 
            #
            # right now this formatted string has incorrect unit strings
            formatted_string += '[{0}^{1:0.0f}]'.format(unit_str,expn)
        #
        #
        return(initial_factor,formatted_string)   
    #
    #
    @classmethod
    def build_unit_list(cls,formatted_unit_string,avail_units):
        r"""
        Parses a structured unit string to build a complex unit list. 
        It assumes any prefixes on the top level units have been accounted 
        for and removed. i.e. centipoise is already been made into poise 
        accounting for the 0.01 factor. 
        
        All units are enclosed in brackets and an exponent is required
        even if that expoenent is 1
        Example patterns: [pascal^1][second^1], [pound-force^1][inch^-2]
        """
        #
        units =  re.findall('(?:\[(.*?)\])',formatted_unit_string)
        unit_list = []
        for comp in units:
            try:
                key,exp = re.search('^(.*?)[\^](-?\d+)',comp).groups()
                exp = int(exp)
                for unit_tuple in avail_units[key]:
                    new_exp = unit_tuple.exponent * exp
                    unit_list.append(unit_tuple._replace(exponent=new_exp))
            except AttributeError:
                raise(Exception('Error - component in unit string was in invalid format: '+
                                formatted_unit_string+' -> '+comp))
            except KeyError:
                try:
                    root_unit,factor = cls.check_prefix(key)
                    # attempting to use root unit as key
                    for unit_tuple in avail_units[root_unit]:
                        new_exp = unit_tuple.exponent * exp
                        unit_list.append(unit_tuple._replace(exponent=new_exp,name=key))
                except KeyError:
                    raise(Exception('Error - unknown component in unit string: '+
                                    formatted_unit_string+' -> '+key))
        #
        return(unit_list)
#
# 
def convert_value(value,unit_str_in='SI',unit_str_out='SI'):
    r"""
    This returns a converted value. 
    """
    #
    # code to decompose unit strings
    # additional logic to convert between C,F,R,K temperatures
    #
    # if the unit_out = 'SI' just return early
    #
    raise(NotImplementedError('under construction'))
    return value
#
# 
def get_conversion_factor(unit_str_in='SI',unit_str_out='SI'):
    r"""
    This returns a conversion factor, invalid for Fahrenheit and Celcius 
    temperature conversions. 
    """
    #
    # code to decompose unit strings
    # make sure there is a check for F and C conversions somewhere
    # depending on my implementation might be handled by the conversion class
    #
    # if the unit_out = 'SI' just return early
    #
    raise(NotImplementedError('under construction'))
    return factor
#
#
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
    return(factor)
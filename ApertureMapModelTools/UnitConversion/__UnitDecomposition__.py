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

    Parts of a compound unit are stored in a namedtuple class called 'Component'
    that holds the kind of unit, the unit string and the exponent of that unit.

    When doing the inital parsing of a unit string, the formatted dict
    will be checked first. If that fails then the progam will attempt to
    parse the string based on the common_unit_abbrev dic and the SI prefix
    abbrevations.
    """
    #
    Component = namedtuple('unit',['kind','name','exponent'])
    #
    compound_units = {
      'dyne' : (Component(convert.Mass,'gram',1),
                Component(convert.Distance,'centimeter',1),
                Component(convert.Temporal,'second',-2)),
      'newton' : (Component(convert.Mass,'kilogram',1),
                  Component(convert.Distance,'meter',1),
                  Component(convert.Temporal,'second',-2)),
      'pascal' : (Component(convert.Mass,'kilogram',1),
                  Component(convert.Distance,'meter',-1),
                  Component(convert.Temporal,'second',-2)),
      'poise' : (Component(convert.Mass,'gram',1),
                 Component(convert.Distance,'centimeter',-1),
                 Component(convert.Temporal,'second',-1)),
      'pound-force' : (Component(convert.Mass,'slug',1),
                       Component(convert.Distance,'foot',1),
                       Component(convert.Temporal,'second',-2)),
    }
    #
    # making a list of all the units available
    all_units = {}
    for kind in convert.__dict__.values():
        try:
            for unit in kind.unit_to_si.keys():
                all_units[unit] = tuple([Component(kind,unit,1)])
        except AttributeError:
            pass
    #
    for unit,component_list in compound_units.items():
        all_units[unit] = component_list
    #
    common_unit_abrev = {
        'atm' : 'atmosphere',
        'C' : 'celsius',
        'cc' : 'milliliter',
        'dyn' : 'dyne',
        'ft' : 'foot',
        'fl-oz' : 'fluid-ounce',
        'F' : 'fahrenheit',
        'gal' : 'gallon',
        'hr' : 'hour',
        'in' : 'inch',
        'K' : 'kelvin',
        'kg' : 'kilogram',
        'l' : 'liter',
        'lb' : 'pound-mass',
        'lbf' : 'pound-force',
        'lbm' : 'pound-mass',
        'lbs' : 'pound-mass',
        'm' : 'meter',
        'min' : 'minute',
        'N' : 'newton',
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
        'psi' : '[pound-force^1][inch^-2]',
    }
    #
    #
    @classmethod
    def parse_unit_string(cls,unit_string):
        r"""
        Returns a structured unit format for build_unit_list to read.
        Outputs a unit component list and initial conversion factor.

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
        factor = 1.0
        unit_string = re.sub(r'\s','',unit_string)
        #
        # checking for a pre-formatted unit string
        if (unit_string.lower() in cls.formatted_unit_strings.keys()):
            formatted_string = cls.formatted_unit_strings[unit_string.lower()]
            return(cls.build_unit_list(formatted_string),factor)
        #
        #
        # locating all * and / in the unit string
        matches = re.finditer('([*/])',unit_string)
        formatted_string = ''
        components = []
        st = 0
        for m in matches:
            components.append(unit_string[st:m.start()])
            st = m.start()
        components.append(unit_string[st:])
        #
        # processing the unit components
        for i in range(len(components)):
            comp_str = components[i]
            try:
                components[i],comp_factor = cls.parse_component_string(comp_str)
            except (KeyError,ValueError):
                components[i],comp_factor = cls.parse_component_string(comp_str.lower())
            #
            factor = factor * comp_factor
        #
        unit_list = []
        for comp in components:
            unit_list += comp
        #
        return(unit_list,factor)
    #
    #
    @classmethod
    def parse_component_string(cls,comp_str):
        r"""
        Parses a component of a unit string and attempts to return an inital
        conversion factor as well as a unit list for the component.
        """
        #
        expn = 1.0
        factor = 1.0
        #
        comp_str = (comp_str[1:] if comp_str[0] == '*' else comp_str)
        m = re.search(r'^(?P<bksl>/)?(?P<unit>.+?)(?:[\^](?P<expn>-?\d+))?$',
                      comp_str)
        unit_str = m.group('unit')
        if m.group('bksl'):
            expn = expn * -1
        if m.group('expn'):
            expn = expn * int(m.group('expn'))
        #
        # inital check for matching unit
        try:
            comp_list,factor = cls._test_unit_str(unit_str,expn)
            return(comp_list,factor)
        except ValueError:
            pass
        #
        # checking against known abbreviations
        try:
            unit_str = cls.common_unit_abrev[unit_str]
            comp_list,factor = cls._test_unit_str(unit_str,expn)
            return(comp_list,factor)
        except KeyError:
            # removing an si prefix abbreviations
            unit_str,prefix = cls.check_abbreviation(unit_str)
            unit_str = cls.common_unit_abrev[unit_str]
            comp_list,factor = cls._test_unit_str(prefix+unit_str,expn)
            return(comp_list,factor)
    #
    #
    @classmethod
    def _test_unit_str(cls,unit_str,expn):
        r"""
        This performs a repeated test for a valid key in the all_units dict.
        It first checks the string as whole and if it fails then attemps to
        remove a prefix and then retests.
        """
        #
        # lambda expr to update tuple exponents
        def new_exp(tup,exp): return(tup._replace(exponent=tup.exponent * exp))
        #
        factor = 1.0
        #
        # checking unit_str against defined units
        try:
            comp_list = [new_exp(tup,expn) for tup in cls.all_units[unit_str]]
            return(comp_list,factor**expn)
        except KeyError:
            # removing any prefixes
            unit_str,factor = cls.check_prefix(unit_str)
        #
        try:
            comp_list = [new_exp(tup,expn) for tup in cls.all_units[unit_str]]
            return(comp_list,factor**expn)
        except KeyError:
            if (unit_str == 'celsius'):
                raise(Exception('Error - celsius does not have a valid '+
                                'conversion factor. Use convert_temperature instead.'))
            elif (unit_str == 'fahrenheit'):
                raise(Exception('Error - fahrenheit does not have a valid '+
                                'conversion factor. Use convert_temperature instead.'))
            else:
                raise(ValueError('Error - no matching unit could be found for '+unit_str))
    #
    #
    @classmethod
    def build_unit_list(cls,formatted_unit_string):
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
        units =  re.findall(r'(?:\[(.*?)\])',formatted_unit_string)
        unit_list = []
        for comp in units:
            try:
                key,exp = re.search(r'^(.*?)[\^](-?\d+)',comp).groups()
                exp = int(exp)
                for unit_tuple in cls.all_units[key]:
                    new_exp = unit_tuple.exponent * exp
                    unit_list.append(unit_tuple._replace(exponent=new_exp))
            except AttributeError:
                raise(Exception('Error - component in unit string was in invalid format: '+
                                formatted_unit_string+' -> '+comp))
            except KeyError:
                try:
                    root_unit,factor = cls.check_prefix(key)
                    # checking if root unit was a compound unit that still had the prefix
                    if (root_unit in cls.compound_units.keys()):
                        raise(ValueError)
                    # attempting to use root unit as key
                    for unit_tuple in cls.all_units[root_unit]:
                        new_exp = unit_tuple.exponent * exp
                        unit_list.append(unit_tuple._replace(exponent=new_exp,name=key))
                except KeyError:
                    raise(Exception('Error - unknown component in unit string: '+
                                    formatted_unit_string+' -> '+key))
                except ValueError:
                    raise(Exception('Error - component in unit string was a '+
                                    'compound unit with a prefix: '+
                                    formatted_unit_string+' -> '+key))
        #
        return(unit_list)
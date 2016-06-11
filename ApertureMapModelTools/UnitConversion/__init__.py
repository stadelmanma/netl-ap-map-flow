"""
Automatically imports the unit conversion classes and core routines.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/22
#
"""
#
#
from .__UnitDecomposition__ import UnitDecomposition
from .__converter_core__ import convert_value, get_conversion_factor
from .__converter_core__ import convert_temperature
#
print('Notice - Unit conversion is largely case sensitive and conforms to' +
      'standard abbreviations and SI prefixes.')

===============
Unit Conversion
===============

.. contents::


Overview
========

Unit conversions are facilitated with three functions, :code:`register_voxel_unit`, :code:`convert_value`, :code:`get_conversion_factor`. All of the functionality is build on top of (pint)[https://github.com/hgrecco/pint] with the functions acting as a basic layer of abstraction. Additionally the 'micron' unit which is equivalent to a micrometer is automatically defined. Access to the pint :code:`UnitRegistry` instance is available through the :code:`UnitConversion.unit_registry` attribute.

register_voxel_unit
-------------------
 :code:`register_voxel_unit(length, unit)` is used as expected to define the 'voxel' unit in the registry because it is not a standard unit of measurement. Once registered conversions can be applied as usual. The unit describing the length must be a standard unit of measurement such as millimeters, inches, microns, etc.

 convert_value
 -------------
 :code:`convert_value(value, unit_in, unit_out='SI')` converts a value in the current unit to the unit specified by unit_out. If unit_out is not provided then the value is converted to the proper SI units.

 get_conversion_factor
 ---------------------
 :code:`get_conversion_factor(unit_in, unit_out='SI')` returns a conversion factor from the current unit to the unit specified by unit_out. If unit_out is not provided then a conversion factor to the SI unit is returned.

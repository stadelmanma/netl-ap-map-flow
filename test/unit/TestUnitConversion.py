"""
Handles testing of the unit conversion module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2017/03/06
#
"""
from pint import UnitRegistry
from ApertureMapModelTools import unit_conversion


class TestUnitConversion:
    r"""
    Executes a set of functions to handle testing of the unit conversion
    routines
    """
    def setup_class(self):
        #
        ureg = UnitRegistry()
        ureg.define('micron = um')
        self.ureg = ureg
        #
        self.convert_value_test = [
            (0.0, 'degC', 'degK', ureg.Quantity(0.0, 'degC').to('degK')),
            (1.0, 'psi', 'SI', ureg.Quantity(1, 'psi').to_base_units()),
            (1.0, 'cP', 'dyne*s/cm^2', ureg.Quantity(1.0, 'cP').to('dyne*s/cm^2')),
            (1000.0, 'microns', 'SI', ureg.Quantity(1000, 'microns').to_base_units())
        ]
        #
        self._convertion_factor_test = [
            ('psi', 'kN/m^2', ureg('psi').to('kN/m^2').magnitude),
            ('lbf', 'N', ureg('lbf').to('N').magnitude),
            ('micron', 'SI', ureg('micron').to('m').magnitude),
            ('ml/min', 'SI', ureg('ml/min').to('m^3/sec').magnitude)
        ]

    def test_register_voxel_unit(self):
        r"""
        Checks that voxel can be registered and converted with
        """
        unit_conversion.register_voxel_unit(10.0, 'microns')
        self.ureg.define('voxel = 10.0 * microns = vox')

        value = unit_conversion.convert_value(1000, 'vox', 'SI')
        test_value = 1000 * self.ureg('vox').to_base_units()
        #
        assert value == test_value.magnitude

    def test_convert_value(self):
        r"""
        Testing values returned by a general test of many conversions
        """
        for val_in, unit_in, unit_out, val_out in self.convert_value_test:
            val = unit_conversion.convert_value(val_in, unit_in, unit_out)
            #
            # applying a tolerance since were working with floating point values
            val = round(val * 1.0E9)
            val_out = round(val_out.magnitude * 1.0E9)
            msg = 'Mutlitple unit conversion from {} to {} failed.'
            msg = msg.format(unit_in, unit_out)
            #
            assert val == val_out, msg

    def test_get_conversion_factor(self):
        r"""
        Testing the get_conversion_factor function
        """
        for unit_in, unit_out, test_fact in self._convertion_factor_test:
            fact = unit_conversion.get_conversion_factor(unit_in, unit_out)
            fact = round(fact * 1.0E9)
            test_fact = round(test_fact * 1.0E9)
            msg = 'Get conversion factor for {} to {} failed.'
            msg = msg.format(unit_in, unit_out)
            #
            assert fact == test_fact, msg

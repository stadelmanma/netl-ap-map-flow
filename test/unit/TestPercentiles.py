"""
Handles testing of the Percentiles class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/06/12
#
"""
import os
import scipy as sp
from ApertureMapModelTools.DataProcessing.__Percentiles__ import Percentiles


class TestPercentiles:
    r"""
    Testing each method of the Percentiles class
    """
    def test_initialization(self, data_field_class):
        r"""
        Testing class initialization
        """
        pctle = Percentiles(data_field_class())
        assert len(pctle.arg_processors.keys()) == 1
        assert pctle.arg_processors['perc']

    def test_process_data(self, data_field_class):
        r"""
        Testing the process data method
        """
        pctle = Percentiles(data_field_class())
        pctle.args = {'perc': [0, 10, 50, 90, 100]}
        #
        pctle.process_data()
        for perc in pctle.args['perc']:
            assert pctle.processed_data['{:4.2f}'.format(perc)] is not None
        #
        assert pctle.processed_data['{:4.2f}'.format(pctle.args['perc'][0])] == pctle.data_vector[0]
        assert pctle.processed_data['{:4.2f}'.format(pctle.args['perc'][-1])] == pctle.data_vector[-1]

    def test_output_data(self, data_field_class):
        r"""
        Testing output content generation
        """
        pctle = Percentiles(data_field_class())
        pctle.infile = os.path.join(TEMP_DIR, 'test-pctle.csv')
        pctle.processed_data = {'10.00': 10, '0.00': 0, '100.00': 99, '90.00': 90, '50.00': 50}
        #
        pctle.output_data()

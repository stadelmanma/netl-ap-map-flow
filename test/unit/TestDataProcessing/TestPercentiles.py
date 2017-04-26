"""
Handles testing of the Percentiles class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/10/25
#
"""
import argparse
import os
from ApertureMapModelTools.DataProcessing.percentiles import Percentiles


class TestPercentiles:
    r"""
    Testing each method of the Percentiles class
    """
    def test_initialization(self, data_field_class):
        r"""
        Testing class initialization
        """
        pctle = Percentiles(data_field_class(), )
        assert not pctle.args
        #
        pctle = Percentiles(data_field_class(), percentiles=[1, 2, 3])
        assert pctle.args['percentiles'] == [1, 2, 3]

    def test_add_sub_parser(self):
        # setting up required parsers
        parser = argparse.ArgumentParser()
        parent = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers()

        # adding percentiles subparser
        Percentiles._add_subparser(subparsers, parent)

        # testing parser
        cargs = 'Percentiles 10 20 30 40 50 --key-format {:6f} --value-format {:10f}'.split()
        args = parser.parse_args(cargs)
        cargs = 'perc 10 20 30 40 50 --key-format {:6f} --value-format {:10f}'.split()
        args = parser.parse_args(cargs)
        #
        assert args.percentiles == [10, 20, 30, 40, 50]
        assert args.key_format == '{:6f}'
        assert args.value_format == '{:10f}'

    def test_process_data(self, data_field_class):
        r"""
        Testing the process data method
        """
        pctle = Percentiles(data_field_class())
        pctle.args = {'percentiles': [0, 10, 50, 90, 100]}
        #
        pctle._process_data()
        for perc in pctle.args['percentiles']:
            assert pctle.processed_data['{:4.2f}'.format(perc)] is not None
        #
        assert pctle.processed_data['{:4.2f}'.format(pctle.args['percentiles'][0])] == pctle.data_vector[0]
        assert pctle.processed_data['{:4.2f}'.format(pctle.args['percentiles'][-1])] == pctle.data_vector[-1]

    def test_output_data(self, data_field_class):
        r"""
        Testing output content generation
        """
        pctle = Percentiles(data_field_class())
        pctle.infile = os.path.join(TEMP_DIR, 'test-pctle.csv')
        pctle.processed_data = {'10.00': 10, '0.00': 0, '100.00': 99, '90.00': 90, '50.00': 50}
        #
        pctle._output_data()
        assert pctle.outfile_content

"""
Handles testing of the Histogram class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/10/25
#
"""
import argparse
import os
import scipy as sp
from ApertureMapModelTools.DataProcessing.__Histogram__ import Histogram


class TestHistogram:
    r"""
    Testing each method of the Histogram class
    """
    def test_initialization(self, data_field_class):
        r"""
        Testing class initialization
        """
        pctle = Histogram(data_field_class(), )
        assert not pctle.args
        #
        pctle = Histogram(data_field_class(), num_bins=10)
        assert pctle.args['num_bins'] == 10

    def test_add_sub_parser(self):
        # setting up required parsers
        parser = argparse.ArgumentParser()
        parent = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers()

        # adding percentiles subparser
        Histogram._add_subparser(subparsers, parent)

        # testing parser
        cargs = 'Histogram 10'.split()
        args = parser.parse_args(cargs)
        cargs = 'hist 5'.split()
        args = parser.parse_args(cargs)
        #
        assert args.num_bins == 5

    def test_define_bins(self, data_field_class):
        r"""
        Testing bin generation
        """
        hist = Histogram(data_field_class())
        hist.args = {'num_bins': 10}
        hist.nz = 100
        hist.nx = 100
        hist.data_map = sp.ones((hist.nz, hist.nx), dtype=int)
        for i in range(hist.nz):
            hist.data_map[i, :] = 1 * (i+1)
        hist.data_map[0] = -1
        hist.data_vector = sp.ravel(hist.data_map)
        #
        hist.define_bins()
        assert len(hist.bins) == hist.args['num_bins'] + 1

    def test_process_data(self, data_field_class):
        r"""
        running through the histogram data processing
        """
        hist = Histogram(data_field_class())
        hist.args = {'num_bins': 10}
        hist.data_map = sp.ones((hist.nz, hist.nx), dtype=int)
        for i in range(hist.nz):
            hist.data_map[i, :] = 1 * (i+1)
        hist.data_vector = sp.ravel(hist.data_map)
        hist.bins = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10.01)]
        #
        hist._process_data()
        for bounds, data_bin in zip(hist.bins, hist.processed_data):
            assert len(data_bin) == 3
            assert data_bin[0] == bounds[0]
            assert data_bin[1] == bounds[1]
            assert data_bin[2] == 10
        #
        # testing perserve bins
        hist.data_vector = sp.array([-1, 1, 2, 3])
        hist.bins = [(0, 5), (5, 10)]
        hist._process_data(preserve_bins=True)
        assert len(hist.bins) == 2

    def test_output_data(self, data_field_class):
        r"""
        running through the output data generation
        """
        hist = Histogram(data_field_class())
        hist.infile = os.path.join(TEMP_DIR, 'hist-test.csv')
        hist.processed_data = [(0, 2, 10), (2, 4, 10), (4, 6, 10), (6, 8, 10), (8, 10.01, 10)]
        #
        hist._output_data()
        assert hist.outfile_content

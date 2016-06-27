"""
Handles testing of the Histogram class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/06/12
#
"""
import os
import scipy as sp
from ApertureMapModelTools.DataProcessing.__Histogram__ import Histogram


class TestHistogram:
    r"""
    Testing each method of the Histogram class
    """
    def test_initialization(self, data_field_class):
        r"""
        Checking args so an error is generated if they change and the test does not
        """
        hist = Histogram(data_field_class())
        args = list(hist.arg_processors.keys())
        args.sort()
        #
        assert len(args) == 1
        for arg, test in zip(args, ['num_bins']):
            assert arg == test

    def test_define_bins(self, data_field_class):
        r"""
        Testing bin generation
        """
        hist = Histogram(data_field_class())
        hist.args = {'num_bins': 10}
        hist.data_map = sp.ones((hist.nz, hist.nx), dtype=int)
        for i in range(hist.nz):
            hist.data_map[i, :] = 1 * (i+1)
        hist.data_vector = sp.ravel(hist.data_map)
        #
        hist.define_bins()
        assert len(hist.bins) == hist.args['num_bins']

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
        hist.process_data()
        for bounds, data_bin in zip(hist.bins, hist.processed_data):
            assert len(data_bin) == 3
            assert data_bin[0] == bounds[0]
            assert data_bin[1] == bounds[1]
            assert data_bin[2] == 10
        #
        # testing perserve bins
        hist.data_vector = sp.array([-1, 1, 2, 3])
        hist.bins = [(0, 5), (5, 10)]
        hist.process_data(preserve_bins=True)
        assert len(hist.bins) == 2

    def test_output_data(self, data_field_class):
        r"""
        running through the output data generation
        """
        hist = Histogram(data_field_class())
        hist.infile = os.path.join(TEMP_DIR, 'hist-test.csv')
        hist.processed_data = [(0, 2, 10), (2, 4, 10), (4, 6, 10), (6, 8, 10), (8, 10.01, 10)]
        #
        hist.output_data()

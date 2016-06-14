"""
Handles testing of the HistogramRange class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/06/12
#
"""
import scipy as sp
from ApertureMapModelTools.DataProcessing.__HistogramRange__ import HistogramRange


class TestHistogramLogscale:
    r"""
    Testing each method of the HistogramLogscale class
    """
    def test_initialization(self, data_field_class):
        r"""
        Checking args so an error is generated if they change and the test does not
        """
        hist = HistogramRange(data_field_class())
        args = list(hist.arg_processors.keys())
        args.sort()
        #
        assert len(args) == 2
        for arg, test in zip(args, ['num_bins', 'range']):
            assert arg == test

    def test_define_bins(self, data_field_class):
        r"""
        Testing range bin generation
        """
        hist = HistogramRange(data_field_class())
        hist.args = {'num_bins': 10, 'range': [10.0, 90.0]}
        hist.data_map = sp.ones((hist.nz, hist.nx), dtype=int)
        for i in range(hist.nz):
            hist.data_map[i, :] = 10 * (i+1)
        hist.data_vector = sp.ravel(hist.data_map)
        #
        hist.define_bins()
        #
        assert len(hist.bins) == 10

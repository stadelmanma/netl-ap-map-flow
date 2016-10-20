"""
Handles testing of the HistogramLogscale class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/10/20
#
"""
import scipy as sp
from ApertureMapModelTools.DataProcessing.__HistogramLogscale__ import HistogramLogscale


class TestHistogramLogscale:
    r"""
    Testing each method of the HistogramLogscale class
    """
    def test_initialization(self, data_field_class):
        r"""
        Testing class initialization
        """
        hist = HistogramLogscale(data_field_class(), )
        assert not hist.args
        #
        hist = HistogramLogscale(data_field_class(), scale_fact=5)
        assert hist.args['scale_fact'] == 5

    def test_define_bins(self, data_field_class):
        r"""
        Testing logscale bin generation
        """
        hist = HistogramLogscale(data_field_class())
        hist.args = {'scale_fact': 10}
        hist.data_map = sp.ones((hist.nz, hist.nx), dtype=int)
        for i in range(hist.nz):
            hist.data_map[i, :] = 10 * (i+2)
        hist.data_vector = sp.ravel(hist.data_map)
        hist.data_vector[0] = -1
        #
        hist.define_bins()
        #
        assert len(hist.bins) == 5
        assert hist.bins[0][0] == hist.data_vector[0]
        assert hist.bins[-1][1] > hist.data_vector[-1]

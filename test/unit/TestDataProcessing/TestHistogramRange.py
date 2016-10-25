"""
Handles testing of the HistogramRange class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/10/25
#
"""
import argparse
import scipy as sp
from ApertureMapModelTools.DataProcessing.__HistogramRange__ import HistogramRange


class TestHistogramRange:
    r"""
    Testing each method of the HistogramRange class
    """
    def test_initialization(self, data_field_class):
        r"""
        Testing class initialization
        """
        hist = HistogramRange(data_field_class(), )
        assert not hist.args
        #
        hist = HistogramRange(data_field_class(), range=[5, 95])
        assert hist.args['range'] == [5, 95]

    def test_add_sub_parser(self):
        # setting up required parsers
        parser = argparse.ArgumentParser()
        parent = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers()

        # adding percentiles subparser
        HistogramRange._add_subparser(subparsers, parent)

        # testing parser
        cargs = 'HistogramRange 10'.split()
        args = parser.parse_args(cargs)
        #
        assert args.num_bins == 10
        assert args.range == [1.0, 99.0]
        #
        cargs = 'histrng 13 -r 0 100'.split()
        args = parser.parse_args(cargs)
        #
        assert args.num_bins == 13
        assert args.range == [0.0, 100.0]
        #
        cargs = 'histrng 7 --range 5 95'.split()
        args = parser.parse_args(cargs)
        #
        assert args.num_bins == 7
        assert args.range == [5.0, 95.0]

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

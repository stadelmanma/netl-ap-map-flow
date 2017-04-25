"""
Calculates a histogram over a defined percentile range for a data map.
Inherits most of it's structure from Histogram
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/10/25
#
"""
import scipy as sp
from ..__core__ import calc_percentile
from .__Histogram__ import Histogram


class HistogramRange(Histogram):
    r"""
    Performs a histogram where the minimum and maximum bin limits are set
    by percentiles and all values outside of that range are excluded. The
    interior values are handled the same as a basic histogram with bin sizes
    evenly spaced between the min and max percentiles given.

    kwargs include:
        num_bins - integer value for the total number of bins
        range - list with two numeric values to define the minimum and maximum
            data percentiles.
    """

    def __init__(self, field, **kwargs):
        super().__init__(field)
        self.args.update(kwargs)
        self.output_key = 'hist'
        self.action = 'histogram_range'

    @classmethod
    def _add_subparser(cls, subparsers, parent):
        r"""
        Adds a specific action based sub-parser to the supplied arg_parser
        instance.
        """
        parser = subparsers.add_parser(cls.__name__,
                                       aliases=['histrng'],
                                       parents=[parent],
                                       help=cls.__doc__)
        #
        parser.add_argument('num_bins', type=int,
                            help='number of bins to utilze in histogram')
        parser.add_argument('-r', '--range', nargs=2, type=float,
                            default=[1.0, 99.0],
                            help='percentile range to use %(default)s')
        parser.set_defaults(func=cls)

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a range histogram
        """
        self.data_vector.sort()
        num_bins = self.args['num_bins'] + 1
        min_val = self.args['range'][0]
        max_val = self.args['range'][1]
        #
        min_val = calc_percentile(min_val, self.data_vector, False)
        max_val = calc_percentile(max_val, self.data_vector, False)
        #
        low = list(sp.linspace(min_val, max_val, num_bins))[:-1]
        high = list(sp.linspace(min_val, max_val, num_bins))[1:]
        #
        self.bins = [bin_ for bin_ in zip(low, high)]

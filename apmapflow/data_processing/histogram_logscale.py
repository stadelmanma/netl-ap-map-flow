"""
================================================================================
Logscaled Histogram
================================================================================
| Calculates a logarithmically spaced histogram for a data map.

| Written By: Matthew Stadelman
| Date Written: 2016/03/07
| Last Modifed: 2016/10/20

"""
import scipy as sp
from .histogram import Histogram


class HistogramLogscale(Histogram):
    r"""
    Performs a histogram where the bin limits are logarithmically spaced
    based on the supplied scale factor. If there are negative values then
    the first bin contains everything below 0, the next bin will contain
    everything between 0 and 1.
    kwargs include:
        scale_fact - numeric value to generate axis scale for bins. A
            scale fact of 10 creates bins: 0-1, 1-10, 10-100, etc.
    """
    def __init__(self, field, **kwargs):
        super().__init__(field)
        self.args.update(kwargs)
        self.output_key = 'hist_logscale'
        self.action = 'histogram_logscale'

    @classmethod
    def _add_subparser(cls, subparsers, parent):
        r"""
        Adds a specific action based sub-parser to the supplied arg_parser
        instance.
        """
        parser = subparsers.add_parser(cls.__name__,
                                       aliases=['histlog'],
                                       parents=[parent],
                                       help=cls.__doc__)
        #
        parser.add_argument('scale_fact', type=float, nargs='?', default=10.0,
                            help='base to generate logscale from')
        parser.set_defaults(func=cls)

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a logscaled histogram
        """
        self.data_vector.sort()
        sf = self.args['scale_fact']
        num_bins = int(sp.logn(sf, self.data_vector[-1]) + 1)
        #
        # generating initial bins from 1 - sf**num_bins
        low = list(sp.logspace(0, num_bins, num_bins + 1, base=sf))[:-1]
        high = list(sp.logspace(0, num_bins, num_bins + 1, base=sf))[1:]
        #
        # Adding "catch all" bins for anything between 0 - 1 and less than 0
        if self.data_vector[0] < 1.0:
            low.insert(0, 0.0)
            high.insert(0, 1.0)
        if self.data_vector[0] < 0.0:
            low.insert(0, self.data_vector[0])
            high.insert(0, 0.0)
        #
        self.bins = [bin_ for bin_ in zip(low, high)]

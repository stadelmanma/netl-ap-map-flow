"""
Calculates a logarithmically spaced histogram for a data map.
Inherits most of it's structure from Histogram
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/10/20
#
"""
from .__Histogram__ import Histogram


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

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a logscaled histogram
        """
        self.data_vector.sort()
        sf = self.args['scale_fact']
        #
        # Adding "catch all" bins for anything less than 0 and between 0 - 1
        self.bins = []
        if (self.data_vector[0] < 0.0):
            self.bins.append((self.data_vector[0], 0.0))
        self.bins.append((0.0, 1.0))
        #
        low = 1.0
        exp = 1.0
        while (low < self.data_vector[-1]):
            high = sf**exp
            self.bins.append((low, high))
            low = high
            exp += 1.0

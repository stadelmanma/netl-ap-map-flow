"""
Calculates a logarithmically spaced histogram for a data map.
Inherits most of it's structure from Histogram
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/03/22
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor
from .__Histogram__ import Histogram


class HistogramLogscale(Histogram):

    def __init__(self, field, **kwargs):
        super().__init__(field, **kwargs)
        self.output_key = 'hist_logscale'
        self.action = 'histogram_logscale'
        self.arg_processors = {
            'scale_fact': ArgProcessor('scale_fact',
                                       map_func=lambda x: float(x),
                                       min_num_vals=1,
                                       out_type='single',
                                       expected='##',
                                       err_desc_str='to have a numeric value')
        }

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a logscaled histogram
        """
        sf = self.args['scale_fact']
        #
        # Adding "catch all" bins for anything less than 0 and between 0 - 1
        self.bins = []
        if (self.data_map[0] < 0.0):
            self.bins.append((self.data_map[0], 0.0))
        self.bins.append((0.0, 1.0))
        #
        low = 1.0
        exp = 1.0
        while (low < self.data_map[-1]):
            high = sf**exp
            self.bins.append((low, high))
            low = high
            exp += 1.0

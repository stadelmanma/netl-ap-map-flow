"""
Calculates a histogram over a defined percentile range for a data map.
Inherits most of it's structure from Histogram
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/03/22
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor, calc_percentile
from .__Histogram__ import Histogram


class HistogramRange(Histogram):

    def __init__(self, field, **kwargs):
        super().__init__(field, **kwargs)
        self.output_key = 'hist'
        self.action = 'histogram_range'
        self.arg_processors = {
            'num_bins': ArgProcessor('num_bins',
                                     map_func=lambda x: int(x),
                                     min_num_vals=1,
                                     out_type='single',
                                     expected='##',
                                     err_desc_str='to have a numeric value'),
            'range': ArgProcessor('range',
                                  map_func=lambda x: float(x),
                                  min_num_vals=2,
                                  out_type='list',
                                  expected='##, ##',
                                  err_desc_str='to have two numeric values')
        }

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a range histogram
        """
        num_bins = self.args['num_bins']
        min_val = calc_percentile(self.args['range'][0], self.data_vector)
        max_val = calc_percentile(self.args['range'][1], self.data_vector)
        step = (max_val - min_val)/float(num_bins)
        #
        low = min_val
        self.bins = []
        while (low < max_val):
            high = low + step
            self.bins.append((low, high))
            low = high

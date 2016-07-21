"""
Calculates a histogram over a defined percentile range for a data map.
Inherits most of it's structure from Histogram
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/06/13
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor, calc_percentile
from .__Histogram__ import Histogram


class HistogramRange(Histogram):
    r"""
    Performs a histogram where the minimum and maximum bin limits are set
    by percentiles and all values outside of that range are excluded. The
    interior values are handled the same as a basic histogram with bin sizes
    evenly spaced between the min and max percentiles given.
    """
    usage = 'hist_range [flags] num_bins=## range=##,## files=file1,file2,..'
    help_message = __doc__+'\n    '+'-'*80
    help_message += r"""
    Usage:
        apm_process_data_map.py {}

    Arguments:
        num_bins - integer value for the total number of bins
        range    - two numeric values to define the minimum and maximum
            data percentiles.
        files    - comma separated list of filenames

    Outputs:
        A file saved as (input_file)+'-histogram_range'+(extension)

    """.format(usage)
    help_message += '-'*80+'\n'

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
                                  expected='##,##',
                                  err_desc_str='to have two numeric values')
        }

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a range histogram
        """
        self.data_vector.sort()
        num_bins = self.args['num_bins']
        min_val = calc_percentile(self.args['range'][0], self.data_vector, False)
        max_val = calc_percentile(self.args['range'][1], self.data_vector, False)
        step = (max_val - min_val)/float(num_bins)
        #
        low = min_val
        self.bins = []
        while (low < max_val):
            high = low + step
            self.bins.append((low, high))
            low = high

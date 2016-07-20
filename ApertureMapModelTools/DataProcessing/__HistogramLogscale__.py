"""
Calculates a logarithmically spaced histogram for a data map.
Inherits most of it's structure from Histogram
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/06/13
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor
from .__Histogram__ import Histogram


class HistogramLogscale(Histogram):
    r"""
    Performs a histogram where the bin limits are logarithmically spaced
    based on the supplied scale factor. If there are negative values then
    the first bin contains everything below 0, the next bin will contain
    everything between 0 and 1.
    """
    usage = 'hist_logscale [flags] scale_fact=## files=file1,file2,..'
    help_message = __doc__+'\n    '+'-'*80
    help_message += r"""
    Usage:
        apm_process_data_map.py {}

    Arguments:
        scale_fact - numeric value to generate axis scale for bins. A
            scale fact of 10 creates bins: 0-1, 1-10, 10-100, etc.
        files      - comma separated list of filenames

    Outputs:
        A file saved as (input_file)+'-histogram_logscale'+(extension)

    """.format(usage)
    help_message += '-'*80+'\n'

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

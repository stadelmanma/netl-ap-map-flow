"""
Calculates a simple histogram for a data map. This also serves as the
super class for variants of a simple histogram.
#
Written By: Matthew Stadelman
Date Written: 2016/02/29
Last Modifed: 2016/03/07
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor, calc_percentile
from .__BaseProcessor__ import BaseProcessor


class Histogram(BaseProcessor):

    def __init__(self, field, **kwargs):
        super().__init__(field, **kwargs)
        self.output_key = 'hist'
        self.action = 'histogram'
        self.arg_processors = {
            'num_bins': ArgProcessor('num_bins',
                                     map_func=lambda x: int(x),
                                     min_num_vals=1,
                                     out_type='single',
                                     expected='##',
                                     err_desc_str='to have a numeric value')

        }
        self.bins = []

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a regular histogram
        """
        self.data_vector.sort()
        num_bins = self.args['num_bins']
        perc = 1.00
        min_val = self.data_vector[0]
        # ensuring the upper limit is greater than data_map[0]
        while (min_val <= self.data_vector[0]):
            min_val = calc_percentile(perc, self.data_vector)
            perc += 0.050
        print('Upper limit of first bin adjusted to percentile: '+str(perc))
        max_val = calc_percentile(99.0, self.data_vector)
        step = (max_val - min_val)/(num_bins - 2)
        #
        self.bins = [(self.data_vector[0], min_val)]
        low = min_val
        while (low < max_val):
            high = low + step
            self.bins.append((low, high))
            low = high
        # slight increase to prevent last point being excluded
        self.bins.append((low, self.data_vector[-1]*1.0001))

    def process_data(self, **kwargs):
        r"""
        Calculates a histogram from a range of data. This uses the 1st and
        99th percentiles as limits when defining bins
        """
        #
        self.processed_data = []
        self.define_bins()
        #
        # populating bins
        num_vals = 0
        data = self.data_vector.__iter__()
        bins = self.bins.__iter__()
        try:
            val = data.__next__()
            bin = bins.__next__()
            b = 0
            while True:
                if val < bin[0]:
                    val = data.__next__()
                elif ((val >= bin[0]) and (val < bin[1])):
                    num_vals += 1
                    val = data.__next__()
                else:
                    self.processed_data.append((bin[0], bin[1], num_vals))
                    num_vals = 0
                    bin = bins.__next__()
                    b += 1
        except StopIteration:
            for b in range(b, len(self.bins)):
                bin = self.bins[b]
                self.processed_data.append((bin[0], bin[1], num_vals))
                num_vals = 0  # setting to 0 for all subsequent bins

    def output_data(self, filename=None, delim=',', **kwargs):
        r"""
        Creates the output content for histograms
        """
        #
        if filename is None:
            filename = self.infile
        #
        # getting index before the extension
        ldot = filename.rfind('.')
        #
        # naming ouput file
        self.outfile_name = filename[:ldot]+'-'+self.action+filename[ldot:]
        #
        # outputting data
        content = 'Histogram data from file: '+self.infile+'\n'
        content += 'Low value, High value, # Data Points\n'
        fmt_str = '{0}'+delim+'{1}'+delim+'{2}\n'
        for dat in self.processed_data:
            content += fmt_str.format(dat[0], dat[1], dat[2])
        content += '\n'
        #
        self.outfile_content = content

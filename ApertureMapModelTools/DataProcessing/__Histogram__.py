"""
Calculates a simple histogram for a data map. This also serves as the
super class for variants of a simple histogram.
#
Written By: Matthew Stadelman
Date Written: 2016/02/29
Last Modifed: 2016/06/13
#
"""
from ApertureMapModelTools.__core__ import _get_logger, calc_percentile
from .__BaseProcessor__ import BaseProcessor
logger = _get_logger(__name__)


class Histogram(BaseProcessor):
    r"""
    Performs a basic histogram of the data based on the number of bins
    desired. The first bin contains all values below the 1st percentile
    and the last bin contains all values above the 99th percentile to keep
    axis scales from being bloated by extrema.
    kwargs include:
        num_bins - integer value for the total number of bins
    """
    def __init__(self, field, **kwargs):
        super().__init__(field)
        self.args.update(kwargs)
        self.output_key = 'hist'
        self.action = 'histogram'
        self.bins = []

    def define_bins(self, **kwargs):
        r"""
        This defines the bins for a regular histogram
        """
        self.data_vector.sort()
        num_bins = self.args['num_bins']
        perc = 1.00
        min_val = self.data_vector[0]
        #
        # ensuring the upper limit is greater than data_map[0]
        while (min_val <= self.data_vector[0]):
            min_val = calc_percentile(perc, self.data_vector)
            perc += 0.050
        #
        msg = 'Upper limit of first bin adjusted to percentile: {}'
        logger.info(msg.format(perc))
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

    def process_data(self, preserve_bins=False, **kwargs):
        r"""
        Calculates a histogram from a range of data. This uses the 1st and
        99th percentiles as limits when defining bins
        """
        #
        self.processed_data = []
        if not preserve_bins:
            self.define_bins()
        #
        # populating bins
        num_vals = 0
        data = self.data_vector.__iter__()
        bins = self.bins.__iter__()
        try:
            val = data.__next__()
            data_bin = bins.__next__()
            b = 0
            while True:
                if val < data_bin[0]:
                    val = data.__next__()
                elif val >= data_bin[0] and val < data_bin[1]:
                    num_vals += 1
                    val = data.__next__()
                else:
                    data_bin = (data_bin[0], data_bin[1], num_vals)
                    self.processed_data.append(data_bin)
                    num_vals = 0
                    data_bin = bins.__next__()
                    b += 1

        except StopIteration:
            for b in range(b, len(self.bins)):
                data_bin = self.bins[b]
                self.processed_data.append((data_bin[0], data_bin[1], num_vals))
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

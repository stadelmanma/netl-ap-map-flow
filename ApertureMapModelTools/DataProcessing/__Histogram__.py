"""
Calculates a simple histogram for a data map. This also serves as the
super class for variants of a simple histogram.
#
Written By: Matthew Stadelman
Date Written: 2016/02/29
Last Modifed: 2016/10/25
#
"""
import scipy as sp
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

    @classmethod
    def _add_subparser(cls, subparsers, parent):
        r"""
        Adds a specific action based sub-parser to the supplied arg_parser
        instance.
        """
        parser = subparsers.add_parser(cls.__name__,
                                       aliases=['hist'],
                                       parents=[parent],
                                       help='calculates histogram of data')
        #
        parser.add_argument('num_bins', type=int,
                            help='number of bins to utilze in histogram')

    def define_bins(self):
        r"""
        This defines the bins for a regular histogram
        """
        self.data_vector.sort()
        num_bins = self.args['num_bins']
        min_val = calc_percentile(1.0, self.data_vector, False)
        max_val = calc_percentile(99.0, self.data_vector, False)
        #
        # creating initial bins
        low = list(sp.linspace(min_val, max_val, num_bins))
        high = list(sp.linspace(min_val, max_val, num_bins))[1:]
        high.append(self.data_vector[-1]*1.0001)
        #
        # adding lower bin if needed
        if self.data_vector[0] < min_val:
            low.insert(0, self.data_vector[0])
            high.insert(0, min_val)
        #
        self.bins = [bin_ for bin_ in zip(low, high)]

    def _process_data(self, preserve_bins=False):
        r"""
        Calculates a histogram from a range of data. This uses the 1st and
        99th percentiles as limits when defining bins
        """
        #
        if not preserve_bins:
            self.define_bins()
        #
        # populating bins
        edges = sp.array(self.bins[0][0])
        edges = sp.append(edges, sp.array(self.bins)[:, 1])
        data, edges = sp.histogram(self.data_vector, bins=edges)
        #
        # storing data
        self.processed_data = []
        for (low, high), count in zip(self.bins, data):
            self.processed_data.append((low, high, count))

    def _output_data(self, filename=None, delim=','):
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

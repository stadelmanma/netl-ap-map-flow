"""
Calculates a set of percentiles for a dataset
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/10/20
#
"""
from collections import OrderedDict
from ..__core__ import calc_percentile
from .__BaseProcessor__ import BaseProcessor


class Percentiles(BaseProcessor):
    r"""
    Automatic method to calculate and output a list of data percentiles.
    kwargs include:
       perc : list of percentiles to calculate (required)
       key_format : format to write percentile dictionary keys in (optional)
       value_format : format to write percentile values in (optional)

    """
    def __init__(self, field, **kwargs):
        super().__init__(field)
        self.args.update(kwargs)
        self.output_key = 'perc'
        self.action = 'percentile'

    def _process_data(self):
        r"""
        Takes a list of percentiles specified in self.args and generates
        the corresponding set of values.
        """
        perc_list = self.args['perc']
        perc_list.sort()
        key_fmt = self.args.get('key_format', '{:4.2f}')
        #
        # getting percentiles from data map
        self.data_vector.sort()
        self.processed_data = OrderedDict()
        for perc in perc_list:
            val = calc_percentile(perc, self.data_vector, sort=False)
            self.processed_data[key_fmt.format(perc)] = val

    def _output_data(self, filename=None, delim=','):
        r"""
        Creates the output content for percentiles
        """
        #
        if filename is None:
            filename = self.infile
        #
        # getting index before the extension
        ldot = filename.rfind('.')
        #
        # naming ouput file
        self.outfile_name = filename[:ldot]+'-percentiles'+filename[ldot:]
        #
        # outputting data
        content = 'Percentile data from file: '+self.infile+'\n'
        content += 'percentile'+delim+'value\n'
        #
        fmt = '{{}}{}{}\n'.format(delim, self.args.get('value_format', '{}'))
        for perc, value in self.processed_data.items():
            content += fmt.format(perc, value)
        content += '\n'
        #
        self.outfile_content = content

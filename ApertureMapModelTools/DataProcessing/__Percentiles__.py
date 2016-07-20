"""
Calculates a set of percentiles for a dataset
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/06/13
#
"""
from ApertureMapModelTools.__core__ import ArgProcessor, calc_percentile
from .__BaseProcessor__ import BaseProcessor


class Percentiles(BaseProcessor):
    r"""
    Automatic method to calculate and output a list of data percentiles
    """
    usage = 'pctle [flags] perc=##,##,..,## files=file1,file2,..'
    help_message = __doc__+'\n    '+'-'*80
    help_message += r"""
    Usage:
        apm_process_data_map.py {}

    Arguments:
        perc - comma separated list of numbers, ex: perc=10,25,50,75,90
        files- comma separated list of filenames

    Outputs:
        A file saved as (input_file)+'-percentiles'+(extension)

    """.format(usage)
    help_message += '-'*80+'\n'

    def __init__(self, field, **kwargs):
        super().__init__(field, **kwargs)
        self.output_key = 'perc'
        self.action = 'percentile'
        self.arg_processors = {
            'perc': ArgProcessor('perc',
                                 map_func=lambda x: float(x),
                                 min_num_vals=1,
                                 out_type='list',
                                 expected='##, ##, ##, ..., ##',
                                 err_desc_str='to have 1 -> n numeric values')
        }

    def process_data(self, **kwargs):
        r"""
        Takes a list of percentiles specified in self.args and generates
        the corresponding set of values.
        """
        perc_list = self.args['perc']
        perc_list.sort()
        #
        # getting percentiles from data map
        self.data_vector.sort()
        self.processed_data = dict()
        for perc in perc_list:
            val = calc_percentile(perc, self.data_vector, sort=False)
            self.processed_data['{:4.2f}'.format(perc)] = val

    def output_data(self, filename=None, delim=',', **kwargs):
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
        perc_keys = list(self.processed_data.keys())
        perc_keys.sort()
        for perc in perc_keys:
            content += perc + delim + str(self.processed_data[perc]) + '\n'
        content += '\n'
        #
        self.outfile_content = content

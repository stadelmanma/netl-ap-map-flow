"""
Calculates a set of percentiles for a dataset
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/03/22
#
"""
#
from ApertureMapModelTools.__core__ import ArgProcessor, calc_percentile
from .__BaseProcessor__ import BaseProcessor
#
#
class Percentiles(BaseProcessor):
    #
    def __init__(self, field, **kwargs):
        super().__init__(field, **kwargs)
        self.output_key = 'perc'
        self.action = 'percentile'
        self.arg_processors = {
            'perc': ArgProcessor('perc',
                                   map_func = lambda x: float(x),
                                   min_num_vals = 1,
                                   out_type = 'list' ,
                                   expected = '##, ##, ##, ..., ##',
                                   err_desc_str='to have 1 -> n numeric values')
        }
    #
    def process_data(self, **kwargs):
        r"""
        Takes a list of percentiles specified in self.args and generates
        the corresponding set of values.
        """
        perc_list = self.args["perc"]
        perc_list.sort()
        #
        # getting percentiles from data map
        self.data_map.sort()
        self.processed_data = dict()
        for perc in perc_list:
            self.processed_data[perc] = calc_percentile(perc, self.data_map, sort=False)
    #
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
            content += str(perc)+delim+str(self.processed_data[perc])+"\n"
        content += "\n"
        #
        self.outfile_content = content
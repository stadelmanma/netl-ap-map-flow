"""
Calculates a simple histogram from a data map. This also serves as the 
super class for varients of a simple histogram.
#
Written By: Matthew Stadelman
Date Written: 2016/02/29
Last Modifed: 2016/02/29
#
"""
#
from ApertureMapModelTools.__core__ import *
from .__BaseProcessor__ import BaseProcessor
#
#
class Histogram(BaseProcessor):
    #
    def __init__(self,field,**kwargs):
        super().__init__(field,**kwargs)
        self.output_key = 'hist'
        self.action = 'histogram'
        self.arg_processors = {
            'num_bins' :  ArgProcessor('num_bins',
                                       map_func = lambda x : int(x),
                                       min_num_vals = 1,
                                       out_type = 'single' ,
                                       expected = '##',
                                       err_desc_str='to have a numeric value')

        }
    #
    def process_data(self,**kwargs):
        r"""
        Calculates a histogram from a range of data. This uses the 1st and
        99th percentiles as limits when defining bins
        """
        #
        self.data_map.sort()
        self.processed_data = dict()
        self.define_bins()
    #
    def define_bins(self,**kwargs):
        r"""
        This defines the bins for a regular histogram
        """
        num_bins = self.args['num_bins']
        perc = 1.00
        min_val = self.data_map[0]
        while (min_val <= self.data_map[0]):
            min_val = calc_percentile(perc,self.data_map)
            perc += 0.100
        max_val = calc_percentile(99.0,self.data_map)
        step = (max_val - min_val)/(num_bins-1.0)
        #
        self.bins = [(self.data_map[0],min_val)]
        low = min_val
        while (low < max_val):
            high = low + step
            self.bins.append((low,high))
            low = high
        self.bins.append((low,max_val))
    #
    def output_data(self,filename=None,delim = ',',**kwargs):
        r"""
        Creates the output content for histograms
        """
        raise NotImplementedError('Not finished yet')

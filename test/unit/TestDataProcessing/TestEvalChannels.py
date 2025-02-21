"""
Handles testing of the EvalChannels class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/10/25
#
"""
import argparse
import os
import pytest
import numpy as np
from apmapflow.data_processing.eval_channels import EvalChannels


class TestEvalChannels:
    r"""
    Testing each method of the EvalChannels class
    """
    def test_initialization(self, data_field_class):
        eval_chans = EvalChannels(data_field_class())
        assert not eval_chans.args
        #
        eval_chans = EvalChannels(data_field_class(), thresh='x')
        assert eval_chans.args['thresh'] == 'x'

    def test_add_sub_parser(self):
        # setting up required parsers
        parser = argparse.ArgumentParser()
        parent = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers()

        # adding percentiles subparser
        EvalChannels._add_subparser(subparsers, parent)

        # testing parser
        cargs = 'EvalChannels x 10.0'.split()
        args = parser.parse_args(cargs)
        cargs = 'chans z 5'.split()
        args = parser.parse_args(cargs)
        #
        assert args.axis == 'z'
        assert args.thresh == 5.0
        #
        cargs = 'chans y 5'.split()
        with pytest.raises(SystemExit):
            args = parser.parse_args(cargs)

    def test_process_data(self, data_field_class):
        r"""
        checking if the process data method works
        """
        #
        # creating horizontal channels
        eval_chans = EvalChannels(data_field_class())
        eval_chans.data_map = np.zeros((eval_chans.nz, eval_chans.nx), dtype=int)
        eval_chans.data_map[2:4, :] = 255
        eval_chans.data_map[6:9, :] = 255
        eval_chans.data_vector = np.ravel(eval_chans.data_map)
        eval_chans.args = {
            'axis': 'x',
            'thresh': 100
        }
        eval_chans._process_data()
        #
        # creating vertical channels
        eval_chans = EvalChannels(data_field_class())
        eval_chans.data_map = np.zeros((eval_chans.nz, eval_chans.nx), dtype=int)
        eval_chans.data_map[:, 2:4] = 255
        eval_chans.data_map[:, 6:9] = 255
        eval_chans.data_vector = np.ravel(eval_chans.data_map)
        eval_chans.args = {
            'axis': 'z',
            'thresh': 100
        }
        eval_chans._process_data()
        #
        eval_chans.args = {
            'axis': 'y',
            'thresh': 100
        }
        eval_chans._process_data()

    def test_output_data(self, data_field_class):
        #
        eval_chans = EvalChannels(data_field_class())
        eval_chans.infile = os.path.join(TEMP_DIR, 'eval-chans')
        eval_chans.args = {
            'axis': 'z',
            'thresh': 100
        }
        eval_chans.processed_data = {}
        #
        eval_chans.processed_data['chan_indicies_per_row'] = [
            [(2, 3), (6, 8)], [(12, 13), (16, 18)], [(22, 23), (26, 28)],
            [(32, 33), (36, 38)], [(42, 43), (46, 48)], [(52, 53), (56, 58)],
            [(62, 63), (66, 68)], [(72, 73), (76, 78)], [(82, 83), (86, 88)],
            [(92, 93), (96, 98)]
        ]
        eval_chans.processed_data['chans_per_row'] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        eval_chans.processed_data['chan_widths_per_row'] = [[2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3]]
        eval_chans.processed_data['avg_chan_width_per_row'] = [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5]
        #
        eval_chans._output_data()
        assert eval_chans.outfile_content

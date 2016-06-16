"""
Handles testing of the EvalChannels class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/06/12
#
"""
import os
import scipy as sp
from ApertureMapModelTools.DataProcessing.__EvalChannels__ import EvalChannels


class TestEvalChannels:
    r"""
    Testing each method of the EvalChannels class
    """
    def test_initialization(self, data_field_class):
        r"""
        Checking args so an error is generated if they change and the test does not
        """
        eval_chans = EvalChannels(data_field_class())
        args = list(eval_chans.arg_processors.keys())
        args.sort()
        #
        assert len(args) == 2
        for arg, test in zip(args, ['dir', 'thresh']):
            assert arg == test

    def test_process_data(self, data_field_class):
        r"""
        checking if the process data method works
        """
        #
        # creating horizontal channels
        eval_chans = EvalChannels(data_field_class())
        eval_chans.data_map = sp.zeros((eval_chans.nz, eval_chans.nx), dtype=int)
        eval_chans.data_map[2:4, :] = 255
        eval_chans.data_map[6:9, :] = 255
        eval_chans.data_vector = sp.ravel(eval_chans.data_map)
        eval_chans.args = {
            'dir': 'x',
            'thresh': 100
        }
        eval_chans.process_data()
        #
        # creating vertical channels
        eval_chans = EvalChannels(data_field_class())
        eval_chans.data_map = sp.zeros((eval_chans.nz, eval_chans.nx), dtype=int)
        eval_chans.data_map[:, 2:4] = 255
        eval_chans.data_map[:, 6:9] = 255
        eval_chans.data_vector = sp.ravel(eval_chans.data_map)
        eval_chans.args = {
            'dir': 'z',
            'thresh': 100
        }
        eval_chans.process_data()
        #
        eval_chans.args = {
            'dir': 'y',
            'thresh': 100
        }
        eval_chans.process_data()

    def test_output_data(self, data_field_class):
        #
        eval_chans = EvalChannels(data_field_class())
        eval_chans.infile = os.path.join(TEMP_DIR, 'eval-chans')
        eval_chans.args = {
            'dir': 'z',
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
        eval_chans.output_data()

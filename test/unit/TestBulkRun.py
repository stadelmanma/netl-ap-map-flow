"""
Handles testing of the bulk run module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/11
#
"""
#
import os
import pytest
from ApertureMapModelTools import BulkRun


class TestBulkRun:
    r"""
    Executes a set of functions to handle testing of the bulk run
    routines
    """
    def setup_class(self):
        pass

    def test_arg_input(self):
        r"""
        Testing various inputs to the argument parser
        """
        # regular input line
        line = 'FRAC-PRESS:   100  KPA'
        arg = BulkRun.ArgInput(line)
        assert arg.value == '100'
        arg.update_value('200')
        assert arg.value == '200'
        #
        # commented regular line
        line = ';OVERWRITE EXISTING FILES'
        arg = BulkRun.ArgInput(line)
        arg.update_value('OVERWRITE')
        line = arg.output_line()
        assert line == 'OVERWRITE'
        # line with colon but no following value
        line = 'FRAC-PRESS: '
        arg = BulkRun.ArgInput(line)
        # empty line
        line = ''
        arg = BulkRun.ArgInput(line)

    def test_dummy_process(self):
        r"""
        Ensuring dummy process class returns 0
        """
        proc = BulkRun.DummyProcess()
        assert proc.poll() == 0

    def test_input_file(self):
        #
        inp_file = BulkRun.InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        assert inp_file.arg_order
        inp_file2 = inp_file.clone()
        assert inp_file.arg_order == inp_file2.arg_order
        #
        new_args = {
            'FRAC-PRESS': '300',
            'MANIFOLD': 'TRUE',
            'BAD-ARG': 'IN FORMATS'
        }
        inp_file.update_args(new_args)
        assert inp_file.arg_dict['FRAC-PRESS'].value == new_args['FRAC-PRESS']
        assert inp_file.arg_dict['MANIFOLD'].value == new_args['MANIFOLD']
        assert inp_file.filename_format_args['BAD-ARG'] == new_args['BAD-ARG']
        #
        # testing __repr__ function with an undefined file in formats
        with pytest.raises(KeyError):
            inp_file.filename_formats['NONEXISTANT-FILE'] = 'NONEXISTANT-FILE-FORMAT'
            print(inp_file)
        #
        # testing __repr__ with valid file inputs
        del inp_file.filename_formats['NONEXISTANT-FILE']
        print(inp_file)
        #
        # writing the output file to TEMP_DIR without an EXE-FILE and a directory needing created
        del inp_file.arg_order[inp_file.arg_order.index('EXE-FILE')]
        del inp_file.arg_dict['EXE-FILE']
        inp_file.filename_formats['PVT-PATH'] = os.path.join(TEMP_DIR, 'new-dir', 'PVT/H2O_TEMP_058F.CSV')
        inp_file.write_inp_file(alt_path=TEMP_DIR)
        #
        # re-reading the output file to test what happens with no EXE-FILE
        with pytest.raises(SystemExit):
            inp_file = BulkRun.InputFile(os.path.join(TEMP_DIR, inp_file.outfile_name))

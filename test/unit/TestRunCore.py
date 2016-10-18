"""
Handles testing of the run model module core methods and objects
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/11
#
"""
import os
import pytest
from ApertureMapModelTools import RunModel
from ApertureMapModelTools.RunModel.__run_model_core__ import ArgInput


class TestRunCore:
    r"""
    Executes a set of functions to test each of the core objects and methods
    """
    def setup_class(self):
        pass

    def test_arg_input(self):
        r"""
        Testing various inputs to the argument parser
        """
        # regular input line
        line = 'INLET-PRESS:   100  KPA ;CMT-MSG'
        arg = ArgInput(line)
        assert arg.keyword == 'INLET-PRESS'
        assert arg.value == '100'
        assert arg.comment_msg == ';CMT-MSG'
        arg.update_value('200')
        assert arg.value == '200'
        #
        # commented regular line
        line = ';OVERWRITE EXISTING FILES'
        arg = ArgInput(line)
        assert arg.commented_out is True
        arg.update_value('OVERWRITE')
        assert arg.commented_out is False
        line = arg.output_line()
        assert line.strip() == 'OVERWRITE'
        # line with colon but no following value
        line = 'INLET-PRESS: '
        arg = ArgInput(line)
        assert arg.value == 'NONE'
        # empty line
        line = ''
        arg = ArgInput(line)
        # line with quote
        line = 'KEYWORD: "VALUE1 + VALUE2"'
        arg = ArgInput(line)
        assert arg.value == 'VALUE1 + VALUE2'
        # line with un-matched quote, causes shlex_split to fail
        line = 'TEST: "UNMATCHED QUOTE'
        arg = ArgInput(line)
        assert arg.value == '"UNMATCHED'

    def test_input_file(self):
        #
        inp_file = RunModel.InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        assert inp_file.keys()
        #
        # testing clone method
        inp_file2 = inp_file.clone()
        assert [inp_file[k].value for k in inp_file.keys() if k] == [inp_file[k].value for k in inp_file2.keys() if k]
        #
        # creating instance of InputFil using an existing instance
        inp_file2 = RunModel.InputFile(inp_file)
        #
        new_args = {
            'INLET-PRESS': '300',
            'BAD-ARG': 'IN FORMATS'
        }
        inp_file.update_args(new_args)
        assert inp_file['INLET-PRESS'].value == new_args['INLET-PRESS']
        assert inp_file.filename_format_args['BAD-ARG'] == new_args['BAD-ARG']
        #
        # testing retrivial of uncommented values
        uncmt_keys = [k for k, v in inp_file.items() if not v.commented_out]
        uncmt_dict = inp_file.get_uncommented_values()
        assert uncmt_keys == list(uncmt_dict.keys())
        #
        # testing __repr__ function with an undefined file in formats
        with pytest.raises(KeyError):
            inp_file.filename_formats['NONEXISTANT-FILE'] = 'NONEXISTANT-FILE-FORMAT'
            print(inp_file)
        del inp_file.filename_formats['NONEXISTANT-FILE']
        #
        # writing the output file to TEMP_DIR without an EXE-FILE and a directory needing created
        del inp_file['EXE-FILE']
        inp_file.filename_formats['PVT-FILE'] = os.path.join(TEMP_DIR, 'new-dir', 'PVT/H2O_TEMP_058F.CSV')
        inp_file.filename_formats['input_file'] = 'BAD-INPUT-FILE.INP'
        inp_file.write_inp_file(alt_path=TEMP_DIR)
        #
        # re-reading the output file to test what happens with no EXE-FILE
        with pytest.raises(SystemExit):
            inp_file = RunModel.InputFile(os.path.join(TEMP_DIR, inp_file.outfile_name))

    def test_estimate_req_RAM(self):
        r"""
        Ensuring RAM req is being calculated
        """
        map_file = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'parallel-plate-01vox.txt')
        RunModel.estimate_req_RAM([map_file], 10)
        with pytest.raises(EnvironmentError):
            RunModel.estimate_req_RAM([map_file], 0)

    def test_run_model(self):
        r"""
        Testing the method used to run a single instance of the model. This also
        hits the InputFile class pretty heavy
        """
        inp_file = RunModel.InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        #
        # updating paths so they are absolute
        files = ['SUMMARY-FILE', 'STAT-FILE', 'APER-FILE', 'FLOW-FILE', 'PRESS-FILE', 'VTK-FILE']
        for file in files:
            inp_file[file].update_value(os.path.join(TEMP_DIR, file+'.RCTEST'))
        inp_file.filename_formats['input_file'] = os.path.join(TEMP_DIR, 'TEST_INIT.INP')
        #
        dirs = os.path.split(inp_file['PVT-FILE'].value)
        new_path = os.path.join(FIXTURE_DIR, 'PVT', 'H2O_TEMP_058F.CSV')
        inp_file['PVT-FILE'].update_value(new_path)
        #
        dirs = os.path.split(inp_file['APER-MAP'].value)
        new_path = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'parallel-plate-01vox.txt')
        inp_file['APER-MAP'].update_value(new_path)
        #
        inp_file.outfile_name = os.path.join(TEMP_DIR, 'TEST-INIT-run-model.INP')
        exe_path = os.path.realpath(os.path.join('.', inp_file['EXE-FILE'].value))
        inp_file['EXE-FILE'].update_value(exe_path, False)
        #
        # running the model both async and in sync
        proc = RunModel.run_model(inp_file, synchronous=False)
        assert proc.poll() is None
        #
        proc = RunModel.run_model(inp_file, synchronous=True, show_stdout=True)
        assert proc.poll() == 0

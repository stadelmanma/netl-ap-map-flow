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
import ApertureMapModelTools as amt
from ApertureMapModelTools import run_model
from ApertureMapModelTools.run_model.run_model import ArgInput


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
        line = ';INLET-PRESS:   100  KPA ;CMT-MSG'
        arg = ArgInput(line)
        assert arg.keyword == 'INLET-PRESS'
        assert arg.value == '100'
        assert arg.unit == 'KPA'
        assert arg.comment_msg == ';CMT-MSG'
        assert arg.commented_out is True
        assert arg.line == str(arg)
        #
        arg.value = 200
        arg.unit = 'PSI'
        assert arg.value == '200'
        assert arg.unit == 'PSI'
        assert arg.commented_out is False
        #
        # line with no value
        line = ';OVERWRITE EXISTING FILES'
        arg = ArgInput(line)
        assert arg.value == 'OVERWRITE EXISTING FILES'
        assert arg.unit is None
        arg.value = ('', True)
        assert arg.line == ';'
        #
        # line with colon but no following value
        line = 'INLET-PRESS:'
        arg = ArgInput(line)
        assert arg.value == ''
        assert arg.unit == ''
        assert arg.commented_out is False
        #
        # empty line
        line = ''
        arg = ArgInput(line)
        assert arg.value == arg.line
        #
        # line with quote
        line = 'KEYWORD: "VALUE1 + VALUE2"'
        arg = ArgInput(line)
        assert arg.value == '"VALUE1 + VALUE2"'
        #
        # line with un-matched quote, causes shlex_split to fail
        line = 'TEST: "UNMATCHED QUOTE'
        arg = ArgInput(line)
        assert arg.value == '"UNMATCHED'
        assert arg.unit == 'QUOTE'

    def test_input_file(self):
        #
        inp_file = run_model.InputFile(os.path.join(FIXTURE_DIR, 'test-model-inputs.txt'))
        assert inp_file.keys()
        #
        # testing clone method
        inp_file2 = inp_file.clone()
        assert [inp_file[k].value for k in inp_file.keys() if k] == [inp_file[k].value for k in inp_file2.keys() if k]
        #
        # creating instance of InputFil using an existing instance
        inp_file2 = run_model.InputFile(inp_file)
        #
        new_args = {
            'INLET-PRESS': '300',
            'BAD-ARG': 'IN FORMATS'
        }
        inp_file.update(new_args)
        assert inp_file['INLET-PRESS'].value == new_args['INLET-PRESS']
        assert inp_file.filename_format_args['BAD-ARG'] == new_args['BAD-ARG']
        #
        with pytest.raises(TypeError):
            inp_file.update('a', 'b', 'c')
        #
        # adding a new parameter to the file
        model_path = os.path.join(amt.__path__[0], amt.DEFAULT_MODEL_NAME)
        inp_file.add_parameter(';EXE-FILE: ' + model_path)
        assert inp_file['EXE-FILE'].value == model_path
        #
        # testing retrivial of uncommented values
        uncmt_keys = [k for k, v in inp_file.items() if not v.commented_out]
        uncmt_dict = inp_file.get_uncommented_values()
        assert uncmt_keys == list(uncmt_dict.keys())
        #
        # testing __str__ function with an undefined file in formats
        with pytest.raises(KeyError):
            inp_file.filename_formats['NONEXISTANT-FILE'] = 'NONEXISTANT-FILE-FORMAT'
            print(inp_file)
        del inp_file.filename_formats['NONEXISTANT-FILE']
        #
        # writing the output file to TEMP_DIR with a valid EXE-FILE

        inp_file.filename_formats['input_file'] = 'BAD-INPUT-FILE.INP'
        inp_file.write_inp_file(alt_path=TEMP_DIR)
        #
        # re-reading the output file to test a valid EXE-FILE
        inp_file = run_model.InputFile(os.path.join(TEMP_DIR, inp_file.outfile_name))
        assert inp_file.executable == model_path
        #
        # writing the output file to TEMP_DIR with a non-existant EXE-FILE
        inp_file['EXE-FILE'] = amt.DEFAULT_MODEL_NAME + '-junk'
        inp_file.filename_formats['input_file'] = 'BAD-INPUT-FILE.INP'
        inp_file.write_inp_file(alt_path=TEMP_DIR)
        #
        # re-reading the output file to test an invalid EXE-FILE
        inp_file = run_model.InputFile(os.path.join(TEMP_DIR, inp_file.outfile_name))
        assert inp_file.executable == model_path

    def test_estimate_req_RAM(self):
        r"""
        Ensuring RAM req is being calculated
        """
        map_file = os.path.join(FIXTURE_DIR, 'maps', 'parallel-plate-01vox.txt')
        run_model.estimate_req_RAM([map_file], 10)
        with pytest.raises(EnvironmentError):
            run_model.estimate_req_RAM([map_file], 0)

    def test_run_model(self):
        r"""
        Testing the method used to run a single instance of the model. This also
        hits the InputFile class pretty heavy
        """
        inp_file = run_model.InputFile(os.path.join(FIXTURE_DIR, 'test-model-inputs.txt'))
        #
        # updating paths so they are absolute
        files = ['SUMMARY-FILE', 'STAT-FILE', 'APER-FILE', 'FLOW-FILE', 'PRESS-FILE', 'VTK-FILE']
        for file in files:
            inp_file.filename_formats[file] = os.path.join(TEMP_DIR, 'extra', file+'.RCTEST')
        inp_file.filename_formats['input_file'] = os.path.join(TEMP_DIR, 'test-model-inputs.txt')
        #
        new_path = os.path.join(FIXTURE_DIR, 'maps', 'parallel-plate-01vox.txt')
        inp_file['APER-MAP'] = new_path
        #
        # running the model both async and in sync
        proc = run_model.run_model(inp_file, synchronous=False)
        assert proc.poll() is None
        #
        proc = run_model.run_model(inp_file, synchronous=True, show_stdout=True)
        assert proc.poll() == 0
        assert os.path.isfile(os.path.join(TEMP_DIR, 'extra', 'SUMMARY-FILE.RCTEST'))

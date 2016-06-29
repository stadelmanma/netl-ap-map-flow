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
        line = 'FRAC-PRESS:   100  KPA'
        arg = ArgInput(line)
        assert arg.value == '100'
        arg.update_value('200')
        assert arg.value == '200'
        #
        # commented regular line
        line = ';OVERWRITE EXISTING FILES'
        arg = ArgInput(line)
        arg.update_value('OVERWRITE')
        line = arg.output_line()
        assert line == 'OVERWRITE'
        # line with colon but no following value
        line = 'FRAC-PRESS: '
        arg = ArgInput(line)
        # empty line
        line = ''
        arg = ArgInput(line)

    def test_input_file(self):
        #
        inp_file = RunModel.InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        assert inp_file.arg_order
        #
        # testing clone method
        inp_file2 = inp_file.clone()
        assert [l for l in inp_file.arg_order if l] == [l for l in inp_file2.arg_order if l]
        assert [inp_file[k].value for k in inp_file.arg_order if k] == [inp_file[k].value for k in inp_file2.arg_order if k]
        #
        # creating instance of InputFil using an existing instance
        inp_file2 = RunModel.InputFile(inp_file)
        #
        new_args = {
            'FRAC-PRESS': '300',
            'MANIFOLD': 'TRUE',
            'BAD-ARG': 'IN FORMATS'
        }
        inp_file.update_args(new_args)
        assert inp_file['FRAC-PRESS'].value == new_args['FRAC-PRESS']
        assert inp_file['MANIFOLD'].value == new_args['MANIFOLD']
        assert inp_file.filename_format_args['BAD-ARG'] == new_args['BAD-ARG']
        #
        # testing __repr__ function with an undefined file in formats
        with pytest.raises(KeyError):
            inp_file.filename_formats['NONEXISTANT-FILE'] = 'NONEXISTANT-FILE-FORMAT'
            print(inp_file)
        del inp_file.filename_formats['NONEXISTANT-FILE']
        #
        # writing the output file to TEMP_DIR without an EXE-FILE and a directory needing created
        del inp_file.arg_order[inp_file.arg_order.index('EXE-FILE')]
        del inp_file['EXE-FILE']
        inp_file.filename_formats['PVT-PATH'] = os.path.join(TEMP_DIR, 'new-dir', 'PVT/H2O_TEMP_058F.CSV')
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
        map_file = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT')
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
        files = ['SUMMARY-PATH', 'STAT-FILE', 'APER-FILE', 'FLOW-FILE', 'PRESS-FILE', 'VTK-FILE']
        for file in files:
            dirs = os.path.split(inp_file[file].value)
            new_path = os.path.join(TEMP_DIR, dirs[-1])
            inp_file[file].update_value(new_path)
        inp_file.filename_formats['input_file'] = os.path.join(TEMP_DIR, 'TEST_INIT.INP')
        #
        dirs = os.path.split(inp_file['PVT-PATH'].value)
        new_path = os.path.join(FIXTURE_DIR, 'PVT', 'H2O_TEMP_058F.CSV')
        inp_file['PVT-PATH'].update_value(new_path)
        #
        dirs = os.path.split(inp_file['APER-MAP'].value)
        new_path = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT')
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
        proc = RunModel.run_model(inp_file, synchronous=True, pipe_output=True)
        assert proc.poll() == 0
        assert proc.stdout.read()

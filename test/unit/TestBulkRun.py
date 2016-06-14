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

    def test_estimate_req_RAM(self):
        r"""
        Ensuring RAM req is being calculated
        """
        map_file = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT')
        BulkRun.estimate_req_RAM([map_file], 10)
        with pytest.raises(SystemExit):
            BulkRun.estimate_req_RAM([map_file], 0)

    def test_combine_run_args(self, input_file_class):
        r"""
        ensuring this returns a valid list of input file objects
        """
        map_args = [{'aperture_map': 'test-map.txt',
                     'filename_formats': {'APER-FILE': 'test-map.txt',
                                          'FLOW-FILE': 'test-flow.csv',
                                          'PRESS-FILE': 'test-press.csv',
                                          'STAT-FILE': 'test-stat.csv',
                                          'SUMMARY-PATH': 'test-summary.txt',
                                          'VTK-FILE': 'test-para.vtk',
                                          'input_file': 'test-init.inp'},
                     'run_params': {'FRAC-PRESS': ['1000'],
                                    'MAP': ['1'],
                                    'OUTLET-PRESS': ['995.13', '993.02', '989.04', '977.78', '966.20', '960.53'],
                                    'OUTPUT-UNITS': ['PSI, MM, MM^3/MIN'],
                                    'ROUGHNESS': ['2.50'],
                                    'VOXEL': ['26.8']},
                     'RAM_req': 0.0}]
        inp_file_list = BulkRun.combine_run_args(map_args, input_file_class())
        assert len(inp_file_list) == 6

    def test_check_processes(self):
        r"""
        Testing if check processes works properly
        """

        class TestProcess:
            def __init__(self):
                self.value = None

            def poll(self):
                if self.value is None:
                    self.value = 0
                    return None
                #
                return self.value

        processes = [TestProcess()]
        RAM_in_use = [0.0]
        #
        BulkRun.check_processes(processes, RAM_in_use, retest_delay=0)
        #
        assert not processes
        assert not RAM_in_use

    def test_bulk_run(self):
        r"""
        Passes nothing to the function but still hits most of the lines.
        True testing will be done in integration tests
        """
        inp_file = BulkRun.InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        BulkRun.bulk_run(init_infile=inp_file, start_delay=0)

    def test_dry_run(self):
        r"""
        Testing dry run function
        """
        # first with no inputs
        inp_file = BulkRun.InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        BulkRun.dry_run(init_infile=inp_file)
        input_params = [{'aperture_map': os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT'),
                         'filename_formats': {'APER-FILE': os.path.join(TEMP_DIR, 'test-map.txt'),
                                              'FLOW-FILE': os.path.join(TEMP_DIR, 'test-flow.csv'),
                                              'PRESS-FILE': os.path.join(TEMP_DIR, 'test-press.csv'),
                                              'STAT-FILE': os.path.join(TEMP_DIR, 'test-stat.csv'),
                                              'SUMMARY-PATH': os.path.join(TEMP_DIR, 'test-summary.txt'),
                                              'VTK-FILE': os.path.join(TEMP_DIR, 'test-para.vtk'),
                                              'input_file': os.path.join(TEMP_DIR, 'test-init.inp')},
                         'run_params': {'FRAC-PRESS': ['1000'],
                                        'OUTLET-PRESS': ['990.00']}}]
        #
        BulkRun.dry_run(sim_inputs=input_params, init_infile=inp_file)
        assert 0

    @pytest.mark.skip(reason='Can not be unit tested')
    def test_start_simulations(self):
        pass

    @pytest.mark.skip(reason='Can not be unit tested')
    def test_start_run(self):
        pass

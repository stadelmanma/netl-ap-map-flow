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

    def test_input_file(self):
        self.inp_file = os.path.join(FIXTURE_DIR, 'BULK_RUN_INIT.INP')
        #
        inp_file = BulkRun.InputFile(self.inp_file)
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
        # writing the output file to TEMP_DIR
        inp_file.write_inp_file(alt_path=TEMP_DIR)

    def test_dummy_process(self):
        r"""
        Ensuring dummy process class returns 0
        """
        proc = BulkRun.DummyProcess()
        assert proc.poll() == 0

    def test_estimate_req_RAM(self):
        r"""
        Ensuring RAM req is being calculated
        """
        map_file = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT')
        BulkRun.estimate_req_RAM([map_file], 10)
        with pytest.raises(SystemExit):
            BulkRun.estimate_req_RAM([map_file], 0)

    def test_dry_run(self):
        r"""
        Testing the dry run routine
        """
        #
        self.inp_file = os.path.join(FIXTURE_DIR, 'BULK_RUN_INIT.INP')
        #
        file_formats = {
            'SUMMARY-PATH': os.path.join(TEMP_DIR,
                                         '{0}-OUT_PRESS_%OUTLET-PRESS%-LOG.TXT'),
            'STAT-FILE': os.path.join(TEMP_DIR,
                                      '{0}-OUT_PRESS_%OUTLET-PRESS%-STAT.CSV'),
            'APER-FILE': os.path.join(TEMP_DIR,
                                      '{0}-OUT_PRESS_%OUTLET-PRESS%-APER.CSV'),
            'FLOW-FILE': os.path.join(TEMP_DIR,
                                      '{0}-OUT_PRESS_%OUTLET-PRESS%-FLOW.CSV'),
            'PRESS-FILE': os.path.join(TEMP_DIR,
                                       '{0}-OUT_PRESS_%OUTLET-PRESS%-PRES.CSV'),
            'VTK-FILE': os.path.join(TEMP_DIR,
                                     '{0}-OUT_PRESS_%OUTLET-PRESS%-VTK.vtk'),
            'input_file': os.path.join(TEMP_DIR,
                                       '{0}-OUT_PRESS_%OUTLET-PRESS%-INIT.INP')
        }
        #
        maps = [
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES',
                         'PARALELL-PLATE-01VOX.TXT'),
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES',
                         'PARALELL-PLATE-10VOX.TXT'),
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES',
                         'PARALELL-PLATE-10VOX-0AP-BANDS.TXT')
        ]
        #
        global_run_params = {
            'FRAC-PRESS': ['1000'],
            'MAP': ['10'],
            'ROUGHNESS': ['1.00'],
            'OUTPUT-UNITS': ['PA, MM, MM^3/SEC'],
            'VOXEL': ['26.8']
        }
        #
        input_params = [
            #
            (maps[0:1], {'OUTLET-PRESS': ['995.13']},
             {k: file_formats[k].format('01VOX') for k in file_formats}),
            (maps[1:2], {'OUTLET-PRESS': ['995.32']},
             {k: file_formats[k].format('10VOX') for k in file_formats}),
            (maps[2:3], {'OUTLET-PRESS': ['997.84']},
             {k: file_formats[k].format('10VOX-ZAB') for k in file_formats}),
        ]
        #
        sim_inputs = BulkRun.process_input_tuples(input_params)
        sim_inputs = BulkRun.process_input_tuples(input_params, global_run_params)
        #
        BulkRun.dry_run(sim_inputs=sim_inputs, init_infile=self.inp_file)

    def skip_test_bulk_run(self):
        r"""
        Testing the bulk run routine
        """
        #
        self.inp_file = os.path.join(FIXTURE_DIR, 'BULK_RUN_INIT.INP')
        #
        OUT_DIR = os.path.join(FIXTURE_DIR, os.pardir, 'OUTFILES')
        OUT_DIR = os.path.realpath(OUT_DIR)
        #
        file_formats = {
            'SUMMARY-PATH': os.path.join(OUT_DIR,
                                         '{0}-OUT_PRESS_%OUTLET-PRESS%-LOG.TXT'),
            'STAT-FILE': os.path.join(OUT_DIR,
                                      '{0}-OUT_PRESS_%OUTLET-PRESS%-STAT.CSV'),
            'APER-FILE': os.path.join(OUT_DIR,
                                      '{0}-OUT_PRESS_%OUTLET-PRESS%-APER.CSV'),
            'FLOW-FILE': os.path.join(OUT_DIR,
                                      '{0}-OUT_PRESS_%OUTLET-PRESS%-FLOW.CSV'),
            'PRESS-FILE': os.path.join(OUT_DIR,
                                       '{0}-OUT_PRESS_%OUTLET-PRESS%-PRES.CSV'),
            'VTK-FILE': os.path.join(OUT_DIR,
                                     '{0}-OUT_PRESS_%OUTLET-PRESS%-VTK.vtk'),
            'input_file': os.path.join(OUT_DIR,
                                       '{0}-OUT_PRESS_%OUTLET-PRESS%-INIT.INP')
        }
        #
        maps = [
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES',
                         'PARALELL-PLATE-01VOX.TXT'),
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES',
                         'PARALELL-PLATE-10VOX.TXT'),
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES',
                         'PARALELL-PLATE-10VOX-0AP-BANDS.TXT')
        ]
        #
        global_run_params = {
            'EXE-FILE': [os.path.realpath(os.path.join(FIXTURE_DIR, os.pardir,
                                                       'APM-MODEL.EXE'))],
            'FRAC-PRESS': ['1000'],
            'MAP': ['10'],
            'ROUGHNESS': ['1.00'],
            'OUTPUT-UNITS': ['PA, MM, MM^3/SEC'],
            'VOXEL': ['26.8']
        }
        #
        input_params = [
            #
            (maps[0:1], {'OUTLET-PRESS': ['995.13']},
             {k: file_formats[k].format('01VOX') for k in file_formats}),
            (maps[1:2], {'OUTLET-PRESS': ['995.32']},
             {k: file_formats[k].format('10VOX') for k in file_formats}),
            (maps[2:3], {'OUTLET-PRESS': ['997.84']},
             {k: file_formats[k].format('10VOX-ZAB') for k in file_formats}),
        ]
        #
        sim_inputs = BulkRun.process_input_tuples(input_params, global_run_params)
        #
        init_inp_file = os.path.join(FIXTURE_DIR, self.inp_file)
        #
        #
        BulkRun.bulk_run(sim_inputs=sim_inputs,
                         init_infile=init_inp_file,
                         start_delay=1.0)

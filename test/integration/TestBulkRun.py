"""
Handles testing of the bulk run module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
#
import os
from ApertureMapModelTools import BulkRun
#
class TestBulkRun:
    r"""
    Executes a set of functions to handle testing of the bulk run
    routines
    """
    def setup_class(self):
        pass

    def test_dry_run(self):
        r"""
        Testing the dry run routine
        """
        file_formats = {
            'SUMMARY-PATH' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-LOG.TXT'),
            'STAT-FILE' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-STAT.CSV'),
            'APER-FILE' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-APER.CSV'),
            'FLOW-FILE' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-FLOW.CSV'),
            'PRESS-FILE' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-PRES.CSV'),
            'VTK-FILE' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-VTK.vtk'),
            'input_file' : os.path.join(TEMP_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-INIT.INP')
        }
        #
        maps = [
            os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-01VOX.TXT'),
            os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-10VOX.TXT'),
            os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-10VOX-0AP-BANDS.TXT')
        ]
        #
        global_run_params = {
            'FRAC-PRESS' : ['1000'],
            'MAP' : ['10'],
            'ROUGHNESS' : ['1.00'],
            'OUTPUT-UNITS' : ['PA,MM,MM^3/SEC'],
            'VOXEL' : ['26.8']
        }
        #
        input_params = [
            #
            (maps[0:1], {'OUTLET-PRESS' : ['995.13']},
             {k : file_formats[k].format('01VOX') for k in file_formats}),
            (maps[1:2], {'OUTLET-PRESS' : ['995.32']},
             {k : file_formats[k].format('10VOX') for k in file_formats}),
            (maps[2:3], {'OUTLET-PRESS' : ['997.84']},
             {k : file_formats[k].format('10VOX-ZAB') for k in file_formats}),
        ]
        #
        sim_inputs = BulkRun.process_input_tuples(input_params,
                                                       global_run_params)
        #
        init_inp_file = os.path.join(FIXTURE_DIR,'PARALELL-PLATE-01VOX_INIT.INP')
        #
        BulkRun.dry_run(sim_inputs=sim_inputs, init_infile=init_inp_file)

    def skip_test_bulk_run(self):
        r"""
        Testing the bulk run routine
        """
        #
        OUT_DIR = os.path.join(FIXTURE_DIR,os.pardir,'OUTFILES')
        OUT_DIR = os.path.realpath(OUT_DIR)
        #
        file_formats = {
            'SUMMARY-PATH' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-LOG.TXT'),
            'STAT-FILE' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-STAT.CSV'),
            'APER-FILE' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-APER.CSV'),
            'FLOW-FILE' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-FLOW.CSV'),
            'PRESS-FILE' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-PRES.CSV'),
            'VTK-FILE' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-VTK.vtk'),
            'input_file' : os.path.join(OUT_DIR,'{0}-OUT_PRESS_%OUTLET-PRESS%-INIT.INP')
        }
        #
        maps = [
            os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-01VOX.TXT'),
            os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-10VOX.TXT'),
            os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-10VOX-0AP-BANDS.TXT')
        ]
        #
        global_run_params = {
            'EXE-FILE' : [os.path.realpath(os.path.join(FIXTURE_DIR,os.pardir,'APM-MODEL.EXE'))],
            'FRAC-PRESS' : ['1000'],
            'MAP' : ['10'],
            'ROUGHNESS' : ['1.00'],
            'OUTPUT-UNITS' : ['PA,MM,MM^3/SEC'],
            'VOXEL' : ['26.8']
        }
        #
        input_params = [
            #
            (maps[0:1], {'OUTLET-PRESS' : ['995.13']},
             {k : file_formats[k].format('01VOX') for k in file_formats}),
            (maps[1:2], {'OUTLET-PRESS' : ['995.32']},
             {k : file_formats[k].format('10VOX') for k in file_formats}),
            (maps[2:3], {'OUTLET-PRESS' : ['997.84']},
             {k : file_formats[k].format('10VOX-ZAB') for k in file_formats}),
        ]
        #
        sim_inputs = BulkRun.process_input_tuples(input_params,
                                                       global_run_params)
        #
        init_inp_file = os.path.join(FIXTURE_DIR,'PARALELL-PLATE-01VOX_INIT.INP')
        #
        #
        BulkRun.bulk_run(sim_inputs=sim_inputs, init_infile=init_inp_file, start_delay=1.0)

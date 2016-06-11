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
    def __init__(self):
        file_formats = {
            'SUMMARY-PATH' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-LOG.TXT'),
            'STAT-FILE' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-STAT.CSV'),
            'APER-FILE' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-APER.CSV'),
            'FLOW-FILE' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-FLOW.CSV'),
            'PRESS-FILE' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-PRES.CSV'),
            'VTK-FILE' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-VTK.vtk'),
            'input_file' : os.path.join('OUTFILES','{0}-OUT_PRESS_%OUTLET-PRESS%-INIT.INP')
        }
        #
        maps = [
            os.path.join('TEST-FRACTURES','PARALELL-PLATE-01VOX.TXT'),
            os.path.join('TEST-FRACTURES','PARALELL-PLATE-10VOX.TXT'),
            os.path.join('TEST-FRACTURES','PARALELL-PLATE-10VOX-0AP-BANDS.TXT')
        ]
        #
        self.init_inp_file = 'PARALELL-PLATE-01VOX_INIT.INP'
        self.sim_inputs = None
        #
        self.global_run_params = {
            'FRAC-PRESS' : ['1000'],
            'MAP' : ['10'],
            'ROUGHNESS' : ['1.00'],
            'OUTPUT-UNITS' : ['PA,MM,MM^3/SEC'],
            'VOXEL' : ['26.8']
        }
        #
        self.input_params = [
            #
            (maps[0:1], {'OUTLET-PRESS' : ['995.13','993.02','989.04']},
             {k : file_formats[k].format('01VOX') for k in file_formats}),
            (maps[1:2], {'OUTLET-PRESS' : ['995.32','979.55','945.06']},
             {k : file_formats[k].format('10VOX') for k in file_formats}),
            (maps[2:3], {'OUTLET-PRESS' : ['997.84','993.04','982.18']},
             {k : file_formats[k].format('10VOX-ZAB') for k in file_formats}),
        ]

    def run_tests(self):
        r"""
        Loops through supplied testing functions
        """
        #
        test_functions = [
            self.test_dry_run,
            self.test_bulk_run
        ]
        #
        errors = False
        try:
            self.test_process_input_tuples()
        except Exception as err:
            errors = True
            print('*** Error - :'+self.__class__.__name__+':', err, ' ***')
            print('Unable to process input tuples could not continue!')
            return errors
        #
        for func in test_functions:
            try:
                func()
            except Exception as err:
                errors = True
                print('*** Error - :'+self.__class__.__name__+':', err, ' ***')
        #
        return errors

    def test_process_input_tuples(self):
        r"""
        Runs the input tuple processing routine
        """
        self.sim_inputs = BulkRun.process_input_tuples(self.input_params,
                                                       self.global_run_params)

    def test_dry_run(self):
        r"""
        Testing the dry run routine
        """
        BulkRun.dry_run(sim_inputs=self.sim_inputs, init_infile=self.init_inp_file)

    def test_bulk_run(self):
        r"""
        Testing the bulk run routine
        """
        BulkRun.bulk_run(sim_inputs=self.sim_inputs, init_infile=self.init_inp_file)


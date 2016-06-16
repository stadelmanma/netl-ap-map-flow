"""
Performs a real test of the bulk run script
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/11
#
"""
#
import os
import pytest
from ApertureMapModelTools.RunModel import InputFile
from ApertureMapModelTools.RunModel import BulkRun


class TestBulkRun:
    r"""
    Executes a full run of the bulk run program
    """
    def setup_class(self):
        pass

    def test_bulk_run_integration(self):
        #
        # setting inputs for a full test
        maps = [
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT'),
            os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-10VOX.TXT')
        ]
        #
        global_file_formats = {
            'PVT-PATH': os.path.join(FIXTURE_DIR, 'PVT', 'H2O_TEMP_058F.CSV'),
            'SUMMARY-PATH': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-LOG.TXT'),
            'STAT-FILE': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-STAT.CSV'),
            'APER-FILE': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-APER.CSV'),
            'FLOW-FILE': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-FLOW.CSV'),
            'PRESS-FILE': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-PRES.CSV'),
            'VTK-FILE': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-VTK.vtk'),
            'input_file': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-INIT.INP')
        }
        global_run_params = {
            'FRAC-PRESS': ['1000'],
            'MAP': ['10'],
            'ROUGHNESS': ['0.00', '1.00'],
            'OUTPUT-UNITS': ['PA, MM, MM^3/MIN'],
            'VOXEL': ['10.0']
        }
        #
        run_params = [
            {'APERMAP': ['PARALELL-PLATE-01VOX'], 'OUTLET-PRESS': ['500', '400']},
            {'APERMAP': ['PARALELL-PLATE-10VOX'], 'OUTLET-PRESS': ['800', '700']}
        ]
        #
        input_tuples = [
            (maps[0:1], run_params[0], {}),
            (maps[1:2], run_params[1], {'SUMMARY-PATH': os.path.join(TEMP_DIR, '%APERMAP%-RF%ROUGHNESS%-%OUTLET-PRESS%PA-LOG2.TXT')})
        ]
        #
        inp_file = InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        exe_path = os.path.realpath(os.path.join('.', inp_file['EXE-FILE'].value))
        inp_file['EXE-FILE'].update_value(exe_path, False)
        #
        # creating the class and then building the inputs
        args = {'start_delay': 1.0, 'spawn_delay': 1.0, 'retest_delay': 1.0}
        test_bulk_run = BulkRun(inp_file, **args)
        test_bulk_run.process_input_tuples(input_tuples,
                                           default_params=global_run_params,
                                           default_name_format=global_file_formats)
        test_bulk_run.dry_run()
        #
        test_bulk_run.start()

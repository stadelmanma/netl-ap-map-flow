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
from ApertureMapModelTools.BulkRun import InputFile, process_input_tuples
from ApertureMapModelTools.BulkRun import bulk_run, dry_run


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
        simulation_inputs = process_input_tuples(input_tuples,
                                                 global_params=global_run_params,
                                                 global_name_format=global_file_formats)
        #
        inp_file = InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        exe_path = os.path.realpath(os.path.join('.', inp_file.arg_dict['EXE-FILE'].value))
        inp_file.arg_dict['EXE-FILE'].update_value(exe_path, False)
        dry_run(simulation_inputs,
                num_CPUs=2.0,
                sys_RAM=8.0,
                delim='auto',
                init_infile=inp_file)
        #
        os.system('echo '+inp_file.arg_dict['EXE-FILE'].output_line())
        os.system('ls '+TEMP_DIR)
        #
        bulk_run(simulation_inputs,
                 num_CPUs=2.0,
                 sys_RAM=4.0,
                 delim='auto',
                 init_infile=os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'),
                 start_delay=1.0)

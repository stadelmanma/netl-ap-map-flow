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
        file_formats = {
            'PVT-FILE': os.path.join(FIXTURE_DIR, 'PVT', 'H2O_TEMP_058F.CSV'),
            'APER-MAP': os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', '{aper-map}.txt'),
            'SUMMARY-FILE': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-LOG.TXT'),
            'STAT-FILE': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-STAT.CSV'),
            'APER-FILE': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-APER.CSV'),
            'FLOW-FILE': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-FLOW.CSV'),
            'PRESS-FILE': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-PRES.CSV'),
            'VTK-FILE': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-VTK.vtk'),
            'input_file': os.path.join(TEMP_DIR, '{aper-map}-RF{ROUGHNESS}-{OUTLET-PRESS}PA-INIT.INP')
        }
        run_params = {
            'INLET-PRESS': ['1000'],
            'OUTLET-PRESS': ['300', '200'],
            'MAP': ['10'],
            'ROUGHNESS': ['0.00', '1.00'],
            'OUTPUT-UNITS': ['PA, MM, MM^3/MIN'],
            'VOXEL': ['10.0'],
            'aper-map': ['parallel-plate-01vox', 'parallel-plate-10vox', 'Fracture1ApertureMap-10avg']
        }
        #
        case_params = {
            'parallel-plate-01vox': {'OUTLET-PRESS': ['500', '400', '100']},
            'parallel-plate-10vox': {'OUTLET-PRESS': ['800', '700', '600']},
        }
        #
        inp_file = InputFile(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        exe_path = os.path.realpath(os.path.join('.', inp_file['EXE-FILE'].value))
        inp_file['EXE-FILE'].update_value(exe_path, False)
        #
        # creating the class and then building the inputs
        args = {'start_delay': 1.0, 'spawn_delay': 1.0, 'retest_delay': 1.0, 'sys_RAM': 0.01, 'num_CPUs': 2}
        test_bulk_run = BulkRun(inp_file, **args)
        test_bulk_run.generate_input_files(run_params,
                                           file_formats,
                                           case_identifer='{aper-map}',
                                           case_params=case_params)
        test_bulk_run.dry_run()
        #
        test_bulk_run.start()
        #
        # checking that some files were created
        assert os.path.isfile(os.path.join(TEMP_DIR, 'parallel-plate-01vox-RF1.00-400PA-STAT.CSV'))
        assert os.path.isfile(os.path.join(TEMP_DIR, 'parallel-plate-10vox-RF1.00-700PA-LOG.TXT'))
        assert os.path.isfile(os.path.join(TEMP_DIR, 'Fracture1ApertureMap-10avg-RF0.00-300PA-INIT.INP'))

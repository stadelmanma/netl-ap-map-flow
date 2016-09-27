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
from ApertureMapModelTools.RunModel.__BulkRun__ import BulkRun


class TestBulkRun:
    r"""
    Executes a set of functions to handle testing of the bulk run
    routines
    """
    def setup_class(self):
        pass

    def test_bulk_run(self, input_file_class):
        r"""
        Testing BulkRun initiailization
        """
        bulk_run = BulkRun(os.path.join(FIXTURE_DIR, 'TEST_INIT.INP'))
        #
        assert not bulk_run.sim_inputs
        assert not bulk_run.input_file_list
        assert bulk_run.num_CPUs == 2.0
        assert bulk_run.sys_RAM == 4.0

    def test_combine_run_args(self, bulk_run_class, input_file_class):
        r"""
        ensuring this returns a valid list of input file objects
        """
        sim_inputs = [{'aperture_map': 'test-map.txt',
                       'filename_formats': {'APER-FILE': 'test-map.txt',
                                            'FLOW-FILE': 'test-flow.csv',
                                            'PRESS-FILE': 'test-press.csv',
                                            'STAT-FILE': 'test-stat.csv',
                                            'SUMMARY-FILE': 'test-summary.txt',
                                            'VTK-FILE': 'test-para.vtk',
                                            'input_file': 'test-init.inp'},
                       'run_params': {'FRAC-PRESS': ['1000'],
                                      'MAP': ['1'],
                                      'OUTLET-PRESS': ['995.13', '993.02', '989.04', '977.78', '966.20', '960.53'],
                                      'OUTPUT-UNITS': ['PSI, MM, MM^3/MIN'],
                                      'ROUGHNESS': ['2.50'],
                                      'VOXEL': ['26.8']},
                       'RAM_req': 0.0}]
        #
        bulk_run_obj = bulk_run_class()
        bulk_run_obj.sim_inputs = sim_inputs
        BulkRun._combine_run_args(bulk_run_obj)
        assert len(bulk_run_obj.input_file_list) == 6

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
        BulkRun._check_processes(processes, RAM_in_use, retest_delay=0)
        #
        assert not processes
        assert not RAM_in_use

    def test_process_input_tuples(self, bulk_run_class):
        r"""
        Testing the front end input processing function
        """
        #
        input_tuples = [
            (['test-map1', 'test-map2'], {'test-param1': [1000]}, {'test-format': 'path-to-file12'}),
            (['test-map3', 'test-map4'], {'test-param2': 'ABC'}, {'test-format': 'path-to-file34'}),
            (['test-map5'], {'test-param3': 'LEFT'}, {'test-format': 'path-to-file5'})
        ]
        #
        bulk_run = bulk_run_class()
        sim_inputs = BulkRun.process_input_tuples(bulk_run, input_tuples)
        print(bulk_run.sim_inputs)
        assert len(bulk_run.sim_inputs) == 5
        assert {'aperture_map', 'filename_formats', 'run_params'}.issubset(bulk_run.sim_inputs[0].keys())

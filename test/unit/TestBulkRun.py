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
        assert not bulk_run.input_file_list
        assert bulk_run.num_CPUs == 2.0
        assert bulk_run.sys_RAM == 4.0
        assert bulk_run.avail_RAM == 3.6

    def test_combine_run_params(self, bulk_run_class):
        params = {
            'param1': [1, 2, 3],
            'param2': [4, 5],
            'param3': [6],
            'param4': None
        }
        bulk_run_obj = bulk_run_class()
        combs = bulk_run_obj._combine_run_params(params)
        #
        assert len(combs) == 6
        assert list(combs[0].keys()) == ['param3', 'param2', 'param1']
        assert list(combs[0].values()) == [6, 4, 1]
        assert list(combs[-1].values()) == [6, 5, 3]

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

    def test_generate_input_files(self, bulk_run_class):
        r"""
        Testing the front end input processing function
        """
        # !!! need to fix this test
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

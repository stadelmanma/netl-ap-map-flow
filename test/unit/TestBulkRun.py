"""
Handles testing of the bulk run module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/11
#
"""
#
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
        bulk_run = BulkRun(input_file_class())
        #
        assert not bulk_run.input_file_list
        assert bulk_run.num_CPUs == 2.0
        assert bulk_run.sys_RAM == 4.0
        assert bulk_run.avail_RAM == 3.6

    def test_combine_run_params(self):
        params = {
            'param1': [1, 2, 3],
            'param2': [4, 5],
            'param3': [6],
            'param4': None
        }
        combs = BulkRun._combine_run_params(params)
        #
        assert len(combs) == 6
        assert set(combs[0].keys()) == set(['param3', 'param2', 'param1'])
        assert set(combs[0].values()) == set([6, 4, 1])
        assert set(combs[-1].values()) == set([6, 5, 3])

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
        bulk_run = bulk_run_class()
        #
        # testing when only defaults are provided
        default_params = {
            'test-param1': [1000, 2000],
            'test-param2': ['ABC', 'DEF']
        }
        name_formats = {
            'test-format': 'path-to-file12{test-param1}',
            'test-format2': 'path-to-file34{test-param2}'
        }
        #
        BulkRun.generate_input_files(bulk_run, default_params, name_formats)
        assert len(bulk_run.input_file_list) == 4
        #
        # testing when adding a case spefic args
        case_key = '{test-param2}'
        case_params = {
            'ABC': {'test-param3': [100, 200]}
        }
        BulkRun.generate_input_files(bulk_run, default_params, name_formats, case_key, case_params)
        assert len(bulk_run.input_file_list) == 6

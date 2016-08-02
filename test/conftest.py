from collections import OrderedDict
from os.path import join, dirname, realpath
from os import mkdir
import pytest
from shutil import rmtree
import scipy as sp
import ApertureMapModelTools as amt


@pytest.fixture(autouse=True)
def fixtures_directory(request):
    r"""
    Defines FIXTURE_DIR global for loading files
    """
    fixture_dir = join(dirname(realpath(__file__)), 'fixtures')
    request.function.__globals__['FIXTURE_DIR'] = fixture_dir


@pytest.fixture(scope='session')
def setup_temp_directory(request):
    r"""
    Defines TEMP_DIR global for saving files
    """
    temp_dir = join(dirname(realpath(__file__)), 'temp')
    try:
        mkdir(temp_dir)
    except:
        pass

    def clean():
        try:
            rmtree(temp_dir)
        except:
            pass
    request.addfinalizer(clean)
    #
    return temp_dir


@pytest.fixture(scope='function', autouse=True)
def temp_directory(request, setup_temp_directory):
    r"""
    Defines TEMP_DIR global for saving files
    """
    temp_dir = join(dirname(realpath(__file__)), 'temp')
    try:
        mkdir(temp_dir)
    except:
        pass
    request.function.__globals__['TEMP_DIR'] = setup_temp_directory


@pytest.fixture
def arg_processor_class():
    r"""
    Returns a pseudo ArgProcessor class object with the proper methods
    and placeholder data
    """

    class PseudoArgProcessor:
        r"""
        Handles testing of the data field object without needing to create one
        """
        def __init__(self,
                     field,
                     map_func=lambda x: x,
                     min_num_vals=1,
                     out_type='single',
                     expected='str',
                     err_desc_str='to have a value'):
            #
            self.field = field
            self.map_func = map_func
            self.min_num_vals = min_num_vals
            self.out_type = out_type
            self.expected = expected
            self.err_desc_str = err_desc_str

    return PseudoArgProcessor


@pytest.fixture
def data_field_class():
    r"""
    Returns a pseudo DataField class object with the proper methods
    and placeholder data
    """

    class PseudoDataField(amt.DataField):
        r"""
        Handles testing of the data field object without needing to create one
        """
        def __init__(self):
            self.infile = 'pytest-DataFeld-fixture'
            self.outfile = ''
            self.nx = 10
            self.nz = 10
            self.data_map = sp.arange(100).reshape(10, 10)
            self.data_vector = sp.arange(100)
            self.point_data = None
            self._raw_data = None
            self._cell_interfaces = None
            self.output_data = dict()
            #
            self._define_cell_interfaces()

        def parse_data_file(self):
            pass

        def create_point_data(self):
            self.point_data = sp.zeros((self.nz, self.nx, 4))
            self.point_data[:, :, 1] = sp.arange(100).reshape(10, 10)*1.0
            self.point_data[:, :, 1] = sp.arange(100).reshape(10, 10)*2.0
            self.point_data[:, :, 1] = sp.arange(100).reshape(10, 10)*3.0
            self.point_data[:, :, 1] = sp.arange(100).reshape(10, 10)*4.0

    return PseudoDataField


@pytest.fixture
def input_file_class():
    r"""
    Returns a pseudo InputFile class object with the proper methods. Due to
    the amount of data required for the real class this may not be applicable
    to use in all functions that require an InputFile object
    """
    class PseudoInputFile(OrderedDict):
        r"""
        Setting up placeholder methods
        """
        def __init__(self):
            super().__init__()
            self.filename_format_args = {}
            self.filename_formats = {
                'input_file': 'FRACTURE_INITIALIZATION.INP'
            }
            self.arg_order = []
            self.RAM_req = 0.0
            self.outfile_name = 'FRACTURE_INITIALIZATION.INP'

        def parse_input_file(self, infile):
            pass

        def clone(self, file_formats=None):
            return PseudoInputFile()

        def update_args(self, args):
            pass

        def construct_file_names(self):
            pass

        def write_inp_file(self, alt_path=None):
            pass

    return PseudoInputFile


@pytest.fixture
def bulk_run_class(input_file_class):
    r"""
    Returns a pseduo BulkRun class object for unit testing of the class where
    possible
    """
    class PseudoBulkRun(dict):
        r"""
        Setting placeholder methods and arguments
        """
        def __init__(self):
            super().__init__()
            self.init_input_file = input_file_class()
            self.sim_inputs = []
            self.num_CPUs = 2.0
            self.sys_RAM = 4.0
            self.avail_RAM = self.sys_RAM * 0.90
            self.input_file_list = []
            #
            # setting keys
            self['delim'] = 'auto'
            self['start_delay'] = 10.0
            self['spawn_delay'] = 2.5
            self['retest_delay'] = 1.5

        def process_input_tuples(self, *args, **kwargs):
            pass

        def dry_run(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            pass

        def _combine_run_args(self, *args, **kwargs):
            pass

        @staticmethod
        def _check_processes(*args, **kwargs):
            pass

        def _start_simulations(self, *args, **kwargs):
            pass

    return PseudoBulkRun

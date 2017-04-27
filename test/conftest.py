from collections import OrderedDict
from os import path, mkdir, environ
import pytest
from shutil import rmtree
import scipy as sp
import apmapflow as apm


def pytest_addoption(parser):
    hlp = 'Use OpenFoam executables instead of fixtures, some unit tests will fail'
    parser.addoption('--use-openfoam', action='store_true', help=hlp)


@pytest.fixture(autouse=True)
def test_root_directory(request):
    r"""
    Defines TEST_ROOT global
    """
    test_root = path.dirname(path.realpath(__file__))
    request.function.__globals__['TEST_ROOT'] = test_root


@pytest.fixture(autouse=True)
def fixtures_directory(request):
    r"""
    Defines FIXTURE_DIR global for loading files
    """
    fixture_dir = path.join(path.dirname(path.realpath(__file__)), 'fixtures')
    request.function.__globals__['FIXTURE_DIR'] = fixture_dir


@pytest.fixture(scope='session')
def setup_temp_directory(request):
    r"""
    Defines TEMP_DIR global for saving files
    """
    temp_dir = path.join(path.dirname(path.realpath(__file__)), 'temp')
    try:
        mkdir(temp_dir)
    except FileExistsError:
        pass

    def clean():
        rmtree(temp_dir, ignore_errors=True)

    request.addfinalizer(clean)
    #
    return temp_dir


@pytest.fixture(scope='function', autouse=True)
def temp_directory(request, setup_temp_directory):
    r"""
    Defines TEMP_DIR global for saving files
    """
    request.function.__globals__['TEMP_DIR'] = setup_temp_directory


@pytest.fixture(scope='class')
def set_openfoam_path():
    r"""
    Appends the path to use local dummy fixtures instead of actual openFoam
    executables unless the option --use-openfoam was added
    """
    if not pytest.config.option.use_openfoam:
        fixture_bin = path.join(path.dirname(__file__), 'fixtures', 'bin')
        environ['PATH'] = fixture_bin + path.pathsep + environ['PATH']


@pytest.fixture
def data_field_class():
    r"""
    Returns a pseudo DataField class object with the proper methods
    and placeholder data
    """

    class PseudoDataField(apm.DataField):
        r"""
        Handles testing of the data field object without needing to create one
        """
        def __init__(self):
            test_root = path.dirname(path.realpath(__file__))
            #
            self.infile = path.join(test_root, 'pytest-DataFeld-fixture')
            self.outfile = ''
            self._data_map = sp.arange(100).reshape(10, 10)
            self.point_data = None
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
def openfoam_file_class():
    r"""
    Returns a pseduo OpenFoamFile class object with some methods and
    placeholder data.
    """

    class PseduoOpenFoamFile(apm.openfoam.OpenFoamFile):
        r"""
        Simplfies testing of functions needing an OpenFoamFile instance
        """
        def __init__(self):
            super().__init__('conftest', 'pseduoOpenFoamFile')
            self.name = 'pseduoOpenFoamFile'
            self['keyword'] = 'value'

        def write_foam_file(self, *args, **kwargs):
            print('PseduoOpenFoamFile.write_foam_file() was called')

    return PseduoOpenFoamFile


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
            self.outfile_name = './FRACTURE_INITIALIZATION.INP'

        def parse_input_file(self, infile):
            pass

        def clone(self, file_formats=None):
            return PseudoInputFile()

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
    class PseudoBulkRun(apm.run_model.BulkRun):
        r"""
        Setting placeholder methods and arguments
        """
        def __init__(self):
            inp_file = input_file_class()
            super().__init__(inp_file)
            self.init_input_file = inp_file
            #
            self.num_CPUs = 2.0
            self.sys_RAM = 4.0
            self.avail_RAM = self.sys_RAM * 0.90
            self.input_file_list = []
            #
            # setting keys
            self['delim'] = 'auto'
            self['spawn_delay'] = 2.5
            self['retest_delay'] = 1.5

        def generate_input_files(self, *args, **kwargs):
            pass

        def dry_run(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            pass

        def _initialize_run(self, *args, **kwargs):
            pass

        @staticmethod
        def _check_processes(*args, **kwargs):
            pass

        def _start_simulations(self, *args, **kwargs):
            pass

    return PseudoBulkRun

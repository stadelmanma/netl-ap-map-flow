import pytest
from os.path import join, dirname, realpath
from os import mkdir
from shutil import rmtree
import scipy as sp


@pytest.fixture(autouse=True)
def fixtures_directory(request):
    r"""
    Defines FIXTURE_DIR global for loading files
    """
    fixture_dir = join(dirname(realpath(__file__)), 'fixtures')
    request.function.__globals__['FIXTURE_DIR'] = fixture_dir


@pytest.fixture(autouse=True)
def temp_directory(request):
    r"""
    Defines TEMP_DIR global for saving files
    """
    temp_dir = join(dirname(realpath(__file__)), 'temp')
    try:
        mkdir(temp_dir)
    except:
        pass
    request.function.__globals__['TEMP_DIR'] = temp_dir

    def clean():
        try:
            rmtree(temp_dir)
        except:
            pass
    request.addfinalizer(clean)


@pytest.fixture
def data_field_class():
    r"""
    Returns a pseudo DataField class object with the proper methods
    and placeholder data
    """

    class PseudoDataField:
        r"""
        Handles testing of the data field object without needing to create one
        """
        def __init__(self):
            self.infile = 'pytest-DataFeld-fixture'
            self.outfile = ''
            self.nx = 10
            self.nz = 10
            self.data_map = sp.arange(100).reshape(10, 10)
            self.point_data = None
            self.output_data = dict()

        def copy_data(self, obj):
            obj.infile = self.infile
            obj.nx = self.nx
            obj.nz = self.nz
            obj.data_map = sp.copy(self.data_map)
            obj.point_data = sp.copy(self.point_data)

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

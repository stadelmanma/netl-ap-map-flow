import pytest
from os.path import join, dirname, realpath
from os import mkdir
from shutil import rmtree


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

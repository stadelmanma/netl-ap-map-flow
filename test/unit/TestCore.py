"""
Handles testing of the core object and function module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2017/03/03
#
"""
from argparse import Namespace
import logging
import os
import pytest
import re
import sys
import scipy as sp
import PIL
import apmapflow as apm
import apmapflow.ap_map_flow as apm_core


class TestCore:
    r"""
    Tests each of the functions an classes used in the ap_map_flow module
    """

    def test_data_field(self):
        r"""
        Builds a data field and tests its properties
        """
        #
        # covering basic methods
        map_file = 'parallel-plate-01vox.txt'
        fname = os.path.join(FIXTURE_DIR, 'maps', map_file)
        field = apm.DataField(fname)
        field.create_point_data()
        #
        # testing initization from data
        obj = apm.DataField(field.data_map)
        assert obj.nx == 100
        assert obj.nz == 100
        assert obj.data_map.size == 10000
        #
        obj = Namespace()
        field.copy_data(obj)
        #
        assert obj.nx == 100
        assert obj.nz == 100
        assert obj.data_map.size == 10000
        assert obj.point_data.size == 40000
        #
        # testing adjacency matrix
        matrix = field.create_adjacency_matrix()
        assert matrix is not None
        #
        # testing thresholding
        field._data_map = sp.arange(field.nz*field.nx, dtype=float).reshape(field.nz, field.nx)
        low_inds = sp.where(field.data_vector <= 100)
        high_inds = sp.where(field.data_vector >= 900)
        field.threshold_data(min_value=100, repl=-1)
        field.threshold_data(max_value=900)
        assert sp.all(field.data_vector[low_inds] == -1)
        assert sp.all(sp.isnan(field.data_vector[high_inds]))
        #
        # testing VTK file generation
        field.infile = os.path.join(TEMP_DIR, 'test-export.csv')
        field.export_vtk()
        fname = os.path.join(TEMP_DIR, 'test-export.vtk')
        assert os.path.isfile(fname)
        #
        with open(fname, 'r') as file:
            content = file.read()
            assert re.search('DATASET STRUCTURED_GRID\n', content)
            assert re.search('DIMENSIONS 101 2 101\n', content)
            assert re.search('POINTS 20402 float\n', content)
            assert re.search('CELL_DATA 10000\n', content)
            assert re.search('SCALARS data float\n', content)
        #
        with pytest.raises(FileExistsError):
            field.export_vtk()

    def test_fracture_image_stack(self):
        r"""
        Loads and builds an image stack to test its properties
        """
        #
        # testing initialization from data array
        img_data = sp.ones((10, 11, 12))
        fracture_stack = apm.FractureImageStack(img_data, dtype=sp.uint8)
        assert issubclass(fracture_stack.__class__, sp.ndarray)
        assert fracture_stack.dtype == sp.uint8
        assert fracture_stack.shape == img_data.shape
        assert fracture_stack.size == img_data.size
        #
        # testing initialization from image file
        fname = os.path.join(FIXTURE_DIR, 'binary-fracture.tif')
        fracture_stack = apm.FractureImageStack(fname)
        assert issubclass(fracture_stack.__class__, sp.ndarray)
        assert fracture_stack.dtype == bool
        assert fracture_stack.shape == (507, 46, 300)
        assert fracture_stack.nx == fracture_stack.shape[0]
        assert fracture_stack.ny == fracture_stack.shape[1]
        assert fracture_stack.nz == fracture_stack.shape[2]
        #
        # test fetching of fracture voxels
        voxels = fracture_stack.get_fracture_voxels()
        assert voxels.size == 733409
        del voxels
        #
        # checking all coordinates are between 0 and maximum axis size
        x_c, y_c, z_c = fracture_stack.get_fracture_voxels(coordinates=True)
        assert x_c.size == y_c.size == z_c.size == 733409
        assert sp.all(x_c < fracture_stack.nx)
        assert sp.all(~x_c < 0)
        assert sp.all(y_c < fracture_stack.ny)
        assert sp.all(~y_c < 0)
        assert sp.all(z_c < fracture_stack.nz)
        assert sp.all(~z_c < 0)
        #
        # testing aperture map output
        fname = os.path.join(FIXTURE_DIR, 'maps', 'binary-fracture-aperture-map.txt')
        test_map = fracture_stack.create_aperture_map()
        data_map = sp.loadtxt(fname, delimiter='\t')
        assert sp.all(test_map == data_map)
        #
        # testing offset map output
        fname = os.path.join(FIXTURE_DIR, 'maps', 'binary-fracture-offset-map.txt')
        test_map = fracture_stack.create_offset_map()
        data_map = sp.loadtxt(fname, delimiter='\t')
        assert sp.all(test_map == data_map)
        del test_map
        del data_map
        #
        # testing image stack saving
        fname = os.path.join(TEMP_DIR, 'test.tif')
        fracture_stack.save(fname)
        new_stack = apm.FractureImageStack(fname)
        assert sp.all(fracture_stack == new_stack)
        del new_stack
        # testing overwrite parameter
        with pytest.raises(FileExistsError):
            fracture_stack.save(fname)
        #
        fracture_stack.save(fname, overwrite=True)

    def test_toplevel_logger(self):
        r"""
        Tests the configuation of the top level logger
        """
        logger = apm_core._get_logger('apmapflow')
        assert logger.name == 'APM'
        assert len(logger.handlers) == 0

    def test_get_logger(self):
        r"""
        Tests creation of a logger
        """
        logger = apm_core._get_logger('apmapflow.Test.TestCore')
        #
        assert logger.name == 'APM.Test.TestCore'

    def test_set_main_logger_level(self):
        r"""
        Tests adjudtment of primary logger level
        """
        #
        logger = logging.getLogger('APM')
        #
        apm_core.set_main_logger_level('debug')
        assert logger.getEffectiveLevel() == logging.DEBUG
        #
        apm_core.set_main_logger_level(logging.INFO)
        assert logger.getEffectiveLevel() == logging.INFO

    def test_files_from_directory(self):
        r"""
        Runs the files_from_directory command with various args
        """
        files = apm.files_from_directory('.', '*')
        assert len(files)
        files = apm.files_from_directory('.', re.compile('.'))
        assert len(files)

    def test_load_infile_list(self):
        r"""
        Sends a list of infiles
        """
        fname1 = os.path.join(FIXTURE_DIR, 'maps', 'parallel-plate-01vox.txt')
        fname2 = os.path.join(FIXTURE_DIR, 'maps', 'parallel-plate-10vox.txt')
        infile_list = [fname1, fname2]
        #
        fields = apm.load_infile_list(infile_list)
        assert fields

    def test_calc_percentile(self):
        r"""
        Sends a test array to the calc percentile function
        """
        data_list = list(range(100))
        val = apm.calc_percentile(99, data_list)
        assert val == 99

    def test_calc_percentile_num(self):
        r"""
        Sends a test array to the calc percentile function
        """
        data_list = list(range(100))
        val = apm.calc_percentile_num(50, data_list, last=False)
        assert val*100 == 50
        val = apm.calc_percentile_num(50, data_list, last=True)
        assert val*100 == 51

    def test_get_data_vect(self):
        r"""
        Tests extraction of a vector from a data array
        """
        data = sp.arange(100)
        data = data.reshape(10, 10)
        #
        vect = apm.get_data_vect(data, 'x', 0)
        assert sp.all(vect == data[0, :])
        vect = apm.get_data_vect(data, 'x', 11)
        assert sp.all(vect == data[9, :])
        vect = apm.get_data_vect(data, 'z', 0)
        assert sp.all(vect == data[:, 0])
        vect = apm.get_data_vect(data, 'z', 11)
        assert sp.all(vect == data[:, 9])
        #
        with pytest.raises(ValueError):
            apm.get_data_vect(data, 'y')

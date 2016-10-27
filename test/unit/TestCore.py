"""
Handles testing of the core object and function module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
from collections import namedtuple
from imp import reload
import logging
import os
import pytest
import re
import sys
import scipy as sp
import ApertureMapModelTools as amt
import ApertureMapModelTools.__core__ as amt_core


class TestCore:
    r"""
    Tests each of the functions an classes used in the __core__ module
    """
    def setup_class(self):
        pass

    def test_import(self):
        r"""
        Tests that the main __init__ module method properly flags early
        versions of python
        """
        version = namedtuple('version', ['major', 'minor', 'micro', 'releaselevel', 'serial'])
        test_vers = version(major=2, minor=7, micro=5, releaselevel='final', serial='')
        #
        sys.version_info = test_vers
        with pytest.raises(Exception):
            reload(amt)

    def test_data_field(self):
        r"""
        Builds a data field and tests its properties
        """
        #
        # covering basic methods
        map_file = 'parallel-plate-01vox.txt'
        fname = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', map_file)
        field = amt.DataField(fname)
        field.create_point_data()
        field.copy_data(field)
        #
        assert field.nx == 100
        assert field.nz == 100
        assert field.data_map.size == 10000
        assert field.point_data.size == 40000
        #
        # testing clone method returns proper data and class reference
        cloned_field = field.clone()
        assert isinstance(cloned_field, field.__class__)
        assert sp.all(cloned_field.data_map == field.data_map)
        assert sp.all(cloned_field._raw_data == field._raw_data)
        #
        # testing adjacency matrix
        matrix = field.create_adjacency_matrix()
        assert matrix is not None
        #
        # testing thresholding
        field.data_map = sp.arange(field.nz*field.nx, dtype=float).reshape(field.nz, field.nx)
        field.data_vector = sp.ravel(field.data_map)
        low_inds = sp.where(field.data_vector <= 100)
        high_inds = sp.where(field.data_vector >= 900)
        field.threshold_data(min_value=100, repl=-1)
        field.threshold_data(max_value=900)
        assert sp.all(field.data_vector[low_inds] == -1)
        assert sp.all(sp.isnan(field.data_vector[high_inds]))

    def test_stat_file(self):
        r"""
        Builds a stat file and test its properties
        """
        fname = os.path.join(FIXTURE_DIR, 'TEST-STAT-FILE.CSV')
        stat_file = amt.StatFile(fname)
        assert stat_file.map_file
        assert stat_file.pvt_file
        assert stat_file.keys()
        assert stat_file.values()
        assert stat_file['NX'] == 136
        assert stat_file['NZ'] == 138
        assert stat_file['INLET PRESS'] == [1000, 'PA']

    def test_toplevel_logger(self):
        r"""
        Tests te configuation of the top level logger
        """
        logger = amt_core._get_logger('ApertureMapModelTools')
        assert logger.name == 'AMT'
        assert len(logger.handlers) == 0

    def test_get_logger(self):
        r"""
        Tests creation of a logger
        """
        logger = amt_core._get_logger('ApertureMapModelTools.Test.TestCore')
        #
        assert logger.name == 'AMT.Test.TestCore'

    def test_set_main_logger_level(self):
        r"""
        Tests adjudtment of primary logger level
        """
        #
        logger = logging.getLogger('AMT')
        amt_core.set_main_logger_level('debug')
        #
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_files_from_directory(self):
        r"""
        Runs the files_from_directory command with various args
        """
        files = amt.files_from_directory('.', '*')
        assert len(files)
        files = amt.files_from_directory('.', re.compile('.'))
        assert len(files)

    def test_load_infile_list(self):
        r"""
        Sends a list of infiles
        """
        fname1 = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'parallel-plate-01vox.txt')
        fname2 = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'parallel-plate-10vox.txt')
        infile_list = [fname1, fname2]
        #
        fields = amt.load_infile_list(infile_list)
        assert fields

    def test_calc_percentile(self):
        r"""
        Sends a test array to the calc percentile function
        """
        data_list = list(range(100))
        val = amt.calc_percentile(99, data_list)
        assert val == 99

    def test_calc_percentile_num(self):
        r"""
        Sends a test array to the calc percentile function
        """
        data_list = list(range(100))
        val = amt.calc_percentile_num(50, data_list, last=False)
        assert val*100 == 50
        val = amt.calc_percentile_num(50, data_list, last=True)
        assert val*100 == 51

    def test_get_data_vect(self):
        r"""
        Tests extraction of a vector from a data array
        """
        data = sp.arange(100)
        data = data.reshape(10, 10)
        #
        vect = amt.get_data_vect(data, 'x', 0)
        assert sp.all(vect == data[0, :])
        vect = amt.get_data_vect(data, 'x', 11)
        assert sp.all(vect == data[9, :])
        vect = amt.get_data_vect(data, 'z', 0)
        assert sp.all(vect == data[:, 0])
        vect = amt.get_data_vect(data, 'z', 11)
        assert sp.all(vect == data[:, 9])
        #
        with pytest.raises(ValueError):
            amt.get_data_vect(data, 'y')

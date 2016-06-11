"""
Handles testing of the core object and function module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
import os
import pytest
import re
import scipy as sp
import ApertureMapModelTools as amt


class TestCore:
    r"""
    Tests each of the functions an classes used in the __core__ module
    """
    def setup_class(self):
        pass

    def test_data_field(self):
        r"""
        Builds a data field and tests its properties
        """
        fname = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT')
        field = amt.DataField(fname)
        field.create_point_data()
        assert field.nx == 100
        assert field.nz == 100
        assert field.data_map.size == 10000
        assert field.point_data.size == 40000

    def test_stat_file(self):
        r"""
        Builds a stat file and test its properties
        """
        fname = os.path.join(FIXTURE_DIR, 'TEST-STAT-FILE.CSV')
        stat_file = amt.StatFile(fname)
        assert stat_file.map_file

    def test_arg_processor(self):
        r"""
        Builds an ArgProcessor object
        """
        arg = amt.ArgProcessor(True)
        assert arg.field

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
        fname1 = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-01VOX.TXT')
        fname2 = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'PARALELL-PLATE-10VOX.TXT')
        infile_list = [fname1, fname2]
        #
        fields = amt.load_infile_list(infile_list)

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

    def test_multi_output_columns(self):
        r"""
        Adding this test so it will throw an error later when I fix the
        output function. That way I'll rememeber to make a test function
        """
        with pytest.raises(NotImplementedError):
            amt.multi_output_columns(None)

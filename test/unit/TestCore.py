"""
Handles testing of the core object and function module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
import os
import re
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

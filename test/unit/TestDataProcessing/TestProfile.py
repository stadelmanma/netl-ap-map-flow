"""
Handles testing of the Profile class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/10/25
#
"""
import argparse
import os
import pytest
import scipy as sp
from ApertureMapModelTools.data_processing.profile import Profile


class TestProfile:
    r"""
    Testing each method of the Profile class
    """
    def test_initialization(self, data_field_class):
        r"""
        Testing class initialization
        """
        prof = Profile(data_field_class(), )
        assert not prof.args
        #
        prof = Profile(data_field_class(), locations=[1, 2, 3])
        assert prof.args['locations'] == [1, 2, 3]

    def test_add_sub_parser(self):
        # setting up required parsers
        parser = argparse.ArgumentParser()
        parent = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers()

        # adding percentiles subparser
        Profile._add_subparser(subparsers, parent)

        # testing parser
        cargs = 'Profile x 10'.split()
        args = parser.parse_args(cargs)
        cargs = 'prof z 5 20 50'.split()
        args = parser.parse_args(cargs)
        #
        assert args.axis == 'z'
        assert args.locations == [5, 20, 50]
        #
        cargs = 'prof y 5'.split()
        with pytest.raises(SystemExit):
            args = parser.parse_args(cargs)

    def test_process_data(self, data_field_class):
        r"""
        Testing the results of getting data vectors in multiple directions
        """
        fmt = '{:4.2f}'
        prof = Profile(data_field_class())
        prof.args = {'axis': 'x', 'locations': [0, 50, 100]}
        prof._process_data()
        assert sp.all(prof.processed_data[fmt.format(0)] == prof.data_map[0, :])
        assert sp.all(prof.processed_data[fmt.format(50)] == prof.data_map[5, :])
        assert sp.all(prof.processed_data[fmt.format(100)] == prof.data_map[9, :])
        #
        prof.args = {'axis': 'z', 'locations': [0, 50, 100]}
        prof._process_data()
        assert sp.all(prof.processed_data[fmt.format(0)] == prof.data_map[:, 0])
        assert sp.all(prof.processed_data[fmt.format(50)] == prof.data_map[:, 5])
        assert sp.all(prof.processed_data[fmt.format(100)] == prof.data_map[:, 9])
        #
        prof.args = {'axis': 'y', 'locations': [0, 50, 100]}
        prof._process_data()
        assert prof.processed_data is None

    def test_output_data(self, data_field_class):
        r"""
        Testing output content generation
        """
        fmt = '{:4.2f}'
        prof = Profile(data_field_class())
        prof.infile = os.path.join(TEMP_DIR, 'test-profile.txt')
        prof.args = {'axis': 'x', 'locations': [0, 50, 100]}
        #
        start_ids = [(int(l/100.0*prof.nz)+1) for l in prof.args['locations']]
        prof.loc_ids = {fmt.format(loc): sid for loc, sid in zip(prof.args['locations'], start_ids)}
        prof.processed_data = {}
        #
        prof.processed_data[fmt.format(0)] = prof.data_map[0, :]
        prof.processed_data[fmt.format(50)] = prof.data_map[5, :]
        prof.processed_data[fmt.format(100)] = prof.data_map[9, :]
        #
        prof._output_data(delim='\t')
        assert prof.outfile_content

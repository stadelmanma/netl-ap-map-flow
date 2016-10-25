"""
Handles testing of the BaseProcessor class
#
Written By: Matthew Stadelman
Date Written: 2016/06/12
Last Modifed: 2016/06/12
#
"""
import os
import pytest
import scipy as sp
from ApertureMapModelTools.DataProcessing.__BaseProcessor__ import BaseProcessor


class TestBaseProcessor:
    r"""
    Testing each method of the BaseProcessor class
    """
    def test_initialization(self, data_field_class):
        r"""
        Hitting the init method specifically
        """
        field = data_field_class()
        base_proc = BaseProcessor(field)
        #
        # checking native attributes
        assert base_proc.action == 'base'
        assert base_proc.infile == field.infile
        assert (base_proc.data_vector == field.data_vector).all()
        assert (base_proc.data_map == field.data_map).all()
        assert not base_proc.args
        assert not base_proc.outfile_name
        assert not base_proc.outfile_content
        assert not base_proc.output_key
        assert not base_proc.processed_data

    def test_setup(self, data_field_class):
        r"""
        Hitting set_args
        """
        base_proc = BaseProcessor(data_field_class())
        #
        base_proc.setup(param1='value1', param2=2, param3=[1, 2, 3])
        assert base_proc.args['param1'] == 'value1'
        assert base_proc.args['param2'] == 2
        assert base_proc.args['param3'] == [1, 2, 3]

    def test_notimplemented_methods(self, data_field_class):
        r"""
        Tests the various methods that need to be implemented by a subclass
        and their parent calling methods if they have one
        """
        base_proc = BaseProcessor(data_field_class())
        #
        #
        with pytest.raises(NotImplementedError):
            base_proc._add_subparser(None)
        #
        #
        with pytest.raises(NotImplementedError):
            base_proc.process()
            base_proc.args = True
            base_proc.process()
        #
        #
        with pytest.raises(NotImplementedError):
            base_proc.gen_output()
            base_proc.processed_data = True
            base_proc.gen_output()
        #
        #
        base_proc.processed_data = False
        base_proc.copy_processed_data({}, alt_key='test')
        data = {}
        base_proc.processed_data = True
        base_proc.copy_processed_data(data, alt_key='test')
        assert data['test'] is True
        #
        #
        base_proc.print_data()
        base_proc.outfile_content = 'test content'
        base_proc.print_data()
        #
        #
        base_proc.outfile_content = None
        base_proc.write_data()
        base_proc.outfile_content = 'test'
        base_proc.outfile_name = os.path.join(TEMP_DIR, 'test.txt')
        base_proc.write_data()

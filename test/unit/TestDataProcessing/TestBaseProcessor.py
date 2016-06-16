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
from ApertureMapModelTools.DataProcessing.__BaseProcessor__ import BaseProcessor


class TestBaseProcessor:
    r"""
    Testing each method of the BaseProcessor class
    """
    def test_initialization(self, data_field_class):
        r"""
        Hitting the init method specifically
        """
        base_proc = BaseProcessor(data_field_class())
        #
        # checking native attributes
        assert base_proc.action == 'base'
        assert not base_proc.args
        assert not base_proc.arg_processors
        assert not base_proc.outfile_name
        assert not base_proc.outfile_content
        assert not base_proc.output_key
        assert not base_proc.processed_data
        assert not base_proc.validated

    def test_set_args(self, data_field_class):
        r"""
        Hitting set_args
        """
        base_proc = BaseProcessor(data_field_class())
        #
        base_proc.set_args({})
        base_proc.set_args({}, skip_validation=True)

    def test_validate_args(self, data_field_class, arg_processor_class):
        r"""
        Hitting validate args testing valid and invalid inputs. This
        also will cover the input_error class
        """
        base_proc = BaseProcessor(data_field_class())
        #
        # testing valid args
        base_proc.args = {
            'test-single': 'pass',
            'test-list': 'pass1,pass2'
        }
        base_proc.arg_processors = {
            'test-single': arg_processor_class('test-single'),
            'test-list': arg_processor_class('test-list', min_num_vals=2, out_type='list')
        }
        base_proc.validated = base_proc.validate_args()
        assert base_proc.validated
        #
        # checking if repeated validation is skipped
        base_proc.validated = base_proc.validate_args()
        assert base_proc.validated is None
        #
        # checking bad arguments
        base_proc.args = {
            'bad-single': '',
            'bad-list': 'should-be-list',
            'bad-value': 'should-be-number'
        }
        base_proc.arg_processors = {
            'bad-single': arg_processor_class('bad-single'),
            'bad-list': arg_processor_class('bad-list', min_num_vals=2, out_type='list'),
            'bad-value': arg_processor_class('bad-value', map_func=lambda x: int(x)),
            'missing-arg': arg_processor_class('missing-arg')
        }
        base_proc.validated = base_proc.validate_args()
        assert not base_proc.validated
        #
        base_proc.args = {
            'unhandled-err': '0'
        }
        base_proc.arg_processors = {
            'unhandled-err': arg_processor_class('bad-value', map_func=lambda x: 1/int(x))
        }
        with pytest.raises(ZeroDivisionError):
            base_proc.validated = base_proc.validate_args()

    def test_notimplemented_methods(self, data_field_class):
        r"""
        Tests the various methods that need to be implemented by a subclass
        and their parent calling methods if they have one
        """
        base_proc = BaseProcessor(data_field_class())
        #
        #
        with pytest.raises(NotImplementedError):
            base_proc.process()
            base_proc.validated = True
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

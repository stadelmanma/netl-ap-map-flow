"""
================================================================================
Base Processor
================================================================================
| This is a template that is used to add additional processors to
| the package.

| Written By: Matthew Stadelman
| Date Written: 2016/02/26
| Last Modifed: 2016/10/25

"""
import os
from .. import _get_logger
logger = _get_logger(__name__)


class BaseProcessor(object):
    r"""
    Only required parameter is a data field object, initializes properties
    defined by subclassses.
    """

    def __init__(self, field):
        # initializing properties
        self.action = 'base'
        self.args = {}
        self.infile = field.infile
        self.data_vector = None
        self.data_map = None
        self.outfile_name = os.path.basename(self.infile) if self.infile else ''
        self.outfile_content = None
        self.output_key = None
        self.processed_data = None

        # copying field data
        field.copy_data(self)

    @classmethod
    def _add_subparser(cls, subparser):
        r"""
        Adds a specific action based sub-parser to the supplied arg_parser
        instance.
        """
        msg = 'This method must be implemented by a specific '
        msg += 'data processing class'
        raise NotImplementedError(msg)

    def setup(self, **kwargs):
        r"""
        Sets or resets arguments
        """
        self.args.update(kwargs)

    def process(self, **kwargs):
        r"""
        Calls the subclassed routine process_data to create outfile content
        """
        if not self.args:
            msg = 'No arguments have been set, use setup(**kwargs) method'
            logger.error(msg)
            return
        #
        self._process_data(**kwargs)

    def _process_data(self, **kwargs):
        r"""
        Not implemented
        """
        msg = 'This method must be implemented by a specific '
        msg += 'data processing class'
        raise NotImplementedError(msg)

    def gen_output(self, **kwargs):
        r"""
        Calls the subclassed routine output_data to create outfile content
        """
        if not self.processed_data:
            msg = 'No data has been processed. Run process() method'
            logger.error(msg)
            return
        #
        self._output_data(**kwargs)

    def _output_data(self, filename=None, delim=','):
        r"""
        Not implemented
        """
        msg = 'This method must be implemented by a specific '
        msg += 'data processing class'
        raise NotImplementedError(msg)

    def copy_processed_data(self, data_dict, alt_key=False):
        r"""
        Copys the current processed data array to a dict object using a
        key defined in the subclass initialization or a key supplied by the
        alt_key keyword.
        """
        if not self.processed_data:
            msg = 'No data has been processed. Run process() method'
            logger.error(msg)
            return
        #
        key = alt_key if alt_key else self.output_key
        data_dict[key] = self.processed_data

    def print_data(self):
        r"""
        Writes the data processor's data the screen
        """
        if (not self.outfile_content):
            msg = 'No output content. Run gen_output() method'
            logger.error(msg)
            return
        #
        print(self.outfile_content)
        print('')

    def write_data(self, path=os.path.realpath(os.curdir)):
        r"""
        Writes the data processor's data to its outfile
        """
        if (not self.outfile_content):
            msg = 'No output content. Run gen_output() method'
            logger.error(msg)
            return
        #
        filename = os.path.join(path, self.outfile_name)
        with open(filename, 'w') as f:
            f.write(self.outfile_content)
        #
        logger.info('Output saved as: ' + filename)

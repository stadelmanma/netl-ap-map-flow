"""
Outputs a set of data profiles along either the X or Z axis
#
Written By: Matthew Stadelman
Date Written: 2016/03/07
Last Modifed: 2016/10/25
#
"""
from collections import OrderedDict
from ApertureMapModelTools.__core__ import _get_logger, get_data_vect
from .__BaseProcessor__ import BaseProcessor
logger = _get_logger(__name__)


class Profile(BaseProcessor):
    r"""
    Automatic method to export data vectors for a range of distances
    along a specified axis. Locations are given as percentages from the
    bottom or left edge of the 2-D data map
        locs  -  list of numbers, ex: [10, 25, 50, 75, 90]
        axis   - (x or z) specifies which axis to export along
    """
    def __init__(self, field, **kwargs):
        super().__init__(field)
        self.args.update(kwargs)
        self.output_key = 'profile'
        self.action = 'profile'

    @classmethod
    def _add_subparser(cls, subparsers, parent):
        r"""
        Adds a specific action based sub-parser to the supplied arg_parser
        instance.
        """
        parser = subparsers.add_parser(cls.__name__,
                                     aliases=['prof'],
                                     parents=[parent],
                                     help='''exports profiles along an axis
                                     at specified locations''')
        #
        parser.add_argument('axis', choices=['x', 'z'],
                          help='x or z for the corresponding axis')
        parser.add_argument('locations', nargs='+', type=float,
                            help='location as percent distance from axis')

    def _process_data(self, **kwargs):
        r"""
        Takes a list of percentiles specified in **kwargs and generates
        the corresponding set of values.
        """
        #
        axis = self.args['axis']
        locs = self.args['locs']
        locs.sort()
        #
        if axis.lower() == 'x':
            # first row is bottom of fracture
            inds = [(int(l/100.0*self.nz) + 1) for l in locs]
        elif axis.lower() == 'z':
            # first column is left side of fracture
            inds = [(int(l/100.0*self.nx) + 1) for l in locs]
        else:
            msg = 'Invalid axis: "{}" supplied, valid values are x or z'
            logger.error(msg.format(axis))
            self.processed_data = None
            return
        #
        # getting data vectors
        fmt = '{:4.2f}'
        self.processed_data = OrderedDict()
        for loc, row in zip(locs, inds):
            loc = fmt.format(loc)
            self.processed_data[loc] = get_data_vect(self.data_map, axis, row)

    def _output_data(self, filename=None, delim=','):
        r"""
        Creates the output content for data profiles
        """
        #
        if filename is None:
            filename = self.infile
        #
        # getting index before the extension
        ldot = filename.rfind('.')
        #
        # naming ouput file
        axis = self.args['axis'].upper()
        name = filename[:ldot]+'-profiles-'+axis+'-axis'+filename[ldot:]
        self.outfile_name = name
        #
        # outputting data
        fmt = 'Location: {0}%{1}\n'
        content = axis+'-axis profile data from file: '+self.infile+'\n'
        for loc, vector in self.processed_data.items():
            content += fmt.format(loc, delim)
            vector = [str(val) for val in vector]
            content += delim.join(vector)+'\n'
        content += '\n'
        #
        self.outfile_content = content

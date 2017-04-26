"""
Evaluates channelization in flow data based on the number and widths of channels
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/10/25
#
"""
#
from ..ap_map_flow import _get_logger
from .base_processor import BaseProcessor
logger = _get_logger(__name__)


class EvalChannels(BaseProcessor):
    r"""
    Evaluates channelization in flow data based on the number and widths
    of channels. More work needs to be done on this class to make it
    not dependent on a specfic direction.
    kwargs include:
        thresh - minimum numeric value considered to be part of a flow channel
        axis - (x or z) specifies which axis to export along
    """
    def __init__(self, field, **kwargs):
        super().__init__(field)
        self.args.update(kwargs)
        self.output_key = 'eval_chan'
        self.action = 'evaluate channels'

    @classmethod
    def _add_subparser(cls, subparsers, parent):
        r"""
        Adds a specific action based sub-parser to the supplied arg_parser
        instance.
        """
        parser = subparsers.add_parser(cls.__name__,
                                       aliases=['chans'],
                                       parents=[parent],
                                       help=cls.__doc__)
        #
        parser.add_argument('axis', choices=['x', 'z'],
                            help='x or z for the corresponding axis')
        parser.add_argument('thresh', type=float,
                            help='minimum value to consider as part of a channel')
        parser.set_defaults(func=cls)

    def _process_data(self, **kwargs):
        r"""
        Examines the dataset along one axis to determine the number and
        width of channels.
        """
        #
        direction = self.args['axis']
        min_val = self.args['thresh']
        #
        if (direction.lower() == 'x'):
            span = self.nx
            step = self.nz
        elif (direction.lower() == 'z'):
            span = self.nz
            step = self.nx
        else:
            logger.error('invalid direction supplied, can only be x or z')
            return
        #
        self.processed_data = dict()
        channels = []
        num_channels = []
        channel_widths = []
        avg_channel_width = []
        st = 0
        for i in range(span):
            channels.append([])
            channel_widths.append([])
            bounds = [-1, -1]
            en = st + step
            for j in range(st, en, 1):
                if (self.data_vector[j] > min_val):
                    bounds[0] = (j if bounds[0] < 0 else bounds[0])
                else:
                    if (bounds[0] > 0):
                        bounds[1] = j-1
                        # adding to channel list and then resetting bounds
                        channels[i].append((bounds[0], bounds[1]))
                        channel_widths[i].append(bounds[1] - bounds[0] + 1)
                        bounds = [-1, -1]
            # adding end point if channel butts up against edge of fracture
            if (bounds[0] > 0):
                bounds[1] = j
                # adding to channel list and then resetting bounds
                channels[i].append((bounds[0], bounds[1]))
                bounds = [-1, -1]
            # calculating average channel width
            avg = 0
            for chan in channel_widths[i]:
                avg += chan
            n = len(channel_widths[i]) if len(channel_widths[i]) > 0 else 1.0
            avg = avg / n
            num_channels.append(len(channels[i]))
            avg_channel_width.append(avg)
            st = en
        #
        # putting data into storage dict
        self.processed_data['chan_indicies_per_row'] = channels
        self.processed_data['chans_per_row'] = num_channels
        self.processed_data['chan_widths_per_row'] = channel_widths
        self.processed_data['avg_chan_width_per_row'] = avg_channel_width

    def _output_data(self, filename=None, delim=',', **kwargs):
        r"""
        creates the output content for channelization
        """
        #
        if filename is None:
            filename = self.outfile_name
            #
            # getting index before the extension
            ldot = filename.rfind('.')
            #
            # naming ouput file
            dir_ = self.args['axis'].upper()
            filename = filename[:ldot]+'-channel_data-'+dir_+'-axis'+filename[ldot:]
        self.outfile_name = filename
        #
        # outputting data
        content = 'Channelization data from file: '+self.infile+'\n'
        content += (self.args['axis']+'-index'+delim+'Number of Channels' +
                    delim+'Average Width'+delim+'Channel Widths\n')
        #
        num_channels = list(self.processed_data['chans_per_row'])
        avg_width = list(self.processed_data['avg_chan_width_per_row'])
        widths = list(self.processed_data['chan_widths_per_row'])
        for i in range(len(num_channels)):
            chans = [str(x) for x in widths[i]]
            chans = '('+', '.join(chans)+')'
            row = '{0:4d}'+delim+'{1:3d}'+delim+'{2:0.3}'+delim+'{3}'
            row = row.format(i, num_channels[i], avg_width[i], chans)
            content += row+'\n'
        content += '\n'
        #
        self.outfile_content = content

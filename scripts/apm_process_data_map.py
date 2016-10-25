#!/usr/bin/env python3
r""" Loads and processes data maps using the requested processor class """
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import re
from ApertureMapModelTools import _get_logger, set_main_logger_level, DataField
from ApertureMapModelTools import DataProcessing
#
########################################################################
#
desc_str = r"""
Description: Processes data maps using the desired DataProcessing class
and either writes data to file or prints to screen.

Written By: Matthew stadelman
Date Written: 2015/10/01
Last Modfied: 2016/10/25
"""
#
# fetching logger
logger = _get_logger('ApertureMapModelTools.Scripts')
#
# setting up the argument parser
parser = argparse.ArgumentParser(description=desc_str,
                                 formatter_class=RawDesc)
#
# defining main arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help="prints debug messages (default: %(default)s)")
parser.add_argument('-f', '--force', action='store_true',
                    help="can overwrite existing files (default: %(default)s)")
parser.add_argument('-W', '--no-write', action='store_true',
                    help="does not write data to file (default: %(default)s)")
parser.add_argument('-s', '--screen', action='store_true',
                    help="print data to screen (default: %(default)s)")
#
# defining sub-parsers
subparse_parent = argparse.ArgumentParser(add_help=False)
subparse_parent.add_argument('-files', nargs='+', type=os.path.realpath,
                             required=True,
                             help='data file to process')
subparsers = parser.add_subparsers(dest='processor',
                                   title='Data Processing Commands',
                                   metavar='{command}')

classes = [k for k in DataProcessing.__dict__.keys() if not re.match('^__', k)]
for cls in classes:
    DataProcessing.__dict__[cls]._add_subparser(subparsers, subparse_parent)

#
########################################################################


def apm_process_data_map():
    r"""
    Parses command line arguments and delegates tasks to helper functions
    for actual data processing
    """
    args = parser.parse_args()
    #
    if args.verbose:
        set_main_logger_level('debug')
    #
    process_files(args)


def process_files(args):
    r"""
    Handles processing of the input maps based on the supplied arguments
    """
    for file in args.files:
        field = DataField(file)
        processor = args.func(field, **args.__dict__)
        processor.process()

        # printing data to screen if -s flag
        if args.screen:
            processor.gen_output(delim='\t')
            processor.print_data()

        # writing data if -W was not used
        if not args.no_write:
            processor.gen_output(delim=',')
            if os.path.exists(processor.outfile_name) and not args.force:
                msg = '{} already exists, use "-f" option to overwrite'
                raise FileExistsError(msg.format(processor.outfile_name))
            processor.write_data()

if __name__ == '__main__':
    apm_process_data_map()

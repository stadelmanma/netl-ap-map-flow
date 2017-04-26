#!/usr/bin/env python3
r""" Loads and processes data maps using the requested processor class """
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import re
from apmapflow import _get_logger, set_main_logger_level, DataField
from apmapflow import data_processing
#
########################################################################
#
desc_str = r"""
Description: Processes data maps using the desired data_processing class
and either writes data to file or prints to screen.

Written By: Matthew stadelman
Date Written: 2015/10/01
Last Modfied: 2017/04/23
"""
#
# fetching logger
logger = _get_logger('apmapflow.Scripts')
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
subparse_parent.add_argument('-o', '--output-dir',
                             type=os.path.realpath, default=os.getcwd(),
                             help='''outputs files to the specified
                             directory, sub-directories are created as needed''')
subparsers = parser.add_subparsers(dest='processor',
                                   title='Data Processing Commands',
                                   metavar='{command}')

classes = data_processing.__dict__.values()
for cls in classes:
    try:
        cls._add_subparser(subparsers, subparse_parent)
    except AttributeError:
        pass

#
########################################################################


def main():
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
            #
            filename = os.path.join(args.output_dir, processor.outfile_name)
            if os.path.exists(filename) and not args.force:
                msg = '{} already exists, use "-f" option to overwrite'
                raise FileExistsError(msg.format(filename))
            #
            processor.write_data(path=args.output_dir)

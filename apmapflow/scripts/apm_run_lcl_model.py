#!/usr/bin/env python3
r"""
Description: Runs each of the provided input files through the modified local
cubic law model. Add the line ;EXE-FILE: (exec file) to the input file to use a
different version of the local cubic law model.

For usage information run: ``apm_run_lcl_model -h``

Written By: Matthew stadelman
Date Written: 2017/04/04
Last Modfied: 2017/04/23
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
from apmapflow import _get_logger, set_main_logger_level
from apmapflow.run_model import InputFile, estimate_req_RAM, run_model


# setting log level
set_main_logger_level('info')
logger = _get_logger('apmapflow.scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-e', '--executable', default=None, type=os.path.realpath,
                    help='debug messages are printed to the screen')

parser.add_argument('input_files', nargs='+', type=os.path.realpath,
                    help='1 or more model parameter files to load')


def main():
    r"""
    Driver function to handle parsing command line args and running the model.
    """
    # parsing commandline args
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')
    #
    for n, input_file in enumerate(args.input_files):
        msg = 'Processing input file {} of {}: {}'
        fname = os.path.split(input_file)[1]
        logger.debug(msg.format(n + 1, len(args.input_files), fname))
        input_file = InputFile(input_file)
        #
        ram_req = estimate_req_RAM([input_file['APER-MAP'].value])[0]
        msg = 'Map will require approimately {:0.6f} GBs of RAM'.format(ram_req)
        logger.info(msg)
        #
        if args.executable:
            input_file.executable = args.executable
        #
        proc = run_model(input_file, synchronous=True, show_stdout=True)

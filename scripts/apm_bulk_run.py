#!/usr/bin/env python3
r"""
Parses YAML formatted file(s) to automatically setup a bulk run of the
LCL model.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import yaml
from ApertureMapModelTools import set_main_logger_level
from ApertureMapModelTools.RunModel import BulkRun, InputFile

#
desc_str = r"""
Description: Parses a set of YAML formatted input files and creates a
set of InputFiles to run through the LCL model in parallel. The --start flag
must be supplied to run the simulations, otherwise a dry run is performed.
Only the keyword args of the first YAML file are used to instantiate the
bulk_run_class.

Written By: Matthew stadelman
Date Written: 2016/08/04
Last Modfied: 2016/10/18
"""

# setting log level
set_main_logger_level('info')

# creating arg parser
parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('--start', action='store_true', default=False,
                    help='flag must be supplied to "start" the bulk run')

parser.add_argument('input_files', nargs='+', type=os.path.realpath,
                    help='1 or more YAML input files to load')


def apm_bulk_run():
    r"""
    Driver function to handle parsing of command line args and setting up
    the bulk run
    """
    # parsing commandline args
    namespace = parser.parse_args()
    if namespace.verbose:
        set_main_logger_level('debug')

    bulk_run = None
    for input_file in namespace.input_files:
        #
        # loading yaml file and parsing input file
        input_file = open(input_file, 'r')
        inputs = yaml.load(input_file)
        inp_file = InputFile(inputs['initial_input_file'])

        # Creating class with provided kwargs
        if not bulk_run:
            bulk_run = BulkRun(inp_file, **inputs['bulk_run_keyword_args'])

        # Generating the InputFile list
        bulk_run.generate_input_files(inputs['default_run_parameters'],
                                      inputs['default_file_formats'],
                                      case_identifer=inputs.get('case_identifier', None),
                                      case_params=inputs.get('case_parameters', None),
                                      append=True)

    # starting or dry running sims
    if namespace.start:
        bulk_run.start()
    else:
        bulk_run.dry_run()
        print('Add "--start" flag to begin simulations')


#
if __name__ == '__main__':
    apm_bulk_run()

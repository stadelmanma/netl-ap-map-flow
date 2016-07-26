#!/usr/bin/env python3
import argparse
from argparse import RawDescriptionHelpFormatter
import logging
import os
import re
import subprocess
import sys
from ApertureMapModelTools import DataField, files_from_directory
from ApertureMapModelTools.OpenFoamExport import OpenFoamExport, OpenFoamFile
from ApertureMapModelTools.RunModel import InputFile
#
#
########################################################################
#
desc_str = r"""
Description: Generates a complete OpenFoam simulation from an APM-MODEL
input file and existing OpenFoam files which are used as templates.

Written By: Matthew stadelman
Date Written: 2015/07/25
Last Modfied: 2016/07/25
"""

interactive_message = r"""
-------------------------------------------------------------------------------
apm_open_foam_export script has been run in interactive mode

The following global variables have been defined:
    raw_files - list of file names in searched directories
    foam_files - dictionary of OpenFoam files generated
    apm_input_file - InputFile object if an input file was passed in
    namespace - argparse namespace object of command line args used
-------------------------------------------------------------------------------
"""
#
#logging.basicConfig(format='%(levelname)s:%(message)s')
#
# creating arg parser
parser = argparse.ArgumentParser(description=desc_str,
                                 formatter_class=RawDescriptionHelpFormatter)
parser.add_argument('-f', '--force', action='store_true',
                    help='''"force/overwrite mode",
                    allows program to overwrite existing files''')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='''"verbose mode", extra messages are printed to
                    the screen''')
parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''"output to", outputs all files to the specified
                    directory, sub-directories are created as needed''')
parser.add_argument('-r', '--read-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''"read from", reads existing OpenFoam files from
                    the supplied directory. If not specfied will read files
                    from current directory.''')
parser.add_argument('-i', '--interactive', action='store_true',
                    help='''"interactive mode", processes commandline arguments
                    inside the spawned python intepreter''')

parser.add_argument('--no-interactive', action='store_true',
                    help='''Internal arg used to prevent run_interactive
                         from looping''')

parser.add_argument('input_file', nargs='?', type=os.path.realpath,
                    help='APM-MODEL input file to read in')
#
# globals defined for easier interactive use
raw_files = None
foam_files = {}
apm_input_file = None
namespace = None
#
########################################################################


def eprint(*args, **kwargs):
    r"""
    Prints messages to stderr instead of stdout
    """
    print(*args, file=sys.stderr, **kwargs)


def apm_open_foam_export(carg_list):
    r"""
    Handles processing of commandline args and generation of open foam files
    """
    global namespace
    namespace = parser.parse_args()
    #
    if namespace.verbose:
        logging.basicConfig(level=logging.DEBUG)
    #
    if namespace.interactive and not namespace.no_interactive:
        run_interactive(carg_list)
        return
    #
    load_foam_files()
    if namespace.input_file:
        load_inp_file()
    #
    if namespace.interactive:
        print(interactive_message)

def run_interactive(carg_list):
    r"""
    Creates an interactive session to manually update files
    """
    cmd = ['python3', '-i'] + carg_list + ['--no-interactive']
    subprocess.call(cmd)


def load_foam_files():
    r"""
    Loads any existing files from the supplied directory path. Only checks for
    local files and any files in constant/ system if the directories exist.
    """
    global namespace, raw_files, foam_files
    #
    # making directories
    path = namespace.read_dir
    con_path = os.path.join(path, 'constant')
    sys_path = os.path.join(path, 'system')
    #
    # non-recursively loading files
    raw_files = files_from_directory('.', '*', deep=False)
    #
    if os.path.exists(con_path):
        raw_files += files_from_directory(con_path, '*', deep=False)
    #
    if os.path.exists(sys_path):
        raw_files += files_from_directory(sys_path, '*', deep=False)
    #
    # processing valid OpenFoamFiles
    for file in raw_files:
        of_file = None
        try:
            of_file = OpenFoamFile.init_from_file(file)
            key = '{location}.{object}'.format(**of_file.head_dict)
            key = re.sub('"', '', key)
            foam_files[key] = of_file
        except Exception as err:
            msg = 'Skipping file: {} - Encountered {}: {}'
            msg = msg.format(file, err.__class__.__name__, str(err))
            logging.debug(msg)

def load_inp_file():
    r"""
    Loads in an APM-MODEL input file if it was supplied and pulls out
    required information.
    """
    global namespace, apm_input_file
    apm_input_file = InputFile(namespace.input_file)

#
########################################################################
#
# Runs the function if being invoked directly, acts as a module otherwise.
if __name__ == '__main__':
    apm_open_foam_export(sys.argv)





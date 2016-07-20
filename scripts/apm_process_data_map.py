#!/usr/bin/env python3
import os
import re
import sys
import ApertureMapModelTools as apm
#
########################################################################
#
desc_str = r"""
Description: This program calls the desired class in the DataProcessing
          module and processes input files based on supplied parameters.

Written By: Matthew stadelman
Date Written: 2015/10/01
Last Modfied: 2016/07/19
"""

usage_str = r"""
usage:
    apm_process_data_map [command] [flags] [args] files=<file1,file2,...>
  OR
    apm_process_data_map --help
  OR
    apm_process_data_map [command] --help
"""

cmd_str = r"""
commands:
    eval_chans: "EvalChannels", processes the data to determine
        the number and widths of any channels present.
        (only really useful for flow data)

    hist: "Histogram", does a full min -> max val histogram of
        each input file

    hist_range: "HistogramRange", does a histrogram for the
        provided percentile range, i.e. 10th - 90th percentile

    hist_logscale: "HistogramLogscale" full range of data with logarithmic
        bin sizes

    profile: "Profile", outputs a vector of cells in either the x or z
        direction straight from the data file. Location is based on percentage
        from the bottom or left sides. i.e. locs=10,90 will output a profile
        at 1cm and 9cm if the axis is 10cm long.

    pctle: "Percentiles", outputs one or more percentiles from the data map
"""

flag_str = r"""
flags:

    -v or --verbose: "verbose mode", data and messages are printed to the
        screen

    -w or --write: "write output", (default), ouputs data csv file(s)

    -W or --no-write: "no-write", does not write data to an output file

    -f or --force: "force/overwrite mode", allows program to overwrite an
        existing file

    --help, prints this message and exits, use --help after a command to
            get detailed information about that command.
"""

sample_str = r"""
sample inputs:
    process_data_map.py hist num_bins=100 file=test_file.csv

    process_data_map.py pctle -vW perc=25,50,75 files=test_file1.csv
"""

dash_line = '-'*80
help_str = dash_line.join([desc_str, usage_str, cmd_str, flag_str, sample_str])
#
# dictionary to hold classes
COMMANDS = {
    'eval_chans': apm.DataProcessing.EvalChannels,
    'hist': apm.DataProcessing.Histogram,
    'hist_logscale': apm.DataProcessing.HistogramLogscale,
    'hist_range': apm.DataProcessing.HistogramRange,
    'profile': apm.DataProcessing.Profile,
    'pctle': apm.DataProcessing.Percentiles
}
# dictionary for handling flags in argument list
FLAGS = {
    'f': False,
    'v': False,
    'w': True,
    'W': False,
    'help': False
}
# dictionary for handling extended flags in argument list
EXT_FLAGS = {
    'force': 'f',
    'verbose': 'v',
    'write': 'w',
    'no-write': 'W',
    'help': 'help'
}
#
########################################################################


def process_cargs(arg_dict):
    r"""
    Handles parsing of command line arguments
    """
    #
    # checking number of args to ensure something was given on the command line
    if (len(sys.argv) <= 1):
        print('Error: This program requires command line arguments')
        print(usage_str)
        exit(1)
    #
    # getting command
    command = sys.argv[1]
    if command == '--help':
        print(help_str)
        exit(0)
    else:
        try:
            dat_proc = COMMANDS[command]
        except KeyError:
            print('Invalid command provided: '+command)
            print(usage_str)
            print(cmd_str)
            exit(1)
    #
    # processing remaining commandline arguments
    for i in range(2, len(sys.argv)):
        arg = sys.argv[i]
        if (re.match('^--?\w', arg)):
            process_flags(arg, arg_dict)
        else:
            # splitting arg into a key,value pair
            kv_pair = arg.split('=')
            if (len(kv_pair) < 2):
                msg = 'Error - invalid argument: "'+arg+'" provided. '
                msg += 'Required to have form of arg=values\n'
                print(msg)
                exit(1)
            arg_dict[kv_pair[0]] = kv_pair[1]
    #
    # checking if a help argument was passed
    if arg_dict['flags']['help']:
        print('')
        print(dat_proc.help_message)
        exit(0)
    #
    return dat_proc


def process_flags(flags_in, arg_dict):
    r"""
    Handles setting flags given on the command line
    """
    #
    # turning flags_in into a list of flags
    if re.match('--', flags_in):
        flag_list = [re.match('--(.+)', flags_in).group(1)]
    else:
        flag_list = re.findall(r'\w', flags_in)
    #
    # checking flags existance
    for flag in flag_list:
        if (flag in FLAGS.keys()):
            arg_dict['flags'][flag] = True
        elif (flag in EXT_FLAGS.keys()):
            arg_dict['flags'][EXT_FLAGS[flag]] = True
        else:
            print('Error - invalid flag: "'+flag+'" provided.')
            print(usage_str)
            print(flag_str)
            exit(1)

#
########################################################################
#
# dictionary storing command line arguments
arg_dict = {
    'delim': None,
    'flags': {flag: val for flag, val in FLAGS.items()}
}
#
# parsing the command line arguments
dat_proc = process_cargs(arg_dict)
print(arg_dict)
#
# checking files value
file_error = False
try:
    files = re.split(',', arg_dict['files'])
    files = [f for f in files if f]
    if (len(files) == 0):
        raise IndexError
except KeyError:
    file_error = True
    msg = 'Error - No input files provided. '
    msg += 'Final argument needs to be files=file1,file2,...,file_n\n'
except IndexError:
    file_error = True
    msg = 'Error - file argument specified but no files listed. '
    msg += 'Check for spaces, valid format is: files=file1,file2,...,file_n\n'
#
if file_error:
    print(msg)
    exit(1)
#
# processing data fields
data_fields = apm.load_infile_list(files)
data_processors = [dat_proc(field) for field in data_fields]
print('')
#
for dat_proc in data_processors:
    #
    # checking if args passed validation test
    dat_proc.set_args(arg_dict)
    if not dat_proc.validated:
        print('')
        continue
    #
    dat_proc.process()
    #
    # printing to screen
    if (arg_dict['flags']['v']):
        dat_proc.gen_output(delim='\t')
        dat_proc.print_data()
    #
    # writting data
    if (arg_dict['flags']['w'] and not arg_dict['flags']['W']):
        dat_proc.gen_output(delim=',')
        exists = os.path.isfile(dat_proc.outfile_name)
        if (exists and not arg_dict['flags']['f']):
            msg = 'Error: Outfile - '+dat_proc.outfile_name+' already exists. '
            msg += 'The -f or --force flags need to be added to allow'
            msg += ' overwritting of an existing file.'
            print(msg)
            continue
        #
        dat_proc.write_data()


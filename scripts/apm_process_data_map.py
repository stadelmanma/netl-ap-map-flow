#!/usr/bin/env python3
import re
import sys
import ApertureMapModelTools as apm
#
########################################################################
#
help_str = r"""
------------------------------------------------------------------------
Description: This program calls the desired class in the DataProcessing
          module and processes input files based on supplied parameters.

Written By: Matthew stadelman
Date Written: 2015/10/01
Last Modfied: 2016/07/19

------------------------------------------------------------------------
usage:
    apm_process_data_map [command] [flags] [args] files=<file1,file2,...>

flags:
    -so: "screen only output", instead of writing file(s) the data
          will be output to the screen, in csv files commas become tabs

    -sw: "screen and write output", prints data to screen and
          ouptuts csv file(s)

    -ow: "overwrite", allows program to overwrite an existing file

commands:
    eval_chans: "EvalChannels", processes the data to
        the number and widths of channels present.
        (only really useful for flow data)

    hist: "Histogram", does a full min -> max val histogram of
        each input file

    hist_range: "HistogramRange", does a histrogram for the
        provided percentile range, i.e. 10th - 90th percentile

    hist_logscale: "HistogramLogscale" full range of data

    profile: "Profile", outputs a vector of cells
        in either the x or z direction straight from the data file. Location
        is based on percentage from the bottom or left sides. i.e.
        locs=10 will output a profile at 1cm if the axis is 10cm long.

    pctle: "Percentiles", outputs one or more percentiles from the data map

command args:
    eval_chans: thresh=## dir=(x or z)

    hist: num_bins=###

    hist_range: num_bins=### range=##,##

    hist_logscale: num_bins=###

    profile: locs=##1,##2,##3,...,##n dir=(x or z)

    pctle: perc=##1,##2,##3,...,##n


------------------------------------------------------------------------
sample inputs:

    process_data_map.py hist num_bins=100 file=test_file.csv

    process_data_map.py pctle perc=25,50,75 files=test_file1.csv,test_file2.csv

------------------------------------------------------------------------
"""
#
########################################################################
#
file_error = False
#
# dictionary to hold classes
action_dict = {
    'eval_chans': apm.DataProcessing.EvalChannels,
    'hist': apm.DataProcessing.Histogram,
    'hist_logscale': apm.DataProcessing.HistogramLogscale,
    'hist_range': apm.DataProcessing.HistogramRange,
    'profile': apm.DataProcessing.Profile,
    'pctle': apm.DataProcessing.Percentiles
}
# dictionary for handling flags in argument list
flag_dict = {
    '-so': False,
    '-sw': False,
}
# dictionary storing command line arguments
arg_dict = {
    'delim': None,
    'flag_list': []
}
# list holding DataField objects
data_fields = []
#
# checking number of args to ensure something was given on the command line
if (len(sys.argv) <= 1):
    print('Error: This program requires command line arguments')
    print(r"""usage:
    apm_process_data_map.py [command] [flags] [args] files=<file1,file2,...

    use apm_process_data_map.py --help for more information""")
    exit(1)
#
# getting command
command = sys.argv[1]
if command == '--help':
    print(help_str)
    exit(0)
else:
    try:
        dat_proc = action_dict[command]
    except KeyError:
        action_error = True
        print('Error - Invalid command provided. Valid commands are: ')
        print('\t'+', '.join(action_dict.keys())+'\n')
        exit(1)
#
# processing remaining commandline arguments
for i in range(2, len(sys.argv)):
    arg = sys.argv[i]
    if (re.match('^-', arg)):
        if (arg in flag_dict.keys()):
            flag_dict[arg] = True
            arg_dict['flag_list'].append(arg)
        else:
            print('Error - invalid flag: "'+arg+'" provided.')
            exit(1)
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
# checking files value
try:
    files = re.split(',', arg_dict['files'])
    files = [f for f in files if f]
    if (len(files) == 0):
        raise IndexError
except KeyError:
    file_error = True
    msg = 'Error - No input files provided. '
    msg += 'Final argument needs to be files=file1,file2,...,file_n\n'
    print(msg)
except IndexError:
    file_error = True
    msg = 'Error - file argument specified but no files listed. '
    msg += 'Check for spaces, valid format is: files=file1,file2,...,file_n\n'
    print(msg)
#
if file_error:
    exit(1)
#
# processing data fields
data_fields = apm.load_infile_list(files)
data_processors = [dat_proc(field) for field in data_fields]
print('')
#
for dat_proc in data_processors:
    dat_proc.set_args(arg_dict)
    if not dat_proc.validated:
        print('')
        continue
    #
    dat_proc.process()
    #
    if (flag_dict['-so']):
        # printing to screen only
        dat_proc.gen_output(delim='\t')
        dat_proc.print_data()
    elif (flag_dict['-sw']):
        # printing and then writting data
        dat_proc.gen_output(delim='\t')
        dat_proc.print_data()
        #
        dat_proc.gen_output(delim=',')
        dat_proc.write_data()
    else:
        # only writting data
        dat_proc.gen_output(delim=',')
        dat_proc.write_data()

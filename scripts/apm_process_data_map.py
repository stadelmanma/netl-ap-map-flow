########################################################################
#
# Description: This program reads the provided data file(s) and
#     generates output based on the arguments provided on the command line.
#     Output types are a full histogram, range histogram, log-binned histogram,
#     percentiles, data profiles along an axis and channelization data.
#     Flags are prefereed to preceed any other type of argument.
#     Action type is required next, followed by its parameters and
#     then input file(s) are provided.
#
# Written By: Matthew stadelman
# Date Written: 2015/10/01
# Last Modfied: 2016/03/07
#
########################################################################
#
# command line input parameters:
#     flags:
#           -so: "screen only output", instead of writing file(s) the data
#                  will be output to the screen, in csv files commas become tabs
#           -sw: "screen and write output", prints data to screen and
#                  ouptuts csv file(s)
#           -ow: "overwrite", allows program to overwrite an existsing file
#
#     actions:
#           eval_chans: "evaluate channelization", processes the data to
#                  the number and widths of channels present. (only really useful for flow data)
#           hist: "histogram", does a full min -> max val histogram of
#                  each input file
#           hist_range: "range histogram", does a histrogram for the
#                  provided percentile range, i.e. 10th - 90th percentile
#           hist_logscale: "logrithmic binned histogram" full range of data
#                  with special logic to handle negatives and values inbetween -1 and 1
#           profile: "flowrate profile", outputs a vector of cells
#                  in either the x or z direction straight from the flow file. location
#                  is based on percentage, i.e. 10% outputs a line at 10cm of a 100cm long field
#           pctle: "percentile", outputs one or more percentiles from the
#                  flow field
#
#     action-inputs:
#           eval_chans: thresh=### dir=(x or z)
#
#           hist: num_bins=### files=file1, file2, ..., file_n
#
#           hist_range: num_bins=### range=##, ## files=file1, file2, ..., file_n
#
#           hist_logscale: num_bins=### files=file1, file2, ..., file_n
#
#           profile: locs=##1, ##2, ##3, ..., ##n dir=(x or z) files=file1, file2, ..., file_n
#
#           pctle: perc=##1, ##2, ##3, ..., ##n files=file1, file2, ..., file_n
#
#
########################################################################
#
# sample inputs
#
# single file
#     python process_data_map.py action=hist num_bins=100 file=test_flow_file.csv
#
# multiple files
#     python process_data_map.py action=hist_range num_bins=100 range=10, 90 files=test_flow_file1.csv, test_flow_file2.csv
#
# multiple files and group output
#     python process_data_map.py -m action=profile locs=25, 50, 75 files=test_flow_file1.csv, test_flow_file2.csv
#
# single file with screen output
#     python process_data_map.py -so action=pctle perc=10, 5, 50, 75, 100 files=test_flow_file1.csv
#
# multiple files and group only output to screen and file
#     python process_data_map.py -mo -sw action=pctle perc=10, 5, 50, 75, 100 files=test_flow_file1.csv, test_flow_file2.csv
#
########################################################################
#
import re
import sys
import ApertureMapModelTools as apm
import ApertureMapModelTools.DataProcessing as apm_dp
#
########################################################################
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
    'delim': 'auto',
    'flag_list': []
}
# list holding DataField objects
data_fields = []
# dictionary holding all group data incase the -m flag is applied
group_data_dict = {}
#
# checking number of args and if > 1 processing them
if (len(sys.argv) <= 1):
    msg = 'Fatal Error: This program requires command line arguments'
    raise SystemExit(msg)
else:
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if (re.match('^-', arg)):
            if (arg in flag_dict.keys()):
                flag_dict[arg] = True
                arg_dict['flag_list'].append(arg)
            else:
                raise SystemExit('Error - invalid flag: "'+arg+'" provided.')
        else:
            # splitting arg into a key,value pair
            kv_pair = arg.split('=')
            if (len(kv_pair) < 2):
                msg = 'Error - invalid argument: "'+arg+'" provided. '
                msg += 'Required to have form of arg=values'
                raise SystemExit(msg)
            arg_dict[kv_pair[0]] = kv_pair[1]
print('')
print('')
#
# checking action values
action_error = False
file_error = False
try:
    action = arg_dict['action']
    if not action_dict.__contains__(action):
        raise IndexError
except KeyError:
    action_error = True
    print('Error - No action provided. One argument needs to be action=val')
except IndexError:
    action_error = True
    print('Error - Invalid action provided. Valid actions are: ')
    print('\t'+', '.join(action_dict.keys())+'\n')
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
    msg += 'One argument needs to be files=file1,file2,...,file_n'
    print(msg)
except IndexError:
    file_error = True
    msg = 'Error - file argument specified but no files listed. '
    msg += 'Check for spaces, valid format is: files=file1,file2,...,file_n'
    print(msg)
#
if ((action_error) or (file_error)):
    raise SystemExit
#
# processing data field data
data_fields = apm.load_infile_list(files, arg_dict['delim'])
print(data_fields)
#
dat_proc = action_dict[action]
data_processors = [dat_proc(field) for field in data_fields]
print(data_processors)
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

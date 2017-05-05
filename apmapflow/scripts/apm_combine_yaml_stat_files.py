r"""
Description: Recurses through a directory to find all YAML stat files
based on the supplied pattern and combine them into a single CSV file.
This script assumes all stat files have the same set of values.

For usage information run: ``apm_combine_yaml_stat_files -h``

| Written By: Matthew stadelman
| Date Written: 2017/02/12
| Last Modfied: 2017/04/23

|

"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import re
import os
import yaml
from apmapflow import _get_logger, set_main_logger_level
from apmapflow import files_from_directory

# setting up logger
set_main_logger_level('info')
logger = _get_logger('apmapflow.scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-f', '--force', action='store_true',
                    help='allows program to overwrite existing files')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-r', '--recursive', action='store_true',
                    help='Recurively search directory')

parser.add_argument('-p', '--pattern', default='.*yaml',
                    help='Regular expression pattern to select files')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs files to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('directory',
                    help='Directory to search for stat files')

parser.add_argument('outfile_name', nargs='?',
                    default='combined-fracture-stats.csv',
                    help='name to save CSV file under')


def main():
    r"""
    Driver program to handles combining YAML stat files into a single
    CSV file.
    """
    #
    args = parser.parse_args()
    #
    if args.verbose:
        set_main_logger_level('debug')
    #
    # checking ouput file path
    filename = os.path.join(args.output_dir, args.outfile_name)
    if (os.path.exists(filename) and not args.force):
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(filename))
    #
    # finding files
    files = files_from_directory(directory=args.directory,
                                 pattern=args.pattern,
                                 deep=args.recursive)
    if not files:
        msg = 'Pattern: {} found no files in searched directory: {}'
        logger.fatal(msg.format(args.pattern, args.directory))
        return
    #
    # printing files found
    logger.debug('Found the following files:')
    for f in files:
            logger.debug(' - %s', os.path.relpath(f, start=args.directory))
    #
    # ordering CSV keys using the same order in first YAML file
    key_order = determine_key_order(files[0])
    #
    # reading all YAML files
    data_list = []
    for stat_file in files:
        with open(stat_file, 'r') as f:
            data_list.append(yaml.load(f))
            data_list[-1]['_stat_file'] = stat_file
    #
    # outputing data
    output_stat_data(filename, key_order, data_list)


def determine_key_order(stat_file):
    r"""
    reads the first file to determine key order
    """
    #
    # reading data into a dictionary
    with open(stat_file, 'r') as f:
        data = yaml.load(f)
    #
    # re-opening file and reading into an array to match key order
    with open(stat_file, 'r') as f:
        content = f.read()
        content = content.split('\n')
    #
    # determining order and storing in dictionary
    key_order = {}
    for key in data.keys():
        for i, line in enumerate(content):
            if (re.match(key, line)):
                key_order[i] = key
                break
    #
    order = list(key_order.keys())
    order.sort()
    key_order = [key_order[k] for k in order]
    #
    return key_order


def output_stat_data(outfile, key_order, data_list):
    r"""
    Generates the combined stat output file. If all the units match
    then the unit will be moved up into the header otherwise it is output
    as an additional column
    """
    #
    # initializing content as a list of lists
    header = []
    content = [[] for data in data_list]
    #
    # looping over keys
    for key in key_order:
        header.append(key)
        #
        # checking units for all values of a key
        process_data_key(key, header, data_list)
        #
        for i, data in enumerate(data_list):
            content[i].extend(data[key])
    #
    # building final content string
    header.insert(0, 'STAT-FILE')
    header.insert(0, 'STAT-FILE-PATH')
    header = ','.join(header)
    for i, data in enumerate(data_list):
        content[i].insert(0, os.path.basename(data['_stat_file']))
        content[i].insert(0, os.path.dirname(data['_stat_file']))
        #
        content[i] = ','.join(content[i])
    #
    content.insert(0, header)
    content = '\n'.join(content)
    #
    # writing to file
    with open(outfile, 'w') as f:
        f.write(content)
    logger.info('Output file saved as: %s', os.path.relpath(outfile, os.getcwd()))


def process_data_key(key, header, data_list):
    r"""
    Checks the units for a data key and update lists in place. If all units
    match then it is moved up into the header. If not an additional column
    is output with the units
    """
    #
    all_match = True
    #
    # ensuring all entries are a list of [value, unit]
    for data in data_list:
        if not isinstance(data[key], list):
            data[key] = [data[key], '-']
    #
    # checking if all units match
    test_value = data_list[0][key][1].strip()
    for data in data_list:
        if data[key][1] != test_value.strip():
            all_match = False
        #
        # converting to strings
        data[key] = [str(data[key][0]), str(data[key][1])]
    #
    # adjusting lists according
    if not all_match:
        header.append(key + ' UNITS')
    else:
        header[-1] += ' [{}]'.format(test_value)
    #
    for data in data_list:
        if all_match:
            data[key] = [data[key][0]]

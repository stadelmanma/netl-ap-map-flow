#!/usr/bin/env python3
r"""
Script designed to take a CSV stat file and convert it to a yaml file
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import re
import yaml
from ApertureMapModelTools import _get_logger, set_main_logger_level

#
desc_str = r"""
Description: Generates a YAML formatted file from a CSV stat file.

Written By: Matthew stadelman
Date Written: 2017/03/03
Last Modfied: 2017/03/03
"""
# setting up logger
set_main_logger_level('info')
logger = _get_logger('ApertureMapModelTools.Scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-f', '--force', action='store_true',
                    help='allows program to overwrite an existing file')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs files to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('stat_file', type=os.path.realpath,
                    help='CSV stat file to process')

parser.add_argument('out_name', nargs='?', default=None,
                    help='alternate name to save YAML file under')


class StatFile(dict):
    r"""
    Parses and stores information from a simulation statisitics file. This
    class helps facilitate data mining of legacy simulation results. If
    available the YAML formatted file should be used instead as it can be
    directly parsed into a dictionary by the yaml module.
    """

    def __init__(self, infile):
        super().__init__()
        self.infile = infile
        self.map_file = ''
        self.pvt_file = ''
        self.parse_stat_file()

    def parse_stat_file(self, stat_file=None):
        r"""
        Parses either the supplied infile or the class's infile and
        uses the data to populate the data_dict.
        """
        self.infile = (stat_file if stat_file else self.infile)
        #
        with open(self.infile, 'r') as stat_file:
            content = stat_file.read()
            content_arr = content.split('\n')
            content_arr = [re.sub(r', *$', '', l).strip() for l in content_arr]
            content_arr = [re.sub(r'^#.*', '', l) for l in content_arr]
            content_arr = [l for l in content_arr if l]
        #
        # pulling out aperture map and pvt file key-value pairs
        if (re.match('APER', content_arr[0])):
            map_line = content_arr.pop(0).split(',')
            self.map_file = map_line[1].strip()
            self[map_line[0].replace(':', '').strip()] = self.map_file
        #
        if (re.match('PVT', content_arr[0])):
            pvt_line = content_arr.pop(0).split(',')
            self.pvt_file = pvt_line[1].strip()
            self[pvt_line[0].replace(':', '').strip()] = self.pvt_file
        #
        # stepping through pairs of lines to get key -> values
        for i in range(0, len(content_arr), 2):
            key_list = re.split(r',', content_arr[i])
            key_list = [k.strip() for k in key_list]
            val_list = re.split(r',', content_arr[i + 1])
            val_list = [float(v) for v in val_list]
            #
            for key, val in zip(key_list, val_list):
                m = re.search(r'\[(.*?)\]$', key)
                unit = (m.group(1) if m else '-')
                key = re.sub(r'\[.*?\]$', '', key).strip()
                self[key] = [val, unit]
        #
        # modifiying NX and NZ keys to just be an integer instead of list
        self['NX'] = self['NX'][0]
        self['NZ'] = self['NZ'][0]


def apm_convert_csv_stats_file():
    r"""
    Driver function to process the stat file.
    """
    # parsing commandline args
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')

    # checking path to prevent accidental overwriting
    if not args.out_name:
        args.out_name = os.path.basename(args.stat_file)
        args.out_name = os.path.splitext(args.out_name)[0] + '.yaml'
    filename = os.path.join(args.output_dir, args.out_name)
    #
    if os.path.exists(filename) and not args.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(filename))

    # loading data
    logger.info('parsing csv stat file')
    data = StatFile(args.stat_file)

    # saving data
    logger.info('saving yaml file as {}'.format(filename))
    with open(filename, 'w') as outfile:
        yaml.dump(dict(data), outfile)


if __name__ == '__main__':
    apm_convert_csv_stats_file()

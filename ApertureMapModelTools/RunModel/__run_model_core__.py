"""
This stores the basic classes and functions needed to the run model
#
Written By: Matthew Stadelman
Date Written: 2016/06/16
Last Modifed: 2016/06/16
#
"""
from collections import OrderedDict
import os
import re
from shlex import split as shlex_split
from subprocess import PIPE
from subprocess import Popen
from threading import Thread
from time import time
from scipy import inf as sp_inf
import ApertureMapModelTools as amt
from ApertureMapModelTools.__core__ import _get_logger, DataField

# module globals
logger = _get_logger(__name__)


class ArgInput(object):
    r"""
    Stores the value of a single input line of an INP file
    """

    def __init__(self, line):
        r"""
        Parses the line for the input key string and value
        """
        # inital values
        self.line_arr = []
        self.keyword = ''
        self.value_index = -1
        self.unit = ''
        self.comment_msg = ''
        self.commented_out = False
        #
        # removing semi-colon if whole line was commented out
        line = line.strip()
        mat = re.match(r'^;(.*)', line)
        if mat:
            line = mat.group(1)
            self.commented_out = True
        #
        # removing any comments after occurring the value
        mat = re.search(r';.*', line)
        if mat:
            self.comment_msg = line[mat.start():].strip()
            line = line[:mat.start()]
        #
        self.line = line
        self.value = line
        try:
            self.line_arr = shlex_split(line) or ['']
        except ValueError:
            # TODO: Add debug message here saying shlex failed
            self.line_arr = re.split(r'\s+', line)
            self.line_arr = [v for v in self.line_arr if v]
        self.keyword = re.match(r'[a-zA-z_-]*', self.line).group()
        #
        # if line has a colon the field after it will be used as the value
        # otherwise the whole line is considered the value
        if not re.search(r':(:?\s|$)', self.line):
            return
        #
        for ifld, field in enumerate(self.line_arr):
            if re.search(r':$', field):
                try:
                    self.value = self.line_arr[ifld+1]
                    self.value_index = ifld+1
                    if len(self.line_arr) > ifld + 2:
                        self.unit = self.line_arr[ifld+2]
                except IndexError:
                    self.value = 'NONE'
                    self.value_index = ifld+1
                    self.line_arr.append(self.value)
                    self.line = ' '.join(self.line_arr)

    def __str__(self):
        r"""
        Returns an input line repsentation of the object
        """
        #
        cmt = (';' if self.commented_out else '')
        line = '{}{} {}'.format(cmt, self.line, self.comment_msg)
        #
        return line

    def update_value(self, new_value, uncomment=True):
        r"""
        Updates the line with the new value and uncomments the line by default
        """
        #
        new_value = str(new_value)
        if uncomment:
            self.commented_out = False
        #
        if self.value_index > 0:
            self.line_arr[self.value_index] = new_value
        else:
            self.line_arr = re.split(r'\s', new_value)
            self.line_arr = [l for l in self.line_arr if l is not None]
        self.line = ' '.join(self.line_arr)
        self.value = new_value

    def output_line(self):
        return str(self)


class AsyncCommunicate(Thread):
    r"""
    Handles asyncronous usage of Popen.communicate()
    """
    def __init__(self, popen_obj):
        self.popen_obj = popen_obj
        super().__init__()

    def run(self):
        out, err = self.popen_obj.communicate()
        self.popen_obj.stdout_content, self.popen_obj.stderr_content = out, err
        self.popen_obj.end_time = time()
        #
        msg = '\n\t'.join([
            'Completed Simulation:',
            'input file: {}',
            'Time Required: {:0.3f} minutes',
            'Exit Code: {}'
        ])
        treq = (self.popen_obj.end_time - self.popen_obj.start_time)/60.0
        logger.info(msg.format(
            self.popen_obj.input_file.outfile_name,
            treq,
            self.popen_obj.returncode))


class InputFile(OrderedDict):
    r"""
    Stores the data for an input file and methods to generate and write
    an input file.
    """
    def __init__(self, infile, filename_formats=None):
        #
        super().__init__()
        self.filename_format_args = {}
        self.RAM_req = None
        self.outfile_name = 'lcl_model_param_file.inp'
        #
        if filename_formats is None:
            filename_formats = {}
        self.filename_formats = dict(filename_formats)
        #
        if isinstance(infile, InputFile):
            self.outfile_name = infile.outfile_name
        else:
            self.outfile_name = infile
        #
        self.parse_input_file(infile)
        #
        if 'input_file' not in filename_formats:
            self.filename_formats['input_file'] = self.outfile_name

    def __str__(self):
        r"""
        Writes an input file to the screen
        """
        #
        # updating filenames to match current args
        self._construct_file_names()
        #
        # builidng content from ArgInput class line attribute
        content = ''
        for arg_input in self.values():
            content += arg_input.output_line()+'\n'
        #
        return content

    def parse_input_file(self, infile):
        r"""
        Populates the InputFile instance with data from a file or copies
        an existing instance passed in.
        """
        #
        if isinstance(infile, self.__class__):
            content = str(infile)
            file_path = os.path.realpath(infile.outfile_name)
        else:
            file_path = os.path.realpath(infile)
            with open(infile, 'r') as fname:
                content = fname.read()
        self.infile = file_path
        #
        # parsing contents into input_file object
        content_arr = content.split('\n')
        for line in content_arr:
            line = re.sub(r'^(;+)\s+', r'\1', line)
            arg = ArgInput(line)
            self[arg.keyword] = ArgInput(line)
        #
        self.set_executable()

    def set_executable(self, exec_file=None):
        r"""
        Sets the path to the model executable, defaulting to the version compiled
        with the module.
        """
        self.executable = None
        #
        if exec_file is None and self.get('EXE-FILE', None):
            exec_file = self['EXE-FILE'].value
            if not os.path.isabs(exec_file):
                exec_file = os.path.join(os.path.dirname(self.infile), exec_file)
                exec_file = os.path.realpath(exec_file)
            if os.path.exists(exec_file):
                self.executable = exec_file
            else:
                logger.warning('The exe file specified does not exist: ' + exec_file)
        #
        if not self.executable:
            self.executable = os.path.join(amt.__path__[0], amt.DEFAULT_MODEL_NAME)

    def clone(self, file_formats=None):
        r"""
        Creates a new InputFile obj and then populates it with the current
        object's data. New ArgInput instances are created to prevent mutation.
        """
        if file_formats is None:
            file_formats = self.filename_formats
        #
        input_file = InputFile(self, filename_formats=file_formats)
        #
        return input_file

    def update_args(self, args):
        r"""
        Passes data to the ArgInput update_value function
        """
        for key in args:
            try:
                self[key].update_value(args[key])
            except KeyError:
                self.filename_format_args[key] = args[key]
        #
        # setting up new filenames
        self._construct_file_names()

    def get_uncommented_values(self):
        r"""
        Returns an OrderedDict of all args that are uncommented in
        the input file. An ArgInput object is stored under each keyword.
        """
        #
        args = [(key, arg) for key, arg in self.items() if not arg.commented_out]
        arg_dict = OrderedDict(args)
        #
        return arg_dict

    def _construct_file_names(self, make_dirs=False):
        r"""
        This updates the INP file's base outfile names to match current
        arguments and creates file paths if directories do not exist yet
        """
        #
        outfiles = {key: value for key, value in self.filename_formats.items()}
        format_args = {key: arg.value for key, arg in self.items()}
        format_args.update(self.filename_format_args)
        #
        for keyword in outfiles.keys():
            outfiles[keyword] = outfiles[keyword].format(**format_args)
        #
        # checking existance of directories and updating dict
        for fname in outfiles.keys():
            try:
                self[fname].update_value(outfiles[fname])
            except KeyError:
                if fname == 'input_file':
                    pass
                else:
                    msg = 'Error - outfile: {} not defined in initialization file'
                    print(msg.format(fname))
                    print('')
                    print('')
                    raise KeyError(fname)
            #
            if not make_dirs:
                continue
            #
            # using path split to prevent creating directories out of filenames
            dir_arr = list(os.path.split(outfiles[fname]))
            dir_arr[0] = '.' if not dir_arr[0] else dir_arr[0]
            path = os.path.join(*dir_arr[:-1])
            if not os.path.isdir(path):
                os.makedirs(path)
            #
        self.outfile_name = outfiles['input_file']

    def write_inp_file(self, alt_path=None):
        r"""
        Writes an input file to the outfile_name based on the current args
        """
        #
        # creating file directories and generating input file
        self.set_executable()
        self._construct_file_names(make_dirs=True)
        content = str(self)
        #
        file_name = self.outfile_name
        if alt_path:
            file_name = os.path.join(alt_path, file_name)
        #
        with open(file_name, 'w') as fname:
            fname.write(content)
        #
        logger.info('Input file saved as: '+file_name)


def estimate_req_RAM(input_maps, avail_RAM=sp_inf, suppress=False, **kwargs):
    r"""
    Reads in the input maps to estimate the RAM requirement of each map
    and to make sure the user has alloted enough space.
    """
    RAM_per_map = []
    error = False
    for fname in input_maps:
        #
        field = DataField(fname, **kwargs)
        tot_coef = (field.nx * field.nz)**2
        RAM = 0.00505193 * tot_coef**(0.72578813)
        RAM = RAM * 2**(-20)  # KB -> GB
        RAM_per_map.append(RAM)
        if RAM > avail_RAM:
            error = True
            fmt = 'Map {} requires {} GBs of RAM only {} GBs was alloted.'
            logger.fatal(fmt.format(fname, RAM, avail_RAM))
    if error and not suppress:
        raise EnvironmentError
    #
    return RAM_per_map


def run_model(input_file_obj, synchronous=False, show_stdout=False):
    r"""
    Runs the default version of the model compiled with the module or a version
    specified by the 'EXE-FILE' argument in the input file. If synhronous is True
    then the program will pause until the model finishes running.
    --
    input_file_obj - InputFile class object to be written and run by the model
    synchronous - Bool, default=False if True the script pauses until the model
        finishes executing
    show_stdout - Bool, default=False if True stdout and stderr are printed to
        the screen instead of being stored on the Popen object as stdout_content
        and stderr_content.

    Returns a Popen object
    """
    input_file_obj.write_inp_file()
    exe_file = os.path.abspath(input_file_obj.executable)
    logger.debug('Using executable located at: ' + exe_file)
    cmd = (exe_file, input_file_obj.outfile_name)
    #
    out = PIPE
    if show_stdout:
        out = None
    #
    # beginning simulation
    proc = Popen(cmd, stdout=out, stderr=out, universal_newlines=True)
    proc.input_file = input_file_obj
    proc.start_time = time()
    #
    msg = 'Beginning Simulation:\n\tInput File: {} \n\tProcess ID: {}'
    logger.info(msg.format(input_file_obj.outfile_name, proc.pid))
    #
    async_comm = AsyncCommunicate(proc)
    async_comm.start()
    #
    if synchronous:
        async_comm.join()
    #
    return proc

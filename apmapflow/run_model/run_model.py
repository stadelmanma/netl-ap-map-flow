"""
================================================================================
Run Model Core
================================================================================
| This stores the basic classes and functions needed to the run model

| Written By: Matthew Stadelman
| Date Written: 2016/06/16
| Last Modifed: 2017/04/05

"""
from collections import OrderedDict
import os
import re
from shlex import split as shlex_split
from subprocess import PIPE, Popen
from threading import Thread
from time import time
from scipy import inf as sp_inf
from .. import _get_logger, DataField

# module globals
logger = _get_logger(__name__)
DEFAULT_MODEL_PATH = os.path.split(os.path.split(__file__)[0])[0]
DEFAULT_MODEL_NAME = 'apm-lcl-model.exe'


class ArgInput(object):
    r"""
    Stores the value of a single input line of an INP file
    """

    def __init__(self, line):
        r"""
        Parses the line for the input key string and value
        """
        # inital values
        self._line_arr = []
        self._value_index = -1
        self.comment_msg = ''
        self.commented_out = False
        #
        self._parse_line(line)

    def __str__(self):
        r""" Allows direct printing of an ArgInput object """
        return self.line

    def _parse_line(self, line):
        r"""
        Handles parsing a line to build the ArgInput class
        """
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
            line = line[:mat.start()].strip()
        #
        # split the line into an array
        try:
            # posix=False to preserve double quotes and windows paths
            self._line_arr = shlex_split(line, posix=False)
        except ValueError as err:
            msg = 'shlex split failed on line {} with ValueError: {}'
            logger.debug(msg.format(line, err))
            self._line_arr = re.split(r'\s+', line)
            self._line_arr = [v.strip() for v in self._line_arr if v.strip()]
        #
        # ensure even a blank line produces a value array
        if not self._line_arr:
            self._line_arr = ['']
        #
        # if line has a colon the field after it will be used as the value
        # otherwise the whole line is considered the value
        if not re.search(r':(:?\s|$)', line):
            return
        #
        for ifld, field in enumerate(self._line_arr):
            if not re.search(r':$', field):
                continue
            #
            self._value_index = ifld + 1
            if len(self._line_arr) <= self._value_index:
                self._line_arr.append('')  # add index for value
            if len(self._line_arr) <= self._value_index + 1:
                self._line_arr.append('')  # add index for unit
            break

    @property
    def keyword(self):
        r""" Return first index of line arr """
        return re.sub(r':$', '', self._line_arr[0])

    @property
    def value(self):
        r""" Returns the value_index from the line arr """
        if self._value_index > -1:
            return self._line_arr[self._value_index]
        else:
            return ' '.join(self._line_arr)

    @value.setter
    def value(self, value):
        r"""
        Sets the value of an arg input, if a tuple is passed in the second
        value is used to determine if the value should be commented out or not
        """
        comment = False
        if (isinstance(value, (list, tuple))):
            comment = True if value[1] else False
            value = value[0]
        self.commented_out = comment
        #
        if self._value_index == -1:
            self._parse_line(str(value))
        else:
            self._line_arr[self._value_index] = str(value)

    @property
    def unit(self):
        r""" Returns the value_index from the line arr """
        if self._value_index > -1:
            return self._line_arr[self._value_index + 1]
        else:
            return None

    @unit.setter
    def unit(self, unit):
        self._line_arr[self._value_index + 1] = str(unit)

    @property
    def line(self):
        r""" Return a formatted line """
        cmt = ';' if self.commented_out else ''
        return cmt + ' '.join(self._line_arr) + self.comment_msg


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
            content += arg_input.line + '\n'
        #
        return content

    def __setitem__(self, key, value, new_param=False):
        r"""
        Subclassed to pass the value directly to the arg input
        """
        if new_param:
            super().__setitem__(key, value)
        else:
            try:
                self[key].value = value
            except KeyError:
                msg = "'{}' is not set, use .add_parameter method to set param"
                raise KeyError(msg.format(key))
        #
        if key == 'EXE-FILE':
            self.set_executable()

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
            self.add_parameter(line)
        #
        self.set_executable()

    def add_parameter(self, line):
        r"""
        Adds a parameter to the input file by parsing the line that would have
        been added to the input file if directly editing it.
        """
        line = re.sub(r'^(;+)\s+', r'\1', line)
        arg = ArgInput(line)
        self.__setitem__(arg.keyword, arg, new_param=True)

    def set_executable(self):
        r"""
        Sets the path to the model executable, defaulting to the version compiled
        with the module.
        """
        self.executable = None
        #
        if self.__contains__('EXE-FILE'):
            self['EXE-FILE'].commented_out = True
            exec_file = self['EXE-FILE'].value
            #
            if not os.path.isabs(exec_file):
                exec_file = os.path.join(os.path.dirname(self.infile), exec_file)
                exec_file = os.path.realpath(exec_file)
            if os.path.exists(exec_file):
                self.executable = exec_file
            else:
                logger.warning('The exe file specified does not exist: ' + exec_file)
        #
        if not self.executable:
            self.executable = os.path.join(DEFAULT_MODEL_PATH, DEFAULT_MODEL_NAME)

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

    def update(self, *args, **kwargs):
        r"""
        Updates the InputFile instance, passing any unknown keys to the
        filename_format_args dictionary instead of raising a KeyError like
        in __setitem__
        """
        if len(args) > 1:
            msg = 'update expected at most 1 arguments, got {:d}'
            raise TypeError(msg.format(len(args)))
        other = dict(*args, **kwargs)
        for key in other:
            try:
                self[key] = other[key]
            except KeyError:
                self.filename_format_args[key] = other[key]
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
        #
        return OrderedDict(args)

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
                self[fname] = outfiles[fname]
            except KeyError:
                if fname == 'input_file':
                    pass
                else:
                    msg = 'Outfile: {} not defined in initialization file'
                    logger.error(msg.format(fname))
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
        logger.info('Input file saved as: ' + file_name)


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

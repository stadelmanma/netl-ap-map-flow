"""
This stores the basic classes and functions needed to the run model
#
Written By: Matthew Stadelman
Date Written: 2016/06/16
Last Modifed: 2016/06/16
#
"""
import os
import re
from subprocess import PIPE
from subprocess import Popen
from threading import Thread
from ApertureMapModelTools.__core__ import DataField


class ArgInput(object):
    r"""
    Stores the value of a single input line of an INP file
    """

    def __init__(self, line):
        r"""
        Parses the line for the input key string and value
        """
        # inital values
        self.line = line
        self.line_arr = []
        self.keyword = ''
        self.value = line
        self.value_index = -1
        self.commented_out = False
        #
        # testing if line was commented out
        mat = re.match(r'^;(.*)', line)
        if mat:
            self.commented_out = True
            self.line = mat.group(1)
            self.value = mat.group(1)
        #
        line_arr = re.split(r'\s', self.line)
        line_arr = [l for l in line_arr if l]
        if not line_arr:
            line_arr = ['']
        self.line_arr = line_arr
        #
        mat = re.match(r'[; ]*([a-zA-z, -]*)', line_arr[0])
        self.keyword = mat.group(1)
        #
        # if line has a colon the field after it will be used as the value
        # otherwise the whole line is considered the value
        if re.search(r':(:?\s|$)', self.line):
            for ifld, field in enumerate(line_arr):
                if re.search(r':$', field):
                    try:
                        self.value = line_arr[ifld+1]
                        self.value_index = ifld+1
                    except IndexError:
                        self.value = 'NONE'
                        self.value_index = ifld+1
                        self.line_arr.append(self.value)
                        self.line = ' '.join(self.line_arr)

    def update_value(self, new_value, uncomment=True):
        r"""
        Updates the line with the new value and uncomments the line by default
        """
        #
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
        r"""
        Returns and input line repsentation of the object
        """
        #
        cmt = (';' if self.commented_out else '')
        line = cmt + self.line
        return line


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


class InputFile(dict):
    r"""
    Stores the data for an entire input file and methods to output one
    """
    def __init__(self, infile, filename_formats=None):
        self.filename_format_args = {}
        self.arg_order = []
        self.RAM_req = 0.0
        self.outfile_name = 'FRACTURE_INITIALIZATION.INP'
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

    def __repr__(self):
        r"""
        Writes an input file to the screen
        """
        #
        # updating filenames to match current args
        self._construct_file_names()
        #
        # builidng content from ArgInput class line attribute
        content = ''
        for key in self.arg_order:
            content += self[key].output_line()+'\n'
        #
        print('Input file would be saved as: '+self.outfile_name)
        #
        return content

    def parse_input_file(self, infile):
        r"""
        This function is used to create the first InputFile from which the
        rest will be copied from.
        """
        #
        if isinstance(infile, InputFile):
            content = infile.__repr__()
        else:
            with open(infile, 'r') as fname:
                content = fname.read()
        #
        # parsing contents into input_file object
        content_arr = content.split('\n')
        for line in content_arr:
            line = re.sub(r'^(;+)\s+', r'\1', line)
            arg = ArgInput(line)
            self.arg_order.append(arg.keyword)
            self[arg.keyword] = ArgInput(line)
        #
        try:
            msg = 'Using executable defined in inital file header: '
            print(msg + self['EXE-FILE'].value)
        except KeyError:
            msg = 'Fatal Error: '
            msg += 'No EXE-FILE specified in initialization file header.'
            msg += ' \n Exiting...'
            raise SystemExit(msg)

    def clone(self, file_formats=None):
        r"""
        Creates a new InputFile obj and then populates it with the current
        objects data, created nre references to prevent mutation.
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

    def _construct_file_names(self, make_dirs=False):
        r"""
        This updates the INP file's base outfile names to match current
        arguments and creates file paths if directories do not exist yet
        """
        #
        formats = self.filename_formats
        outfiles = {k: formats[k] for k in formats.keys()}
        #
        for arg in self.keys():
            pattern = re.compile('%'+arg+'%', flags=re.I)
            for fname in outfiles.keys():
                name = pattern.sub(self[arg].value, outfiles[fname])
                outfiles[fname] = name
        #
        for arg in self.filename_format_args.keys():
            pattern = re.compile('%'+arg+'%', flags=re.I)
            for fname in outfiles.keys():
                name = pattern.sub(self.filename_format_args[arg], outfiles[fname])
                outfiles[fname] = name
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
        # updating filenames to match current args
        self._construct_file_names(make_dirs=True)
        #
        # builidng content from ArgInput class line attribute
        content = ''
        for key in self.arg_order:
            content += self[key].output_line()+'\n'
        #
        file_name = self.outfile_name
        if alt_path:
            file_name = os.path.join(alt_path, file_name)
        #
        with open(file_name, 'w') as fname:
            fname.write(content)
        #
        print('Input file saved as: '+file_name)


def estimate_req_RAM(input_maps, avail_RAM, suppress=False, **kwargs):
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
            fmt = 'Fatal Error: '
            fmt += 'Map {} requires {} GBs of RAM only {} GBs was alloted.'
            print(fmt.format(fname, RAM, avail_RAM))
    if error and not suppress:
        raise EnvironmentError
    #
    return RAM_per_map


def run_model(input_file_obj, synchronous=False, show_stdout=False):
    r"""
    Runs an instance of the aperture map model specified in the 'EXE-FILE' argument
    in the input file. If synhronous is True then a while loop is used to hold the
    program until the model finishes running.
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
    exe_file = os.path.abspath(input_file_obj['EXE-FILE'].value)
    cmd = (exe_file, input_file_obj.outfile_name)
    #
    out = PIPE
    if show_stdout:
        out = None
    #
    proc = Popen(cmd, stdout=out, stderr=out, universal_newlines=True)
    async_comm = AsyncCommunicate(proc)
    async_comm.start()
    #
    if synchronous:
        async_comm.join()
    #
    return proc

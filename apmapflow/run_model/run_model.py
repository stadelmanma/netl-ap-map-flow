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
    Stores the value of a single input line of a LCL model input file. Instances
    of this class are stored in an InputFile instance's dict to manage each
    parameter.

    Parameters
    ----------
    line : string
        input line to parse.
    """

    def __init__(self, line):
        r"""
        Parses the line for the input key string and value.
        """
        # inital values
        self._line_arr = []
        self._value_index = -1
        self.comment_msg = ''
        self.commented_out = False
        #
        self._parse_line(line)

    def __str__(self):
        r"""
        Allows direct printing of an ArgInput object in output format.

        Examples
        --------
        >>> from apmapflow.run_model.run_model import ArgInput
        >>> param = ArgInput('test-param: 123 ft')
        >>> print(param)
        test-param: 123 ft

        See Also
        --------
        line
        """
        return self.line

    def _parse_line(self, line):
        r"""
        Parses a line to set attributes of the class instance.

        Parameters
        ----------
        line : string
            input line to parse.
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
        r"""
        Returns the keyword used to register this instance to an
        InputFile instance.
        """
        return re.sub(r':$', '', self._line_arr[0])

    @property
    def value(self):
        r"""
        Returns the value of the parameter stored by the class instance or sets
        the value of the instance. When setting the value if a tuple is passed
        instead of a scalar the first entry is used to set the value and
        the second's truth value sets the .commented out attribute of the instance.

        Parameters
        ----------
        value : scalar or tuple, optional
            When value is supplied the property is set

        Examples
        --------
        >>> from apmapflow.run_model.run_model import ArgInput
        >>> param = ArgInput('test-param: value-123')
        >>> param.value
        'value-123'
        >>> param.commented_out
        False
        >>> param.value = 'new-value'
        >>> param.value
        'new-value'
        >>> param.value = ('commented-out', True)
        >>> param.value
        'commented-out'
        >>> param.commented_out
        True
        """
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
        r"""
        Returns the given units a value is in or None, and can also be used
        to set the units of a value.

        Parameters
        ----------
        value : string, optional
            If supplied with a value then the units of a instance are set to it.

        Examples
        --------
        >>> from apmapflow.run_model.run_model import ArgInput
        >>> param = ArgInput('test-param: 123 ft')
        >>> param.unit
        'ft'
        >>> param.unit = 'mm'
        >>> param.unit
        'mm'
        """
        if self._value_index > -1:
            return self._line_arr[self._value_index + 1]
        else:
            return None

    @unit.setter
    def unit(self, unit):
        self._line_arr[self._value_index + 1] = str(unit)

    @property
    def line(self):
        r"""
        Return a formatted line meant for use when writing an InputFile isntance
        to disk. The line is prefixed by ``;`` if the parameter is supposed to
        be commented out.

        Examples
        --------
        >>> from apmapflow.run_model.run_model import ArgInput
        >>> param = ArgInput('test-param: 123 ft')
        >>> param.line
        'test-param: 123 ft'
        >>> param.commented_out = True
        >>> param.line
        ';test-param: 123 ft'

        See Also
        --------
        __str__
        """
        cmt = ';' if self.commented_out else ''
        return cmt + ' '.join(self._line_arr) + self.comment_msg


class AsyncCommunicate(Thread):
    r"""
    Allows an executable to be run in a separate thread so it does not block the
    main Python process.

    Parameters
    ----------
    popen_obj : Popen instance
        An instance containing a process that is currently executing.
    """
    def __init__(self, popen_obj):
        self.popen_obj = popen_obj
        super().__init__()

    def run(self):
        r"""
        Calls the communicate method on the Popen object registered to the class
        which blocks the thread until the process terminates. The total execution
        time, stdout and stderr of the process are passed back to the Popen object.
        """
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
    Used to read and write and manipulate LCL model input files. Each key-value
    pair stored on an instance of this class is actually an instance of the
    ArgInput class.

    Parameters
    ----------
    infile : string or InputFile instance
        Either is a filepath to read an input file from or an existing instance
        to copy.
    filename_formats : dictionary, optional
        A dictionary of filename formats which use Python format strings to
        dynamically generate names for the LCL model input and output files.

    Examples
    --------
    >>> from apmapflow.run_model import InputFile
    >>> inp_file = InputFile('input-file-path.inp')
    >>> fmts = {'VTK-FILE': '{apmap}-data.vtk'}
    >>> inp_file2 = InputFile(inp_file, filename_formats=fmts)

    Notes
    -----
    Any ``filename_formats`` defined will overwrite a parameter that was
    manually defined by directly setting the value.
    The ``__setitem__`` method of
    has been subclassed to transparently update the value attribute of the
    ArgInput instance for the corresponding key instead of the value itself.

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
        Writes out the input file as if it was being written to disk.
        """
        #
        # updating filenames to match current args
        self._construct_file_names()
        #
        # building content from ArgInput class line attribute
        content = ''
        for arg_input in self.values():
            content += arg_input.line + '\n'
        #
        return content

    def __setitem__(self, key, value, new_param=False):
        r"""
        Subclassed to pass the value directly to the value attribute of the
        ArgInput instance stored on the provided key unless the ``new_param``
        argument evaluates to ``True``.

        Parameters
        ----------
        key : string
            The key on the dictionary to update
        value : string or ArgInput instance
            The value to set the given key to
        new_param : boolean, optional
            If ``True`` then the value is not passed on to the ArgInput instance
            and the actual value on the InputFile instance is changed.

        Examples
        --------
        >>> from apmapflow.run_model import InputFile
        >>> inp_file = InputFile('input-file-path.inp')
        >>> inp_file['parameter'] = '123'
        >>> inp_file['parameter']
        <apmapflow.run_model.run_model.ArgInput object at #########>
        >>> inp_file['parameter'].value
        '123'
        >>> inp_file.__setitem__('parameter', 'param-value', new_param=True)
        >>> inp_file['parameter']
        'param-value'

        Notes
        -----
        If ``new_param`` is falsy and the key does not already exist a KeyError
        exeception is raised. The ``add_parameter`` method is the standard way to
        add new ArgInput instances to the InputFile instance

        See Also
        --------
        add_parameter
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

        Parameters
        ----------
        infile : string or InputFile instance
            Either is a filepath to read an input file from or an existing InputFile
            instance to copy.

        See Also
        --------
        InputFile
        clone
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
        Adds a parameter to the input file by parsing a line into an ArgInput
        class instance. The line supplied needs to be the same as if it were being
        manually typed into the actual input file.

        Parameters
        ----------
        line: string
            The provided line to parse and append to the InputFile instance.

        Examples
        --------
        >>> from apmapflow.run_model import InputFile
        >>> inp_file = InputFile('input-file-path.inp')
        >>> inp_file.add_parameter('NEW-PARAM: 1337 ;elite param')
        >>> inp_file['NEW-PARAM'].value
        '1337'

        Notes
        -----
        The InputFile inheirits from an OrderedDict so new parameters get added
        to the bottom of the file.
        """
        line = re.sub(r'^(;+)\s+', r'\1', line)
        arg = ArgInput(line)
        self.__setitem__(arg.keyword, arg, new_param=True)

    def set_executable(self):
        r"""
        Sets the path to an LCL model executable based on the ``EXE-FILE``
        parameter for the current InputFile instance. The path is checked relative
        to the InputFile instance's ``infile`` attribute. If no file is found
        a warning is issued and the executable path defaults to the version
        packaged with the module.

        Examples
        --------
        >>> from apmapflow.run_model import InputFile
        >>> inp_file = InputFile('./input-file-path.inp')
        >>> inp_file['EXE-FILE'] = 'my-locally-compiled-model.exe'
        >>> inp_file.set_executable()
        >>> inp_file.executable
        './my-locally-compiled-model.exe'


        Notes
        -----
        This method needs to be called if the ``EXE-FILE`` parameter is added,
        changed or removed.
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
        Creates a new InputFile instance populated with the current instance
        data. New ArgInput instances are created to prevent mutation.

        Parameters
        ----------
        filename_formats : dictionary, optional
            A dictionary of filename formats which use Python format strings to
            dynamically generate names for the LCL model input and output files.

        Returns
        -------
        input_file : apmapflow.run_model.InputFile
            The cloned input file instance

        Examples
        --------
        >>> from apmapflow.run_model import InputFile
        >>> fmts = {'VTK-FILE': '{apmap}-data.vtk'}
        >>> inp_file = InputFile('input-file-path.inp', filename_formats=fmts)
        >>> inp_file_copy = inp_file.clone()
        >>> inp_file_copy.filename_formats
        {'VTK-FILE': '{apmap}-data.vtk'}
        >>> inp_file_copy = inp_file.clone(file_formats={})
        >>> inp_file_copy.filename_formats
        {}

        Notes
        -----
        If the ``filename_formats`` parameter is omitted then the formats from
        the current instance are copied over.
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

        Parameters
        ----------
        \*args, \*\*kwargs : any valid dictionary initializer value set
            The resulting dictionary formed internally is used to update the
            instance

        Examples
        --------
        >>> from apmapflow.run_model import InputFile
        >>> fmts = {'VTK-FILE': '{apmap}-data.vtk'}
        >>> inp_file = InputFile('input-file-path.inp', filename_formats=fmts)
        >>> new_vals = {'OUTLET-SIDE': 'LEFT', 'apmap': 'fracture-1'}
        >>> inp_file.update(new_vals)
        >>> inp_file['OUTLET-SIDE'].value
        'LEFT'
        >>> inp_file.filename_format_args
        {'apmap': 'fracture-1'}

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
        Generate and return all uncommented parameters as an OrderedDict.

        Returns
        -------
        uncommented_values : OrderedDict
            An OrderedDict containing all ArgInput instances that were not
            commented out
        """
        #
        args = [(key, arg) for key, arg in self.items() if not arg.commented_out]
        #
        return OrderedDict(args)

    def _construct_file_names(self, make_dirs=False):
        r"""
        This updates the instance's outfile names to match current arguments.

        Parameters
        ----------
        make_dirs : boolean, optional
            If ``make_dirs`` evaluates to True then all parent directories for each
            output file are created as well.
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
        Writes an input file to the ``outfile_name`` attribute applying any
        formats defined based the current parameter values.

        Parameters
        ----------
        alt_path : string,
            An alternate path to preappend to the generated filename

        >>> from apmapflow.run_model import InputFile
        >>> inp_file = InputFile('input-file-path.inp')
        >>> inp_file.write_inp_file(alt_path='.')
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
    and to make sure the user has alloted enough space. The RAM estimation is a
    rough estimate based on a linear regression of several simulations of varying
    aperture map size.

    Parameters
    ----------
    input_maps : list
        A list of filepaths to read in
    avail_RAM : float, optional
        The maximum amount of RAM avilable on the system to be used. When exceeded
        an EnvironmentError is raised and an error message is generated.
    suppress : boolan, optional
        If it evaluates out to True and a map exceeds the ``avail_RAM`` the
        EnvironmentError is suppressed.
    **kwargs : optional
        Additional keyword args to pass on to the DataField initialization.

    Returns
    -------
    ram_values : list
        A list of floats with the corresponding RAM estimate for each of the maps
        passed in.

    Examples
    --------
    >>> from apmapflow.run_model import estimate_req_RAM
    >>> maps = ['fracture-1.txt', 'fracture-2.txt', 'fracture-3.txt']
    >>> estimate_req_RAM(maps, avail_RAM=8.0, suppress=True)
    [6.7342, 8.1023, 5.7833]

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
    Runs an instance of the LCL model defined by the InputFile instance passed in.

    Parameters
    ----------
    input_file_obj : apmapflow.run_model.InputFile
        An InputFile instance with the desired simulation parameters to run.
    synchronous : boolean, optional
        If True then run_model will block the main Python execution thread until
        the simulation is complete.
    show_stdout : boolean, optional
        If True then the stdout and stderr produced during the simulation run are
        printed to the screen instead of being stored on the Popen instance

    Returns
    -------
    model_popen_obj : Popen
        The Popen instance that contains the LCL model process, which may or man
        not be finished executing at upon return.

    Examples
    --------
    >>> from apmapflow.run_model import InputFile, run_model
    >>> inp_file = InputFile('input-file-path.inp')
    >>> proc = run_model(inp_file) # asynchronous run process isn't completed yet
    >>> proc.returncode
    None
    >>> # process is finished upon return when using synchronous=True
    >>> proc2 = run_model(inp_file, synchronous=True)
    >>> proc2.returncode
    0

    Notes
    -----
    This writes out the inputfile at the perscribed path, a pre-existing file
    will be overwritten.
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

"""
This stores the basic classes and functions needed for the bulk run code
#
Written By: Matthew Stadelman
Date Written: 2016/03/02
Last Modifed: 2016/03/02
#
"""
from itertools import product
import os
import re
from subprocess import Popen
from time import sleep
from ApertureMapModelTools.__core__ import DataField
#
########################################################################
#
# Class Definitions
#
class ArgInput:
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
        line_arr = [l for l in line_arr if l is not None]
        if len(line_arr) == 0:
            line_arr = ['']
        self.line_arr = line_arr
        #
        try:
            mat = re.match(r'[; ]*([a-zA-z, -]*)', line_arr[0])
            self.keyword = mat.group(1)
        except IndexError:
            print("Error - Bad line input provided - line: '", line, "'")
            raise SystemExit
        #
        # if line has a colon the field after it will be used as the value
        # otherwise the whole line is considered the value
        if re.search(r':\s', self.line):
            for ifld, field in enumerate(line_arr):
                if re.search(r':$', field):
                    try:
                        self.value = line_arr[ifld+1]
                        self.value_index = ifld+1
                    except IndexError:
                        self.value = "NONE"
                        self.value_index = ifld+1
    #
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
    #
    def output_line(self):
        r"""
        Returns and input line repsentation of the object
        """
        #
        cmt = (';' if self.commented_out else '')
        line = cmt + self.line
        return line
#
class InputFile:
    r"""
    Stores the data for an entire input file and methods to output one
    """
    def __init__(self, filename_formats=None):
        self.arg_dict = {}
        self.filename_format_args = {}
        self.arg_order = []
        self.RAM_req = 0.0
        self.outfile_name = 'FRACTURE_INITIALIZATION.INP'
        #
        if filename_formats is None:
            filename_formats = {}
        self.filename_formats = dict(filename_formats)
        if 'input_file' not in filename_formats:
            self.filename_formats['input_file'] = self.outfile_name
    #
    def __repr__(self):
        r"""
        Writes an input file to the screen
        """
        #
        # updating filenames to match current args
        self.construct_file_names()
        #
        # builidng content from ArgInput class line attribute
        content = ''
        for key in self.arg_order:
            content += self.arg_dict[key].output_line()+'\n'
        #
        print('Input file would be saved as: '+self.outfile_name)
        #
        return content
    #
    def clone(self, file_formats=None):
        r"""
        Creates a new InputFile obj and then populates it with the current
        objects data, created nre references to prevent mutation.
        """
        if file_formats is None:
            file_formats = self.filename_formats
        #
        input_file = InputFile(file_formats)
        input_file.arg_dict = {k : ArgInput(self.arg_dict[k].output_line()) for k in self.arg_dict.keys()}
        input_file.arg_order = [arg for arg in self.arg_order]
        #
        return input_file
    #
    def update_args(self, args):
        r"""
        Passes data to the ArgLine update_value function
        """
        for key in args:
            try:
                self.arg_dict[key].update_value(args[key])
            except KeyError:
                self.filename_format_args[key] = args[key]
    #
    def construct_file_names(self):
        r"""
        This updates the INP file's base outfile names to match current
        arguments and creates file paths if directories do not exist yet
        """
        #
        outfiles = {k : self.filename_formats[k] for k in self.filename_formats.keys()}
        #
        for arg in self.arg_dict.keys():
            pattern = re.compile('%'+arg+'%', flags=re.I)
            for file in outfiles.keys():
                outfiles[file] = pattern.sub(self.arg_dict[arg].value, outfiles[file])
        #
        for arg in self.filename_format_args.keys():
            pattern = re.compile('%'+arg+'%', flags=re.I)
            for file in outfiles.keys():
                outfiles[file] = pattern.sub(self.filename_format_args[arg], outfiles[file])
        #
        # checking existance of directories and updating arg_dict
        for file in outfiles.keys():
            try:
                self.arg_dict[file].update_value(outfiles[file])
            except KeyError:
                if file == 'input_file':
                    pass
                else:
                    print('Error - outfile: '+file+' not defined in initialization file')
                    print('')
                    print('')
                    raise KeyError(file)
            #
            i = outfiles[file].rfind('\\')
            path = outfiles[file][:i]
            if not os.path.isdir(path):
                syscmd = 'mkdir '+path
                os.system(syscmd)
        self.outfile_name = outfiles['input_file']
        #
    #
    def write_inp_file(self):
        r"""
        Writes an input file to the outfile_name based on the current args
        """
        #
        # updating filenames to match current args
        self.construct_file_names()
        #
        # builidng content from ArgInput class line attribute
        content = ''
        for key in self.arg_order:
            content += self.arg_dict[key].output_line()+'\n'
        #
        with open(self.outfile_name, 'w') as file:
            file.write(content)
        print('Input file saved as: '+self.outfile_name)
#
class dummy_process:
    r"""
    A palceholder used to initialize the processes list cleanly. Returns
    0 to simulate a successful completion and signal the start of a new process
    """
    def __init__(self):
        pass
    #
    def poll(self):
        r"""
        mimics a successful execution return code
        """
        return 0
#
########################################################################
#
# Function Definitions
#
def parse_input_file(infile):
    r"""
    This function is used to create the first InputFile from which the
    rest will be copied from.
    """
    #
    with open(infile, 'r') as file:
        content = file.read()
    #
    input_file = InputFile()
    #
    # parsing contents into input_file object
    content_arr = content.split('\n')
    for line in content_arr:
        line = re.sub(r'^(;+)\s+', r'\1', line)
        arg = ArgInput(line)
        input_file.arg_order.append(arg.keyword)
        input_file.arg_dict[arg.keyword] = ArgInput(line)
    #
    try:
        msg = 'Using executable defined in inital file header: '
        print(msg + input_file.arg_dict['EXE-FILE'].value)
    except KeyError:
        print('Fatal Error: No EXE-FILE specified in initialization file header. \n Exiting...')
        raise SystemExit
    #
    return input_file
#
def estimate_req_RAM(input_maps, avail_RAM, delim='auto'):
    r"""
    Reads in the input maps to estimate the RAM requirement of each map
    and to make sure the user has alloted enough space.
    """
    RAM_per_map = []
    error = False
    for file in input_maps:
        #
        field = DataField(file, delim=delim)
        tot_coef = (field.nx * field.nz)**2
        RAM = 0.00505193 * tot_coef**(0.72578813)
        RAM = RAM * 2**(-20) # KB -> GB
        RAM_per_map.append(RAM)
        if RAM > avail_RAM:
            error = True
            fmt = 'Fatal Error: Map {} requires {} GBs of RAM only {} GBs was alloted.'
            print(fmt.format(file, RAM, avail_RAM))
    if error:
        raise SystemExit
    #
    return RAM_per_map
#
def combine_run_args(input_map_args, init_input_file):
    r"""
    This function takes all of the args for each input map and then makes
    a list of InputFile objects to be run in parallel.
    """
    #
    # creating a combination of all arg lists for each input map
    input_file_list = []
    for map_args in input_map_args:
        keys, values = list(map_args['run_params'].keys()), list(map_args['run_params'].values())
        param_combs = list(product(*values))
        for comb in param_combs:
            #
            args = {k : v for k, v in zip(keys, comb)}
            args['APER-MAP'] = map_args['aperture_map']
            inp_file = init_input_file.clone(map_args['filename_formats'])
            inp_file.RAM_req = map_args['RAM_req']
            inp_file.update_args(args)
            input_file_list.append(inp_file)
    #
    return input_file_list
#
def start_simulations(input_file_list, num_CPUs, avail_RAM, start_delay=5):
    r"""
    Handles the stepping through all of the desired simulations
    """
    # initializing processes list with dummy processes
    processes = [dummy_process()]
    RAM_in_use = [0.0]
    sleep(start_delay)
    #
    # testing if processes have finished and starting additional ones if they have
    while input_file_list:
        check_processes(processes, RAM_in_use)
        start_run(processes, input_file_list, num_CPUs, avail_RAM, RAM_in_use)
#
def check_processes(processes, RAM_in_use, retest_delay=5):
    r"""
    This tests the processes list for any of them that have completed.
    A small delay is used to prevent an obscene amount of queries.
    """
    while True:
        for i, proc in enumerate(processes):
            if proc.poll() is not None:
                del processes[i]
                del RAM_in_use[i]
                return
        #
        sleep(retest_delay)
    #
    return
#
def start_run(processes, input_file_list, num_CPUs, avail_RAM, RAM_in_use, start_delay=5):
    r"""
    This starts additional simulations if there is enough free RAM.
    """
    #
    free_RAM = avail_RAM - sum(RAM_in_use)
    #
    while True:
        recheck = False
        #
        if len(processes) >= num_CPUs:
            break
        #
        for i, inp_file in enumerate(input_file_list):
            if inp_file.RAM_req <= free_RAM:
                inp_file = input_file_list.pop(i)
                inp_file.write_inp_file()
                cmd = '{0} {1}'.format(inp_file.arg_dict['EXE-FILE'].value,
                                       inp_file.outfile_name)
                #
                processes.append(Popen(cmd))
                RAM_in_use.append(inp_file.RAM_req)
                free_RAM = avail_RAM - sum(RAM_in_use)
                recheck = True
                sleep(start_delay)
                break
        #
        if not recheck:
            break
    #
    return
#
def process_input_tuples(input_tuples, global_params=None, global_name_format=None):
    r"""
    This program takes the tuples containing a list of aperture maps, run params and
    file formats and turns it into a standard format for teh bulk simulator.
    """
    #
    if global_params is None:
        global_params = {}
    if global_name_format is None:
        global_name_format = {}
    #
    sim_inputs = []
    for tup in input_tuples:
        for apm in tup[0]:
            args = dict()
            args['aperture_map'] = apm
            #
            # setting global run params first and then map specific params
            args['run_params'] = {k : list(global_params[k]) for k in global_params}
            for key in tup[1].keys():
                args['run_params'][key] = tup[1][key]
            #
            # setting global name format first and then map specific formats
            args['filename_formats'] = {k : global_name_format[k] for k in global_name_format}
            for key in tup[2].keys():
                args['filename_formats'][key] = tup[2][key]
            sim_inputs.append(dict(args))
    #
    return sim_inputs
#
def bulk_run(num_CPUs=4.0, sys_RAM=8.0, sim_inputs=None, delim='auto', init_infile='FRACTURE_INITIALIZATION.INP'):
    r"""
    This acts as the driver function for the entire bulk run of simulations.
    It handles calling the required functions in the required order.
    """
    #
    print('Beginning bulk run of aperture map simulations')
    #
    if sim_inputs is None:
        sim_inputs = []
    #
    avail_RAM = sys_RAM * 0.90
    input_maps = [args['aperture_map'] for args in sim_inputs]
    RAM_per_map = estimate_req_RAM(input_maps, avail_RAM, delim)
    #
    for i, RAM in enumerate(RAM_per_map):
        sim_inputs[i]['RAM_req'] = RAM
    #
    init_input_file = parse_input_file(init_infile)
    input_file_list = combine_run_args(sim_inputs, init_input_file)
    #
    print('')
    print('Total Number of simulations to perform: {:d}'.format(len(input_file_list)))
    print('')
    print('Simulations will begin in 20 seconds, hit ctrl+c to cancel at anytime.')
    sleep(20)
    #
    start_simulations(input_file_list, num_CPUs, avail_RAM, start_delay=5)
    print("")
    print("")
    #
    return
#
def dry_run(num_CPUs=4.0, sys_RAM=8.0, sim_inputs=None, delim='auto', init_infile='FRACTURE_INITIALIZATION.INP'):
    r"""
    This steps through the entire simulation creating directories and
    input files without actually starting any of the simulations.
    """
    #
    print('Beginning dry run of aperture map simulations on INP files output')
    print("Use function 'bulk_run' with same arguments to actually run models")
    #
    if sim_inputs is None:
        sim_inputs = []
    #
    avail_RAM = sys_RAM * 0.90
    input_maps = [args['aperture_map'] for args in sim_inputs]
    RAM_per_map = estimate_req_RAM(input_maps, avail_RAM, delim)
    #
    for i, RAM in enumerate(RAM_per_map):
        sim_inputs[i]['RAM_req'] = RAM
    #
    init_input_file = parse_input_file(init_infile)
    input_file_list = combine_run_args(sim_inputs, init_input_file)
    #
    print('')
    print('Total Number of simulations that would be performed: {:d}'.format(len(input_file_list)))
    #
    for file in input_file_list:
        file.write_inp_file()
        print(' Est. RAM reqired for this run: {:f}'.format(file.RAM_req))
        print('')
    #
    return


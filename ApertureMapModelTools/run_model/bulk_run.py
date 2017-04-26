"""
This stores BulkRun class used for running multiple concurrent simulations
#
Written By: Matthew Stadelman
Date Written: 2016/06/16
Last Modifed: 2016/06/16
#
"""
from collections import defaultdict
from itertools import product
import string
from time import sleep
from ..__core__ import _get_logger, set_main_logger_level
from .run_model import estimate_req_RAM, run_model

# module globals
logger = _get_logger(__name__)


class BulkRun(dict):
    r"""
    Stores properties and methods to handle mass runs of the model
    """
    def __init__(self, init_input_file, num_CPUs=2.0, sys_RAM=4.0, **kwargs):
        r"""
        Setting basic properties of the class.
        Useful kwargs include:
          delim: the expected delimiter in the aperture map files
          spawn_delay: minimum time between spawning of new processes
          retest_delay: time to wait between checking for completed processes
        """
        super().__init__()
        self.init_input_file = init_input_file.clone()
        self.num_CPUs = num_CPUs
        self.sys_RAM = sys_RAM
        self.avail_RAM = sys_RAM * 0.90
        self.input_file_list = []
        #
        # updating keys
        self.update(kwargs)
        #
        msg = 'Utilizing a maximum of {:d} cores, and {:f} gigabtyes of RAM'
        logger.debug(msg.format(int(self.num_CPUs), self.sys_RAM))

    def dry_run(self):
        r"""
        This steps through the entire simulation creating directories and
        input files without actually starting any of the simulations.
        """
        #
        orig_level = logger.getEffectiveLevel()
        set_main_logger_level('debug')
        #
        self._initialize_run()
        fmt = '{:d} simulations would be performed'
        logger.info(fmt.format(len(self.input_file_list)))
        #
        logger.info('Writing model input files to disk for inspection')
        for inp_file in self.input_file_list:
            inp_file.write_inp_file()
        #
        logger.info('Dry run has been completed.')
        logger.info('Use the start() method to begin simulations')
        set_main_logger_level(orig_level)

    def start(self):
        r"""
        Acts as the driver function for the entire bulk run of simulations.
        """
        #
        logger.info('Beginning bulk run of simulations')
        self._initialize_run()
        #
        # initializing processes list and starting loop
        processes = []
        RAM_in_use = []
        self._start_simulations(processes, RAM_in_use, **self)
        while self.input_file_list:
            self._check_processes(processes, RAM_in_use, **self)
            self._start_simulations(processes, RAM_in_use, **self)

    def generate_input_files(self,
                             default_params,
                             default_name_formats,
                             case_identifer='',
                             case_params=None,
                             append=False):
        r"""
        Generates the input file list based on the default parameters
        and case specific parameters. An InputFile instance is generated for
        each unique combination of model parameters.
        - If append is True, then the files are appended to the input_file_list
        instead of resetting it.
        """
        #
        #  processing unique identifier and setting up cases
        if case_identifer:
            case_params = case_params or {}
            #
            # pulling format keys out an combining them specifically
            keys = string.Formatter().parse(case_identifer)
            keys = [key[1] for key in keys if key[1]]
            params = {key: default_params[key] for key in keys}
            param_combs = self._combine_run_params(params)
            #
            # updating default params for each case
            keys = default_params.keys()
            run_cases = []
            for params in param_combs:
                #
                # updating default params to only use identifer values
                identifier = case_identifer.format(**params)
                params = {key: [val] for key, val in params.items()}
                params = {key: params.get(key, default_params[key]) for key in keys}
                #
                # updating params with the case specific params
                params.update(case_params.get(identifier, {}))
                run_cases.append(params)
        else:
            run_cases = [default_params]
        #
        # checking if file list needs reset or not
        if not append:
            self.input_file_list = []
        #
        # stepping through each case and combining args
        for params in run_cases:
            param_combs = self._combine_run_params(params)
            for comb in param_combs:
                #
                # generating new InputFile with parameter combination
                inp_file = self.init_input_file.clone(default_name_formats)
                inp_file.update(comb)
                self.input_file_list.append(inp_file)

    @staticmethod
    def _combine_run_params(run_params):
        r"""
        Generates all possible unique combinations from a set of
        parameter arrays.
        """
        #
        # processing run_params for falsy values, i.e. empty arrays or None
        run_params = {key: val for key, val in run_params.items() if val}
        #
        # creating a combination of all arg lists for each input map
        combinations = []
        for comb in product(*run_params.values()):
            #
            args = {key: val for key, val in zip(run_params.keys(), comb)}
            combinations.append(args)
        #
        return combinations

    def _initialize_run(self):
        r"""
        Handles initialization steps after generation of input files
        """
        logger.info('Assesing RAM requirements of each aperture map')
        #
        # storing InputFile instances by aperture map for easy RAM_req updates
        maps = defaultdict(list)
        for inp_file in self.input_file_list:
            maps[inp_file['APER-MAP'].value].append(inp_file)
        #
        # estimating the RAM requirement for each aperture map
        keys = list(maps.keys())
        RAM_per_map = estimate_req_RAM(keys, self.avail_RAM, **self)
        RAM_per_map = {key: value for key, value in zip(keys, RAM_per_map)}
        #
        # Updating the InputFile instances with their RAM requirement
        for key, value in RAM_per_map.items():
            msg = 'Estimated {:f}gb RAM reqired for map: {}'
            logger.info(msg.format(value, key))
            for inp_file in maps[key]:
                inp_file.RAM_req = value

    @staticmethod
    def _check_processes(processes, RAM_in_use, retest_delay=5, **kwargs):
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

    def _start_simulations(self, processes, RAM_in_use, spawn_delay=5, **kwargs):
        r"""
        This starts additional simulations if there is enough free RAM.
        """
        #
        free_RAM = self.avail_RAM - sum(RAM_in_use)
        #
        while True:
            recheck = False
            #
            if len(processes) >= self.num_CPUs:
                break
            #
            for i, inp_file in enumerate(self.input_file_list):
                if inp_file.RAM_req <= free_RAM:
                    inp_file = self.input_file_list.pop(i)
                    processes.append(run_model(inp_file))
                    #
                    RAM_in_use.append(inp_file.RAM_req)
                    free_RAM = self.avail_RAM - sum(RAM_in_use)
                    recheck = True
                    sleep(spawn_delay)
                    break
            #
            if not recheck:
                break

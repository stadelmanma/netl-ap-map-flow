"""
This stores BulkRun class used for running multiple concurrent simulations
#
Written By: Matthew Stadelman
Date Written: 2016/06/16
Last Modifed: 2016/06/16
#
"""
from itertools import product
import string
from time import sleep
from .__run_model_core__ import InputFile, estimate_req_RAM, run_model


class BulkRun(dict):
    r"""
    Stores properties and methods to handle mass runs of the model
    """
    def __init__(self, init_input_file, sim_inputs=None, num_CPUs=2.0, sys_RAM=4.0,
                 **kwargs):
        r"""
        Setting basic properties of the class.
        Useful kwargs include:
          delim: the expected delimiter in the aperture map files
          start_delay: time to delay starting of the overall run
          spawn_delay: minimum time between spawning of new processes
          retest_delay: time to wait between checking for completed processes
        """
        super().__init__()
        self.init_input_file = InputFile(init_input_file)
        self.sim_inputs = sim_inputs if sim_inputs else []
        self.num_CPUs = num_CPUs
        self.sys_RAM = sys_RAM
        self.avail_RAM = sys_RAM * 0.90
        self.input_file_list = []
        #
        # setting useful keys and removing two I don't want passed around
        [self.__setitem__(key, value) for key, value in kwargs.items()]

    def dry_run(self):
        r"""
        This steps through the entire simulation creating directories and
        input files without actually starting any of the simulations.
        """
        #
        print('Beginning dry run of aperture map simulations on INP files output')
        print('Use method "start" to actually run models')
        #
        input_maps = [args['aperture_map'] for args in self.sim_inputs]
        RAM_per_map = estimate_req_RAM(input_maps, self.avail_RAM, **self)
        #
        for i, RAM in enumerate(RAM_per_map):
            self.sim_inputs[i]['RAM_req'] = RAM
        #
        self._combine_run_args()
        #
        fmt = 'Total Number of simulations that would be performed: {:d}'
        print('')
        print(fmt.format(len(self.input_file_list)))
        #
        for inp_file in self.input_file_list:
            inp_file.write_inp_file()
            print(' Est. RAM reqired for this run: {:f}'.format(inp_file.RAM_req))
            print('')

    def start(self):
        r"""
        Handles properly passing any internal arguments to start bulk run
        """
        self._start_bulk_run(**self)

    def _start_bulk_run(self, start_delay=20.0, **kwargs):
        r"""
        This acts as the driver function for the entire bulk run of simulations.
        """
        class dummy:
            r"""
            Dummy class used to simulate a Popen object
            """
            def poll():
                return 0

        print('Beginning bulk run of aperture map simulations')
        #
        input_maps = [args['aperture_map'] for args in self.sim_inputs]
        RAM_per_map = estimate_req_RAM(input_maps, self.avail_RAM, **self)
        #
        for i, RAM in enumerate(RAM_per_map):
            self.sim_inputs[i]['RAM_req'] = RAM
        #
        self._combine_run_args()
        #
        fmt = 'Total Number of simulations to perform: {:d}'
        print('')
        print(fmt.format(len(self.input_file_list)))
        print('')
        fmt = 'Simulations will begin in {} seconds.'
        print(fmt.format(start_delay))
        sleep(start_delay)
        #
        # initializing processes list with dummy processes and beginning loop
        processes = [dummy]
        RAM_in_use = [0.0]
        while self.input_file_list:
            self._check_processes(processes, RAM_in_use, **self)
            self._start_simulations(processes, RAM_in_use, **self)
        #
        print('')
        print('')

    def generate_input_files(self,
                             default_params,
                             default_name_formats,
                             case_identifer='',
                             case_params=None):
        r"""
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
                # updating default params to only use identifer values
                print(params)
                identifier = case_identifer.format(**params)
                params = {key: [val] for key, val in params.items()}
                params = {key: params.get(key, default_params[key]) for key in keys}
                # updating params with the case specific params
                params.update(case_params.get(identifier, {}))
                run_cases.append(params)
        else:
            run_cases = [default_params]
        #
        # stepping through each case and combining args
        self.input_file_list = []
        for params in run_cases:
            param_combs = self._combine_run_params(params)
            for comb in param_combs:
                # generating new InputFile with parameter combination
                args = {key: val for key, val in zip(params.keys(), comb)}
                inp_file = self.init_input_file.clone(default_name_formats)
                inp_file.update_args(args)
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

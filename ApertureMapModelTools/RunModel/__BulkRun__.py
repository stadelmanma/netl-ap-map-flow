"""
This stores BulkRun class used for running mulitple concurrent simulations
#
Written By: Matthew Stadelman
Date Written: 2016/06/16
Last Modifed: 2016/06/16
#
"""
from itertools import product
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

    def process_input_tuples(self,
                             input_tuples,
                             default_params=None,
                             default_name_format=None):
        r"""
        This function takes the tuples containing a list of aperture maps, run params
        and file formats and turns it into a standard format for the bulk simulator.
        """
        #
        def_params = default_params
        def_name_format = default_name_format
        if default_params is None:
            def_params = {}
        if default_name_format is None:
            def_name_format = {}
        #
        sim_inputs = []
        for tup in input_tuples:
            for apm in tup[0]:
                args = dict()
                args['aperture_map'] = apm
                #
                # setting global run params first and then map specific params
                args['run_params'] = {k: list(def_params[k]) for k in def_params}
                for key in tup[1].keys():
                    args['run_params'][key] = tup[1][key]
                #
                # setting global name format first and then map specific formats
                formats = {k: def_name_format[k] for k in def_name_format}
                args['filename_formats'] = formats
                for key in tup[2].keys():
                    args['filename_formats'][key] = tup[2][key]
                sim_inputs.append(dict(args))
        #
        self.sim_inputs = sim_inputs

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

    def _combine_run_args(self):
        r"""
        This function takes all of the args for each input map and then makes
        a list of InputFile objects to be run in parallel.
        """
        #
        # creating a combination of all arg lists for each input map
        input_file_list = []
        for map_args in self.sim_inputs:
            keys = list(map_args['run_params'].keys())
            values = list(map_args['run_params'].values())
            param_combs = list(product(*values))
            for comb in param_combs:
                #
                args = {k: v for k, v in zip(keys, comb)}
                args['APER-MAP'] = map_args['aperture_map']
                inp_file = self.init_input_file.clone(map_args['filename_formats'])
                inp_file.RAM_req = map_args['RAM_req']
                inp_file.update_args(args)
                input_file_list.append(inp_file)
        #
        self.input_file_list = input_file_list

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

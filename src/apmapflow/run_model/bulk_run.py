"""
================================================================================
Bulk Run
================================================================================
| This stores BulkRun class used for running multiple concurrent simulations

| Written By: Matthew Stadelman
| Date Written: 2016/06/16
| Last Modifed: 2016/06/16

"""
from collections import defaultdict
from itertools import product
import string
from time import sleep
from .. import _get_logger, set_main_logger_level
from .run_model import estimate_req_RAM, run_model

# module globals
logger = _get_logger(__name__)


class BulkRun(dict):
    r"""
    Handles generating a collection of input files from the provided parameters
    and then running multiple instances of the LCL model concurrently to
    produce simulation data for each simulation parameter combination. A
    comprehensive example of this class and the associated script is avilable
    under the Usage Examples page.

    Parameters
    ----------
    init_input_file : apmapflow.run_model.InputFile
        An inital InputFile instance to define the static parameters of the bulk run.
    num_CPUs : int, optional
        The maximum number of CPUs to utilize
    sys_RAM : float, optional
        The maximum amount of RAM avilable for use.
    **kwargs : multiple
        * delim : string
            The expected delimiter in the aperture map files
        * spawn_delay : float
            The minimum time between spawning of new LCL instances in seconds
        * retest_delay : float
            The time to wait between checking for completed processes.
    Examples
    --------
    >>> from apmapflow import BulkRun, InputFile
    >>> inp_file = InputFile('./input-file-path.inp')
    >>> blk_run = BulkRun(inp_file, num_CPUs=16, sys_RAM=32.0, spawn_delay=10.0)

    Notes
    -----
    ``spawn_delay`` is useful to help ensure shared resources are not accessed
    at the same time.
    """
    def __init__(self, init_input_file, num_CPUs=2, sys_RAM=4.0, **kwargs):
        r"""
        Setting properties of the class.
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
        Steps through the entire simulation creating directories and
        input files without actually starting any of the simulations. This Allows
        the LCL input files to be inspected before actually starting the run.

        Examples
        --------
        >>> from apmapflow import BulkRun, InputFile
        >>> inp_file = InputFile('./input-file-path.inp')
        >>> blk_run = BulkRun(inp_file, num_CPUs=16, sys_RAM=32.0, spawn_delay=10.0)
        >>> blk_run.dry_run()

        See Also
        --------
        start
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
        Starts the bulk run, first creating the input files and then managing
        the multiple processes until all input files have been processed. The
        input file list must have already been generated prior to calling this
        method.

        See Also
        --------
        generate_input_files
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
        each unique combination of model parameters which is then written to disk
        to be run by the LCL model.

        Parameters
        ----------
        default_params : dictionary
            A dictionary containing lists of parameter values to use in the
            simulations.
        default_name_formats : dictionary
            A dictionary containing the infile and outfile name formats to use.
        case_identifer : string, optional
            A format string used to identify cases that need special parameters
        case_params : dictionary, optional
            A dictionary setup where each key is an evaluation of the case_identifer
            format string and the value is a dictionary containing lists of
            parameter values used to update the default params for that case.
        append : boolean, optional
            When ``True`` the BulkRun.input_file_list attribute is appended to
            instead of reset by this method.

        Notes
        -----
        The ``default_name_formats`` parameter is passed directly to the InputFile
        instance initialization and is no modified in any way. When using a
        ``case_identifier`` only the evaluations that matter need to be added to
        the ``case_params`` dictionary. Missing permuatations of the identifer are
        """
        #
        #  processing unique identifier and setting up cases
        if case_identifer:
            case_params = case_params or {}
            #
            # pulling format keys used in the identifer and combining them
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

        Parameters
        ----------
        run_params : dictionary
            A dictionary of parameter lists to combine together

        Returns
        -------
        parameter combinations : dictionary
            A list of dictionaries where each parameter only has a single value
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
        Assesses RAM requirements of each aperture map in use and registers the
        value with the InputFile instance. This RAM measurement is later used
        when determining if there is enough space available to begin a simulation.
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
        Checks the list of currently running processes for any that have completed
        removing and them from a list. If no processes have completed then the
        routine sleep for a specified amount of time before checking again.

        Parameters
        ----------
        processes : list of Popen instances
            The list of processes to curate.
        RAM_in_use : list of floats
            The list of maximum RAM each process is estimated to use.
        retest_delay : floats
            The time delay between testing for completed processes.
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
        This starts additional simulations if there is enough free RAM and
        avilable CPUs.

        Parameters
        ----------
        processes : list of Popen instances
            The list of processes to add any new simulations to.
        RAM_in_use : list of floats
            The list of maximum RAM to a new simulations requirement to.
        spawn_delay : floats
            The time delay between spawning of processes.
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

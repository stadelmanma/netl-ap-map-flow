=======================
Using the BulkRun Class
=======================
.. contents::


Intro
=====

The BulkRun class housed in the RunModel submodule allows the user to setup a test matrix where all combinations of a parameter set can be tested taking advantage of multiple cores on the computer. It relies heavily on the core methods and classes in the RunModel submodule and it is recommended that you go through the example  `running-the-flow-model <running-the-flow-model.rst>`_ before trying to use the script to be familiar with how the code will work behind the scenes. In addition to the core methods a special class is used to facilitate running a test matrix, `BulkRun <../ApertureMapModelTools/RunModel/__BulkRun__.py>`_. It is also recommended you view the source of the class to understand the flow of the program. Lastly the script `apm_bulk_run.py <../scripts/apm_bulk_run.py>`_ contains additional documentation and an example of setting up an entire bulk simulation.

The BulkRun Class
=================

This class wraps up the core functionality contained in the RunModel submodule into a format allowing easy processing of a test matrix in parallel. The Local Cubic Law (LCL) model itself is not parallelized however this limitation is overcome by calling the :code:`run_model` function in asynchronous mode and capturing the screen output produced. The class accepts many arguments during instantiation but the only required argument is an initial model input file to read or clone. This input file acts as a template for all of the subsequent runs and can either be a filename or an InputFile class object. The block below shows accepted arguments and defaults. 

.. code-block:: python

	bulk_run = BulkRun(input_file, # Used as a template to generate simulation runs from
	                   sim_inputs=None, # list of map parameter dictionaries
	                   num_CPUs=2.0, # Maximum number of CPUs to try and use
	                   sys_RAM=4.0, # Maximum amount of RAM to use
	                   **kwargs)

Useful kwargs and defaults are:
 * :code:`start_delay=20.0`: time to delay starting of the overall run
 * :code:`spawn_delay=5.0`: minimum time between spawning of new processes
 * :code:`retest_delay=5.0`: time to wait between checking for completed processes

It is more convenient to use the process_input_tuples method to generate :code:`sim_inputs` than to specify a valid argument yourself. When running the simulations the program considers the available RAM first and if there is enough space will then check for an open CPU to start a simulation on. The RAM requirement is an estimation based on the size of the map, the code will only seek to use 90% of the supplied value because the LCL model carries a small fraction of additional overhead which can not be predicted. The program is not guaranteed to run simulations sequentially with respect to the sim_inputs list. If the next map on the list is too large it will loop through the remaining maps to try and find one small enough to run. Time between tests and simulation spawns are controlled by the keywords listed above. The class has three public methods :code:`process_input_tuples`, :code:`dry_run` and :code:`start` these will be gone over next. 

The process_input_tuples Method
-------------------------------

The format the BulkRun class expects its parameters to be in is not the most convenient for a user to manually create, this function was designed to address that issue. The raw format the BulkRun class expects its inputs to be in is a dictionary specifying the aperture map file, a dictionary of parameters to vary and a dictionary storing filename formats. The structure is required to simplify code when running maps but is inherently inflexible in the presence of running many maps with mostly the same formats and parameters. 

The method accepts three arguments :code:`process_input_tuples(input_tuples, default_params=None, default_name_format=None)`. The fist argument is a list of tuples, the next two are dictionaries defining the default values for each map being run. 
BulkRun simulation settings have the following input resolution order:

 1. Hard-coded model defaults 
 2. Values in the initial input file used to instantiate the class 
 3. default_params/name_formats passed into process_input_tuples 
 4. map specific parameters/formats defined inside each tuple

The arguments to the method have the following general format:

.. code-block:: python

	default_params = {
		'param1 keyword': ['value1', 'value2'],
		'param2 keyword': ['value1', 'value2', 'value3']
	}

	default_formats = {
		'outfile keyword': 'path/filename_p1-%param1 keyword%-p2_%param2 keyword%'
	}

	input_tuples = [
		(['list of map files'], {group specific parameters}, {group specific filename formats}),
		(['file1'], {'param1 keyword': ['value1', 'value2', 'value3']}, {}),
		(['file2', 'file3'], {}, {}) #this one only uses default values defined.
	]

The first value in the tuple has to be a list even if it is a single map. Each entry in the param dictionaries also have to be lists, even for a single value. Additionally each parameter value needs to already be a string. This string is directly placed into the input file as well in the place of any :code:`%param keyword%` portions of the filename format. Strings are required to avoid the added complexity of attempting to format an arbitrary user defined value. If no group specific settings are required an empty dictionary, :code:`{}`, can be used. When the function is executed each tuple is processed and a map specific dictionary is generated for each map supplied in the `list of maps`. This allows you to easily create a large amount of simulation inputs without having to write duplicate definitions. :code:`default_params` and :code:`default_name_formats` are not required arguments and if omitted only group specific values will be used. 

The result of processing the input_tuples is stored on the class object in the attribute :code:`sim_inputs` which is a list. This is the same attribute where the value of the optional argument :code:`sim_inputs=None` is stored. **This function will overwrite the value of sim_inputs passed in during class instantiation.** You can add additional map dictionaries to the :code:`sim_inputs` attribute by appending them to the list after running this function. There are no limits to the number of parameters or parameter values to vary but keep in mind every parameter with more than one value increases the total number of simulations multiplicatively. Conflicting parameters will also need to be carefully managed, i.e. varying the boundary conditions. When using conflicting inputs you will need to have all conflicting lines commented out in the initial input file so only valid combinations are uncommented when the file is generated.

The dry_run and start Methods
-----------------------------

The :code:`dry_run()` method works exactly as its name implies, doing everything except actually starting simulations. It is best if you always run this method before calling the :code:`start()` method to ensure everything checks out. :code:`dry_run` will generate and write out all model input files used allowing you to ensure the input parameters and any name formatting is properly executed. Also, as the code runs it calculates and stores the estimated RAM required for each map. If a map is found to exceed the available RAM an EnvironmentError/OSError will be raised halting the program. The BulkRun code does not actually require each input file to have a unique name since the LCL model only references it during initialization. However, if you are overwriting an existing file ensure the spawn_delay is non-zero to avoid creating a race condition or an IO error from simultaneous access. Non-unique output filenames can also cause an IO error in the FORTRAN code if two simulations attempt to use the same file at the same time.

The :code:`start()` method simply begins the simulations. One slight difference from the :code:`dry_run()` method is that input files are only written when a simulation is about to be spawned, instead of writing them all out in the beginning. One additional caveat is that although the BulkRun code takes advantage of the threading and subprocess modules to run simulations asynchronously the BulkRun program itself runs synchronously. This can easily be overcome by the user through the multiprocessing module if desired.

Behind the Scenes
=================

Outside of the public methods used to generate inputs and start a simulation the class does a large portion of the work behind the scenes. Understanding the process can help prevent errors when defining the input ranges. Below is the general flow of the routine after :code:`start()` is called and then each step will be gone over in additional detail. 

 1. :code:`start()` - Begins the bulk run of simulations, passing args along
 2. :code:`_start_bulk_run(start_delay=20.0, **kwargs)` - Acts as a driver function 
 3. :code:`_combine_run_args()` - processes the map specific dictionaries
 4. :code:`_check_processes(processes, RAM_in_use, retest_delay=5, **kwargs)` - Tests to see if any of the simulations have completed
 5. :code:`_start_simulations(processes, RAM_in_use, spawn_delay=5, **kwargs)` - Tests to see if additional simulations are able to be started

The _start_bulk_run Method
--------------------------

:code:`_start_bulk_run` is the actual workhorse of the BulkRun class. The only thing :code:`start()` does is call this method passing the class itself in as a double starred argument. This layer of abstraction is used to prevent errors since the class itself is a subclassed dictionary and stores keywords as entries on itself. The only keyword :code:`_start_bulk_run` expects is :code:`start_delay` and it passes the rest off to other functions.

This method performs several tasks before starting the while loop used to manage simulations. Firstly it creates a list of input maps which are sent to the core method :code:`estimate_req_RAM` to ensure enough RAM was allocated. This RAM value is then stored on each map's dictionary so the routine can later check that value against the amount of free RAM when determining whether to start a new simulation.

If the run has enough RAM then :code:`_combine_run_args()` is called to generate the final list of InputFile objects to start simulations with. After generation, a while loop is entered that runs :code:`_check_processes` and :code:`_start_simulations` until all InputFile objects have been run through the model. 

The _combine_run_args Method
----------------------------

:code:`_combine_run_args` handles generation of the InputFile objects used to run the LCL model from Python. All of the parameters contained in a single map dictionary are combined using the :code:`product` function from the :code:`itertools` module in the standard library. :code:`product` accepts 'N' lists with at least 1 element and returns a list of tuples containing all possible combinations of arguments. 

:code:`_combine_run_args` then loops over all of the tuples returned. First, mapping them back into a dictionary and then calling the :code:`clone` method of the InputFile object generated during the BulkRun class instantiation. The filename formats defined in the map dictionary are passed in during cloning. The cloned version of the input file is then updated with the current combination of args by calling it's :code:`update_args` method passing in the re-mapped args dictionary. The new InputFile object is then appended to the :code:`input_file_list` attribute of the BulkRun class and the process is repeated until all tuples and map dictionaries have been processed. The final list of input files is used to drive the while loop in :code:`_start_bulk_run` 

Running each InputFile
----------------------

The while loop in :code:`_start_bulk_run` operates as long as there is a value left in the :code:`input_file_list` attribute of the BulkRun class object. A non-empty array is treated as a 'True' or 'Truthy' value in Python. The while loop executes two function continuously with a slight delay defined by the user inputs :code:`retest_delay` and :code:`spawn_delay`. The functions it executes are :code:`_check_processes` and :code:`_start_simulations`. 

The _check_processes Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`_check_processes` is a very simple method that essentially pauses the routine until a simulation is completed. It looks through the currently running processes which are stored as an array of Popen objects returned by the core method :code:`run_model`. Popen objects are part of the subprocess module in the standard library, they have a method :code:`poll()` which returns :code:`None` if the process has not yet completed. Regardless of the return code when the :code:`poll()` returns a value the corresponding process is removed and its RAM requirement is released before returning from the method. If no processes have completed then the function waits the amount of time specified by :code:`retest_delay` argument and checks again.

The _start_simulations Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`_start_simulations` handles the spawning of new processes if certain criteria are met. This method is only entered if :code:`_check_processes` registers that a simulation has completed. It first calculates the amount of free RAM based on the maximum requirement of currently running simulations. Then it enters a while loop to test spawn criteria, if either fail the method returns and while loop tests its own exit criteria and calls :code:`_check_processes` otherwise. Return conditions are if the number of current processes is greater than or equal to the number of CPUs or if all maps require more RAM than available.

If both criteria are satisfied then a new process is spawned and its RAM requirement and the process are stored. The method then waits for the duration specified by the :code:`spawn_delay` argument and checks to see if it can spawn any additional processes by retesting the same exit criteria defined above. This method and the one above work in conjunction to process all of the InputFiles generated by :code:`_combine_run_args`.
	

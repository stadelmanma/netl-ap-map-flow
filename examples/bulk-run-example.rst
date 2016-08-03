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

Useful kwargs include:
 * :code:`start_delay`: time to delay starting of the overall run
 * :code:`spawn_delay`: minimum time between spawning of new processes
 * :code:`retest_delay`: time to wait between checking for completed processes

It is more convenient to use the process_input_tuples method to generate :code:`sim_inputs` than to specify a valid argument yourself. When running the simulations the program considers the available RAM first and if there is enough space will then check for an open CPU to start a simulation on. The RAM requirement is an estimation based on the size of the map, the code will only seek to use 90% of the supplied value because the LCL model carries a small fraction of additional overhead which can not be predicted. The program is not guaranteed to run simulations sequentially with respect to the sim_inputs list. If the next map on the list is too large it will loop through the remaining maps to try and find one small enough to run. Time between tests and simulation spawns are controlled by the keywords listed above. The class has three public methods :code:`process_input_tuples`, :code:`dry_run` and :code:`start` these will be gone over next. 

The process_input_tuples Method
-------------------------------

The format the BulkRun class expects its parameters to be in is not the most convenient for a user to manually create, this function was designed to address that issue. The raw format the BulkRun class expects its inputs to be in is a dictionary specifying the aperture map file, a dictionary of parameters to vary and a dictionary storing filename formats. The structure is required to simplify code when running maps but is inherently inflexible in the presence of running many maps with mostly the same formats and parameters. 

The method accepts three arguments :code:`process_input_tuples(input_tuples, default_params=None, default_name_format=None)`. The fist argument is a list of tuples, the next two are dictionaries defining the default values for each map being run. 
BulkRun simulation settings have the follow input resolution order:

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
		([list of map files], {group specific parameters}, {group specific filename formats}),
		([list of map files], {'param1 keyword': ['value1', 'value2', 'value3']}, {}),
		([list of map files], {}, {}) #this one only uses default values defined.
	]

The first value in the tuple has to be a list even if it is a single map. Each entry in the param dictionaries also have to be lists even for a single value. Additionally each parameter value needs to already be a string. This string is directly placed into the input file as well in the place of any %param keyword% portions of the filename format. Strings are required to avoid the added complexity of attempting to format an arbitrary user defined value. If no group specific settings are required an empty dictionary, :code:`{}`, can be used. When the function is executed each tuple is processed and a map specific dictionary is generated for each map supplied in the `list of maps`. This allows you to easily create a large amount of simulation inputs without having to write duplicate definitions. default_params and default_name_formats are not required arguments and if omitted only group specific values will be used. The result of processing the input_tuples is stored on the class object in the attribute :code:`.sim_inputs` which is a list. This is the same attribute where the value of the optional argument :code:`sim_inputs=None` is stored. **This function will overwrite the value of sim_inputs passed in during class instantiation.** You can add additional map dictionaries to the :code:`.sim_inputs` attribute by appending them to the list. There are no limits to the number of parameters or parameter values to vary but keep in mind every parameter with more than one value increases the total number of simulations multiplicatively. Conflicting parameters will also need to be carefully managed,i.e. varying the boundary conditions, by having all conflicting lines commented out in the initial input file so only valid combinations become uncommented when the program generates each simulation input file.

The dry_run and start Methods
-----------------------------

The :code:`dry_run()` method works exactly as its name implies, doing everything except actually starting simulations. It is best if you always run this method before calling the :code:`start()` method to ensure everything checks out. This method will generate and write out all model input files used allowing you to ensure the input parameters and any name formatting is properly executed. Also, as the code runs it calculates and stores the estimated RAM required for each map. If a map is found to exceed the available RAM an Error will be raised and the program will exit. The BulkRun code does not actually require each input file to have a unique name since the LCL model only references it during initialization. However, if you are overwriting an existing file ensure the spawn_delay is non-zero to avoid creating a race condition. Non-unique output filenames can also cause an IO error in the FORTRAN code if two simulations attempt to use the same file at the same time.

The :code:`start()` method simply begins the simulations. One slight difference from the :code:`dry_run()` method is that input files are only written when a simulation is about to be spawned, instead of writing them all out in the beginning. One additional caveat is that although the BulkRun code takes advantage of the threading and subprocess modules to run simulations asynchronously the BulkRun program itself runs synchronously. This can easily be overcome by the user through the multiprocessing module if desired.







	

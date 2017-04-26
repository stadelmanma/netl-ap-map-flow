=======================
Using the BulkRun Class
=======================
.. contents::


Intro
=====

The BulkRun class housed in the run_model submodule allows the user to setup a test matrix where all combinations of a parameter set can be tested taking advantage of multiple cores on the computer. It relies heavily on the core methods and classes in the run_model submodule and it is recommended that you go through the example  `running-the-flow-model <running-the-flow-model.rst>`_ before trying to use the script to be familiar with how the code will work behind the scenes. In addition to the core methods a special class is used to facilitate running a test matrix, `BulkRun <../ApertureMapModelTools/run_model/bulk_run.py>`_. It is also recommended you view the source of the class to understand the flow of the program. Lastly the script `apm-bulk-run.py <../scripts/apm-bulk-run.py>`_ can be used to process a bulk run for you by supplying one or more YAML formatted input files to it. An example YAML file is displayed below.

Using the apm-bulk-run.py Script
================================

Usage
-----

The usage of the apm-bulk-run.py script is very simple because it only needs to parse YAML parameter files using the yaml module which can be installed through pip via the :code:`pyyaml` package. YAML files are read in as series of nested dictionaries which the BulkRun module is designed to use. Any number of YAML files can be read in at once however, the first YAML file sets up the BulkRun class and the others are only used to generate additional InputFile instances from.

Full usage information can be obtained by using the :code:`-h` flag, :code:`./apm-bulk-run.py -h`. More runtim information can be obtained by adding the ``-v`` flag

By default the script does a dry run, the :code:`--start` flag needs to be added to actually begin simulations. Below is an example of calling the script

.. code-block:: shell

    # doing a dry run first
    apm-bulk-run.py -v group-run1.yml group-run2.yml

    # actually running the simulations
    apm-bulk-run.py -v --start group-run1.yml group-run2.yml


Example YAML File
-----------------

.. code-block:: yaml

    # initial model input file to use as a template
    initial_input_file: './model-input-file.inp'

    # keyword arguments passed onto the BulkRun __init__ method
    bulk_run_keyword_args:
        spawn_delay: 1.0  # delay in starting new individual simulations
        retest_delay: 5.0  # time to wait between checks for completed sims
        sys_RAM: 8.0 # amount of RAM allocated for simulations
        num_CPUs: 4 # number of CPUs allocated for simulations

    # filename formats to use when building filenames based on input parameters
    default_file_formats:
        APER-MAP: './maps/{stage}_ApertureMapRB{map_type}.txt'
        SUMMARY-FILE: './{sim-type}/{stage}/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min-log.txt'
        STAT-FILE: './{sim-type}/{stage}/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min-stat.csv'
        APER-FILE: './{sim-type}/{stage}/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min-aper.csv'
        FLOW-FILE: './{sim-type}/{stage}/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min-flow.csv'
        PRESS-FILE: './{sim-type}/{stage}/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min-press.csv'
        VTK-FILE: './{sim-type}/{stage}/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min.vtk'
        input_file: './{sim-type}/inp_files/{stage}{map_type}-inlet_rate_{INLET-RATE}ml_min.inp'


    # parameter lists to combine when generating individual InputFile
    default_run_parameters:
        OUTLET-PRESS: [0.00]
        INLET-RATE: [1.00, 2.00, 4.00, 6.00, 10.00]
        MAP: [1]
        ROUGHNESS: [0.0]
        OUTPUT-UNITS: ['PA,M,M^3/SEC']
        VOXEL: [26.8]
        # these are not model inputs and only affect filename formatting
        stage:
        - 'IS-6_0'
        - 'IS-6_1'
        - 'IS-6_2'
        - 'IS-6_3'
        - 'IS-6_4'
        sim-type: ['const-flow']
        map_type: ['-full', '-10avg']

    # format string used to identify specific cases based on parameters
    case_identifier: '{map_type}'

    # parameters for each desired identifier value
    case_parameters:
        -10avg:
        MAP: ['10']
        OUTLET-PRESS:   # empty key-value pair used to unset a run parmeter

Block or Flow styling may by used based on the user preference, in this example flow style sequences were chosen for parameters and block style for mapppings because of readability and compactness. The block style list for the :code:`stage` keyword was done to denote significance.

Although all values are converted to strings before use in the InputFile instances, values in the YAML file are not *required* to be quoted. However, adding quotes can be safer when a value contains characters that may confuse/error the YAML parser such as the value for :code:`OUTPUT-UNITS`. Without quotes it would be interpreted as a list instead of a string, producing an invalid entry in the InputFile. Additional higher level YAML functionality can likely be used but has not been tested. The basic syntax is used here for a clear and concise example.

The BulkRun Class
=================

This class wraps up the core functionality contained in the run_model submodule into a format allowing easy processing of a test matrix in parallel. The Local Cubic Law (LCL) model itself is not parallelized however this limitation is overcome by calling the :code:`run_model` function in asynchronous mode and capturing the screen output produced. The class accepts many arguments during instantiation but the only required argument is an initial InputFile instance to clone. The InputFile instance acts as a template for all subsequent runs. All arguments that are being varied need to be present even if they only contain a dummy value. The block below shows accepted arguments and defaults.

.. code-block:: python

    bulk_run = BulkRun(input_file, # Used as a template to generate simulation runs from
                       num_CPUs=2.0, # Maximum number of CPUs to try and use
                       sys_RAM=4.0, # Maximum amount of RAM to use
                       **kwargs)

Useful kwargs and defaults are:
 * :code:`spawn_delay=5.0`: minimum time between spawning of new processes
 * :code:`retest_delay=5.0`: time to wait between checking for completed processes

You can manually supply a list of InputFile instances to the class by assigning them to the :code:`bulk_run.input_file_list` attribute. However the better method is to use the :code:`bulk_run.generate_input_files` method which will be explained in detail next. When running the simulations the program considers the available RAM first and then if there is enough space it will check for an open CPU to utiltize. The RAM requirement of an aperture map is an approximation based on a linear relationship with the total number of grid blocks. The code will only seek to use 90% of the supplied value because the LCL model occasionally carries a small fraction of additional overhead which can not be predicted. The order that simulations are run may differ from the order of the input_file_list. This is because the code will loop through the list looking for a map small enough to fit the available RAM when a CPU is available. Time between tests and simulation spawns are controlled by the keywords listed above. The BulkRun class has three public methods :code:`generate_input_files`, :code:`dry_run` and :code:`start` these will be gone over next.

The generate_input_files Method
-------------------------------

The BulkRun class was designed to easily setup and process a large test matrix with no hard limit on the size of the parameter space. For this reason manually creating InputFile instances is not practical and where the :code:`generate_input_files` method comes into play.

The method requries 2 arguments and accepts up to five arguments:
:code:`bulk_run.generate_input_files(default_params, default_name_formats, case_identifer='', case_params=None, append=False)`. The first argument, :code:`default_params`, is a dictionary of parameter lists which define the primary parameter space for the bulk run. The second argument, :code:`default_name_formats`, is a dictionary that defines the filename formats. Filename formats are `Python format strings <https://docs.python.org/3.5/library/string.html#format-string-syntax>`_ used to dynamically generate file names based on the current parameters stored on the InputFile instance. The third argument, :code:`case_identifier`, is also a format string, however it is used to identify a "case" which is a given combination of parameters that you define as significant. A specfic set of parameters can be defined for each case encountered, for example defining your identifier as :code:`{map_type}` and changing the averaging factor for a group of maps based on case parameters. The fourth argument :code:`case_params` is a dictionary of parameter dictionaries where the primary key is the desired case_identifer when formatted with the given parameters. Not all combinations of an identifier need to be defined, only those you want to specify additional parameters for. The final argument :code:`append` tells the routine whether or not to create a new :code:`input_file_list` or append to the existing list on the bulk_run instance.

Individual InputFile instances have the following parameter resolution order:

 1. Hard-coded model defaults
 2. Values in the initial input file used to instantiate the class
 3. default_params/name_formats passed into generate_input_files
 4. case specific parameters defined in the case_params dictionary

The arguments to the method have the following general format:

.. code-block:: python

    default_params = {
        'param1 keyword': ['p1_value1', 'p1_value2'],
        'param2 keyword': ['p2_value1', 'p2_value2', 'p2_value3'],
        'param3 keyword': ['p3_value1', 'p3_value2', 'p3_value3', 'p3_value4']
    }

    default_name_formats = {
        'outfile keyword': './path/filename_p1-{param1 keyword}-p2_{param2 keyword}'
    }

    my_case_identifier = '{param3 keyword}-{param2 keyword}'

    my_case_params = {
        'p3_value1-p2_value2': {'param1 keyword': ['p1_value1', 'p1_value3', 'p1_value3']},
        'p3_value3-p2_value3': {'param4 keyword': ['p4_value1', 'p4_value2'], 'param2 keyword': None}
    }

    bulk_run.generate_input_files(default_params,
                      default_name_formats,
                      case_identifer=my_case_identifier,
                      case_params=my_case_params,
                      append=False)

Each parameter range needs to be a list even if it is a single value. Additionally it is recommend that each value already be a string. The value is directly placed into the input file as well in the place of any :code:`{param keyword}` portions of the filename format. Standard Python formatting syntax is used when generating a filename, so non-string arguments may be passed in and will be formatted as defined. Something like :code:`{OUTLET-PRESS:0.4f}` is perfectly valid in the filename formats to handle a floating point number, however no formatting is applied when the value is output to the InputFile object. To disable a parameter defined in the defaults :code:`None` can passed in the case specific parameters for the desired keyword, as shown above with `param2 keyword`. You can manually add InputFile instances to the :code:`bulk_run.input_file_list` before or after running this method, just set the :code:`append` keyword as appropriate. There are no limits to the number of parameters or parameter values to vary but keep in mind every parameter with more than one value increases the total number of simulations multiplicatively. Conflicting parameters will also need to be carefully managed, i.e. varying the boundary conditions through case specific dictionaries. It can safer to comment out all inputs that will be varied and give them a dummy value such as :code:`AUTO` because they will be uncommented when updated with a value. However, ensure the desired and consistent units are being used because they can not be changed from the inital value defined in the InputFile instance.

The dry_run and start Methods
-----------------------------

The :code:`dry_run()` method works exactly as its name implies, doing everything except actually starting simulations. It is best if you always run this method before calling the :code:`start()` method to ensure everything checks out. :code:`dry_run` will generate and write out all model input files used allowing you to ensure the input parameters and any name formatting is properly executed. Also, as the code runs it calculates and stores the estimated RAM required for each map. If a map is found to exceed the available RAM an :code:`EnvironmentError/OSError` will be raised halting the program. The BulkRun code does not actually require each input file to have a unique name since the LCL model only references it during initialization. However, if you are overwriting an existing file ensure the spawn_delay is non-zero to avoid creating a race condition or an IO error from simultaneous access. Non-unique output filenames can also cause an IO error in the FORTRAN code if two simulations attempt to access the same file at the same time.

The :code:`start()` method simply begins the simulations. One slight difference from the :code:`dry_run()` method is that input files are only written when a simulation is about to be spawned, instead of writing them all out in the beginning. One additional caveat is that although the BulkRun code takes advantage of the threading and subprocess modules to run simulations asynchronously the BulkRun program itself runs synchronously.

Behind the Scenes
=================

Outside of the public methods used to generate inputs and start a simulation the class does a large portion of the work behind the scenes. Understanding the process can help prevent errors when defining the input ranges. Below is the general flow of the routine after :code:`start()` is called.

 1. :code:`_initialize_run()` - processes the aperture maps to estimate requried RAM
 2. :code:`_check_processes(processes, RAM_in_use, retest_delay=5, **kwargs)` - Tests to see if any of the simulations have completed
 3. :code:`_start_simulations(processes, RAM_in_use, spawn_delay=5, **kwargs)` - Tests to see if additional simulations are able to be started

Running each InputFile
----------------------

The while loop in :code:`bulk_run.start` operates as long as there is a value left in the :code:`bulk_run.input_file_list`. A non-empty array is treated as a 'True' or 'Truthy' value in Python. The while loop executes two function continuously with a slight delay defined by the user inputs :code:`retest_delay` and :code:`spawn_delay`. The functions it executes are :code:`_check_processes` and :code:`_start_simulations`.

The _check_processes Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`_check_processes` is a very simple method that essentially pauses the routine until a simulation is completed. It looks through the currently running processes which are stored as an array of :code:`Popen` objects returned by the core method :code:`run_model`. Popen objects are part of the subprocess module in the standard library, they have a method :code:`poll()` which returns :code:`None` if the process has not yet completed. Regardless of the return code when the :code:`poll()` returns a value the corresponding process is removed and its RAM requirement is released before returning from the method. If no processes have completed then the function waits the amount of time specified by :code:`retest_delay` and checks again.

The _start_simulations Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`_start_simulations` handles the spawning of new processes if certain criteria are met. This method is only entered if :code:`_check_processes` registers that a simulation has completed. It first calculates the amount of free RAM based on the maximum requirement of currently running simulations. Then it enters a while loop to test spawn criteria, if either fail the method returns and the while loop tests its own exit criteria or calls :code:`_check_processes` otherwise. Return conditions are if the number of current processes is greater than or equal to the number of CPUs or if all maps require more RAM than available.

If both criteria are satisfied then a new process is spawned and its RAM requirement and the process are stored. The method then waits for the duration specified by the :code:`spawn_delay` argument and checks to see if it can spawn any additional processes by retesting the same exit criteria defined above. This method and the one above work in conjunction to process all of the InputFiles stored in :code:`bulk_run.input_file_list`.

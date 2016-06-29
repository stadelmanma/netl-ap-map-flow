======================
Running the Flow Model
======================

.. contents::


Intro
=====

The Local Cubic Law flow model by default is named :code:`APM-MODEL.EXE`, the added extension doesn't affect UNIX systems and allows Windows to recognize it as executable. There are two methods to run the model, first is directly on the command line specifying your input parameters file and the second is using Python scripting through the :code:`RunModel` sub-module in :code:`ApertureMapModelTools`. The model requires two or three input files and generates several output files. The model works in the X-Z plane where +Z is vertical and +X is to the right. The Y direction is the aperture variation and the model assumes a planar mid surface. This implies that the fracture is symmetric with respect to the X-Z plane. If you envision a spiral bound notebook with the bottom left corner as the origin. The Z-axis follows the metal spiral upward, positive X is the direction moving away from the spiral. Y is the thickness of the notebook.


The Input Parameters File
=========================

A template of the input parameters file can be found in `here <APM-MODEL-INPUT-FILE-TEMPLATE.INP>`_. An additional sample of the input file is located in `test/fixtures <../test/fixtures/TEST_INIT.INP>`_. Editing the input file in `test/fixtures` is not recommended because it will interfere with testing of the model and module. The input file is parsed by a special routine in the model that treats semicolons :code:`;` as comments and one or more spaces as delimiters. A value enclosed in double quotations will have any internal spaces ignored. ApertureMapModelTools also reads the input files when needed and for consistency it is recommended you append a colon :code:`:` onto the end of keywords. Nearly all of the input parameters have default values and they are defined in `APM_SUBROUTINES.F <../source/APM_SUBROUTINES.F>`_ in the first subroutine :code:`INITIALIZE_RUN`

**Important Notes**
 * There must be at least one space separating keyword and value.
 * The names of the keywords can not be changed without editing the model's source code.
 * Physical quantities must have a unit associated with them.
 * The LCL model's unit conversion is independent of the Python module and considerably more restrictive.

At the top of the input file there should be a commented line reading :code:`;EXE-FILE: APM-MODEL.EXE`, or the name of the model executable if it is changed. This is a key input to the RunModel sub-module when it is used.

The input file can be broken down into four main components:

File Paths
----------

This is where the path of input and output files are defined. If the line :code:`OVERWRITE EXISTING FILES` is uncommented any existing files sharing the same name will be replaced. If the line is commented out or absent an error will be raised if a pre-existing file with the same name is encountered. Input file delimiters can be commas, spaces or tabs. The model assumes the aperture map data being input is stored as a 2-D grid with the first value being the origin and the last value being the top right corner. The data maps output by the model also follow this convention. The output files accept the extension the user provides however the expected extensions are noted below.

**Notes:**
 * Any output files that are omitted will be saved using a default name in the current working directory.
 * Output files are opened relative to where the executable is being run. For this reason it makes things much simpler to either use absolute paths or have the executable in the same directory as the input file.

Input Files
~~~~~~~~~~~
  - :code:`PVT-PATH:` File storing state data for liquids or gases, required if :code:`FLUID-TYPE: GAS` is present. Only iso-thermal data is accepted.
  - :code:`APER-MAP PATH:` File that stores the aperture map data.

Output Files
~~~~~~~~~~~~
  - :code:`SUMMARY-PATH:` Logs the information printed to the screen (.txt expected)
  - :code:`STAT-FILE PATH:` Stores statistics calculated and certain simulation parameters (.csv expected)
  - :code:`APER-FILE PATH:` Stores a copy of the input aperture map that is converted to the desired output units and has any applied roughness factored in (.csv expected)
  - :code:`FLOW-FILE PATH:` Used as the root name for the three flow files output: X-component, Z-component and magnitude. The files have -X, -Z, -M suffixes appended to the root name before the extension.  (.csv expected)
  - :code:`PRESS-FILE PATH:` Stores a pressure distribution map of the fracture(.csv expected)
  - :code:`VTK-FILE PATH:` A legacy formatted input file for Paraview which combines all of the former input files and includes several other data maps. (.vtk expected)

Boundary Conditions
-------------------

Defines the boundary conditions for the model, only :code:`OUTLET-PRESS` or :code:`OUTLET-RATE` should be specified. If both keywords are defined unexpected results can occur.

 * :code:`FRAC-PRESS:` value unit ;The pressure value to use at the inlet
 * :code:`OUTLET-PRESS:` value unit ;The pressure value to use at the outlet
 * :code:`OUTLET-RATE:`  value unit ;The flow rate to apply at the outlet.
 * :code:`OUTFLOW-SIDE:` [LEFT, RIGHT, TOP, BOTTOM] sets the outlet side, the inlet is assumed to be the opposite face. i.e. top is outlet, bottom is inlet

Model Properties
----------------

Sets various fluid and model properties.

 * :code:`FLUID-TYPE:` [LIQUID or GAS] ;determines the type of simulation to run. Gas simulations require full set of isothermal PVT data
 * :code:`FLUID-DENSITY:` value unit ;Density of liquid to use in Reynolds number calculation
 * :code:`FLUID-VISCOSITY:` value unit ;Viscosity of liquid, if this is supplied PVT data can be neglected for liquid simulations.
 * :code:`MAXIMUM MAP DIMENSION:` value ;Maximum number of blocks along either axis. Values close to actual axis size slightly improve runtime memory conservation relative to much larger values.
 * :code:`STD-TEMP:` value unit ;User defined standard (or surface) temperature used in gas simulations
 * :code:`STD-PRESS:` value unit ;User defined standard (or surface) pressure used in gas simulations

Other Parameters
----------------

Sets other important miscellaneous runtime parameters.

 * :code:`MAP AVERAGING FACTOR:` value ;The number of voxels required to span an edge of a grid block along the X or Z direction. Grid blocks are assumed square in the X-Z plane.
 * :code:`VOXEL SIZE:` value unit ;Specifies the voxel to meter conversion factor
 * :code:`ROUGHNESS REDUCTION:` value ;**The value is in voxels** Amount to symmetrically bring the front and back fracture surfaces together by.
 * :code:`CALCULATE PERCENTILES:` value1,value2,value3 ;A comma separated list of percentiles to calculate of various quantities during runtime. Commenting this line out tells it to not calculate them at all
 * :code:`HIGH-MASK:` value ;**The value is in voxels** All data values in the aperture map above this value will be reduced to this value.
 * :code:`LOW-MASK:` value ;**The value is in voxels** All data values in the aperture map below this value will be raised to this value

This tells the model what units you want the data output in. Commenting out or omitting this line will output everything in SI (pascals, meters and meters^3/second)

 * :code:`OUTPUT-UNITS:` pressure unit, distance unit, flow rate unit

Blank Input File
----------------

This can be copy and pasted into a blank text document to quickly create a new input file. The inputs you want to use will need to be uncommented. Remember to keep at least one space between the keyword and the value. Some default values have been left in place.

.. code-block:: Scheme

	;
	;EXE-FILE: APM-MODEL.EXE
	;
	;
	; FILE PATHS AND NAMES
	;PVT-PATH:
	;APER-MAP PATH:
	;SUMMARY-PATH:
	;STAT-FILE PATH:
	;APER-FILE PATH:
	;FLOW-FILE PATH:
	;PRESS-FILE PATH:
	;VTK-FILE PATH:
	;OVERWRITE EXISTING FILES
	;
	; BOUNDARY CONDITIONS
	;FRAC-PRESS:
	;OUTLET-PRESS:
	;OUTLET-RATE:
	;OUTFLOW-SIDE:
	;
	; MODEL PROPERTIES
	;FLUID-TYPE: LIQUID
	;FLUID-DENSITY:
	;FLUID-VISCOSITY:
	;MAXIMUM MAP DIMENSION: 1500
	;STD-TEMP:      273.15 K
	;STD-PRESS:       1.00 ATM
	;
	; OTHER PARAMETERS
	;MAP AVERAGING FACTOR: 1.0
	;VOXEL SIZE:
	;ROUGHNESS REDUCTION: 0.00 ;IN VOXELS
	;CALCULATE PERCENTILES: 0,1,5,10,15,20,25,30,40,50,60,70,75,80,85,90,95,99,100
	;HIGH-MASK:
	;LOW-MASK:
	;
	; DEFINE SPECIFIC OUTPUT UNITS TO USE
	; REQUIRED FIELD ORDER: PRESSURE,DISTANCE,FLOW RATE
	;OUTPUT-UNITS:

Running the Model
=================

Before we actually run the model it will be helpful to have a place to store the output files generated. We need to define an input file to use with the model and in this case we will take advantage of many of the predefined defaults. You will also need to have already built the model from source, there are instructions in the main `README <../README.rst#setting-up-the-modeling-package>`_. Running the following code in a terminal while in the top level directory (AP_MAP_FLOW) will get things started.

.. code-block:: bash

    mkdir model-testing
    mv APM-MODEL.EXE model-testing
    cd model-testing
    touch model-input-params.inp

Open model-input-params.inp with your favorite text editor and copy and paste the following block. Notice most of the inputs are **not** preceded by a semicolon here like they were in the blank file above.

.. code-block:: Scheme

	;
	;EXE-FILE: APM-MODEL.EXE
	;
	; FILE PATHS AND NAMES
	APER-MAP PATH: ../examples/AVERAGED-FRACTURES/Fracture1ApertureMap-10avg.txt
	;SUMMARY-PATH:
	;STAT-FILE PATH:
	;APER-FILE PATH:
	;FLOW-FILE PATH:
	;PRESS-FILE PATH:
	;VTK-FILE PATH:
	;OVERWRITE EXISTING FILES
	;
	; BOUNDARY CONDITIONS
	FRAC-PRESS: 100 PA
	OUTLET-PRESS: 0 PA
	OUTFLOW-SIDE: TOP
	;
	; MODEL PROPERTIES
	FLUID-TYPE: LIQUID
	FLUID-DENSITY: 1000.0 KG/M^3
	FLUID-VISCOSITY: 0.890 CP
	;
	; OTHER PARAMETERS
	MAP AVERAGING FACTOR: 10.0
	VOXEL SIZE: 25.0 MICRONS
	CALCULATE PERCENTILES: 0,1,5,10,15,20,25,30,40,50,60,70,75,80,85,90,95,99,100
	;
	; DEFINE SPECIFIC OUTPUT UNITS TO USE
	; REQUIRED FIELD ORDER: PRESSURE,DISTANCE,FLOW RATE
	OUTPUT-UNITS: PA,MM,MM^3/SEC

Running Directly
----------------

With the above steps complete running the model is as simple as this:

.. code-block:: bash

    ./APM-MODEL.EXE model-input-params.inp

You will notice that several output files have been generated in the current directory. They are saved under the default names because we did not specified our own filenames in the input file. You can view the VTK file in paraview and the other CSV data maps in your viewer of choice. The STATS file is not a data map but being saved as a CSV file allows for quick calculations in excel or similar software. If we try to run the model a second time as before line again you will see an error is generated and execution is terminated. This is because the line :code:`;OVERWRITE EXISTING FILES` is preceded by a semicolon meaning it is commented out and by default existing files will not be overwritten.

Running by Python Script
------------------------

The RunModel sub-module allows for much more power and convenience when running the model or multiple instances of the model. The sub-module also houses the BulkRun class which can be used to automate and parallelize the running of many simulations. Usage of the BulkRun class is outside the scope of this example file and is gone over in depth in `this file <bulk-run-example.rst>`_.

The core components of the `RunModule <../ApertureMapModelTools/RunModel/__run_model_core__.py>`_ consist of one class used to manipulate an input parameters files and two functions to handle running of the model. Code snippets below will demonstrate their functionality. The examples here assume you are working with the files created at the beginning of the section `Running the Model`_. The first step is to run the Python interpreter and import them from the parent module.

.. code-block:: python

    import os
    import sys
    from ApertureMapModelTools.RunModel import InputFile
    from ApertureMapModelTools.RunModel import estimate_req_RAM, run_model

    # this allows examples to work for those who didn't add the module to site-packages
    sys.path.insert(0, os.path.abspath(os.pardir)))

The InputFile Class
~~~~~~~~~~~~~~~~~~~
The InputFile class is used to read, write and manipulate an input parameters file. It provides an easy to use interface for updating parameters and can dynamically generate filenames based on those input parameters. One caveat is you can not easily add in new parameters that weren't in the original input file used to instantiate the class. Therefore, when using this class it is best to use a template file that has all of the parameters present and unneeded ones commented out.

Notes:
 * The keywords of the input file class are the first characters occurring before *any* spaces on a line. The keyword for parameter :code:`FLOW-FILE PATH: path/to/filename` is :code:`FLOW-FILE`
 * Currently the original units are preserved and can not easily be updated.

Argument - Type - Description
 * infile - String or InputFile - The path to the file you want to read or the variable storing the InputFile object you want to recycle.
 * filename_formats - dict - A dict containing filename formats to use when creating outfile names and the save name of the input file itself based on current params. If none are provided then the original names read in will be used.

.. code-block:: python

    # Creating an InputFile object
    inp_file = InputFile('model-input-params.inp', filename_formats=None)

    # updating arguments can be done two ways
    #inp_file['param_keyword'].update_value(value, uncomment=True)
    #inp_file.update_args(dict_of_param_values)

    # Directly updating the viscosity value
    inp_file['FLUID-VISCOSITY'].update_value('1.00')

    # updating a set of parameters
    new_param_values = {
        'OVERWRITE': 'OVERWRITE FILES',
        'FRAC-PRESS': '150.00'
    }
    inp_file.update_args(new_param_values)

    # printing the InputFile object shows the changes
    print(inp_file)


You will notice that the line :code:`OVERWRITE EXISTING FILES` has been changed and uncommented. The class by default will uncomment any parameter that is updated. Parameters are stored in their own class called `ArgInput <../ApertureMapModelTools/RunModel/__run_model_core__.py>`_ which can be directly manipulated by accessing the keyword of an InputFile object like so, :code:`inp_file['FLUID-VISCOSITY']`. Earlier when we updated the value of the viscosity directly we called the method :code:`.update_value` which is a method of the ArgInput class not the InputFile class. Directly manipulating the ArgInput objects stored by the InputFile class allows you to perform more complex operations on a parameter such as commenting it out or updating the units.

.. code-block:: python

    # commenting out percentile parameter
    inp_file['CALCULATE'].commented_out = True

    # changing the unit and value of density
    val_index = inp_file['FLUID-DENSITY'].value_index
    inp_file['FLUID-DENSITY'].line_arr[val_index+1] = 'LB/FT^3'
    inp_file['FLUID-DENSITY'].update_value('62.42796')

    #
    print(inp_file)

In addition to updating arguments you can also apply a set of filename formats to the InputFile class. These allow the filenames to be dynamically created based on the argument parameters present. Using the :code:`update_args` method of the InputFile class you can also add a special set of args not used as parameters but instead to format filenames. Any args passed into :code:`update_args` that aren't already a parameter are added to the :code:`filename_format_args` attribute of the class.

.. code-block:: python

    # setting the formats dict up
    # Format replacements are recognized by %KEYWORD% in the filename
    name_formats = {
        'SUMMARY-PATH': '%MAP%-SUMMARY-VISC-%FLUID-VISCOSITY%CP.TXT',
        'STAT-FILE': '%MAP%-STAT-VISC-%FLUID-VISCOSITY%CP.CSV',
        'VTK-FILE': '%MAP%-VTK-VISC-%FLUID-VISCOSITY%CP.vtk'
    }

    # recycling our existing input file object
    inp_file = InputFile(inp_file, filename_formats=name_formats)
    inp_file.update_args({'MAP': 'AVG-FRAC1'})

    # showing the changes
    print(inp_file)

Right below the :code:`print(inp_file)` command, the name the input parameters file would be saved as when being run or written using the "code"`.write_inp_file` method is shown. This name can also be altered with formatting by adding an 'input_file' entry to the filename_formats_dict. An entry in the filename_formats_dict will overwrite any changes directly make to the :code:`.outfile_name` attribute of the InputFile class. The default outfile name is the name of the parameters file being read, so the original file would be overwritten.

The estimate_req_RAM Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The estimate_req_RAM function estimates the maximum amount of RAM the model will use while running. This is handy when running large maps on a smaller workstation or when you want to run several maps asynchronously.

Argument - Type - Description:
 * input_maps - list - A list of filenames of aperture maps.
 * avail_RAM - float - The amount of RAM the user wants to allow for use
 * suppress - boolean - If set to True and too large of a map is read only a message is printed to the screen and no Exception is raised. False is the default value.

Returns a list of required RAM per map.

.. code-block:: python

    # setting the maps list
    maps = [
        os.path.join('..', 'examples', 'AVERAGED-FRACTURES', 'Fracture1ApertureMap-10avg.txt'),
        os.path.join('..', 'examples', 'AVERAGED-FRACTURES', 'Fracture2ApertureMap-10avg.txt'),
        os.path.join('..', 'examples', 'FULL-FRACTURES', 'Fracture1ApertureMap.txt'),
        os.path.join('..', 'examples', 'FULL-FRACTURES', 'Fracture2ApertureMap.txt'),
    ]

    #checking RAM required for each
    estimate_req_RAM(maps, 4.0, suppress=True)

    #raises EnvironmentError
    estimate_req_RAM(maps, 4.0)

Because suppress was true we only received a message along with the amount of RAM each map would require. However the last line generates an error.

The run_model Function
~~~~~~~~~~~~~~~~~~~~~~

The run_model function combines some higher level Python functionality for working with the system shell into a simple package. The model can be both run synchronously or asynchronously but in both cases it returns a `Popen <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`_ object. Running the model synchronously can take a long time when running large aperture maps.

Argument - Type - Description
 * input_file_obj - InputFile - the input file object run with the model. Note: This file has to be written be careful to not overwrite existing files by accident
 * synchronous - boolean - If True the function will halt execution of the script until the model finishes running. The default is False.
 * pipe_output - boolean - If True then stdout and stderr will be stored on the Popen object returned using PIPE. **Warning this can cause a deadlock if stdout and stderr are not read**

 .. code-block:: python

   # running our current input file object
   # synchronous is True here because we need the process to have completed for
   # all of stdout to be seen.
   proc = run_model(inp_file, synchronous=True, pipe_output=True)

   # proc is a Popen object and has several attributes here are a few useful ones
   print('PID: ', proc.pid) # could be useful for tracking progress of async runs
   print('Return Code: ', proc.returncode) # 0 means successful

Another instance where running the model synchronously is helpful would be running data processing scripts after it completes.



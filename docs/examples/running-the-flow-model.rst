======================
Running the Flow Model
======================

.. contents::


Intro
=====

The Local Cubic Law (LCL) flow model by default is named ``apm-lcl-model.exe``, the added extension doesn't affect UNIX systems and allows Windows to recognize it as executable. There are two methods to run the model, first is directly on the command line via the script ``apm_run_lcl_model`` specifying your input parameters file(s) and the second is creating custom scripts using the ``run_model`` sub-module in ``apmapflow``. The model axes are on the X-Z plane where +Z is vertical and +X is to the right. The Y direction is the aperture variation and the model assumes a planar mid surface. This implies that the fracture is symmetric with respect to the X-Z plane. If you envision a spiral bound notebook with the bottom left corner as the origin. The Z-axis follows the metal spiral upward, positive X is the direction moving away from the spiral. Y is the thickness of the notebook.


The Input Parameters File
=========================

A template of the input parameters file can be found in `here <apm-model-inputs-template.inp>`_. The input file is parsed by a special routine in the model that treats all text after a semicolon, ``;``, as comments and one or more spaces as delimiters. A value enclosed in double quotations will have any internal spaces ignored. apmapflow also reads the input files when needed and for consistency it is recommended you append a colon ``:`` onto the end of keywords. Nearly all of the input parameters have default values and they are defined in `APERTURE_MAP_FLOW.F <../source/APERTURE_MAP_FLOW.F>`_ in the subroutine ``INITIALIZE_RUN``

**Important Notes**
 * There must be at least one space separating keyword and value.
 * The names of the keywords can not be changed without editing the model's source code.
 * Physical quantities must have a unit associated with them.
 * The LCL model's unit conversion is independent of the Python module and considerably more restrictive.

To use a diferent version of the LCL model executable than packaged with the module you can add a commented out line reading ``;EXE-FILE: (exe-file-name)``. The code will assume the executable path is relative to the location of the input file itself, **not** the current working directory if they differ.

The input file can be broken down into four main components:

File Paths
----------

This is where the path of input and output files are defined. Files are opened relative to the current working directory, **not** the input file itself. The use the absolute paths can prevent any ambiguity. If the line ``OVERWRITE EXISTING FILES`` is uncommented, any existing files sharing the same name will be replaced. If the line is commented out or absent an error will be raised if a pre-existing file with the same name is encountered. The model assumes the aperture map data being input is stored as a 2-D grid with the first value being the origin and the last value being the top right corner. The data maps output by the model also follow this convention. The output files accept the extension the user provides however the expected extensions are noted below. File names are not required and any omitted files will be saved using a default name.


Input Files
~~~~~~~~~~~
  - ``APER-MAP:`` File that stores the aperture map data.

Output Files
~~~~~~~~~~~~
  - ``SUMMARY-FILE:`` Logs the information printed to the screen (.txt expected)
  - ``STAT-FILE:`` Stores statistics calculated and certain simulation parameters. Provided extension is replaced by ``.csv`` and ``.yaml``
  - ``APER-FILE:`` Stores a copy of the input aperture map that is converted to the desired output units and has any applied roughness factored in (.csv expected)
  - ``FLOW-FILE:`` Used as the root name for the three flow files output: X-component, Z-component and magnitude. The files have -X, -Z, -M suffixes appended to the root name before the extension.  (.csv expected)
  - ``PRESS-FILE:`` Stores a pressure distribution map of the fracture(.csv expected)
  - ``VTK-FILE:`` A legacy formatted input file for Paraview which combines all of the former input files and includes several other data maps. Provided extension is replaced by ``.vtk``

Boundary Conditions
-------------------

Defines the boundary conditions for the simulation. The model does no internal checking to see if the BCs supplied create a valid solvable problem. It is the user's resposiblity to ensure a valid combination is supplied; two Dirichlet (pressure) conditions or one Dirichlet and one Neumann (flow rate) condition on the inlet and outlet.

 * ``INLET-PRESS:`` value unit ;The pressure value to use at the inlet
 * ``INLET-RATE:``  value unit ;The flow rate to apply at the inlet
 * ``OUTLET-PRESS:`` value unit ;The pressure value to use at the outlet
 * ``OUTLET-RATE:``  value unit ;The flow rate to apply at the outlet.
 * ``OUTLET-SIDE:`` [LEFT, RIGHT, TOP, BOTTOM] sets the outlet side, the inlet is assumed to be the opposite face. i.e. top is outlet, bottom is inlet

Model Properties
----------------
 * ``FLUID-DENSITY:`` value unit ;Density of liquid to use in Reynolds number calculation
 * ``FLUID-VISCOSITY:`` value unit ;Viscosity of liquid
 * ``MAXIMUM MAP DIMENSION:`` value ;Maximum number of blocks along either axis (default 2000)

Other Parameters
----------------
 * ``MAP AVERAGING FACTOR:`` value ;The number of voxels required to span an edge of a grid block along the X or Z direction. Grid blocks are assumed square in the X-Z plane.
 * ``VOXEL SIZE:`` value unit ;Specifies the voxel to meter conversion factor
 * ``ROUGHNESS REDUCTION:`` value ;**The value is in voxels** Amount to symmetrically bring the front and back fracture surfaces together by.
 * ``CALCULATE PERCENTILES:`` value1,value2,value3, ..., valueN ;A comma separated list of percentiles to calculate for various quantities during runtime. Commenting this line out tells it to not calculate them at all
 * ``HIGH-MASK:`` value ;**The value is in voxels** All data values in the aperture map above this value will be reduced to this value.
 * ``LOW-MASK:`` value ;**The value is in voxels** All data values in the aperture map below this value will be raised to this value

This tells the model what units you want the data output in. Commenting out or omitting this line will output everything in SI (pascals, meters and meters^3/second)

 * ``OUTPUT-UNITS:`` pressure unit, distance unit, flow rate unit

Running the Model
=================

This guide will assume you setup the modeling package using setup.py which would have installed the script ``apm_run_lcl_model`` on the console PATH and build the model from source code. Alternatively, you can use the actual executable in place of the script for these examples. Before we actually run the model it will be helpful to have a place to store the output files generated. We need to define an input file to use with the model and in this case we will take advantage of many of the predefined defaults. Running the following code in a terminal while in the top level directory (netl-ap-map-flow) will get things started, and show the usage information for the script.

.. code-block:: bash

    mkdir model-testing
    cd model-testing
    touch model-input-params.inp
    # display usage info
    apm_run_lcl_model -h

Open model-input-params.inp with your favorite text editor and copy and paste the following block.

.. code-block:: Scheme

    ;
    ; FILE PATHS AND NAMES
    APER-MAP: ../examples/Fractures/Fracture1ApertureMap-10avg.txt
    ;SUMMARY-FILE:
    ;STAT-FILE:
    ;APER-FILE:
    ;FLOW-FILE:
    ;PRESS-FILE:
    ;VTK-FILE:
    ;OVERWRITE EXISTING FILES
    ;
    ; BOUNDARY CONDITIONS
    INLET-PRESS: 100 PA
    OUTLET-PRESS: 0 PA
    OUTLET-SIDE: TOP
    ;
    ; MODEL PROPERTIES
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

    apm_run_lcl_model model-input-params.inp

You will notice that several output files have been generated in the current directory. They are saved under the default names because we did not specified our own filenames in the input file. You can view the VTK file in Paraview and the other CSV data maps in your viewer of choice. The STATS file is not a data map but being saved as a CSV file allows for quick calculations in excel or similar software. The YAML version of the stats file provides an easy to parse format for programmic manipulation, such as using the ``apm_combine_yaml_stat_files`` script to coalesce the results of multiple simulations. If we try to run the model a second time as before line again you will see an error is generated and execution is terminated. This is because the line ``;OVERWRITE EXISTING FILES`` is preceded by a semicolon meaning it is commented out and by default existing files will not be overwritten.

Running in Python Scripts
-------------------------

The run_model sub-module allows for much more power and convenience when running the model or multiple instances of the model. The sub-module also houses the BulkRun class which can be used to automate and parallelize the running of many simulations. Usage of the BulkRun class is outside the scope of this example file and is gone over in depth in `this file <bulk-run-example.rst>`_.

The core components of the `RunModule <../apmapflow/run_model/run_model.py>`_ consist of one class used to manipulate an input parameters files and two functions to handle running of the model. Code snippets below will demonstrate their functionality. The examples here assume you are working with the files created at the beginning of the section `Running the Model`_. The first step is to run the Python interpreter and import them from the parent module. You will only be able to import the module if you used setup.py to install the it, or manually added it to a location on the Python path, i.e. site-packages.

.. code-block:: python

    import os
    from apmapflow.run_model import InputFile
    from apmapflow.run_model import estimate_req_RAM, run_model

The InputFile Class
~~~~~~~~~~~~~~~~~~~
The InputFile class is used to read, write and manipulate an input parameters file. It provides an easy to use interface for updating parameters and can dynamically generate filenames based on those input parameters. Use of the class is simplest when you have the code read a file with all of the possible parameters already entered and the unneeded ones commented out.

Notes:
 * The keywords of the input file class are the first characters occurring before *any* spaces on a line. The keyword for parameter ``OVERWRITE EXISTING FILES path/to/filename`` is ``OVERWRITE```

Argument - Type - Description
 * infile - String or InputFile - The path to the file you want to read or the variable storing the InputFile object you want to recycle.
 * filename_formats (optional) - dict - A dict containing filename formats to use when creating outfile names and the save name of the input file itself based on current params. If none are provided then the original names read in will be used.

.. code-block:: python

    # Creating an InputFile object
    inp_file = InputFile('model-input-params.inp', filename_formats=None)

    # updating arguments can be done three ways
    #inp_file['param_keyword'] = value
    #inp_file['param_keyword'] = (value, commented_out)
    #inp_file.update(dict_of_param_values)

    # Directly updating the viscosity value
    inp_file['FLUID-VISCOSITY'] = '1.00'

    # updating a set of parameters using a dictionary
    new_param_values = {
        'OVERWRITE': 'OVERWRITE FILES',
        'INLET-PRESS': '150.00'
    }
    inp_file.update(new_param_values)

    # printing the InputFile object shows the changes
    print(inp_file)


You will notice that the line ``OVERWRITE EXISTING FILES`` has been changed and uncommented. The class by default will uncomment any parameter that is updated. To update a value and set the commented_out boolean use a tuple :code:`(value, True/False)`. This will also work when creating a dictionary of values to update. Parameters are stored in their own class called `ArgInput <../apmapflow/run_model/run_model.py>`_ which can be directly manipulated by accessing the keyword of an InputFile object like so, :code:`inp_file['FLUID-VISCOSITY']`. New parameters can not be created by simple assignment, instead you must call the ``add_parameter`` method and pass in the full line intended to go in the file, or a suitable placeholder line.

.. code-block:: python

    # commenting out percentile parameter
    inp_file['CALCULATE'].commented_out = True

    # changing the unit and value of density
    inp_file['FLUID-DENSITY'].unit = 'LB/FT^3'
    inp_file['FLUID-DENSITY'] = '62.42796'

    # adding a new parameter to the input file
    inp_file.add_parameter('NEW-PARAMETER: (value) (unit)')

    # changing the new param and making the line commented out
    inp_file['NEW-PARAMETER'] = ('NULL', True)

    #
    print(inp_file)

In addition to updating arguments you can also apply a set of filename formats to the InputFile class. These allow the filenames to be dynamically created based on the argument parameters present. Using the ``update`` method of the InputFile class you can also add a special set of args not used as parameters but instead to format filenames. Any args passed into ``update`` that aren't already a parameter are added to the ``filename_format_args`` attribute of the class.

.. code-block:: python

    # setting the formats dict up
    # Format replacements are recognized by {KEYWORD} in the filename
    name_formats = {
        'SUMMARY-FILE': '{apmap}-summary-visc-{fluid-viscosity}cp.txt',
        'STAT-FILE': '{apmap}-stat-visc-{fluid-viscosity}cp.csv',
        'VTK-FILE': '{apmap}-vtk-visc-{fluid-viscosity}cp.vtk'
    }

    # recycling our existing input file object
    inp_file = InputFile(inp_file, filename_formats=name_formats)
    inp_file.update({'apmap': 'avg-frac1'})

    # showing the changes
    print(inp_file)

The name of the input file can also be altered with formatting by adding an ``input_file`` entry to the filename_formats_dict. An entry in the filename_formats_dict will overwrite any changes directly make to the ``.outfile_name`` attribute of the InputFile class. The default outfile name is the name of the parameters file being read, so the original file would be overwritten.

The estimate_req_RAM Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The estimate_req_RAM function estimates the maximum amount of RAM the model will use while running. This is handy when running large maps on a smaller workstation or when you want to run several maps asynchronously.

Argument - Type - Description:
 * input_maps - list - A list of filenames of aperture maps.
 * avail_RAM (optional) - float - The amount of RAM the user wants to allow for use, omission implies there is no limit on available RAM.
 * suppress (optional) - boolean - If set to True and too large of a map is read only a message is printed to the screen and no Exception is raised. False is the default value.

Returns a list of required RAM per map.

.. code-block:: python

    # setting the maps list
    maps = [
        os.path.join('..', 'examples', 'Fractures', 'Fracture1ApertureMap-10avg.txt'),
        os.path.join('..', 'examples', 'Fractures', 'Fracture2ApertureMap-10avg.txt'),
        os.path.join('..', 'examples', 'Fractures', 'Fracture1ApertureMap.txt'),
        os.path.join('..', 'examples', 'Fractures', 'Fracture2ApertureMap.txt'),
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
 * input_file_obj - InputFile - the input file object run with the model. Note: This file has to be written to disk, be careful to not overwrite existing files by accident
 * synchronous (optional) - boolean - If True the function will halt execution of the script until the model finishes running. The default is False.
 * show_stdout (optional) - boolean - If True then stdout and stderr will be printed to the screen instead of being stored on the Popen object as stdout_content and stderr_content

 .. code-block:: python

   # running our current input file object
   # synchronous is True here because we need the process to have completed for
   # all of stdout to be seen.
   proc = run_model(inp_file, synchronous=True, show_stdout=False)

   # proc is a Popen object and has several attributes here are a few useful ones
   print('PID: ', proc.pid) # could be useful for tracking progress of async runs
   print('Return Code: ', proc.returncode) # 0 means successful
   print('Standard output generated:\n', proc.stdout_content)
   print('Standard err generated:\n', proc.stderr_content)

Another instance where running the model synchronously is helpful would be running data processing scripts after it completes.

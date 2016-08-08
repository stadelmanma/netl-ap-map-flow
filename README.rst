.. image:: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW.svg?branch=master
   :target: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW

.. image:: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW

AP MAP FLOW
===========

.. contents::


Description
-----------
AP_MAP_FLOW is a package written in Fortran and Python to perform local cubic law (LCL) simulations of single phase flow through a discrete fracture and analyze the data. There are several tools written in `Python <https://www.python.org/>`_ to provide added functionality which are packaged in the ApertureMapModelTools module. The Fortran code was compiled on Windows 7 with the `Cygwin <https://www.cygwin.com/>`_ gfortran 64-bit compiler and using the standalone gfortran compiler on OSX and Linux. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the \*.vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen program reads in the image matrix, the image may appear inverted. The first value in the CSV files corresponds to bottom left corner of the fracture, ImageJ places it instead as the top left corner by default when using the `text-image` upload method.


ApertureMapModelTools contains four sub modules DataProcessing, OpenFoamExport, RunModel and UnitConversion.

|

 * DataProcessing provides an easy to use and customizable platform for post-processing a set of simulation data. It is well suited to be used interactively in the Python interpreter or to create data processing scripts. A pre-made script is apm_process_data.py which accepts various command line arguments to automatically perform basic post-processing. There will be an example of post processing data in the 'examples' directory.

|

 * OpenFoam houses classes and methods to export data into a format acceptable for OpenFoam to use. There are several classes contained in this sub module however the three primary ones are OpenFoamFile, BlockMeshDict and OpenFoamExport. There is an example of how to utilize the BlockMeshDict class in `<examples/blockmeshdict-generation-example.rst>`_ and the OpenFoam module in `<examples/openfoam-example.rst>`_.

|

 * RunModel houses functions used to run the LCL model via python scripts instead of single instances on the command line. In addition to the core methods used to run individual simulations a BulkRun class exists which allows the user to automate the running of mulitple simulations concurrently. The example file for running a 'bulk simulation' is under `<examples/bulk-run-example.rst>`_. Utilization of the RunModel sub-module is in `<examples/running-the-flow-model.rst>`_, section `Running by Python Script <examples/running-the-flow-model.rst#running-by-python-script>`_

|

 * UnitConversion performs unit conversions for the user and is able to handle a wide variety of inputs. However it assumes the user is supplying a valid conversion i.e. meters to feet, where the dimensionality matches. There will be an example of how to use the module in the 'examples' directory.

Setting up the Modeling Package
-------------------------------

Getting the model and module up and running is a very straight forward process. After either cloning or downloading the repository into your chosen location you will need to download gfortran and `Python <https://www.python.org/>`_ if you do not already have them. If you are running Windows you will need to download `Cygwin <https://www.cygwin.com/>`_ or something similar to have access to gfortran and other unix commands. The module uses scipy for many operations and the simplest method to install the scipy stack is through Anaconda from `Continuum Analytics <http://continuum.io/downloads#all?>`_ on both Mac and Linux. Windows users can install the `WinPython <http://winpython.github.io/>`_ package, both provide the Spyder IDE and many other useful modules. The alternative is to manually install the required packages into your version of Python; `requirements.txt <https://github.com/stadelmanma/netl-AP_MAP_FLOW/blob/master/requirements.tx/>`_ lists out the minimum requirements however scipy may require additional packages on its own.

Once you have gfortran and Python you will need to build the flow model from source, the easiest way is by running :code:`./bin/build_model` from the main directory or running :code:`make` in the source directory. That script uses the makefile in the `source` directory which sets proper OS flags. Additionaly it will attempt to symbolically link the module into the user-site directory of Python, this allows global use of the module similar to modules installed via :code:`pip`. Cygwin users can open a command prompt and run the :code:`bash` command to use the script, although the linking step will likely fail. Windows users will likely need to manually track down the user-site directory of their chosen Python version using :code:`python -m site --user-site` and link it using the :code:`mklink` command. If the script and make are not an option the following command should compile the model for all systems assuming gfortran is installed and visible on the system path. If the flag :code:`-DWIN64=1` is added default file paths will be set to the Windows convention. You will need to be in the `source` directory for the following command to work.

.. code-block:: bash

    gfortran -c STRING_MODULE.F APM_MODULE.F APM_SOLVER_MODULE.F UNIT_CONVERSION_MODULE.F PVT_MODULE.F -O3
    gfortran -o APM-MODEL.EXE STRING_MODULE.o APM_MODULE.o APM_SOLVER_MODULE.o UNIT_CONVERSION_MODULE.o PVT_MODULE.o APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_FLOW.F APM_SOLVER.F  APM_OUTPUT.F -O3 -DWIN64=0
    mv APM-MODEL.EXE ..

Basic Usage of APM Model
------------------------

Running the Model in a terminal::

    ./APM-MODEL.EXE  model_initialization_file

Full usage instructions can be found in `<examples/running-the-flow-model.rst>`_.

Pitfalls:
---------
* Make sure required programs are added to the Path, this will likely need to be manually performed in Windows
* If the model is compiled using 32-bit compiler, running too large of a map can cause an integer overflow error
* The LCL Model requires that all of the parent directories of output file locations already exist. Otherwise a :code:`FileDoesNotExist` error or something similar will be raised.




.. image:: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW.svg?branch=master
   :target: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW

.. image:: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW

AP_MAP_FLOW
===========

.. contents::


Description
-----------
AP_MAP_FLOW is a package written in Fortran and Python to perform local cubic law simulations of single phase flow through a discrete fracture and analyze the data. There are several tools written in `Python <https://www.python.org/>`_ to provide added functionality which are packaged in ApertureMapModelTools module. The Fortran code was compiled on Windows 7 with the `Cygwin <https://www.cygwin.com/>`_ gfortran 64-bit compiler and using the standalone gfortran compiler on OSX and Linux. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the \*.vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen reader functions the images may be upside down. The first value in the CSV files correspond to bottom left corner of the fracture, ImageJ places it instead as the top left corner by default when usuing the `text-image` upload method. 


ApertureMapModelTools contains four sub modules DataProcessing, OpenFoamExport, RunModel and UnitConversion. The DataProcessing module provides an easy to use and customizable platform for post-processing a set of simulation data. It is well suited to be used either interactively in the Python interpreter or to create data processing scripts. A pre-made script is apm_process_data.py accepts various command line arguments to automatically perform basic post-processing. The OpenFoamExport module is used to create a blockMeshDict file from the flattened aperture map used in the LCL model. There is an example of how to utilize the OpenFoamExport class in the 'examples' directory. The RunModel module houses functions used to run the LCL model via python scripts instead of single instances on the command line. In addition to the core methods used to run individual simulations a BulkRun class exists which allows the user to automate the running of mulitple simulations concurrently. There is an example of how to utilize the BulkRun class in the 'examples' directory as well as running single instances of the model in Python. The final module UnitConversion can be used to convert between multiple units assuming they are of the same dimension, some complex units such as newtons and psi are directly supported but properly formed strings that only contain fundamental units (distance, mass, time) allow for nearly any conversion to be performed. There is support for the use of prefixes (milli,centi,kilo,etc.) and abbrevations both of which follow standard SI practices. In general explicit (millimeter over mm) will always be safer. There is an example of how to utilize this in the 'examples' directory as well. 

Setting up the Modeling Package
-------------------------------

Getting the model and module up and running is a very straight forward process. After either cloning or downloading the repository


Basic Usage of APM Model
------------------------
sThe simplest method to build the model from source is by running `./bin/build_model` from the main directory, this uses the make file in the `source` directory which sets proper OS flags. If that is not an option the following command will work for all systems assuming gfortran is installed using some method. If the flag -DWIN64=1 is added default file paths will be set to the windows convention.::

    >> gfortran -o APM-MODEL.EXE APM_MODULE.F UNIT_CONVERSION_MODULE.F APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_SOLVER.F APM_FLOW.F APM_OUTPUT.F -O2 -fimplicit-none -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace


Running the Model in a command prompt::

    >> .\APM-MODEL.EXE  model_initialization_file

Full setup and usage instructions can be found in the 'examples' directory.

Pitfalls:
    * If the model is compiled using 32-bit compiler, running too large of a map can cause an integer overflow error




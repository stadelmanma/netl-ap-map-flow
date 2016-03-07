AP_MAP_FLOW
====

.. contents::

Disclaimer
-------
This ReadMe is a work in progress and several aspects of the model are currently being restructured and rewritten so this document may lag behind the most current version.

Description
-----------
AP_MAP_FLOW is a program written in `FORTRAN <https://gcc.gnu.org/onlinedocs/gfortran/>`_ to perform local cubic law simulations of flow through a single discrete fracture. There are several tools written in `Python <https://www.python.org/>`_ to provide added functionality which are packaged in ApertureMapModelTools (in development). The program and its helper routines are run through on the command-line. The FORTRAN code was compiled on Windows 7 with the `Cygwin <https://www.cygwin.com/>`_ gfortran 64-bit compiler during development and the executable requires Cygwin to run. On Unix style systems it will need to be recompiled from source. In general for best results on your system recompile the executable from source with your chosen compiler. `Paraview <http://www.paraview.org/>`_ is the reccomended program to view the *.vtk files output. The Python code requires version 3.X to function and only uses native modules. 


ApertureMapModelTools contains two sub modules DataProcessing and BulkRun. The DataProcessing module provides an easy to use and modify platform for performing post-processing on an existing set of simulation data. It can be used both interactively within the interpreter or to create data processing scripts. A pre-made script is APM_PROCESS_DATA.PY (in development), which accepts various command line arguments to automatically perform basic post-processing. The BulkRun module houses functions used to automate the running of multiple simulations in concurrently. The user defines the parameters for multiple simulations in APM_BULK_RUN.PY and then executes that script on the command-line to start running them.

Basic Usage of APM Model
------------------------
Compiling the model, the flags shown below are apply to the GNU gfortran compiler::

    >> gfortran -o APM-MODEL.EXE APM_MODULE.F APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_SOLVER.F APM_FLOW.F APM_OUTPUT.F -O2 -fimplicit-none -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace

Running the Model::

    >> .\APM-MODEL.EXE  model_initialization_file

Pitfalls:
    * Default file paths are in Windows format 
    * If compiled using 32-bit compiler running too large of a map will cause an integer overflow error
    * Other solver subroutines exist in APM_SOLVER.F, however only GAUSS is the only correctly working solver at this time

Basic Usage of ApertureMapModelTools
------------------------
Forthcoming...

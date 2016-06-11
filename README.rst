AP_MAP_FLOW
====

.. contents::

Notice
-------
** Major reworking of the module is going on
Formal documentation and examples are a work in progress and will be uploaded as time allows.

Description
-----------
AP_MAP_FLOW is a program written in `FORTRAN <https://gcc.gnu.org/onlinedocs/gfortran/>`_ to perform local cubic law simulations of flow through a single discrete fracture. There are several tools written in `Python <https://www.python.org/>`_ to provide added functionality which are packaged in ApertureMapModelTools. The program and its helper routines are run through the command-line. The FORTRAN code was compiled on Windows 7 with the `Cygwin <https://www.cygwin.com/>`_ gfortran 64-bit compiler during development. Here is a `link <https://gcc.gnu.org/wiki/GFortranBinaries>`_  for the gfortran compiler used on OSX. For Linux a simple apt-get of gfortran may be sufficient but I have not tested if there are additional dependencies yet. `Paraview <http://www.paraview.org/>`_ is the recommended  program to view the *.vtk files output. The Python code requires version 3.X to function and only uses native modules, the code was developed in Python 3.5.


ApertureMapModelTools contains two sub modules DataProcessing and BulkRun. The DataProcessing module provides an easy to use and modify platform for performing post-processing on an existing set of simulation data. It can be used both interactively within the interpreter or to create data processing scripts. A pre-made script is APM_PROCESS_DATA.PY (in development), which accepts various command line arguments to automatically perform basic post-processing. The BulkRun module houses functions used to automate the running of multiple simulations in concurrently. The user defines the parameters for multiple simulations in APM_BULK_RUN.PY and then executes that script on the command-line to start running them.

Basic Usage of APM Model
------------------------
The simplest method to build the model from source is using the makefile found in the SOURCE sub-directory, as this sets the proper OS flags. If that is not an option the following commands will work for POISX systems and if the flag -DWIN64=1 is added default file paths will be set to the windows convention.::

    >> gfortran -o APM-MODEL.EXE APM_MODULE.F UNIT_CONVERSION_MODULE.F APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_SOLVER.F APM_FLOW.F APM_OUTPUT.F -O2 -fimplicit-none -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace

    >> gfortran64 -o OPENFOAM-EXPORT.EXE APM_MODULE.F UNIT_CONVERSION_MODULE.F OPENFOAM_EXPORT.F OPENFOAM_EXPORT_SUBROUTINES.F APM_SUBROUTINES.F APM_SOLVER.F -O2 -fimplicit-none -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace

Running the Model::

    >> .\APM-MODEL.EXE  model_initialization_file

Pitfalls:
    * If compiled using 32-bit compiler running too large of a map will cause an integer overflow error
    * Other solver subroutines exist in APM_SOLVER.F, however only GAUSS and D4_GUASS work correctly with D4_GAUSS being the primary and most efficient routine.
    * openFOAM export is functional however not extremely friendly and will be rewritten into a Python routine at a later date

Basic Usage of ApertureMapModelTools
------------------------
This module is designed to ease the process of further data processing and running multiple simulations in parallel. It is currently divided into two sub-modules DataProcessing and BulkRun. The openFOAM export will be the third component when it is converted from a FORTRAN routine.

The DataProcessig sub-module is imported by default when the entire module is imported. It can be run equally easily in an interactive session or used to make automatic post-processing scripts such as the pre-built APM_PROCESS_DATA_MAP.PY script. Although designed in conjunction with the flow model the DataProcessing model in theory can be applied to any 2-D data distribution with some minor modifications. There are several pre-built processing routines in the module and others can be easily added by creating a new class and extending the BaseProcessor routine.

The BulkRun sub-module is not designed to be used interactively although it is possible. It was built to work with the APM_BULK_RUN.PY script where the user defines the input parameters and files. The routines in the module then do the rest of the heavy lifting. The program will spawn as many simultaneous processes as possible based on the RAM requirements of each simulation and the user defined RAM and CPUs available to be used. The routine only uses 90% of the user defined limit because each simulation requires some extra overhead that cannot be pre-determined.


.. image:: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW.svg?branch=master
   :target: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW

.. image:: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW

AP MAP FLOW
===========

.. contents::


Description
-----------
AP_MAP_FLOW is a package written in Fortran and Python to perform local cubic law (LCL) simulations of single phase flow through a discrete fracture and analyze the data. There are several tools written in `Python <https://www.python.org/>`_ to provide added functionality which are packaged in the ApertureMapModelTools module. The project has been primarily developed on Ubuntu, however any Linux or OS X system will likely work as long as the requiste packages are installed. The Fortran code was compiled on Windows 7 with the `MinGW-64 <https://sourceforge.net/projects/mingw-w64/>`_ 64-bit gfortran compiler and using the standalone gfortran compiler on OSX and Linux. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the \*.vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen program reads in the image matrix, the image may appear inverted. The first value in the CSV files corresponds to bottom left corner of the fracture, ImageJ places it instead as the top left corner by default when using the `text-image` upload method. There are a few sub modules available to divide up functionality, they are described below.

|

 * DataProcessing provides an easy to use and customizable platform for post-processing a set of simulation data. It is well suited to be used interactively in the Python interpreter or to create data processing scripts. A pre-made script is apm_process_data_map.py which accepts various command line arguments to automatically perform basic post-processing. 

|

 * OpenFoam houses classes and methods to export data into a format acceptable for OpenFoam to use. There is an example of how to utilize the BlockMeshDict class in `<examples/blockmeshdict-generation-example.rst>`_ and the OpenFoam module in `<examples/openfoam-example.rst>`_.

|

 * RunModel houses functions used to run the LCL model via python scripts instead of single instances on the command line. In addition to the core methods used to run individual simulations a BulkRun class exists which allows the user to automate the running of mulitple simulations concurrently. The example file for running a 'bulk simulation' is under `<examples/bulk-run-example.rst>`_. Utilization of the RunModel sub-module is in `<examples/running-the-flow-model.rst>`_, section `Running by Python Script <examples/running-the-flow-model.rst#running-by-python-script>`_

|

 * UnitConversion performs unit conversions for the user and is able to handle a wide variety of inputs. However it assumes the user is supplying a valid conversion i.e. meters to feet, where the dimensionality matches.

Setting up the Modeling Package
-------------------------------

Linux and OSX
~~~~~~~~~~~~~
Getting the model and module up and running is a very straight forward process on Linux and OSX. Simply download and install a Python3.4+ package from `Anaconda <http://continuum.io/downloads#all?>`_ to setup the Python environment. If you already have a significantly customized Python environment the dependencies listed in `<requirements.txt>`_ can be manually installed. To run the testing suite as well, install the dependencies in `<test_requirements.txt>`_. The next step is to install a Fortran compiler and GNU make, :code:`gfortran` is the expected compiler name in the makefile. Linux may already have both, you will likely need to install them on OS X. The final step is to clone or download the repository into your chosen location and then run :code:`./bin/build_model` from the toplevel directory. That will build the flow model from source and link the ApertureMapModelTools module to the installed version of python3.



Windows
~~~~~~~
1. Download and install the 64 bit version of `Anaconda <https://www.continuum.io/downloads#windows>`_ for Windows
    A. Open a command prompt (it's under Accessories) and enter :code:`python`. If the installion was successful the interpreter will be displayed
    B. Exit the Python interpreter hit :code:`Ctrl+Z` and then :code:`Enter` 
    C. Run the command :code:`conda install git`, you may need an elevated command prompt depending on where Anaconda was installed. Right click the command prompt icon on the start menu and select :code:`Run as Administrator`
2. Download and install `MinGW-w64 <https://sourceforge.net/projects/mingw-w64/>`_ for windows
    A. Double click the installation script that was downloaded and hit :code:`Next`
    B. Change the value of the Architecture select box to :code:`x86_64` and hit :code:`Next`
    C. Modify the installation path to be: :code:`C:\Program Files\mingw-w64`, untick the :code:`create shortcuts` box and hit :code:`next`
    D. Wait for the packages to finish downloading and hit :code:`Next` and then :code:`Finish`
    E. Go to the folder :code:`C:\Program Files\mingw-w64\mingw64\bin` and rename (or duplicate) the file :code:`mingw32-make.exe` as :code:`make.exe`
    F. Finally add the path :code:`C:\Program Files\mingw-w64\mingw64\bin` to the `Windows environment Path <http://stackoverflow.com/a/28545224>`_.
3. Shift + right click in the directory you want to install the AP_MAP_FLOW package and open a command prompt
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`
    B. Run the command :code:`cd netl-AP_MAP_FLOW`
    C. Finally run :code:`.\bin\build_model.bat` which will build the model and link the ApertureMapModelTools package to the installed version of python

Basic Usage of APM Model
------------------------

Running the Model in a terminal::

    ./APM-MODEL.EXE  model_initialization_file

Full usage instructions can be found in `<examples/running-the-flow-model.rst>`_.

Pitfalls:
---------
* Make sure required programs are added to the Path, this will need to be manually performed in Windows
* If the model is compiled using 32-bit compiler, running too large of a map can cause a memory overflow error
* The LCL Model requires that all of the parent directories of output file locations already exist. Otherwise an error will be raised.

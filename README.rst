.. image:: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW.svg?branch=master
   :target: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW

.. image:: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW

AP_MAP_FLOW
===========

.. contents::


Description
-----------
AP_MAP_FLOW is a package written in Fortran and Python to perform local cubic law simulations of single phase flow through a discrete fracture and analyze the data. There are several tools written in `Python <https://www.python.org/>`_ to provide added functionality which are packaged in the ApertureMapModelTools module. The Fortran code was compiled on Windows 7 with the `Cygwin <https://www.cygwin.com/>`_ gfortran 64-bit compiler and using the standalone gfortran compiler on OSX and Linux. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the \*.vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen reader functions the images may be upside down. The first value in the CSV files corresponds to bottom left corner of the fracture, ImageJ places it instead as the top left corner by default when usuing the `text-image` upload method. 


ApertureMapModelTools contains four sub modules DataProcessing, OpenFoamExport, RunModel and UnitConversion.

| 

 * DataProcessing provides an easy to use and customizable platform for post-processing a set of simulation data. It is well suited to be used interactively in the Python interpreter or to create data processing scripts. A pre-made script is apm_process_data.py accepts various command line arguments to automatically perform basic post-processing. 

|

 * OpenFoamExport is used to create a blockMeshDict file from the flattened aperture map used in the LCL model. There is an example of how to utilize the OpenFoamExport class in the 'examples' directory. 

|

 * RunModel houses functions used to run the LCL model via python scripts instead of single instances on the command line. In addition to the core methods used to run individual simulations a BulkRun class exists which allows the user to automate the running of mulitple simulations concurrently. There is an example of how to utilize the BulkRun class in the 'examples' directory as well as running single instances of the model in Python.

|

 * UnitConversion performs unit conversions for the user and is able to handle a wide variety of inputs. However it assumes the user is supplying a valid conversion i.e. meters to feet, where the dimensionality matches. There is an example of how to use the module in the 'examples' directory. 

Setting up the Modeling Package
-------------------------------

Getting the model and module up and running is a very straight forward process. After either cloning or downloading the repository into your chosen location you will need to download gfortran and `Python <https://www.python.org/>`_ if you do not already have them. If you are running Windows you will need to download `Cygwin <https://www.cygwin.com/>`_ or something similar to have access to gfortran and other unix commands. The module uses scipy for many operations and the simplest method to install the scipy stack is through Anaconda from `Continuum Analytics <http://continuum.io/downloads#all?>`_ on both Mac and Linux. Windows users can install the `WinPython <http://winpython.github.io/>`_ package, both provide the Spyder IDE and many other useful modules. The alternative is to manually install the required packages into your version of Python; `requirements.txt <https://github.com/stadelmanma/netl-AP_MAP_FLOW/blob/master/requirements.tx/>`_ lists out the minimum requirements however scipy may require additional packages on its own.

Once you have gfortran and Python you will need to build the flow model from source, the easiest way is by running :code:`./bin/build_model` from the main directory. That script uses the make file in the `source` directory which sets proper OS flags. Cygwin users can open a command prompt and run the :code:`bash` command to use the script. If that is not an option the following command should work for all systems assuming gfortran is installed. If the flag -DWIN64=1 is added default file paths will be set to the windows convention. You will need to be in the `source` directory for the following command to work.

.. code-block:: bash

    gfortran -c APM_MODULE.F
    gfortran -c UNIT_CONVERSION_MODULE.F
    gfortran -o APM-MODEL.EXE APM_MODULE.F UNIT_CONVERSION_MODULE.F APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_SOLVER.F APM_FLOW.F APM_OUTPUT.F -O2 -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp -DWIN64=0 -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
    mv APM-MODEL.EXE ..



Making ApertureMapModuleTools globally visible to the Python install is optional but can simplfy usage of the module. Python stores all third party packages in a local directory, the location of that directory can be found using the following command. If needed substiute "python3" for which ever python executable you have or want to use.  

.. code-block:: bash

    python3 -m site --user-site

After you have the location of that directory you can either move the entire ApertureMapModelTools directory there or symlink it using the command below in a terminal window from **inside the ApertureMapModelTools directory**. The command as written will probably not work for windows systems, with the full cygwin enviroment running :code:`bash` in a command prompt it may. The steps to symlink the module may also slightly differ if you are using the full Spyder environment. For Spyder users you will probably need to open a command prompt within spyder by right clicking the Console pane.

.. code-block:: bash

    module_path=$(pwd)
    cd $(python3 -m site --user-site)
    ln -s "$module_path"
    ls -l
    cd "$module_path"

If the command was successful you should see ApertureMapModelTools listed in the above output of the :code:`ls -l` command. It will likely have additional text beside it denoting the true location of the symlink.


Basic Usage of APM Model
------------------------

Running the Model in a terminal::

    >> .\APM-MODEL.EXE  model_initialization_file

Full usage instructions can be found in the 'examples' directory.

Pitfalls:
    * If the model is compiled using 32-bit compiler, running too large of a map can cause an integer overflow error




.. image:: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW.svg?branch=master
   :target: https://travis-ci.org/stadelmanma/netl-AP_MAP_FLOW

.. image:: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stadelmanma/netl-AP_MAP_FLOW

AP MAP FLOW
===========

.. contents::


Description
-----------
AP_MAP_FLOW is a package written in Fortran and Python to perform local cubic law (LCL) simulations of single phase flow through a discrete fracture and analyze the data. Several tools written in `Python <https://www.python.org/>`_ provide added functionality are packaged in the ApertureMapModelTools module. The project has been primarily developed on Ubuntu, however any OS will likely work as long as the requiste packages are installed. The Fortran code was compiled using a 64-bit GNU Fortran compiler. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the \*.vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen program reads in the image matrix, the image may appear inverted. The first value in the CSV files corresponds to bottom left corner of the fracture, ImageJ places it instead as the top left corner by default when using the `text-image` upload method. There are a few sub modules available to divide up functionality, they are described below.

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
These steps were followed on Ubuntu 14.04 & 16.04, OSX 10.9 & MacOS 10.12 and Windows 7. They are not guaranteed to remain updated however the general process should be relatively stable as all dependencies are being handled by large, community driven projects i.e. Anaconda, MinGW, GCC, etc. Running the test suite in Windows is possible but not without some manual adjustments and extra effort. 

An extra step that may prevent unexpected errors would be to run :code:`sudo conda update --all` or :code:`sudo pip install -r requirements.txt --upgrade` after the final step especially if you are using an existing Anaconda install.

Linux
~~~~~
1. Install :code:`git` using the terminal command :code:`sudo apt-get install git`.
    A. Run :code:`git --version` in a new terminal window to check if it was installed properly.
2. Download and Install the 64 bit, Python 3.X version of  `Anaconda <https://www.continuum.io/downloads#linux>`_ for Linux.
    A. In a terminal, copy and paste the command :code:`bash ~/Downloads/Anaconda3-4.2.0-Linux-x86_64.sh` you may need to tweak the path and or filename if a new version of Anaconda is released. 
    B. Follow the instructions as the installation script runs and enter 'yes' when it prompts to update your :code:`$PATH` variable. 
        * If using a different shell (i.e. zsh) you will likely need to manually update your :code:`$PATH` variable.
    C. Close your existing terminal window and open a new one, enter :code:`python --version` to check if Anaconda has installed Python successfully.
    D. Anaconda's full installation instructions can be found here: https://docs.continuum.io/anaconda/install#linux-install
3. Install :code:`gfortran` using the terminal command :code:`sudo apt-get install gfortran`.
    A. Run :code:`gfortran --version` in a new terminal window to check if it was installed properly.
4. Open a terminal or cd into the directory you want to install the AP_MAP_FLOW package in.
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`.
    B. Run the command :code:`cd netl-AP_MAP_FLOW`.
    C. Finally run :code:`./bin/build_model` which will build the model and link the ApertureMapModelTools module to the python3 user site.
    D. Optional: run :code:`pip install -r test_requirements.txt` to enable running the test suite.
        * When running the test suite, recompile the model using :code:`./bin/build_model debug` which builds the model using additional flags and code coverage

MacOS/ OSX
~~~~~~~~~~
1. Install Xcode from the App Store
    A. Open Xcode once it is install and allow it to install additional components, this includes the Command Line Tools (CLT)
2. Install `homebrew <http://brew.sh>`_
    A. After installation :code:`brew install gcc` to install gfortran and many other useful tools
        * It may take awhile on the :code:`make bootstrap` step, my complete installation took approximately 90 minutes.
3. Download and install the 64 bit, Python 3.X version of `Anaconda <https://www.continuum.io/downloads#osx>`_ for MacOS
    A. Choose the "Install for Me Only" option when prompted
    B. Open or create the ~/.bashrc (or equivalent for your shell i.e. ~/.zshrc) file and preappend :code:`$HOME/anaconda/bin:` to the :code:`$PATH` variable. 
        * If you need to create the ~/.bashrc file or there is no $PATH line in the file, the following line should work: :code:`export PATH=$HOME/anaconda/bin:$PATH`
        * Be careful not to forget the :code:`:` between directory paths or to export the PATH variable i.e. :code:`export $PATH`. 
        * If you edited the ~/.bashrc file in the terminal or have an open window run :code:`source ~/.bashrc` to apply changes, alternatively close and open a term terminal window. 
    C. In a terminal window run :code:`python3 --version` to ensure Anaconda was installed properly
        * :code:`python` will likely also bring up the Anaconda version of 3.5, to regain access to the system version of Python delete the :code:`python` symlink in :code:`~/anaconda/bin`
    B. Anaconda's full installation instructions can be found here: https://docs.continuum.io/anaconda/install#anaconda-for-os-x-graphical-install
4. Open a terminal or cd into the directory you want to install the AP_MAP_FLOW package in
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`
    B. Run the command :code:`cd netl-AP_MAP_FLOW`
    C. Finally run :code:`./bin/build_model` which will build the model and link the ApertureMapModelTools module to the python3 user site
    D. Optional: run :code:`pip install -r test_requirements.txt` to enable running the test suite.
        * When running the test suite, recompile the model using :code:`./bin/build_model debug` which builds the model using additional flags and code coverage

Windows
~~~~~~~
1. Download and install the 64 bit, Python 3.X version of `Anaconda <https://www.continuum.io/downloads#windows>`_ for Windows
    A. Open a command prompt (it's under Accessories) and enter :code:`python`. If the installion was successful the interpreter will be displayed
    B. Exit the Python interpreter hit :code:`Ctrl+Z` and then :code:`Enter` 
    C. Run the command :code:`conda install git`, you may need an elevated command prompt depending on where Anaconda was installed. Right click the command prompt icon on the start menu and select :code:`Run as Administrator`
    D. Anaconda's full installation instructions can be found here: https://docs.continuum.io/anaconda/install#anaconda-for-windows-install
2. Download and install `MinGW-w64 <https://sourceforge.net/projects/mingw-w64/>`_ for windows
    A. Double click the installation script that was downloaded and hit :code:`Next`
    B. Change the value of the Architecture select box to :code:`x86_64` and hit :code:`Next`
    C. Modify the installation path to be: :code:`C:\Program Files\mingw-w64`, untick the :code:`create shortcuts` box and hit :code:`next`
    D. Wait for the packages to finish downloading and hit :code:`Next` and then :code:`Finish`
    E. Go to the folder :code:`C:\Program Files\mingw-w64\mingw64\bin` and rename (or duplicate) the file :code:`mingw32-make.exe` as :code:`make.exe`
    F. Finally add the path :code:`C:\Program Files\mingw-w64\mingw64\bin` to the `Windows environment Path <http://stackoverflow.com/a/28545224>`_.
3. Shift + right click in the directory you want to install the AP_MAP_FLOW package and open a command window.
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
* Make sure required programs are added to the PATH environment variable, this will need to be manually performed in some cases
* If the model is compiled using 32-bit compiler, running too large of a map can cause a memory overflow error
* The LCL Model requires that all of the parent directories of output file locations already exist. Otherwise an error will be raised.

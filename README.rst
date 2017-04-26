.. image:: https://travis-ci.org/stadelmanma/netl-ap-map-flow.svg?branch=master
   :target: https://travis-ci.org/stadelmanma/netl-ap-map-flow

.. image:: https://ci.appveyor.com/api/projects/status/cyaxl3r2mbmymbp3?svg=true
   :target: https://ci.appveyor.com/project/stadelmanma/netl-ap-map-flow

.. image:: https://codecov.io/gh/stadelmanma/netl-ap-map-flow/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/stadelmanma/netl-ap-map-flow

.. image:: https://zenodo.org/badge/50030017.svg
   :target: https://zenodo.org/badge/latestdoi/50030017

AP MAP FLOW
===========

.. contents::


Description
-----------
AP_MAP_FLOW is a package written in Fortran and Python to perform local cubic law (LCL) simulations of single phase flow through a discrete fracture and analyze the data. Several tools written in `Python <https://www.python.org/>`_ provide added functionality are packaged in the ApertureMapModelTools module. The project has been primarily developed on Ubuntu, however any OS will likely work as long as the requiste packages are installed. The Fortran code was compiled using a 64-bit GNU Fortran compiler. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the \*.vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen program reads in the image matrix, the image may appear inverted. The first value in the CSV files corresponds to bottom left corner of the fracture, ImageJ places it instead as the top left corner by default when using the `text-image` upload method. Unit conversions can be handled using three functions provided in unit_conversion.py. The module `pint <https://github.com/hgrecco/pint>`_ is required and needs to be installed via pip or through conda-forge. There are a few submodules available to divide up functionality, they are described below.

|

 * data_processing provides an easy to use and customizable platform for post-processing a set of simulation data. It is well suited to be used interactively in the Python interpreter or to create data processing scripts. A pre-made script is :code:`apm-process-data-map.py` which accepts various command line arguments to automatically perform basic post-processing.

|

 * openfoam houses classes and methods to export data into a format acceptable for OpenFoam to use. There is an example of how to utilize the BlockMeshDict class in `<examples/blockmeshdict-generation-example.rst>`_ and the OpenFoam module in `<examples/openfoam-example.rst>`_.

|

 * run_model houses functions required to build Python scripts to run the model. The script :code:`apm-run-lcl-model.py` can run one or more simulation sequentially. In addition to the core methods used to run individual simulations a BulkRun class exists which allows the user to automate the running of mulitple simulations in parallel. The example file for running a 'bulk simulation' is under `<examples/bulk-run-example.rst>`_. Utilization of the run_model sub-module is in `<examples/running-the-flow-model.rst>`_, section `Running by Python Script <examples/running-the-flow-model.rst#running-by-python-script>`_


Setting up the Modeling Package
-------------------------------
These steps were followed on Ubuntu 14.04 & 16.04, OSX 10.9 & MacOS 10.12 and Windows 7. They are not guaranteed to remain updated however the general process should be relatively stable as all dependencies are being handled by large, community driven projects i.e. Anaconda, MinGW, GCC, etc. Running the test suite in Windows is possible but not without some manual adjustments and extra effort. After installation there are several scripts avilable under the :code:`apm-` prefix upon opening up a new terminal.

Installation Tips
~~~~~~~~~~~~~~~~~
* Anaconda's full installation instructions for all OSes can be found here: https://docs.continuum.io/anaconda/install
* This guide assumes you install Anaconda3 locally. If you choose to install it system wide you will need to run some commands with :code:`sudo` in unix systems or in an elevated command prompt in Windows.
* For unix systems that already have a system version of Python 2.7, :code:`python` will likely also bring up the Anaconda version, to regain access to the system version of Python delete the :code:`python` symlink in :code:`~/anaconda/bin`
* After installing Anaconda3 run :code:`pip --version` in a terminal to ensure it points to the anaconda installation, if not check your PATH.
* Add the `conda-forge <https://conda-forge.github.io/>`_ channel to your conda environment to allow conda to install pint. :code:`conda config --add channels conda-forge`
* After downloading the model run :code:`conda update --all` and :code:`conda install --file requirements.txt` to ensure all packages are up to date, this will also install the pint module.
* Run :code:`pip install -r test_requirements.txt` to enable running the test suite.
* When running the test suite, recompile the model using :code:`./bin/build_model debug` which builds the model using additional flags, code coverage and profiling
* If you want to modify the source code of the model or module you are better off to run :code:`python3 setup.py develop --user` rather than :code:`install`. The former method simply creats a link instead of actually copying the files allowing your changes to take effect upon a fresh start of the interpreter.

Linux
~~~~~
1. Install :code:`git` using the terminal command :code:`sudo apt-get install git`.
    A. Run :code:`git --version` in a new terminal window to check if it was installed properly.
2. Download and Install the 64 bit, Python 3.X version of  `Anaconda <https://www.continuum.io/downloads#linux>`_ for Linux. Follow their instructions to install Anaconda and be sure to let it update your :code:`$PATH` variable. If using a shell other than bash (i.e. zsh) you may need propograte the :code:`$PATH` changes appropriately.
    A. Close your existing terminal window and open a new one, enter :code:`python3 --version` to check if Anaconda has installed Python successfully.
3. Install :code:`gfortran` using the terminal command :code:`sudo apt-get install gfortran`.
    A. Run :code:`gfortran --version` in a new terminal window to check if it was installed properly.
4. Open a terminal or cd into the directory you want to install the AP_MAP_FLOW package in.
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`.
    B. Run the command :code:`cd netl-AP_MAP_FLOW`.
    C. Finally run :code:`python3 setup.py install --user` which will build the model and link the ApertureMapModelTools module to the python3 installation.

MacOS/ OSX
~~~~~~~~~~
1. Install Xcode from the App Store
    A. Open Xcode once it is installed and allow it to install additional components, this includes the Command Line Tools (CLT)
2. Install `homebrew <http://brew.sh>`_
    A. After installation :code:`brew install gcc` to install gfortran and many other useful tools
        * It may take awhile on the :code:`make bootstrap` step, my complete installation took approximately 90 minutes.
3. Download and install the 64 bit, Python 3.X version of `Anaconda <https://www.continuum.io/downloads#osx>`_ for MacOS
    A. Choose the "Install for Me Only" option when prompted
    B. Open or create the ~/.bashrc (or equivalent for your shell i.e. ~/.zshrc) file and add the line :code:`export PATH=$HOME/anaconda/bin:$PATH`.
        * Be careful not to forget the :code:`:` between directory paths
        * If you edited the ~/.bashrc file in the terminal or have an open window run :code:`source ~/.bashrc` to apply changes, alternatively close and open a term terminal window.
    C. In a terminal window run :code:`python3 --version` to ensure Anaconda was installed properly and is accessible
4. Open a terminal and cd into the directory you want to install the AP_MAP_FLOW package in
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`
    B. Run the command :code:`cd netl-AP_MAP_FLOW`
    C. Finally run :code:`python3 setup.py install --user` which will build the model and link the ApertureMapModelTools module to the python3 installation.

Windows
~~~~~~~
1. Download and install the 64 bit, Python 3.X version of `Anaconda <https://www.continuum.io/downloads#windows>`_ for Windows
    A. Open a command prompt (it's under Accessories) and enter :code:`python`. If the installion was successful the interpreter will be displayed
    B. Exit the Python interpreter hit :code:`Ctrl+Z` and then :code:`Enter`
    C. Run the command :code:`conda install git`
2. Download and install `MinGW-w64 <https://sourceforge.net/projects/mingw-w64/>`_ for windows
    A. Double click the installation script that was downloaded and hit :code:`Next`
    B. Change the value of the Architecture select box to :code:`x86_64` and hit :code:`Next`
    C. Modify the installation path to be: :code:`C:\mingw-w64`, untick the :code:`create shortcuts` box and hit :code:`next`
    D. Wait for the packages to finish downloading and hit :code:`Next` and then :code:`Finish`
    E. Go to the folder :code:`C:\mingw-w64\mingw64\bin` and rename (or duplicate) the file :code:`mingw32-make.exe` as :code:`make.exe`
    F. Finally add the path :code:`C:\mingw-w64\mingw64\bin` to the `Windows environment Path <http://stackoverflow.com/a/28545224>`_.
3. Shift + right click in the directory you want to install the AP_MAP_FLOW package and open a command window.
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`
    B. Run the command :code:`cd netl-AP_MAP_FLOW`
    C. Finally run :code:`python3 setup.py install --user` which will build the model and link the ApertureMapModelTools package to the installed version of python

Windows with Babun
~~~~~~~~~~~~~~~~~~
`Babun <http://babun.github.io/>`_ offers a much friendlier terminal experience than the standard cmd.exe prompt. To use the code with Babun follow steps 1 and 2 for regular Windows installation using the cmd.exe prompt and then download and install Babun.

1. Open up a Babun prompt using the start menu.
    A. Run :code:`nano ~/.zshrc` to edit the file and copy and paste the .zshrc code block below into the bottom of the file.
        * Make sure you used the down arrow key to put your cursor at the bottom of the file
        * Once you've copied the block all you have to do in Babun is right click to paste, if you accidently highlighted something in Babun before pasting you will need to copy the block again.
        * If you installed Anaconda somewhere else you will need to tweak the path to match.
    B. Hit Ctrl+O and then Enter to save the file and then Ctrl+X to exit nano.
    C. Run :code:`source ~/.zshrc` to reload everything and try to start Python by running :code:`python3`
        * Exit Anaconda Python3 in Babun using **Ctrl+C** instead of Ctrl+Z or Ctrl+D
2. Run this command in the Babun prompt :code:`ln -s "/cygdrive/c/Users/$USER/Anaconda3/python.exe" "/usr/local/bin/python3"`
    * This allows the module to be linked properly in step 3.
    * As before you will need to tweak the path if you installed Anaconda somewhere else
3. Open a Babun prompt in the same directory that you want to install the modeling package in by right clicking in the folder explorer window or on the Desktop if that is your chosen location.
    A. Run the command :code:`git clone https://github.com/stadelmanma/netl-AP_MAP_FLOW.git`
    B. Run the command :code:`cd netl-AP_MAP_FLOW`
    C. Run the command :code:`dos2unix ./bin/*`
        * This converts Windows line endings :code:`\r\n` into unix line endings :code:`\n`
    C. Run :code:`python3 setup.py install --user` which will build the model and link the ApertureMapModelTools package into Anaconda's Python3 installation

.. code-block:: shell

    # Babun ~/.zshrc code block
    # Append Anaconda directories to override python 2.7 in /usr/bin/
    PATH="/cygdrive/c/Users/$USER/Anaconda3/:$PATH"
    PATH="/cygdrive/c/Users/$USER/Anaconda3/Scripts:$PATH"
    PATH="/cygdrive/c/Users/$USER/Anaconda3/Library/bin:$PATH"
    export PATH
    #
    # alias python3 to work interactively and python back to regular babun version
    alias python="/usr/bin/python"
    alias python3="/cygdrive/c/Users/$USER/Anaconda3/python.exe -i"

Basic Usage of APM Model
------------------------

Running the Model in a terminal::

    apm-run-lcl-model.py  model_initialization_file

Full usage instructions can be found in `<examples/running-the-flow-model.rst>`_.

Pitfalls:
---------
* Make sure required programs are added to the PATH environment variable, this will need to be manually performed in some cases
* If the model is compiled using 32-bit compiler, running too large of a map can cause a memory overflow error
* The LCL Model requires that all of the parent directories of output file locations already exist. Otherwise an error will be raised.

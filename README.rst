================================================================================
netl-ap-map-flow
================================================================================

.. image:: https://travis-ci.org/stadelmanma/netl-ap-map-flow.svg?branch=master
    :target: https://travis-ci.org/stadelmanma/netl-ap-map-flow

.. image:: https://ci.appveyor.com/api/projects/status/cyaxl3r2mbmymbp3?svg=true
    :target: https://ci.appveyor.com/project/stadelmanma/netl-ap-map-flow

.. image:: https://codecov.io/gh/stadelmanma/netl-ap-map-flow/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/stadelmanma/netl-ap-map-flow

.. image:: https://readthedocs.org/projects/netl-ap-map-flow/badge/?version=latest
    :target: http://netl-ap-map-flow.readthedocs.io/en/latest/?badge=latest

.. image:: https://zenodo.org/badge/50030017.svg
    :target: https://zenodo.org/badge/latestdoi/50030017

|

.. contents::

################################################################################
Overview
################################################################################

netl-ap-map-flow is a modeling suite written in Fortran and Python3 to perform local cubic law (LCL) simulations of single phase flow through a discrete fracture and analyze the data. Several tools written in `Python <https://www.python.org/>`_ provide added functionality are packaged in the **apmapflow** module. Dependencies are managed using `Anaconda <https://www.continuum.io/downloads>`_ through `conda-forge <http://conda-forge.github.io/>`_. `Paraview <http://www.paraview.org/>`_ is the recommended program to visualize the output using the legacy vtk files. The CSV output files can be visualized in ImageJ, Excel, etc. However, depending on how your chosen program reads in the image matrix, the image may appear inverted. The first value in the CSV files corresponds to bottom left corner of the fracture. After installation several scripts are avilable under with the prefix ``apm_``.

Full documentation is hosted on `read the docs <http://netl-ap-map-flow.readthedocs.io/en/latest/>`_.

 .. list-table:: **Summary of apmapflow submodules**

     * - **data_processing**
       - Provides an easy to use and extendable platform for post-processing a set of simulation data.
     * - **openfoam**
       - Implements an interface to create simulation cases for OpenFoam.
     * - **run_model**
       - Run the LCL model and manipulate input files programmatically.
     * - **unit_conversion**
       - Provides a unit conversion API powered by `pint <https://github.com/hgrecco/pint>`_

|

################################################################################
Installation
################################################################################

Quick Install Using Anaconda
--------------------------------------------------------------------------------
First install the Python3 version of `Anaconda <https://www.continuum.io/downloads>`_ or `Miniconda <https://conda.io/miniconda.html>`_ for your given platform and allow it to modify your ``PATH`` variable. Then run the following set of commands in a terminal. You can use the module directly in scripts by running ``import apmapflow`` or simply work with the scripts provided. A full list of scripts and basic usage is shown in the documentation section below.

.. code-block:: bash

    conda config --add channels conda-forge
    conda config --add channels stadelmanma
    conda update -y conda
    conda update -y python
    conda install netl-ap-map-flow

Install as a Developer
--------------------------------------------------------------------------------
To develop the package you will need to download Anaconda or Miniconda as above. Additionally, you will need to ensure that `git <https://git-scm.com/>`_, a Fortran compiler (I use `gfortran <https://gcc.gnu.org/wiki/GFortranBinaries>`_) and the make program are installed and available on your path. When using Windows it is recommended you make a copy of the ``mingw32-make.exe`` (or similarly named) executable and rename it ``make.exe``.

The following set of commands can be used in a terminal window to download and setup the package once the aforementioned programs have been installed.

.. code-block:: bash

    conda config --add channels conda-forge
    conda update -y conda
    conda update -y python
    git clone https://github.com/stadelmanma/netl-ap-map-flow.git
    cd netl-ap-map-flow
    conda install --file requirements.txt
    pip install -r test_requirements.txt
    python setup.py develop
    python ./bin/build_model -h
    python ./bin/build_model

################################################################################
Basic Usage of LCL Model
################################################################################

Running the model in a terminal::

    apm_run_lcl_model  model_initialization_file

Full usage instructions can be found in `<docs/examples/running-the-flow-model.rst>`_.


Notes/ Tips/ Pitfalls:
--------------------------------------------------------------------------------
* If the model is compiled using 32-bit compiler, running too large of a map can cause a memory overflow error.
* This guide assumes you install Anaconda3 locally. If you choose to install it system wide you will need to run some commands with :code:`sudo` in unix systems or in an elevated command prompt in Windows.
* Running :code:`./bin/build_model debug` will recompile the model using additional flags, code coverage and profiling
* Using Anaconda inside a `Babun <http://babun.github.io/>`_ prompt is tricky and takes some effort to get fully functional.
    * Your ``$PATH`` variable will need to be manually adjusted so the conda version of Python will shadow the default version used in Babun.
    * Direct use of the conda Python interpreter doesn't work and it instead needs to be called with ``python -i``.

Setting up the Modeling Package
-------------------------------

Getting the model and module up and running is a very straight forward process. After either cloning or downloading the repository into your chosen location the first order of business is downloading gfortran and `Python <https://www.python.org/>`_. If you are running Windows you will need to download `Cygwin <https://www.cygwin.com/>`_ or something similar to have access to gfortran and other unix commands. The module uses scipy for many operations and the simplest method to install the scipy stack is through Anaconda from `Continuum Analytics <http://continuum.io/downloads#all?>`_ on both Mac and Linux. Windows users can install the `WinPython <http://winpython.github.io/>`_ package, both provide the Spyder IDE and many other useful modules. The alternative is to manually install the required packages into your version of Python; `requirements.txt <https://github.com/stadelmanma/netl-AP_MAP_FLOW/blob/master/requirements.tx/>`_ lists out the minimum requirements however scipy may require additional packages on its own.

Once you have gfortran and Python the simplest method to build the flow model from source is by running `./bin/build_model` from the main directory. That script uses the make file in the `source` directory which sets proper OS flags. If that is not an option the following command should work for all systems assuming gfortran is installed. If the flag -DWIN64=1 is added default file paths will be set to the windows convention. The following block can be C/P into the command prompt if you are currently in the `source` directory.

.. code-block:: bash

    gfortran -c APM_MODULE.F
    gfortran -c UNIT_CONVERSION_MODULE.F
    gfortran -o APM-MODEL.EXE APM_MODULE.F UNIT_CONVERSION_MODULE.F APERTURE_MAP_FLOW.F APM_SUBROUTINES.F APM_SOLVER.F APM_FLOW.F APM_OUTPUT.F -O2 -fimplicit-none -fwhole-file -fcheck=all -std=f2008 -pedantic -fbacktrace -cpp -DWIN64=0 -Wall -Wline-truncation -Wcharacter-truncation -Wsurprising -Waliasing -Wunused-parameter
    mv APM-MODEL.EXE ..



The final step is optional but can simplfy usage of the module. Python stores all third party packages in a directory. The location of that directory can be found using the following command.  

.. code-block:: bash

    python3 -m site --user-site


 


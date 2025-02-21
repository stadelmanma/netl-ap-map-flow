"""
================================================================================
Run Model
================================================================================
| This stores the basic classes and functions needed to the run model

| Written By: Matthew Stadelman
| Date Written: 2016/06/16
| Last Modifed: 2017/04/05

.. toctree::
    :maxdepth: 2

    run_model/bulk_run.rst
    run_model/run_model.rst

"""
from .run_model import InputFile, estimate_req_RAM, run_model
from .run_model import DEFAULT_MODEL_PATH, DEFAULT_MODEL_NAME
from .bulk_run import BulkRun

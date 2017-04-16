"""
Automatically imports several modules.
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2017/04/15
#
"""
#
import logging.config as _logging_config
import os as _os
import sys as _sys
import PIL as _pil
from .__core__ import DataField, FractureImageStack
from .__core__ import _get_logger, set_main_logger_level
from .__core__ import files_from_directory, load_infile_list
from .__core__ import calc_percentile, calc_percentile_num, get_data_vect
from . import DataProcessing
from . import RunModel
from . import OpenFoam


__version__ = '0.0.2'
DEFAULT_MODEL_NAME = 'apm-lcl-model.exe'


# reading logging config
_config_file = _os.path.join(_os.path.dirname(__file__), 'logging.conf')
_logging_config.fileConfig(_config_file)

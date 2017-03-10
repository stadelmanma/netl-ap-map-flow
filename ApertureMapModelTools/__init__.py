"""
Automatically imports several modules.
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2017/02/03
#
"""
#
import logging.config as _logging_config
import os as _os
import sys as _sys
import PIL as _pil
#
# checking python version
if _sys.version_info < (3, 4):
    raise Exception('ApertureMapModelTools requires Python 3.4 or greater')

#
# checking pillow version
try:
    _pil_version = _pil.__version__
except AttributeError:
    _pil_version = _pil.PILLOW_VERSION
if _pil_version < '3.4.0':
    raise Exception('ApertureMapModelTools requires pillow 3.4.0 or greater')

#
from .__core__ import DataField, FractureImageStack
from .__core__ import _get_logger, set_main_logger_level
from .__core__ import files_from_directory, load_infile_list
from .__core__ import calc_percentile, calc_percentile_num, get_data_vect
from . import DataProcessing
from . import RunModel
from . import OpenFoam

# reading logging config
_config_file = _os.path.join(_os.path.dirname(__file__), 'logging.conf')
_logging_config.fileConfig(_config_file)

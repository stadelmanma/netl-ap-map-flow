"""
Automatically imports several modules.
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/06/14
#
"""
#
import logging.config as _logging_config
import os as _os
import sys as _sys
#
# checking python version
if _sys.version_info < (3, 3):
    raise Exception('ApertureMapModelTools requires Python 3.3 or greater')

#
from .__core__ import DataField, StatFile
from .__core__ import files_from_directory, load_infile_list
from .__core__ import calc_percentile, calc_percentile_num, get_data_vect
from . import UnitConversion
from . import DataProcessing
from . import RunModel
from . import OpenFoam

# reading logging config
_config_file = _os.path.join(_os.path.dirname(__file__), 'logging.conf')
_logging_config.fileConfig(_config_file)

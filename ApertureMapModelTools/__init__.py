"""
Automatically imports the DataProcessing and units modules.
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/06/14
#
"""
#
import _sys
#
# checking python version
if _sys.version_info < (3, 3):
    raise Exception('ApertureMapModelTools requires Python 3.3 or greater')
#
#
from .__core__ import DataField, StatFile
from .__core__ import files_from_directory, load_infile_list
from .__core__ import calc_percentile, calc_percentile_num, get_data_vect
from . import UnitConversion
from . import DataProcessing

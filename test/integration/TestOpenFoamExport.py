"""
Handles testing of the OpenFOAM export module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
#
import os
from ApertureMapModelTools.__core__ import DataField
from ApertureMapModelTools.OpenFoamExport import OpenFoamExport
#
class TestOpenFoamExport:
    r"""
    Executes a set of functions to handle testing of the export routines
    """
    def setup_class(self):
        pass

    def test_export(self):
        #
        map_file = os.path.join(FIXTURE_DIR,'TEST-FRACTURES','PARALELL-PLATE-10VOX.TXT')
        self._field = DataField(map_file)
        #
        params = {
            'convertToMeters' : '0.000010000',
            'numbersOfCells' : '(5 10 15)',
            'cellExpansionRatios' : 'simpleGrading (1 2 3)',
            #
            'boundary.left.type' : 'empty',
            'boundary.right.type' : 'empty',
            'boundary.top.type' : 'wall',
            'boundary.bottom.type' : 'wall',
            'boundary.front.type' : 'wall',
            'boundary.back.type' : 'wall'
        }
        export = OpenFoamExport(self._field, avg_fact=10.0, export_params=params)
        export.write_mesh_file(TEMP_DIR)
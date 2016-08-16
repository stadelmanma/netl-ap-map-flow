"""
Handles testing of the OpenFoam.ParallelMeshGen submodule module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/08/16
#
"""
#
import os
import pytest
import scipy as sp
from ApertureMapModelTools.OpenFoam.__ParallelMeshGen__ import DataFieldRegion
from ApertureMapModelTools.OpenFoam.__ParallelMeshGen__ import BlockMeshRegion
from ApertureMapModelTools.OpenFoam.__ParallelMeshGen__ import MergeGroup
from ApertureMapModelTools.OpenFoam import ParallelMeshGen


class TestParallelMeshGen:
    r"""
    Executes a set of functions to handle testing of the ParalellMeshGen class
    """

    def test_data_field_region(self, data_field_class):
        data_field = data_field_class()
        data_field.create_point_data()
        #
        region = DataFieldRegion(data_field.data_map[0:5, 0:5],
                                 data_field.point_data[0:5, 0:5, :])
        assert region.data_map.shape == (5, 5)
        assert region.point_data.shape == (5, 5, 4)
        #
        # testing error conditions
        with pytest.raises(ValueError):
            DataFieldRegion(data_field.data_map[0:5, 0:5],
                            data_field.point_data[0:5, 0:7, :])
        #
        with pytest.raises(NotImplementedError):
            region.parse_data_file()
        #
        with pytest.raises(NotImplementedError):
            region.create_point_data()

    def test_block_mesh_region(self, data_field_class):
        data_field = data_field_class()
        mesh_region = BlockMeshRegion(data_field, 10, 7, 5, None)
        #
        # testing mesh_region attributes
        assert mesh_region.avg_fact == 10
        assert mesh_region.x_shift == 7
        assert mesh_region.z_shift == 5
        assert sp.all(mesh_region._vertices[:, 0] - 10*7 >= 0)
        assert sp.all(mesh_region._vertices[:, 2] - 10*5 >= 0)
        #
        # testing mesh code runs, can't test if files actually exist
        sys_dir = os.path.join(FIXTURE_DIR, 'system')
        path = os.path.join(TEMP_DIR, 'simple-test')
        mesh_region.run_block_mesh('simple', path, sys_dir, 'Test Worker 0', True)
        #
        path = os.path.join(TEMP_DIR, 'symmetry-test')
        mesh_region.run_block_mesh('symmetry', TEMP_DIR, sys_dir, 'Test Worker 0', True)
        #
        # sending a failing case
        with pytest.raises(OSError):
            mesh_region.run_block_mesh('simple', '', sys_dir, 'Test Worker 0', True)

    def test_merge_group(self):
        pass

    def test_parallel_mesh_gen(self, data_field_class):
        pass

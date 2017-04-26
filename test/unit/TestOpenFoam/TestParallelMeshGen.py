"""
Handles testing of the OpenFoam.ParallelMeshGen submodule module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/08/18
#
"""
#
import os
import pytest
import sys
import scipy as sp
import ApertureMapModelTools.openfoam.parallel_mesh_gen as pmg_submodule
from ApertureMapModelTools.openfoam.parallel_mesh_gen import DataFieldRegion
from ApertureMapModelTools.openfoam.parallel_mesh_gen import BlockMeshRegion
from ApertureMapModelTools.openfoam.parallel_mesh_gen import MergeGroup
from ApertureMapModelTools.openfoam import ParallelMeshGen


@pytest.mark.xfail(sys.platform == 'win32', reason="OpenFoam doesn't natively run on Windows")
@pytest.mark.usefixtures('set_openfoam_path')
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
            region.create_point_data()

    def test_block_mesh_region(self, data_field_class):
        data_field = data_field_class()
        offset_reg = data_field_class()
        mesh_region = BlockMeshRegion(data_field, 10, 7, 5, None, offset_reg)
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
            path = os.path.join(TEMP_DIR, 'blockmesh-exit1')
            mesh_region.run_block_mesh('simple', path, sys_dir, 'Test Worker 0', True)

    def test_merge_group(self):
        #
        # setting up first group and testing properties
        sides = ['left', 'right', 'top', 'bottom']
        ext_pat = {side: side+'0' for side in ['right', 'top']}
        ext_pat.update({'left': 'left', 'bottom': 'bottom'})
        merge_group0 = MergeGroup(0, ext_pat, TEMP_DIR)
        assert merge_group0.region_id == 0
        assert merge_group0.region_dir == os.path.join(TEMP_DIR, 'mesh-region0')
        assert merge_group0.regions == sp.array([0], ndmin=2, dtype=int)
        assert merge_group0.external_patches == {key: [val] for key, val in ext_pat.items()}
        #
        # setting up additional merge groups to test directions
        ext_pat = {side: side+'1' for side in ['left', 'right', 'top']}
        ext_pat.update({'bottom': 'bottom'})
        merge_group1 = MergeGroup(1, ext_pat, TEMP_DIR)
        ext_pat = {side: side+'2' for side in ['right', 'top', 'bottom']}
        ext_pat.update({'left': 'left'})
        merge_group2 = MergeGroup(2, ext_pat, TEMP_DIR)
        ext_pat = {side: side+'3' for side in sides}
        merge_group3 = MergeGroup(3, ext_pat, TEMP_DIR)
        #
        # adding place holder directories for rmtree to remove
        for i in [1, 2, 3]:
            os.mkdir(os.path.join(TEMP_DIR, 'mesh-region{}'.format(i)))
        #
        # testing merge directions
        merge_group0.merge_regions(merge_group1, 'right', 'test-thread0')
        merge_group2.merge_regions(merge_group3, 'right', 'test-thread2')
        assert sp.all(merge_group0.regions == sp.array([0, 1], ndmin=2, dtype=int))
        assert merge_group0.external_patches == {'left': ['left'], 'right': ['right1'],
                                                 'top': ['top0', 'top1'], 'bottom': ['bottom', 'bottom']}
        merge_group0.merge_regions(merge_group2, 'top', 'test-thread0')
        #
        # testing case when mergeMeshes return code != 0
        ext_pat = {side: side+'2' for side in ['right', 'top', 'bottom']}
        ext_pat.update({'left': 'left'})
        merge_group2 = MergeGroup(2, ext_pat, TEMP_DIR)
        ext_pat = {side: side+'3' for side in sides}
        merge_group3 = MergeGroup(3, ext_pat, os.path.join(TEMP_DIR, 'mergemesh-exit1'))
        with pytest.raises(OSError):
            merge_group2.merge_regions(merge_group3, 'right', 'test-thread2')
        #
        # testing case when stitchMeshes return code != 0
        internal_patches = [('patch1', 'patch2')]
        merge_group2.region_dir = os.path.join(TEMP_DIR, 'stitchmesh-exit1')
        merge_group2.stitch_patches(internal_patches, 'test-thread2')
        assert pmg_submodule._stitchMesh_error.is_set()

    def test_parallel_mesh_gen(self, data_field_class):
        r"""
        only testing initializtion and merge_queue generation. The other functions
        are exercised during integration testing
        """
        #
        # testing ParallelMeshGen init method
        #
        field = data_field_class()
        # testing defaults first
        pmg = ParallelMeshGen(field, 'system-test')
        assert pmg.system_dir == 'system-test'
        assert pmg.nprocs == 4
        assert pmg.mesh_params == {}
        assert pmg.merge_groups == []
        assert pmg.avg_fact == 1.0
        assert pmg.nx == field.nx
        assert pmg.nz == field.nz
        assert sp.all(pmg._mask)
        #
        # checking pmg only has references to data initially, new references are
        # created if the 'threshold' method was used because it resets the arrays
        # using the internal _field which was cloned and independent of the original
        assert id(pmg.data_map) == id(field.data_map)
        assert id(pmg.point_data) == id(field.point_data)
        assert id(pmg._field) != id(field)
        #
        # testing non default values
        params = {'test-key': 'test-value'}
        pmg = ParallelMeshGen(field, 'system-test', nprocs=15, avg_fact=7.0,
                              mesh_params=params)
        assert pmg.nprocs == 15
        assert pmg.avg_fact == 7.0
        assert pmg.mesh_params == params
        #
        # Testing ParaMeshGen _create_merge_queue method
        #
        # testing merge queue for (2**, 2**n) grid shapes
        grid = sp.reshape(sp.arange(4, dtype=int), (2, 2))
        queue, new_grid = pmg._create_merge_queue(grid, 'right')
        assert queue.qsize() == 2
        pairs = []
        while queue.qsize():
            pairs.append(queue.get())
        assert pairs == [(0, 1), (2, 3)]
        assert sp.all(new_grid == sp.array([[0], [2]], ndmin=2, dtype=int))
        #
        grid = sp.reshape(sp.arange(4, dtype=int), (2, 2))
        queue, new_grid = pmg._create_merge_queue(grid, 'top')
        assert queue.qsize() == 2
        pairs = []
        while queue.qsize():
            pairs.append(queue.get())
        assert pairs == [(0, 2), (1, 3)]
        assert sp.all(new_grid == sp.array([[0, 1]], ndmin=2, dtype=int))
        #
        # testing merge queue for (n x n) grid shapes
        grid = sp.reshape(sp.arange(6, dtype=int), (2, 3))
        queue, new_grid = pmg._create_merge_queue(grid, 'right')
        assert queue.qsize() == 2
        pairs = []
        while queue.qsize():
            pairs.append(queue.get())
        assert pairs == [(0, 1), (3, 4)]
        assert sp.all(new_grid == sp.array([[0, 2], [3, 5]], ndmin=2, dtype=int))
        #
        grid = sp.reshape(sp.arange(6, dtype=int), (3, 2))
        queue, new_grid = pmg._create_merge_queue(grid, 'top')
        assert queue.qsize() == 2
        pairs = []
        while queue.qsize():
            pairs.append(queue.get())
        assert pairs == [(0, 2), (1, 3)]
        assert sp.all(new_grid == sp.array([[0, 1], [4, 5]], ndmin=2, dtype=int))

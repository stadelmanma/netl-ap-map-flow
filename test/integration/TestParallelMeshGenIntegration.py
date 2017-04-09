"""
Handles testing of the OpenFoam.ParallelMeshGen class
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/08/16
#
"""
import os
import pytest
import sys
import scipy as sp
from ApertureMapModelTools import DataField
from ApertureMapModelTools.OpenFoam import OpenFoamFile, OpenFoamDict, OpenFoamList
import ApertureMapModelTools.OpenFoam.__ParallelMeshGen__ as pmg_submodule
from ApertureMapModelTools.OpenFoam import ParallelMeshGen


@pytest.mark.xfail(sys.platform == 'win32', reason="OpenFoam doesn't natively run on Windows")
def test_parallel_mesh_gen():
    #
    infile = os.path.join(FIXTURE_DIR, 'maps', 'Fracture1ApertureMap-10avg.txt')
    field = DataField(infile)
    offset_field = DataField(sp.ones(field.data_map.shape))
    #
    # adding a fake boundary file to the mesh-region0 directory
    # this will be overwritten if testing with real OpenFoam programs
    bnd_file = OpenFoamFile(os.path.join('constant', 'polyMesh'), 'boundary')
    face_list = OpenFoamList('boundary')
    face_list.append(OpenFoamDict('top', {'numFaces': 10}))
    face_list.append(OpenFoamDict('mergeTB0', {'numFaces': 0}))
    face_list.append('non-dict-entry blah blah')
    bnd_file[face_list.name] = face_list
    out_path = os.path.join(TEMP_DIR, 'test-pmg', 'mesh-region0')
    bnd_file.write_foam_file(path=out_path, overwrite=True)
    #
    # initialzing mesh generator
    sys_dir = os.path.join(FIXTURE_DIR, 'system')
    out_path = os.path.join(TEMP_DIR, 'test-pmg')
    parallel_mesh_gen = ParallelMeshGen(field, sys_dir, offset_field=offset_field)
    #
    # running each possible mesh type
    parallel_mesh_gen.generate_mesh(mesh_type='simple', path=out_path,
                                    ndivs=2, overwrite=True)
    #
    parallel_mesh_gen.generate_mesh(mesh_type='threshold', path=out_path,
                                    ndivs=4, overwrite=True)
    #
    parallel_mesh_gen.generate_mesh(mesh_type='symmetry', path=out_path,
                                    ndivs=2, overwrite=True)
    #
    # hitting error cases
    parallel_mesh_gen = ParallelMeshGen(field, sys_dir)
    #
    # adding a fake blockMeshDict file to throw an error in mesh gen
    bnd_file.name = 'blockMeshDict'
    out_path = os.path.join(TEMP_DIR, 'test-pmg2-fail', 'mesh-region3')
    bnd_file.write_foam_file(path=out_path, overwrite=True)
    out_path = os.path.join(TEMP_DIR, 'test-pmg2-fail')
    with pytest.raises(OSError):
        parallel_mesh_gen._create_subregion_meshes(4, mesh_type='simple',
                                                   path=out_path)
    #
    pmg_submodule._blockMesh_error.clear()
    parallel_mesh_gen._create_subregion_meshes(4, mesh_type='simple',
                                               path=out_path, overwrite=True)
    grid = sp.arange(0, 16, dtype=int)
    grid = sp.reshape(grid, (4, 4))
    #
    # renaming a merge directory to throw an error
    parallel_mesh_gen.merge_groups[3].region_dir += '-mergemesh-exit1'
    with pytest.raises(OSError):
        parallel_mesh_gen._merge_submeshes(grid)

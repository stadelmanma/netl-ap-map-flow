"""
Handles testing of the OpenFoam.ParallelMeshGen class
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/08/16
#
"""
import os
from time import sleep
from ApertureMapModelTools import DataField
from ApertureMapModelTools.OpenFoam import OpenFoamFile, OpenFoamDict, OpenFoamList
from ApertureMapModelTools.OpenFoam import ParallelMeshGen


def test_parallel_mesh_gen():
    #
    infile = os.path.join(FIXTURE_DIR, 'TEST-FRACTURES', 'Fracture1ApertureMap-10avg.txt')
    field = DataField(infile)
    #
    # adding a fake boundary file to the mesh-region0 directory
    # this will be overwritten if testing with real OpenFoam programs
    bnd_file = OpenFoamFile(os.path.join('constant', 'polyMesh'), 'boundary')
    face_list = OpenFoamList('boundary')
    face_list.append(OpenFoamDict('top', {'numFaces': 10}))
    face_list.append(OpenFoamDict('mergeTB0', {'numFaces': 0}))
    bnd_file[face_list.name] = face_list
    bnd_file.write_foam_file(path=os.path.join(TEMP_DIR, 'test-pmg', 'mesh-region0'), overwrite=True)
    #
    sys_dir = os.path.join(FIXTURE_DIR, 'system')
    out_path = os.path.join(TEMP_DIR, 'test-pmg')
    parallel_mesh_gen = ParallelMeshGen(field, sys_dir)
    #
    # running each possible mesh type
    parallel_mesh_gen.generate_mesh(mesh_type='simple', path=out_path, ndivs=2, overwrite=True)
    sleep(1)
    print('\n\n')
    #
    parallel_mesh_gen.generate_mesh(mesh_type='threshold', path=out_path, ndivs=4, overwrite=True)
    sleep(1)
    print('\n\n')
    #
    parallel_mesh_gen.generate_mesh(mesh_type='symmetry', path=out_path, ndivs=2, overwrite=True)

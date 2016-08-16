#!/usr/bin/env python3
r"""
Little script designed to semi-automatically generate a mesh
"""
import os
import sys
from ApertureMapModelTools import DataField
from ApertureMapModelTools.OpenFoam import ParallelMeshGen

# setting up a basic help message
usage = 'Usage: mesh_gen.py [map file] [avg_fact] [mesh_type] [out_path]\n'
usage += 'All arguments are required.\n'

if len(sys.argv) < 5:
    print(usage)
    exit(1)

if len(sys.argv) > 5:
    print(usage)
    exit(1)

if sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print('Usage: mesh_gen.py [map file] [avg_fact] [mesh_type] [out_path]')
    exit(0)

# getting commandline arg values
infile = sys.argv[1]
avg_fact = int(sys.argv[2])
mesh_type = sys.argv[3]
out_path = sys.argv[4]

# setting mesh params
mesh_params = {
    'convertToMeters': '2.680E-5',
    'numbersOfCells': '(1 1 1)',
    #
    'boundary.left.type': 'wall',
    'boundary.right.type': 'wall',
    'boundary.top.type': 'wall',
    'boundary.bottom.type': 'wall',
    'boundary.front.type': 'wall',
    'boundary.back.type': 'wall'
}

# setting up parallel mesh generator
map_field = DataField(infile)
system_dir = 'system'
np = 16
print('Setting generator up...')
pmg = ParallelMeshGen(map_field, system_dir, nprocs=np, avg_fact=avg_fact, mesh_params=mesh_params)

# creating the mesh
print('Creating the mesh...')
pmg.generate_mesh(mesh_type, path=out_path, overwrite=False)
reg_dir = os.path.join(out_path, 'mesh-region0', '*')
os.system('mv {} {}'.format(reg_dir, out_path))
os.system('rmdir {}'.format(os.path.join(out_path, 'mesh-region0')))

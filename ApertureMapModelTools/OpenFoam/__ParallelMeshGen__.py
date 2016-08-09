"""
A class build to handle generation of a blockMeshDict in parallel using the
mergeMeshes and stitchMesh OpenFoam utilities.
#
Written By: Matthew Stadelman
Date Written: 2016/08/09
Last Modifed: 2016/08/09
#
"""
import os
import scipy as sp
from subprocess import Popen
from ..__core__ import DataField
from .__BlockMeshDict__ import BlockMeshDict
#
########################################################################
#

class BlockMeshRegion(BlockMeshDict):
    r"""
    Used to handle a sub-set of field point data for parallel mesh generation
    """
    def __init__(self, data, point_data, avg_fact, x_shift, z_shift, mesh_params):
        r"""
        Takes a field object and a set of mesh params to set the
        properties of the blockMeshDict

        data : sp.array,
        avg_fact : float, optional, number of voxels along the X and Z axes.
        mesh_params : dict, optional, a dictionary containing parameters to
        use instead of the defaults
        """
        super().__init__('polyMesh', 'blockMeshDict')
        #
        self.nz, self.nx = data.shape
        self.data_map = sp.copy(data)
        self.data_vector = sp.ravel(data)
        self.point_data = sp.copy(point_data)
        self.avg_fact = avg_fact
        self.mesh_params = dict(BlockMeshDict.DEFAULT_PARAMS)
        self.face_labels = {}
        #
        # setting up the internal field
        self._field = DataField(None)
        self._field.nz, self._field.nx = self.nz, self.nx # TODO: TEST THIS!!!!!!!1
        self._field.data_map = sp.copy(data)
        self._field.data_vector = sp.ravel(data)
        self._field.point_data = sp.copy(point_data)
        self._field._define_cell_interfaces()
        #
        # defining default mesh attributes
        self._vertices = None
        self._blocks = None
        self._edges = None
        self._faces = None
        self._merge_patch_pairs = None
        #
        # copying data and updating params
        if mesh_params is not None:
            self.mesh_params.update(mesh_params)
        #
        self.generate_simple_mesh()


class ParallelMeshGen(object):
    r"""
    Handles creation of a large mesh in parallel utilizing the OpenFoam
    utilties mergeMesh and stitchMesh.
    """
    def __init__(self, field, system_dir, avg_fact=1.0, mesh_params=None):
        #
        super().__init__()
        if mesh_params is not None:
            mesh_params = dict(mesh_params)
        #
        # field attributes that are copied over
        self.nx = None
        self.nz = None
        self.data_map = sp.array([])
        self.data_vector = sp.array([])
        self.point_data = sp.array([])
        field.create_point_data()
        field.copy_data(self)
        #
        self.avg_fact = avg_fact
        self.mesh_params = mesh_params
        self._field = field.clone()


    def general_workflow(self):
        from ..__core__ import DataField
        right_df = DataField('right-side-map.txt')
        left_df = DataField('left-side-map.txt')
        #
        # outputting meshes
        mesh = BlockMeshDict(left_df)
        mesh.mesh_params['boundary.mergeRL0.type'] = 'empty'
        mesh.face_labels['boundary.mergeRL0'] = sp.copy(mesh.face_labels['boundary.right'])
        del mesh.face_labels['boundary.right']
        mesh.write_foam_file(path='mesh-region0', overwrite=True)
        mesh = BlockMeshDict(right_df)
        mesh._vertices[:, 0] += left_df.nx
        mesh.mesh_params['boundary.mergeLR1.type'] = 'empty'
        mesh.face_labels['boundary.mergeLR1'] = sp.copy(mesh.face_labels['boundary.left'])
        del mesh.face_labels['boundary.left']
        mesh.write_foam_file(path='mesh-region1', overwrite=True)
        #
        # copying contents of system_dir supplied
        system_dir = 'system'
        cmd = 'cp -r {0} {1}'
        os.system(cmd.format(system_dir, os.path.join('mesh-region0', 'system')))
        os.system(cmd.format(system_dir, os.path.join('mesh-region1', 'system')))
        #
        # generating meshes, merging them and stitching patches together
        proc = Popen(('blockMesh', '-case', 'mesh-region0'))
        proc.wait()
        proc = Popen(('blockMesh', '-case', 'mesh-region1'))
        proc.wait()
        proc = Popen(('mergeMeshes', '-overwrite', 'mesh-region0', 'mesh-region1'))
        proc.wait()
        os.system('rm -rf {}'.format('mesh-region1'))
        proc = Popen(('stitchMesh', '-case', 'mesh-region0', '-overwrite', 'mergeRL0', 'mergeLR1'))
        proc.wait()




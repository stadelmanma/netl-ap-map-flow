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
import re
from shutil import rmtree
from subprocess import Popen, call
import scipy as sp
from ..__core__ import DataField
from .__openfoam_core__ import OpenFoamFile, OpenFoamDict, OpenFoamList
from .__BlockMeshDict__ import BlockMeshDict
#
########################################################################
#


class DataFieldRegion(DataField):
    r"""
    Used to manipulate a specfic data region of a DataField. In order to
    maintain data integrity point data is not able to be recalculated here.
    """
    def __init__(self, data, point_data):
        #
        # setting up the region
        super().__init__(None)
        if data.shape != point_data.shape[0:2]:
            msg = 'data and point_data have different dimensions: {} != {}'
            raise ValueError(msg.format(data.shape, point_data.shape[:2]))
        #
        self.nz, self.nx = data.shape
        self.data_map = sp.copy(data)
        self.data_vector = sp.ravel(data)
        self.point_data = sp.copy(point_data)
        #
        self._raw_data = sp.copy(data)
        self._define_cell_interfaces()

    def parse_data_file(self, delim='auto', **kwargs):
        msg = 'DataFieldRegions cannot read new data use a DataField instead'
        raise NotImplementedError(msg)

    def create_point_data(self):
        msg = 'DataFieldRegions cannot have point_data recalculated'
        raise NotImplementedError(msg)



class BlockMeshRegion(BlockMeshDict):
    r"""
    Used to handle a sub-set of field point data for parallel mesh generation
    """
    def __init__(self, region, avg_fact, x_shift, z_shift, mesh_params):
        r"""
        Takes a field object and a set of mesh params to set the
        properties of the blockMeshDict. The x_shift and z_shift values are
        multipled by avg_fact.

        data_region : DataFieldRegion object
        avg_fact : float, number of voxels along the X and Z axes.
        x_shift : int, number of voxels shifted from orgin
        z_shift : int, number of voxels shifted from origin
        mesh_params : dict, a dictionary containing parameters to
        use instead of the defaults
        """
        self.x_shift = x_shift
        self.z_shift = z_shift
        super().__init__(region, avg_fact, mesh_params)

    def _create_blocks(self, cell_mask=None):
        r"""
        Generates blocks and verticies the same as the parent class and
        then applies the x and z shift
        """
        #
        super()._create_blocks(cell_mask)
        self._vertices[:, 0] += self.avg_fact * self.x_shift
        self._vertices[:, 2] += self.avg_fact * self.z_shift



class ParallelMeshGen(object):
    r"""
    Handles creation of a large mesh in parallel utilizing the OpenFoam
    utilties mergeMesh and stitchMesh.
    """
    def __init__(self, field, system_dir, nprocs=4, **kwargs):
        #
        super().__init__()
        mesh_params = kwargs.pop('mesh_params', None)
        mesh_params = mesh_params or {}
        #
        # field attributes that are copied over
        field.create_point_data()
        self.nx = field.nx
        self.nz = field.nz
        self.data_map = field.data_map
        self.point_data = field.point_data
        #
        self.system_dir = system_dir
        self.nprocs = nprocs
        self.avg_fact = kwargs.pop('avg_fact', 1.0)
        self.mesh_params = mesh_params

    def generate_mesh(self, mesh_type='simple', path='.', **kwargs):
        r"""
        Generates multiple mesh types and outputs them to a specific path.
        Valid mesh_types are: simple, threshold and symmetry. Additional
        kwargs need to be supplied for the given mesh type if it needs
        additional keywords.
        """
        #
        # I only want to check for the existance of the mesh-region0 directory
        # because it stores the final results
        # could be worth while to move the contents of the constant directory
        # to the top level and delete the mesh-region0 directory
        #
        # setting up initial region grid
        ndivs = 2
        grid = sp.arange(0, ndivs*ndivs, dtype=int)
        grid = sp.reshape(grid, (ndivs, ndivs))
        #
        self._create_subregion_meshes(ndivs, mesh_type=mesh_type, **kwargs)
        #self._merge_submeshes(grid, path)
        #self._remove_leftover_patches(path)

    def _create_subregion_meshes(self, ndivs, **kwargs):
        r"""
        Divides the data map into smaller regions and creates a BlockMeshRegion
        object for each one.
        """
        # TODO: This part can be and needs to be parallelized down the road
        #
        # calculating region sizes r0 is first the col and row 0
        # rn is the rest of the region sizes
        r0_nx = int(self.nx/ndivs) + self.nx % ndivs
        r0_nz = int(self.nz/ndivs) + self.nz % ndivs
        rn_nx = int((self.nx - r0_nx)/(ndivs - 1))
        rn_nz = int((self.nz - r0_nz)/(ndivs - 1))
        #
        # setting up data slices
        slice_list = [(slice(0, r0_nz), slice(0, r0_nx))]
        x_st = slice_list[-1][1].stop
        for i in range(1, ndivs):
            slice_list.append((slice(0, r0_nz), slice(x_st, x_st+rn_nx)))
            x_st = slice_list[-1][1].stop
        #
        z_st = slice_list[-1][0].stop
        for i in range(1, ndivs):
            slice_list.append((slice(z_st, z_st+rn_nz), slice(0, r0_nx)))
            x_st = slice_list[-1][1].stop
            #
            for i in range(1, ndivs):
                x_en, z_en = x_st+rn_nx, z_st+rn_nz
                slice_list.append((slice(z_st, z_en), slice(x_st, x_en)))
                x_st = slice_list[-1][1].stop
            #
            z_st = slice_list[-1][0].stop

        for i, (z_slice, x_slice) in enumerate(slice_list):
            #
            # this is where I will check nprocs and spawn new ones when finish
            #
            region_mesh = self._setup_region(i, z_slice, x_slice, **kwargs)
            proc = self._create_region_mesh(i, region_mesh, **kwargs)
            proc.wait()
            if proc.poll() != 0:
                raise OSError

    def _setup_region(self, region_id, z_slice, x_slice, **kwargs):
        r"""
        sets up an individual mesh region
        """
        #
        patch_names = ['mergeLR{}', 'mergeRL{}', 'mergeTB{}', 'mergeBT{}']
        patch_names = ['boundary.'+patch for patch in patch_names]
        #
        # setting offset values and region
        x_offset = x_slice.start
        z_offset = z_slice.start
        region = DataFieldRegion(self.data_map[z_slice, x_slice],
                                 self.point_data[z_slice, x_slice, :])
        #
        # creating regional mesh
        args = [region, self.avg_fact, x_offset, z_offset, self.mesh_params]
        region_mesh = BlockMeshRegion(*args)
        #
        # regenerating a threshold mesh if requsted
        mesh_type = kwargs.pop('mesh_type', 'simple')
        if mesh_type == 'threshold':
            low = kwargs.pop('min_value', 0.0)
            high = kwargs.pop('max_value', 1e9)
            region_mesh.generate_threshold_mesh(min_value=low, max_value=high)
        #
        # updating patches with ones to merge
        face_labels = region_mesh.face_labels
        if x_slice.start != 0:
            patch = patch_names[0].format(region_id)
            region_mesh.mesh_params[patch+'.type'] = 'empty'
            region_mesh.face_labels[patch] = face_labels.pop('boundary.left')
        #
        if x_slice.stop != self.nx:
            patch = patch_names[1].format(region_id)
            region_mesh.mesh_params[patch+'.type'] = 'empty'
            region_mesh.face_labels[patch] = face_labels.pop('boundary.right')
        #
        if z_slice.start != 0:
            patch = patch_names[3].format(region_id)
            region_mesh.mesh_params[patch+'.type'] = 'empty'
            region_mesh.face_labels[patch] = face_labels.pop('boundary.bottom')
        #
        if z_slice.stop != self.nz:
            patch = patch_names[2].format(region_id)
            region_mesh.mesh_params[patch+'.type'] = 'empty'
            region_mesh.face_labels[patch] = face_labels.pop('boundary.top')
        #
        return region_mesh

    def _create_region_mesh(self, region_id, region_mesh, **kwargs):
        r"""
        Handles the process of generating a mesh, writing it and then
        calling blockMesh. Returns a Popen object.
        """
        #
        # setting important keywords
        mesh_type = kwargs.pop('mesh_type', 'simple')
        overwrite = kwargs.pop('overwrite', False)
        path = kwargs.pop('path', '.')
        path = os.path.join(path, 'mesh-region{}'.format(region_id))
        #
        # writing files based on mesh type
        if mesh_type == 'symmetry':
            region_mesh.write_symmetry_plane(path=path, overwrite=overwrite)
        else:
            region_mesh.write_foam_file(path=path, overwrite=overwrite)
        #
        # copying system directory to region directory
        cmd = 'cp -r {0} {1}'
        new_sys_path = os.path.join(path, 'system')
        os.system(cmd.format(self.system_dir, new_sys_path))
        #
        # running blockMesh
        proc = Popen(('blockMesh', '-case', path))
        return proc

    def _merge_submeshes(self, grid, path):
        r"""
        Handles merging and stitching of meshes based on alternating rounds
        of horizontal pairing and then vertical pairing.
        """
        #
        direction = 'left'
        while sp.size(grid) > 1:
            #
            # getting merge list and updating grid
            merge_list, grid = self._create_merge_list(grid, direction)
            for master, slave in merge_list:
                #
                # I think I'll need to use the Threading module to make this
                # since  I have to manage two processes
                #
                self._merge_mesh(master, slave, direction, path)
            #
            # switching directions
            direction = 'top' if direction == 'left' else 'left'

    @staticmethod
    def _create_merge_list(grid, direction):
        r"""
        Determines the region merge list based on the grid supplied
        """
        #
        if direction == 'left':
            # Horizontally pairing up regions
            new_nx = int(grid.shape[1]/2) + grid.shape[1] % 2
            new_grid = -sp.ones(grid.shape[0]*new_nx, dtype=int)
            merge_list = []
            #
            for iz in range(grid.shape[0]):
                i = iz*new_nx
                ix = 0
                for ix in range(0, grid.shape[1]-1, 2):
                    merge_list.append((grid[iz, ix], grid[iz, ix+1]))
                    new_grid[i] = grid[iz, ix]
                    i += 1
                if ix != grid.shape[1]-2:
                    new_grid[i] = grid[iz, -1]
            #
            new_grid = sp.reshape(new_grid, (grid.shape[0], new_nx))
        #
        elif direction == 'top':
            # Vertically pairing up regions
            new_nz = int(grid.shape[0]/2) + grid.shape[0] % 2
            new_grid = -sp.ones(new_nz*grid.shape[1], dtype=int)
            merge_list = []
            #
            for ix in range(grid.shape[1]):
                i = ix
                iz = 0
                for iz in range(0, grid.shape[0]-1, 2):
                    merge_list.append((grid[iz, ix], grid[iz+1, ix]))
                    new_grid[i] = grid[iz, ix]
                    i += grid.shape[1]
                if iz != grid.shape[0]-2:
                    new_grid[i] = grid[-1, ix]
            #
            new_grid = sp.reshape(new_grid, (new_nz, grid.shape[1]))
        #
        return merge_list, new_grid

    @staticmethod
    def _merge_mesh(master_id, slave_id, direction, path):
        r"""
        Merges and stitches two meshes together, overwriting the master
        and removing the slave directory
        """
        #
        # setting region and patch names
        master_region = 'mesh-region{}'.format(master_id)
        master_path = os.path.join(path, master_region)
        slave_region = 'mesh-region{}'.format(slave_id)
        slave_path = os.path.join(path, slave_region)
        #
        master_patch = 'mergeRL{}'
        slave_patch = 'mergeLR{}'
        if direction == 'top':
            master_patch = 'mergeTB{}'
            slave_patch = 'mergeBT{}'
        #
        master_patch = master_patch.format(master_id)
        slave_patch = slave_patch.format(slave_id)
        #
        # merging mesh
        proc = call(('mergeMeshes', '-overwrite', master_path, slave_path))
        if proc != 0:
            raise OSError
        #
        # removing slave directiory and cleaning the polyMesh of merge files
        rmtree(slave_path)
        ParallelMeshGen._clean_polymesh(master_path)
        #
        # stitching faces together to couple them
        proc = call(('stitchMesh', '-case', master_path, '-overwrite',
                    master_patch, slave_patch))
        if proc != 0:
            raise OSError
        ParallelMeshGen._clean_polymesh(master_path)

    @staticmethod
    def _remove_leftover_patches(path):
        r"""
        Removes all left over merge patches
        """
        file_name = os.path.join(path, 'mesh-region0', 'constant', 'polyMesh')
        file_name = os.path.join(file_name, 'boundary')
        #
        boundary_file = OpenFoamFile(file_name)
        list_key = list(boundary_file.keys())[0]
        #
        # only keeping non-merge patches
        face_list = []
        for patch in boundary_file[list_key]:
            if not isinstance(patch, OpenFoamDict):
                continue
            if not re.match('merge', patch.name):
                face_list.append(patch)
        #
        # writing out new file
        del boundary_file[list_key]
        list_key = str(len(face_list))
        boundary_file[list_key] = OpenFoamList(list_key, face_list)
        path = os.path.join(path, 'mesh-region0')
        boundary_file.write_foam_file(path=path, overwrite=True)

    @staticmethod
    def _clean_polymesh(path):
        r"""
        Removes files left over from merging and stitching meshes together
        """
        polymesh_path = os.path.join(path, 'constant', 'polyMesh')
        os.system('rm '+os.path.join(polymesh_path, '*Zones'))
        os.system('rm '+os.path.join(polymesh_path, 'meshMod*'))

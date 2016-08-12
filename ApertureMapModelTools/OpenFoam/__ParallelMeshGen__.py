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
from subprocess import Popen, PIPE
from time import sleep
from threading import Thread, active_count
import scipy as sp
from scipy.sparse import csgraph
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

    def run(self):
        r"""
        Writes the blockMeshDict and runs blockMesh in a separate thread
        """
        #
        # writing files based on mesh type
        if self.mesh_type == 'symmetry':
            self.write_symmetry_plane(path=self.path, overwrite=self.overwrite)
        else:
            self.write_foam_file(path=self.path, overwrite=self.overwrite)
        #
        # copying system directory to region directory
        cmd = 'cp -r {0} {1}'
        new_sys_path = os.path.join(self.path, 'system')
        os.system(cmd.format(self.system_dir, new_sys_path))
        #
        # running blockMesh
        cmd = ('blockMesh', '-case', self.path)
        print('Running: ', ' '.join(cmd), 'in thread: ', self.thread_name)
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = proc.communicate()
        if proc.poll() != 0:
            print(out)
            print(err)
            raise OSError


class MergeGroup(object):
    r"""
    Handles merging of meshes and stitching any patches that become internal
    """
    def __init__(self, region_id, external_patches, path):
        r"""
        Sets up the initial merge group as a single region. External patches
        is a dictionary with an entry for each side, {side: 'patch_name'}.
        The attribute 'external_patches' has the same format except its
        entries for each side are lists.
        """
        #
        super().__init__()
        self.region_id = region_id
        self.regions = sp.array([region_id], ndmin=2, dtype=int)
        self.region_dir = os.path.join(path, 'mesh-region{}'.format(region_id))
        self.region_in = None
        self.thread_name = 'Region {} Thread'.format(self.region_id)
        #
        self.external_patches = {}
        self.internal_patches = []
        for side, patch_name in external_patches.items():
            self.external_patches[side] = [patch_name]

    def run(self):
        r"""
        Manages subprocesses in a separate thread
        """
        #
        # merging regions and then stitching internal patches
        master_path = self.region_dir
        slave_path = self.region_in.region_dir
        cmd = ('mergeMeshes', '-overwrite', master_path, slave_path)
        print('Running: ', ' '.join(cmd), 'in thread: ', self.thread_name)
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, err = proc.communicate()
        if proc.poll() != 0:
            print(out)
            print(err)
            raise OSError
        #
        # removing slave directiory and cleaning the polyMesh of merge files
        rmtree(slave_path)
        self._clean_polymesh(master_path)
        #
        self.stitch_patches()

    def merge_regions(self, region_in, direction):
        r"""
        Merges two regions updating the external_patches dict and stitching
        and patches that become internal. It is assumed the region_in will
        be a higher 'id' than this region.
        """
        #
        # setting direction specific data
        if direction == 'right':
            axis = 1
            external_keys = ['bottom', 'top']
            swap = ['right', 'left']
        elif direction == 'top':
            axis = 0
            external_keys = ['left', 'right']
            swap = ['top', 'bottom']
        #
        # updating regions array
        self.region_in = region_in
        self.regions = sp.append(self.regions, region_in.regions, axis=axis)
        #
        # appending to external_patches
        for key in external_keys:
            self.external_patches[key] += region_in.external_patches[key]
        #
        # swapping patches in merge direction and setting internal patches
        self.internal_patches = zip(self.external_patches[swap[0]],
                                    region_in.external_patches[swap[1]])
        #
        self.external_patches[swap[0]] = region_in.external_patches[swap[0]]
        thread = Thread(name=self.thread_name, target=self.run)
        thread.start()

    def stitch_patches(self):
        r"""
        Stitches all internal patches in the region together
        """
        #
        # stitching faces together to couple them
        path = self.region_dir
        args = ['stitchMesh', '-case', path, '-overwrite', '-perfect', '', '']
        for master, slave in self.internal_patches:
            #
            args[5] = master
            args[6] = slave
            cmd = tuple(args)
            print('Running: ', ' '.join(cmd), 'in thread: ', self.thread_name)
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            out, err = proc.communicate()
            if proc.poll() != 0:
                print(out)
                print(err)
                raise OSError
            self._clean_polymesh(path)

    @staticmethod
    def _clean_polymesh(path):
        r"""
        Removes files left over from merging and stitching meshes together
        """
        polymesh_path = os.path.join(path, 'constant', 'polyMesh')
        os.system('rm -f '+os.path.join(polymesh_path, '*Zones'))
        os.system('rm -f '+os.path.join(polymesh_path, 'meshMod*'))


class ParallelMeshGen(object):
    r"""
    Handles creation of a large mesh in parallel utilizing the OpenFoam
    utilties mergeMesh and stitchMesh.
    """
    def __init__(self, field, system_dir, nprocs=4, **kwargs):
        #
        super().__init__()
        mesh_params = kwargs.get('mesh_params', None)
        mesh_params = mesh_params or {}
        #
        # field attributes that are copied over
        field.create_point_data()
        self.nx = field.nx
        self.nz = field.nz
        self.data_map = field.data_map
        self.point_data = field.point_data
        self._field = field.clone()
        self._mask = sp.ones(self.data_map.shape, dtype=bool)
        #
        self.system_dir = system_dir
        self.nprocs = nprocs
        self.avg_fact = kwargs.get('avg_fact', 1.0)
        self.mesh_params = mesh_params
        self.merge_groups = []

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
        ndivs = 8
        #
        grid = sp.arange(0, ndivs*ndivs, dtype=int)
        grid = sp.reshape(grid, (ndivs, ndivs))
        #
        # updating mask if threshold
        if mesh_type == 'threshold':
            min_value = kwargs.get('min_value', 0.0)
            max_value = kwargs.get('max_value', 1e9)
            self._field.threshold_data(min_value, max_value, repl=0.0)
            self._field.copy_data(self)
            #
            adj_matrix = self._field.create_adjacency_matrix()
            num_cs, cs_ids = csgraph.connected_components(csgraph=adj_matrix,
                                                          directed=False)
            # only saving the largest cluster
            if num_cs > 1:
                cs_count = sp.zeros(num_cs, dtype=int)
                for cs_num in cs_ids:
                    cs_count[cs_num] += 1
                self.data_vector[sp.where(cs_ids != sp.argmax(cs_count))[0]] = 0.0
                self.data_map = sp.reshape(self.data_vector, self.data_map.shape)
            #
            self._mask = self.data_map > 0.0
        #
        self._create_subregion_meshes(ndivs, mesh_type=mesh_type, path=path,
                                      **kwargs)
        self._merge_submeshes(grid)
        self._remove_leftover_patches(path)

    def _create_subregion_meshes(self, ndivs, **kwargs):
        r"""
        Divides the data map into smaller regions and creates a BlockMeshRegion
        object for each one.
        """
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

        init_count = active_count()
        for i, (z_slice, x_slice) in enumerate(slice_list):
            #
            while active_count() - init_count >= self.nprocs:
                # print('Waiting 5 seconds (in for loop mesh gen)...')
                sleep(1)
            region_mesh = self._setup_region(i, z_slice, x_slice, **kwargs)
            self._create_region_mesh(i, region_mesh, **kwargs)
        while active_count() > init_count:
            # print('Waiting 5 seconds (after for loop mesh gen)...')
            sleep(1)

    def _setup_region(self, region_id, z_slice, x_slice, **kwargs):
        r"""
        sets up an individual mesh region
        """
        #
        sides = ['left', 'right', 'bottom', 'top']
        patches = ['mergeLR{}', 'mergeRL{}', 'mergeBT{}', 'mergeTB{}']
        labels = ['boundary.'+patch for patch in patches]
        external_patches = {side: side for side in sides}
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
        region_mesh._generate_masked_mesh(cell_mask=self._mask[z_slice, x_slice])
        #
        # need to test for holes on merge boundaries and change patch to internal
        # creating map indexed 1:_blocks.size but with shape of (nz, nx)
        mesh_map = sp.ones(region_mesh.data_vector.size, dtype=int)
        mesh_map *= -sp.iinfo(int).max
        inds = sp.where(region_mesh.data_vector > 0)[0]
        mesh_map[inds] = sp.arange(inds.size)
        mesh_map = sp.reshape(mesh_map, region_mesh.data_map.shape)
        boundary_dict = {
            'internal':
                {'bottom': [], 'top': [], 'left': [], 'right': []}
        }
        #
        # updating patches
        sides = {}
        if x_slice.start != 0:
            sides['left'] = 0
            for iz in range(region_mesh.nz):
                IZ = iz + z_offset
                IX = x_offset
                if self._mask[IZ, IX] and not self._mask[IZ, IX-1]:
                    boundary_dict['internal']['left'].append(mesh_map[iz, 0])
        #
        if x_slice.stop != self.nx:
            sides['right'] = 1
            for iz in range(region_mesh.nz):
                IZ = iz + z_offset
                IX = x_offset + region_mesh.nx - 1
                if self._mask[IZ, IX] and not self._mask[IZ, IX+1]:
                    boundary_dict['internal']['right'].append(mesh_map[iz, -1])
        #
        if z_slice.start != 0:
            sides['bottom'] = 2
            for ix in range(region_mesh.nx):
                IZ = z_offset
                IX = ix + x_offset
                if self._mask[IZ, IX] and not self._mask[IZ-1, IX]:
                    boundary_dict['internal']['bottom'].append(mesh_map[0, ix])
        #
        if z_slice.stop != self.nz:
            sides['top'] = 3
            for ix in range(region_mesh.nx):
                IZ = z_offset + region_mesh.nz - 1
                IX = ix + x_offset
                if self._mask[IZ, IX] and not self._mask[IZ+1, IX]:
                    boundary_dict['internal']['top'].append(mesh_map[-1, ix])
        #
        face_labels = region_mesh.face_labels
        for side, index in sides.items():
            label = labels[index].format(region_id)
            external_patches[side] = patches[index].format(region_id)
            region_mesh.mesh_params[label+'.type'] = 'empty'
            region_mesh.face_labels[label] = face_labels.pop('boundary.'+side)
        region_mesh.set_boundary_patches(boundary_dict)
        #
        # setting up initial MergeGroup as an individual region
        group = MergeGroup(region_id, external_patches, kwargs.get('path', '.'))
        self.merge_groups.append(group)
        #
        return region_mesh

    def _create_region_mesh(self, region_id, region_mesh, **kwargs):
        r"""
        Handles the process of generating a mesh, writing it and then
        calling blockMesh. Returns a Popen object.
        """
        #
        # setting important attributes to generate the mesh
        region_mesh.mesh_type = kwargs.get('mesh_type', 'simple')
        region_mesh.overwrite = kwargs.get('overwrite', False)
        path = kwargs.get('path', '.')
        region_mesh.path = os.path.join(path, 'mesh-region{}'.format(region_id))
        region_mesh.system_dir = self.system_dir
        #
        # starting mesh generation thread
        region_mesh.thread_name = 'Region {} Thread'.format(region_id)
        thread = Thread(name=region_mesh.thread_name, target=region_mesh.run)
        thread.start()

    def _merge_submeshes(self, grid):
        r"""
        Handles merging and stitching of meshes based on alternating rounds
        of horizontal pairing and then vertical pairing.
        """
        #
        init_count = active_count()
        direction = 'right'
        while sp.size(grid) > 1:
            #
            # getting merge list and updating grid
            merge_list, grid = self._create_merge_list(grid, direction)
            for master, slave in merge_list:
                while active_count() - init_count >= self.nprocs:
                    # print('Waiting 5 seconds (in for loop mesh merge)...')
                    sleep(1)
                master = self.merge_groups[master]
                slave = self.merge_groups[slave]
                master.merge_regions(slave, direction)
            while active_count() > init_count:
                # print('Waiting 5 seconds (after for loop mesh merge)...')
                sleep(1)
            #
            # switching directions
            direction = 'top' if direction == 'right' else 'right'

    @staticmethod
    def _create_merge_list(grid, direction):
        r"""
        Determines the region merge list based on the grid supplied
        """
        #
        new_grid = sp.copy(grid)
        if direction == 'right':
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

"""
A class build to handle generation of a blockMeshDict from an aperturemap.
#
Written By: Matthew Stadelman
Date Written: 2016/08/08
Last Modifed: 2016/08/08
#
"""
#
import os
import re
import scipy as sp
from scipy.sparse import csgraph
from .__openfoam_core__ import OpenFoamFile, OpenFoamDict, OpenFoamList
#
########################################################################
#


class BlockMeshDict(OpenFoamFile):
    r"""
    This is a special subclass of OpenFoamFile used to generate and output
    a blockMeshDict for OpenFoam
    """
    #
    # defining default parameters and attributes
    DEFAULT_PARAMS = {
        'convertToMeters': '1.0',
        'numbersOfCells': '(1 1 1)',
        'cellExpansionRatios': 'simpleGrading (1 1 1)',
        #
        'boundary.left.type': 'wall',
        'boundary.right.type': 'wall',
        'boundary.top.type': 'wall',
        'boundary.bottom.type': 'wall',
        'boundary.front.type': 'wall',
        'boundary.back.type': 'wall',
        'boundary.internal.type': 'wall'
    }

    def __init__(self, field, avg_fact=1.0, mesh_params=None):
        r"""
        Takes a field object and a set of mesh params to set the
        properties of the blockMeshDict

        field : DataField, field that is storing the aperture map data
        avg_fact : float, optional, number of voxels along the X and Z axes.
        mesh_params : dict, optional, a dictionary containing parameters to
        use instead of the defaults
        """
        super().__init__('polyMesh', 'blockMeshDict')
        #
        # field attributes that are copied over
        self.nx = None
        self.nz = None
        self.data_map = sp.array([])
        self.data_vector = sp.array([])
        self.point_data = sp.array([])
        if field.point_data is None:
            field.create_point_data()
        field.copy_data(self)
        #
        # native attributes
        self.avg_fact = avg_fact
        self.mesh_params = dict(BlockMeshDict.DEFAULT_PARAMS)
        self.face_labels = {}
        self._field = field.clone()
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
        self.point_data += 1E-6
        self.generate_simple_mesh()

    def _create_blocks(self, cell_mask):
        r"""
        Sets up the vertices and blocks.

            - cell_mask is a boolean array in the shape of the data_map
        telling the function what blocks to include.

        vert_map stores the 4 vertex indices that make up the
        back surface and the front surface is '+ 1' the index of the
        corresponding lower point. In terms of the very first block
        vert_map[i,j,0] is at the orgin (0,0), bottom left corner
        vert_map[i,j,1] is bottom right corner (1,0)
        vert_map[i,j,2] is the top right corner (1,1)
        vert_map[i,j,3] is the top left corner (0,1)
        """
        #
        map_mask = sp.ones((self.nz+1, self.nx+1), dtype=bool)
        map_mask[0:self.nz, 0:self.nx] = cell_mask
        map_mask[0:self.nz, self.nx] = cell_mask[0:self.nz, self.nx-1]
        map_mask[self.nz, 0:self.nx] = cell_mask[self.nz-1, 0:self.nx]
        #
        # creating temporary arrays to handle vertices
        indices = [0, 1, 1, 0, 3, 2, 2, 3]
        offsets = [0, 0, 1, 1, 0, 0, 1, 1]
        vertices = []
        vert_map = sp.zeros((self.nz+1, self.nx+1, 4), dtype=int)
        vert_map[:] = sp.nan
        #
        # building vertices and setting vert_map
        vert_index = 0
        if map_mask[0, 0]:
            vert_map[0, 0, 0] = 0
            vertices.append([0.0, -self.point_data[0, 0, 0]/2.0, 0.0])
            vertices.append([0.0, self.point_data[0, 0, 0]/2.0, 0.0])
            vert_index = 2
        #
        for iz in range(self.nz):
            if map_mask[iz, 0] or map_mask[iz+1, 0]:
                zdist = (iz + 1.0) * self.avg_fact
                ydist = self.point_data[iz, 0, 3]/2.0
                #
                vertices.append([0.0, -ydist, zdist])
                vert_map[iz, 0, 3] = vert_index
                vert_map[iz+1, 0, 0] = vert_index
                vert_index += 1
                vertices.append([0.0, ydist, zdist])
                vert_index += 1
        #
        for ix in range(self.nx):
            if map_mask[0, ix] or map_mask[0, ix+1]:
                xdist = (ix + 1.0) * self.avg_fact
                ydist = self.point_data[0, ix, 1]/2.0
                vertices.append([xdist, -ydist, 0.0])
                vert_map[0, ix, 1] = vert_index
                vert_map[0, ix+1, 0] = vert_index
                vert_index += 1
                vertices.append([xdist, ydist, 0.0])
                vert_index += 1
        #
        for index in range(self.nx*self.nz):
            iz = int(index/self.nx)
            ix = index % self.nx
            if sp.any(map_mask[iz:iz+2, ix:ix+2]):
                xdist = (ix + 1.0) * self.avg_fact
                ydist = self.point_data[iz, ix, 2]/2.0
                zdist = (iz + 1.0) * self.avg_fact
                #
                vertices.append([xdist, -ydist, zdist])
                vert_map[iz, ix, 2] = vert_index
                vert_map[iz+1, ix, 1] = vert_index
                vert_map[iz, ix+1, 3] = vert_index
                vert_map[iz+1, ix+1, 0] = vert_index
                vert_index += 1
                vertices.append([xdist, ydist, zdist])
                vert_index += 1
        #
        # building block array
        self._blocks = []
        cell_mask = sp.ravel(cell_mask)
        for index in sp.where(cell_mask)[0]:
            iz = int(index/self.nx)
            ix = index % self.nx
            self._blocks.append(vert_map[iz, ix, indices] + offsets)
        #
        # coverting lists to scipy arrays
        self._vertices = sp.array(vertices, ndmin=2, dtype=float)
        self._blocks = sp.array(self._blocks, ndmin=2, dtype=int)

    def set_boundary_patches(self, boundary_blocks, reset=False):
        r"""
        Sets up boundary patches based on the dictionary passed in. Overlapping
        declarations are overwritten by the last patch to use that face.
        The boundary blocks dictionary contains a dictionary entry for
        each patch name.

            - boundary_blocks dictionary has the format of:
                  {patch_name: {
                          <side>: [ block-list ],
                          <side>: [ block-list ],
                          ...
                      },
                      ...
                  }
                  where <side> is left, right, bottom, top, front or back
                  and block list is a list of blocks to add that patch to the
                  side of.
            - reset - boolean : if True then the face labels dictionary
                and _faces array are re-initialized to default values
        """
        #
        offsets = {
            'bottom': (0, (0, 1, 2, 3)),
            'back': (1, (0, 1, 5, 4)),
            'right': (2, (1, 2, 6, 5)),
            'front': (3, (3, 2, 6, 7)),
            'left': (4, (0, 3, 7, 4)),
            'top': (5, (4, 5, 6, 7)),
        }
        #
        # re-initializing all face labels
        num_faces = 6 * len(self._blocks)
        if reset:
            self._faces = sp.ones((num_faces, 4), dtype=int)*-sp.iinfo(int).max
            self.face_labels = {}
        #
        # adding any new face labels to the dictionary
        for patch_name in boundary_blocks.keys():
            key = 'boundary.'+patch_name
            if key not in self.face_labels.keys():
                self.face_labels[key] = sp.zeros(num_faces, dtype=bool)
        #
        # setting new face labels
        for patch_name, side_dict in boundary_blocks.items():
            for side, blocks in side_dict.items():
                indices = sp.array(blocks, dtype=int) * 6 + offsets[side][0]
                face_verts = self._blocks[blocks][:, offsets[side][1]]
                self._faces[indices] = face_verts
                self.face_labels['boundary.'+patch_name][indices] = True
        #
        # preventing overlapping face labels
        for patch_name in boundary_blocks.keys():
            indices = self.face_labels['boundary.'+patch_name]
            reset = {key: indices for key in self.face_labels.keys()}
            del reset['boundary.'+patch_name]
            for key, indices in reset.items():
                self.face_labels[key][indices] = False

    def _generate_masked_mesh(self, cell_mask=None):
        r"""
        Generates the mesh based on the cell mask provided
        """
        #
        if cell_mask is None:
            cell_mask = sp.ones(self.data_map.shape, dtype=bool)
        #
        # initializing arrays
        self._edges = sp.ones(0, dtype=str)
        self._merge_patch_pairs = sp.ones(0, dtype=str)
        self._create_blocks(cell_mask)
        #
        # building face arrays
        mapper = sp.ravel(sp.array(cell_mask, dtype=int))
        mapper[mapper == 1] = sp.arange(sp.count_nonzero(mapper))
        mapper = sp.reshape(mapper, (self.nz, self.nx))
        mapper[~cell_mask] = -sp.iinfo(int).max
        #
        boundary_dict = {
            'bottom':
                {'bottom': mapper[0, :][cell_mask[0, :]]},
            'top':
                {'top': mapper[-1, :][cell_mask[-1, :]]},
            'left':
                {'left': mapper[:, 0][cell_mask[:, 0]]},
            'right':
                {'right': mapper[:, -1][cell_mask[:, -1]]},
            'front':
                {'front': mapper[cell_mask]},
            'back':
                {'back': mapper[cell_mask]},
            'internal':
                {'bottom': [], 'top': [], 'left': [], 'right': []}
        }
        #
        # determining cells linked to a masked cell
        cell_mask = sp.where(~sp.ravel(cell_mask))[0]
        inds = sp.in1d(self._field._cell_interfaces, cell_mask)
        inds = sp.reshape(inds, (len(self._field._cell_interfaces), 2))
        inds = inds[:, 0].astype(int) + inds[:, 1].astype(int)
        inds = (inds == 1)
        links = self._field._cell_interfaces[inds]
        #
        # adjusting order so masked cells are all on links[:, 1]
        swap = sp.in1d(links[:, 0], cell_mask)
        links[swap] = links[swap, ::-1]
        #
        # setting side based on index difference
        sides = sp.ndarray(len(links), dtype='<U6')
        sides[sp.where(links[:, 1] == links[:, 0]-self.nx)[0]] = 'bottom'
        sides[sp.where(links[:, 1] == links[:, 0]+self.nx)[0]] = 'top'
        sides[sp.where(links[:, 1] == links[:, 0]-1)[0]] = 'left'
        sides[sp.where(links[:, 1] == links[:, 0]+1)[0]] = 'right'
        #
        # adding each block to the internal face dictionary
        inds = sp.ravel(mapper)[links[:, 0]]
        for side, block_id in zip(sides, inds):
            boundary_dict['internal'][side].append(block_id)
        self.set_boundary_patches(boundary_dict, reset=True)

    def generate_simple_mesh(self):
        r"""
        Generates a simple mesh including all cells in the data map
        """
        self._generate_masked_mesh(cell_mask=None)

    def generate_threshold_mesh(self, min_value=0.0, max_value=1.0e9):
        r"""
        Generates a mesh excluding all blocks below the min_value arg. Regions
        that are isolated by the thresholding are also automatically removed.
        """
        #
        # thresholding the data and then checking for isolated clusters
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
            self.data_map = sp.reshape(self.data_vector, (self.nz, self.nx))
        #
        self._field.data_map = self.data_map
        self._field.data_vector = sp.ravel(self.data_map)
        #
        # generating blocks and vertices
        mask = self.data_map > 0.0
        self._generate_masked_mesh(cell_mask=mask)

    def generate_mesh_file(self):
        r"""
        Populates keys on itself based on geometry data to output a mesh file
        """
        #
        # removing any old keys to prevent duplicates
        keys = list(self.keys())
        for key in keys:
            del self[key]
        #
        self['convertToMeters '] = self.mesh_params['convertToMeters']
        #
        # writing vertices
        oflist = OpenFoamList('vertices\n{}'.format(len(self._vertices)))
        for val in self._vertices:
            val = ['{:12.9F}'.format(v) for v in val]
            oflist.append('(' + ' '.join(val) + ')')
        self[oflist.name] = oflist
        #
        # writing blocks
        oflist = OpenFoamList('blocks\n{}'.format(len(self._blocks)))
        fmt = 'hex ({0}) {numbersOfCells} {cellExpansionRatios}\n'
        for val in self._blocks:
            val = ['{:7d}'.format(v) for v in val]
            val = ' '.join(val)
            val = fmt.format(val, **self.mesh_params)
            oflist.append(val)
        self[oflist.name] = oflist
        #
        # writing edges
        oflist = OpenFoamList('edges', self._edges)
        self[oflist.name] = oflist
        #
        # getting unique list of boundary faces defined
        bounds = []
        for key in self.face_labels.keys():
            mat = re.match(r'boundary.(\w+)', key)
            mat = bounds.append(mat.group(1)) if mat else None
        #
        # writing boundaries
        oflist = OpenFoamList('boundary\n{}'.format(len(bounds)))
        for side in bounds:
            ofdict = OpenFoamDict(side)
            side_faces = self._faces[self.face_labels['boundary.'+side]]
            ofdict['type'] = self.mesh_params['boundary.'+side+'.type']
            fmt = 'faces\n\t\t{}'
            ofdict['faces'] = OpenFoamList(fmt.format(len(side_faces)))
            #
            for val in side_faces:
                val = ['{:7d}'.format(v) for v in val]
                ofdict['faces'].append('(' + ' '.join(val) + ')')
            #
            oflist.append(ofdict)
        self[oflist.name] = oflist
        #
        # writing mergePatchPairs
        oflist = OpenFoamList('mergePatchPairs', self._merge_patch_pairs)
        self[oflist.name] = oflist

    def write_foam_file(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Writes a full blockMeshDict file based on stored geometry data
        """
        #
        # if create dirs then appending the required openFOAM directories
        if create_dirs:
            path = os.path.join(path, 'constant', 'polyMesh')
        #
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        fname = os.path.join(path, 'blockMeshDict')
        #
        # checking if file exists
        if not overwrite and os.path.exists(fname):
            msg = 'Error - there is already a file at '+fname+'.'
            msg += ' Specify "overwrite=True" to replace it'
            raise FileExistsError(msg)
        #
        # creating content
        self.generate_mesh_file()
        #
        # saving file
        file_content = str(self)
        with open(fname, 'w') as block_mesh_file:
            block_mesh_file.write(file_content)
        #
        print('Mesh file saved as: '+fname)

    def write_mesh_file(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Passes args off to write_foam_file
        """
        self.write_foam_file(path, create_dirs, overwrite)

    def write_symmetry_plane(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Exports the +Y half of the mesh flattening out everything below 0 on
        the Y axis
        """
        # TODO: consider replacing the bottom face type with symmetryPlane
        #
        # storing orginial vertices
        old_verts = sp.copy(self._vertices)
        self._vertices[sp.where(self._vertices[:, 1] <= 0.0), 1] = 0.0
        #
        # outputing mesh
        self.write_foam_file(path=path,
                             create_dirs=create_dirs,
                             overwrite=overwrite)
        #
        # restoring original verts
        self._vertices = sp.copy(old_verts)

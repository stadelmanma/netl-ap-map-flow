"""
This stores the basic classes and functions needed for the openFOAM export script
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/06/10
#
"""
#
import os
import re
import scipy as sp
#
########################################################################
#
# Class Definitions


class OpenFoamExport(dict):
    r"""
    A class to handle exporting an aperture map to an OpenFOAM blockMeshDict
    """
    def __init__(self, field, avg_fact=1.0, export_params=None):
        r"""
        Takes a field object and a set of export params to set the
        properties of the blockMeshDict
        """
        #
        # defining default parameters
        super().__init__()
        default_params = {
            'convertToMeters': '1.0',
            'numbersOfCells': '(1 1 1)',
            'cellExpansionRatios': 'simpleGrading (1 1 1)',
            #
            'boundary.left.type': 'wall',
            'boundary.right.type': 'wall',
            'boundary.top.type': 'wall',
            'boundary.bottom.type': 'wall',
            'boundary.front.type': 'wall',
            'boundary.back.type': 'wall'
        }
        for key, value in default_params.items():
            self[key] = str(value)
        #
        self.nx = None
        self.nz = None
        self.data_map = sp.array([])
        self.point_data = sp.array([])
        field.create_point_data()
        field.copy_data(self)
        if export_params is not None:
            for key, value in export_params.items():
                self[key] = value
        #
        # initializing required arrays
        num_verts = 2*(self.nx - 1)*(self.nz - 1) + 4*(self.nx + self.nz)
        num_faces = 6*self.data_map.size
        #
        self._verticies = -sp.ones((num_verts, 3), dtype=float)
        self._blocks = -sp.ones((self.data_map.size, 8), dtype=int)
        self._faces = -sp.ones((num_faces, 4), dtype=int)
        self._edges = sp.ones(0, dtype=str)
        self._mergePatchPairs = sp.ones(0, dtype=str)
        #
        # initializing boundary face labels
        for side in ['left', 'right', 'top', 'bottom', 'front', 'back']:
            self['boundary.'+side] = sp.zeros(num_faces, dtype=bool)
        #
        self._build_mesh(avg_fact)

    def _build_mesh(self, avg_fact):
        r"""
        Handles population of the arrays and updating boundary face labels
        """
        #
        # vert map stores the vertex number of the 4 points in lower surface
        # the upper surface is + 1 the value of the corresponding lower point
        vert_map = sp.zeros((self.nz+1, self.nx+1, 4), dtype=int)
        #
        # building verticies and setting vert map
        self._verticies[0] = [0.0, -self.data_map[0, 0]/2.0, 0.0]
        self._verticies[1] = [0.0, self.data_map[0, 0]/2.0, 0.0]
        #
        iv = 2
        for iz in range(self.nz):
            for ix in range(self.nx):
                xdist = (ix + 1.0) * avg_fact
                zdist = (iz + 1.0) * avg_fact
                #
                if ix == 0:
                    ydist = self.point_data[iz, ix, 3]/2.0
                    self._verticies[iv] = [0.0, -ydist, zdist]
                    vert_map[iz, ix, 3] = iv
                    vert_map[iz+1, ix, 0] = iv
                    iv += 1
                    self._verticies[iv] = [0.0, ydist, zdist]
                    iv += 1
                #
                if iz == 0:
                    ydist = self.point_data[iz, ix, 1]/2.0
                    self._verticies[iv] = [xdist, -ydist, 0.0]
                    vert_map[iz, ix, 1] = iv
                    vert_map[iz, ix+1, 0] = iv
                    iv += 1
                    self._verticies[iv] = [xdist, ydist, 0.0]
                    iv += 1
                #
                ydist = self.point_data[iz, ix, 2]/2.0
                self._verticies[iv] = [xdist, -ydist, zdist]
                vert_map[iz, ix, 2] = iv
                vert_map[iz+1, ix, 1] = iv
                vert_map[iz, ix+1, 3] = iv
                vert_map[iz+1, ix+1, 0] = iv
                iv += 1
                self._verticies[iv] = [xdist, ydist, zdist]
                iv += 1
        #
        # building block array
        for iz in range(self.nz):
            for ix in range(self.nx):
                ib = iz * self.nx + ix
                #
                self._blocks[ib, 0] = vert_map[iz, ix, 0]      # back bottom left
                self._blocks[ib, 1] = vert_map[iz, ix, 1]      # back bottom right
                self._blocks[ib, 2] = vert_map[iz, ix, 1] + 1  # front bottom right
                self._blocks[ib, 3] = vert_map[iz, ix, 0] + 1  # front bottom left
                self._blocks[ib, 4] = vert_map[iz, ix, 3]      # back top left
                self._blocks[ib, 5] = vert_map[iz, ix, 2]      # back top right
                self._blocks[ib, 6] = vert_map[iz, ix, 2] + 1  # front top right
                self._blocks[ib, 7] = vert_map[iz, ix, 3] + 1  # front top left
        #
        # building face arrays
        i = 0
        for iz in range(self.nz):
            ib = iz * self.nx
            self._faces[i] = self._blocks[ib, [0, 3, 7, 4]]
            self['boundary.left'][i] = True
            i += 1
        for iz in range(self.nz):
            ib = iz * self.nx + (self.nx - 1)
            self._faces[i] = self._blocks[ib, [1, 2, 6, 5]]
            self['boundary.right'][i] = True
            i += 1
        for ix in range(self.nx):
            ib = (self.nz - 1)*self.nx + ix
            self._faces[i] = self._blocks[ib, [4, 5, 6, 7]]
            self['boundary.top'][i] = True
            i += 1
        for ix in range(self.nx):
            ib = ix
            self._faces[i] = self._blocks[ib, [0, 1, 2, 3]]
            self['boundary.bottom'][i] = True
            i += 1
        for iz in range(self.nz):
            for ix in range(self.nx):
                ib = iz * self.nx + ix
                self._faces[i] = self._blocks[ib, [3, 2, 6, 7]]
                self['boundary.front'][i] = True
                i += 1
        for iz in range(self.nz):
            for ix in range(self.nx):
                ib = iz * self.nx + ix
                self._faces[i] = self._blocks[ib, [0, 1, 5, 4]]
                self['boundary.back'][i] = True
                i += 1

    def write_mesh_file(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Creates the directories and the blockMeshDict file.
        """
        #
        # if create dirs then appending the required openFOAM directories
        if create_dirs:
            path = os.path.join(path, 'constant', 'polyMesh')
        #
        try:
            os.makedirs(path)
        except FileExistsError:
            print('Using existing directory structure for provided path '+path)
        fname = os.path.join(path, 'blockMeshDict')
        #
        # checking if file exists
        if not overwrite and os.path.exists(fname):
            msg = 'Error - there is already a file at '+fname+'.'
            msg += ' Specify "overwrite=True" to replace it'
            raise FileExistsError(msg)
        #
        # creating file header
        file_header = 'FoamFile\n{\n'
        file_header += '    version     2.0;\n'
        file_header += '    format      ascii;\n'
        file_header += '    class       dictionary;\n'
        file_header += '    object      blockMeshDict;\n}\n'
        file_header += '// * * * * * * * * * * * * * * * * * * * * * * * * * *//\n\n'
        file_header += 'convertToMeters '+(self['convertToMeters'] or '1.0')+';\n\n'
        #
        file_content = ''
        #
        # writing verticies
        file_content += 'vertices\n(\n'
        for val in self._verticies:
            val = ['{:12.6F}'.format(v) for v in val]
            val = ' '.join(val)
            file_content += '('+val+')\n'
        file_content += ');\n\n'
        #
        # writing blocks
        file_content += 'blocks\n(\n'
        for val in self._blocks:
            val = ['{:7d}'.format(v) for v in val]
            val = ' '.join(val)
            val = 'hex ({0}) {1} {2}\n'.format(val, self['numbersOfCells'],
                                               self['cellExpansionRatios'])
            file_content += val
        file_content += ');\n\n'
        #
        # writing edges
        file_content += 'edges\n(\n'
        for val in self._edges:
            pass
        file_content += ');\n\n'
        #
        # getting unique list of boundary faces defined
        file_content += 'boundary\n(\n'
        bounds = []
        for key in self.keys():
            mat = re.match(r'boundary.(\w+)[.]?', key)
            mat = bounds.append(mat.group(1)) if mat else None
        bounds = set(bounds)
        #
        # writing boundaries
        for side in bounds:
            file_content += '    '+side+'\n    {\n'
            file_content += '        type '+self['boundary.'+side+'.type']+';\n'
            file_content += '        faces\n        (\n'
            #
            for val in self._faces[self['boundary.'+side]]:
                val = ['{:7d}'.format(v) for v in val]
                val = ' '.join(val)
                file_content += '            ('+val+')\n'
            #
            file_content += '        );\n'
            file_content += '    }\n'
        file_content += ');\n\n'
        #
        # writing mergePatchPairs
        file_content += 'mergePatchPairs\n(\n'
        for val in self._mergePatchPairs:
            pass
        file_content += ');\n\n'
        #
        # saving file
        with open(fname, 'w') as mesh_file:
            mesh_file.write(file_header)
            mesh_file.write(file_content)
        #
        print('Mesh file saved as: '+fname)

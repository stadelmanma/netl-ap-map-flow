"""
This stores the basic classes and functions needed to generate an OpenFoam
blockMeshDict and other associated files.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/07/20
#
"""
#
from collections import OrderedDict
import os
import re
import scipy as sp
#
########################################################################
#


class OpenFoamObject:
    r"""
    General class used to recognize other OpenFoam objects
    """
    def __str__(self):
        raise NotImplementedError('__str__ method must be subclassed')


class OpenFoamDict(OpenFoamObject, OrderedDict):
    r"""
    Class used to build the dictionary style OpenFoam input blocks
    """
    def __init__(self, name, values=None):
        r"""
        Creates an OpenFoamDict:
          name - string printed at top of dictionary in files
          values - any valid iterable that can be used to initialize
              a dictionary
        """
        init_vals = {}
        if values:
            init_vals = values
        #
        super().__init__(init_vals)
        self.name = name

    def __str__(self, indent=0):
        r"""
        Prints a formatted output readable by OpenFoam
        """
        fmt_str = '\t{}\t{};\n'
        #
        str_rep = ('\t'*indent) + self.name + '\n'
        str_rep += ('\t'*indent) + '{\n'
        #
        for key, val in self.items():
            if isinstance(val, OpenFoamObject):
                str_rep += '\n'
                str_rep += val.__str__(indent=(indent+1))
            else:
                val = str(val).replace(',', ' ')
                str_rep += ('\t'*indent) + fmt_str.format(key, val)
        #
        str_rep += ('\t'*indent) + '}\n'
        #
        return str_rep


class OpenFoamList(OpenFoamObject, list):
    r"""
    Class used to build the output lists used in blockMeshDict.
    """
    def __init__(self, name, values=None):
        r"""
        Creates an OpenFoamList:
          name - string printed at top of dictionary in files
          values - any valid iterable that can be used to initialize
              a list
        """
        init_vals = []
        if values:
            init_vals = values
        #
        super().__init__(init_vals)
        self.name = name

    def __str__(self, indent=0):
        r"""
        Prints a formatted output readable by OpenFoam
        """
        fmt_str = '\t{}\n'
        #
        str_rep = ('\t'*indent) + self.name + '\n'
        str_rep += ('\t'*indent) + '(\n'
        #
        for val in self:
            if isinstance(val, OpenFoamObject):
                str_rep += '\n'
                str_rep += val.__str__(indent=(indent+1))
            else:
                val = str(val).replace(',', ' ')
                str_rep += ('\t'*indent) + fmt_str.format(val)
        #
        str_rep += ('\t'*indent) + ');\n'
        #
        return str_rep


class OpenFoamFile(OpenFoamObject, OrderedDict):
    r"""
    Class used to build OpenFoam input files
    """
    FOAM_HEADER = r"""
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  4.0                                   |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
"""
    FOAM_SPACER = r"""
// ************************************************************************* //
"""
    HEAD_DICT = OpenFoamDict('FoamFile', [
        ('version', 2.0),
        ('format', 'ascii'),
        ('class', 'dictionary'),
        ('location', None),
        ('object', None)
    ])
    # trimming off leading newlines
    FOAM_HEADER = FOAM_HEADER[1:]
    FOAM_SPACER = FOAM_SPACER[1:]

    def __init__(self, location, object_name, class_name=None, values=None):
        init_vals = {}
        if values:
            init_vals = values
        #
        # initializing head dict
        super().__init__(init_vals)
        self.name = object_name
        self.head_dict = OpenFoamDict(OpenFoamFile.HEAD_DICT.name,
                                      OpenFoamFile.HEAD_DICT.items())
        #
        # setting head dict values
        if class_name:
            self.head_dict['class'] = class_name
        self.head_dict['location'] = '"' + location + '"'
        self.head_dict['object'] = object_name

    def __str__(self):
        r"""
        Prints a formatted OpenFoam input file
        """
        fmt_str = '{}\t{};\n\n'
        #
        str_rep = OpenFoamFile.FOAM_HEADER
        str_rep += str(self.head_dict)
        str_rep += OpenFoamFile.FOAM_SPACER
        str_rep += '\n'
        #
        for key, val in self.items():
            if isinstance(val, OpenFoamObject):
                str_rep += str(val)
                str_rep += '\n'
            else:
                val = str(val).replace(',', ' ')
                str_rep += fmt_str.format(key, val)
        #
        str_rep += '\n'
        str_rep += OpenFoamFile.FOAM_SPACER
        #
        return(str_rep)

    @staticmethod
    def init_from_file(filename):
        r"""
        Reads an existing OpenFoam input file and returns an OpenFoamFile
        instance. Comment lines are not retained.
        """
        #
        def build_dict(content, match, out_obj):
            r"""Recursive function used to build OpenFoamDicts"""
            ofdict = OpenFoamDict(match.group(1))
            content = content[match.end():]
            #
            while not re.match('^}', content):
                content = add_param(content, ofdict)
            #
            content = re.sub('^}\n', '', content)
            if isinstance(out_obj, list):
                out_obj.append(ofdict)
            else:
                out_obj[ofdict.name] = ofdict
            #
            return content

        def build_list(content, match, out_obj):
            r"""Recursive function used to build OpenFoamLists"""
            oflist = OpenFoamList(match.group(1))
            content = content[match.end():]
            #
            while not re.match('^\);', content):
                content = add_param(content, oflist)
            #
            content = re.sub('^\);\n', '', content)
            if isinstance(out_obj, list):
                out_obj.append(oflist)
            else:
                out_obj[oflist.name] = oflist
            #
            return content

        def add_param(content, out_obj):
            r"""Recursive function used to add params to OpenFoamObjects"""
            dict_pat = re.compile(r'.*?(\w+)\n\{\n')
            list_pat = re.compile(r'.*?(\w+)\n\(\n')
            dict_match = dict_pat.match(content)
            list_match = list_pat.match(content)
            if dict_match:
                content = build_dict(content, dict_match, out_obj)
            elif list_match:
                content = build_list(content, list_match, out_obj)
            else:
                line = re.match('.*\n', content).group()
                line = re.sub(';', '', line)
                line = line.strip()
                try:
                    key, value = re.split('\s+', line, maxsplit=1)
                except ValueError:
                    key, value = line, ''
                #
                # removing line from content
                content = re.sub('^.*\n', '', content)
                if isinstance(out_obj, list):
                    out_obj.append(line)
                else:
                    out_obj[key] = value
            #
            return content
        #
        # reading file
        with open(filename, 'r') as file:
            content = file.read()
            if not re.search('FoamFile', content):
                msg = 'Invalid OpenFoam input file, no FoamFile dict'
                raise ValueError(msg)
        #
        # removing comments and other characters
        inline_comment = re.compile(r'(//.*)')
        block_comment = re.compile(r'(/[*].*?[*]/)', flags=re.S)
        content = inline_comment.sub('', content)
        content = block_comment.sub('', content)
        content = re.sub('\s*$', '\n', content, flags=re.M)
        content = re.sub('^\s*', '', content, flags=re.M)
        #
        # parsing content of file
        foam_file_params = OrderedDict()
        while content:
            content = add_param(content, foam_file_params)
        #
        # generating OpenFoamFile
        head_dict = foam_file_params.pop('FoamFile')
        try:
            location = head_dict['location'].replace('"', '')
        except KeyError:
            location = os.path.split(os.path.dirname(filename))[1]
        #
        foam_file = OpenFoamFile(location,
                                 head_dict['object'],
                                 values=foam_file_params)
        foam_file.name = os.path.basename(filename)
        for key, value in head_dict.items():
            foam_file.head_dict[key] = value
        #
        return foam_file

    def write_foam_file(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Writes out the foam file, adding proper location directory if
        create_dirs is True
        """
        #
        # if create_dirs then appending location directory to path
        location = self.head_dict['location'].replace('"', '')
        if create_dirs:
            path = os.path.join(path, location)
        #
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        fname = os.path.join(path, self.name)
        #
        # checking if file exists
        if not overwrite and os.path.exists(fname):
            msg = 'Error - there is already a file at '+fname+'.'
            msg += ' Specify "overwrite=True" to replace it'
            raise FileExistsError(msg)
        #
        # saving file
        file_content = str(self)
        with open(fname, 'w') as foam_file:
            foam_file.write(file_content)
        #
        print(self.head_dict['object'] + ' file saved as: '+fname)


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
        'boundary.back.type': 'wall'
    }

    def __init__(self, field, avg_fact=1.0, mesh_params=None):
        r"""
        Takes a field object and a set of mesh params to set the
        properties of the blockMeshDict
        """
        super().__init__('polyMesh', 'blockMeshDict')
        #
        # field attributes that are copied over
        self.nx = None
        self.nz = None
        self.data_map = sp.array([])
        self.point_data = sp.array([])
        #
        # native attributes
        self._field = field
        self.avg_fact = avg_fact
        self.mesh_params = dict(BlockMeshDict.DEFAULT_PARAMS)
        #
        # copying data and updating params
        field.create_point_data()
        field.copy_data(self)
        if mesh_params is not None:
            self.mesh_params.update(mesh_params)
        #
        self.point_data += 1E-6
        self.generate_simple_mesh()

    def _create_blocks(self, cell_mask=None):
        r"""
        Sets up the verticies and blocks.

            - cell_mask is a boolean array in the shape of the data_map
        telling the function what blocks to skip.

        The vert_map returned stores the 4 vertex indices that make up the
        back surface and the front surface is '+ 1' the index of the
        corresponding lower point.
        """
        #
        vert_map = sp.zeros((self.nz+1, self.nx+1, 4), dtype=int)
        #
        # building verticies and setting vert map
        self._verticies[0] = [0.0, -self.data_map[0, 0]/2.0, 0.0]
        self._verticies[1] = [0.0, self.data_map[0, 0]/2.0, 0.0]
        #
        iv = 2
        for iz in range(self.nz):
            for ix in range(self.nx):
                xdist = (ix + 1.0) * self.avg_fact
                zdist = (iz + 1.0) * self.avg_fact
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
        indices = [0, 1, 1, 0, 3, 2, 2, 3]
        offsets = [0, 0, 1, 1, 0, 0, 1, 1]
        for ib in range(self.nz * self.nx):
            #
            iz = int(ib/self.nx)
            ix = ib % self.nx
            self._blocks[ib] = vert_map[iz, ix, indices] + offsets

    def set_boundary_patches(self, boundary_blocks):
        r"""
        Sets up boundary patches based on the dictionary passed in. Does
        not check for overlap in patch declarations.
            - boundary_blocks dictionary has the format of:
                  boundary_blocks[patch_name] = {
                          side: [ block-list ],
                      }
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
        for patch_name, side_dict in boundary_blocks.items():
            for side, blocks in side_dict.items():
                indices = sp.array(blocks) * 6 + offsets[side][0]
                face_verts = self._blocks[blocks][:, offsets[side][1]]
                self._faces[indices] = face_verts
                self.face_labels['boundary.'+patch_name][indices] = True

    def generate_simple_mesh(self):
        r"""
        Handles population of the arrays and updating boundary face labels
        """
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
        self.face_labels = {}
        for side in ['left', 'right', 'top', 'bottom', 'front', 'back']:
            key = 'boundary.'+side
            self.face_labels[key] = sp.zeros(num_faces, dtype=bool)
        #
        # setting up blocks and verticies
        self._create_blocks(cell_mask=None)
        #
        # building face arrays
        boundary_dict = {
            'bottom':
                {'bottom': [ix for ix in range(self.nx)]},
            'top':
                {'top': [(self.nz-1)*self.nx + ix for ix in range(self.nx)]},
            'left':
                {'left': [iz*self.nx for iz in range(self.nz)]},
            'right':
                {'right': [iz*self.nx + (self.nx-1) for iz in range(self.nz)]},
            'front':
                {'front': [i for i in range(self.nx*self.nz)]},
            'back':
                {'back': [i for i in range(self.nx*self.nz)]},
        }
        self.set_boundary_patches(boundary_dict)

    def generate_mesh_file(self):
        r"""
        Populates keys on itself based on geometry data to output a mesh file
        """
        #
        self['convertToMeters '] = self.mesh_params['convertToMeters']
        #
        # writing verticies
        oflist = OpenFoamList('vertices\n{}'.format(len(self._verticies)))
        for val in self._verticies:
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
        oflist = OpenFoamList('edges')
        self[oflist.name] = oflist
        #
        # getting unique list of boundary faces defined
        bounds = []
        for key in self.face_labels.keys():
            mat = re.match(r'boundary.(\w+)[.]?', key)
            mat = bounds.append(mat.group(1)) if mat else None
        bounds = set(bounds)
        #
        # writing boundaries
        oflist = OpenFoamList('boundary\n{}'.format(len(bounds)))
        for side in bounds:
            ofdict = OpenFoamDict(side)
            side_faces = self._faces[self.face_labels['boundary.'+side]]
            ofdict['type'] = self.mesh_params['boundary.'+side+'.type']
            ofdict['faces'] = OpenFoamList('faces\n\t\t{}'.format(len(side_faces)))
            #
            for val in side_faces:
                val = ['{:7d}'.format(v) for v in val]
                ofdict['faces'].append('(' + ' '.join(val) + ')')
            #
            oflist.append(ofdict)
        self[oflist.name] = oflist
        #
        # writing mergePatchPairs
        oflist = OpenFoamList('mergePatchPairs')
        self[oflist.name] = oflist

    def write_foam_file(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Passes args off to write_mesh_file
        """
        self.write_mesh_file(path, create_dirs, overwrite)

    def write_mesh_file(self, path='.', create_dirs=True, overwrite=False):
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

    def write_symmetry_plane(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Exports the +Y half of the mesh flattening out everything below 0 on
        the Y axis
        """
        #
        # storing orginial verticies
        old_verts = sp.copy(self._verticies)
        self._verticies[sp.where(self._verticies[:, 1] <= 0.0), 1] = 0.0
        #
        # outputting mesh
        self.write_mesh_file(path=path,
                             create_dirs=create_dirs,
                             overwrite=overwrite)
        #
        # restoring original verts
        self._verticies = sp.copy(old_verts)


class OpenFoamExport(dict):
    r"""
    A class to handle generation and exporting of OpenFoam files
    """
    def __init__(self, field=None, avg_fact=1.0, mesh_params=None):
        r"""
        Handles generation and exporting of OpenFoam files
        """
        #
        self.foam_files = {}
        self.block_mesh_dict = None
        if field is not None:
            self.generate_block_mesh_dict(field, avg_fact, mesh_params)

    def generate_block_mesh_dict(self, field, avg_fact=1.0, mesh_params=None):
        r"""
        Passes arguments off to BlockMeshDict init method.
        """
        self.block_mesh_dict = BlockMeshDict(field, avg_fact, mesh_params)

    def generate_foam_files(self, *args):
        r"""
        Generates open foam files and stores them on the export. Each argument
        must be an iterable acceptable to the dictionary constructor with
        two required keys - location and object, class_name is an optional
        key. Those three keys are used to generate file header information.

        The remaining entries in each arg are the desired parameters to put
        in each file.

        Files are stored on the export object in a dictionary attribute called
        'foam_files'. Keys in this dictionary have the format of
        'location.object'.
        TODO: Allow OpenFoamFiles to be incorperated directly.
        """
        #
        # looping through args
        for file in args:
            # generating initial dict from iterable and getting required args
            values = OrderedDict(file)
            location = values.pop('location')
            object_name = values.pop('object')
            class_name = values.pop('class_name', None)
            #
            file = OpenFoamFile(location, object_name, class_name, values=values)
            self.foam_files[location + '.' + object_name] = file

    def write_symmetry_plane(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Passes arguments off to the BlockMeshDict method
        """
        self.block_mesh_dict.write_symmetry_plane(path, create_dirs, overwrite)

    def write_mesh_file(self, path='.', create_dirs=True, overwrite=False):
        r"""
        Passes arguments off to the BlockMeshDict method
        """
        self.block_mesh_dict.write_mesh_file(path, create_dirs, overwrite)

    def write_foam_files(self, path='.', overwrite=False):
        r"""
        Writes the files generated by 'generate_foam_files' to their
        associated directories on the supplied path. If a directory doesn't exist
        then it is created
        """
        #
        # writing files
        for foam_file in self.foam_files.values():
            foam_file.write_foam_file(path=path,
                                      create_dirs=True,
                                      overwrite=overwrite)

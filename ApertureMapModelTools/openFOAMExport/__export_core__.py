"""
This stores the basic classes and functions needed for the openFOAM export script
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/03/22
#
"""
#
import re
import scipy as sp
#
########################################################################
#
# Class Definitions
#
class DataFieldNew:
    r"""
    Base class to store raw data from a 2-D field data file and
    the output data generated by the different processing routines
    """
    def __init__(self, infile, **kwargs):
        self.infile  = infile
        self.outfile = ''
        self.nx = 0
        self.nz = 0
        self.data_map = sp.array([])
        self.output_data = dict()
        self.parse_data_file(**kwargs)

    def copy_data(self, obj):
        r"""
        Copies data properites of the field onto another object created
        """
        obj.infile = self.infile
        obj.nx = self.nx
        obj.nz = self.nz
        obj.data_map = sp.copy(self.data_map)

    def parse_data_file(self, delim='auto'):
        r"""
        Reads the field's infile data and then populates the data_map array
        and sets the fields nx and nz properties.
        """
        #
        if (delim == 'auto'):
            with open(self.infile,'r') as f:
                line = f.readline();
                #
                m = re.search(r'[0-9.]+(\D+)[0-9.]+',line)
                delim = m.group(1)
        #
        self.data_map = sp.loadtxt(self.infile, delimiter=delim)
        #
        self.nz, self.nx = self.data_map.shape

    def create_point_data(self):
        r"""
        The data_map attribute stores the cell data read in from file.
        This function takes that cell data and calculates average values
        at the corners to make a point data map. The Created array is 3-D with
        the final index corresponding to corners.
        Index Locations: 0 = BLC, 1 = BRC, 2 = TRC, 3 = TLC
        """
        #
        self.point_data = sp.zeros((self.nz, self.nx, 4))
        #
        # do stuff
        #
#
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
        if export_params is None:
            export_params = dict()
        #
        field.copy_data(self)
        for key,value in export_params.items():
            self[key] = value
        #
        # initializing required arrays
        num_verts = 2*(self.nx - 1)*( self.nz - 1) + 4*(self.nx + self.nz)
        num_faces = 2*(self.nx + self.nz) + 2*self.data_map.size
        #
        self._verticies = -sp.ones((num_verts, 3), dtype=float)
        self._blocks = -sp.ones((self.data_map.size, 8), dtype=int)
        self._faces = -sp.ones((num_faces, 4), dtype=int)
        self._edges = -sp.ones([])
        self._mergePatchPairs = -sp.ones([])
        #
        # initializing boundary face labels
        for side in ['left', 'right', 'top', 'bottom', 'front', 'back']:
            self['boundary.'+side] = sp.zeros(num_faces, dtype=bool)
        #
        self._build_mesh(avg_fact)

    #
    # May be worthwhile to recreate the corner interpolation I do in the modeling routine
    #

    def _build_mesh(self, avg_fact):
        r"""
        Handles population of the arrays and updating boundary face labels
        """
        #
        # vert map stores the vertex number of the 4 points in lower surface
        # the upper surface is + 1 the value of the corresponding lower point
        vert_map = sp.zeros((self.nz+1,self.nx+1, 4), dtype=int)
        #
        # building verticies and setting vert map
        self._verticies[0] = [0.0, -self.data_map[0,0]/2.0, 0.0]
        self._verticies[1] = [0.0, self.data_map[0,0]/2.0, 0.0]
        #
        iv = 2
        for iz in range(self.nz):
            for ix in range(self.nx):
                xdist = (ix + 1.0) * avg_fact
                ydist = self.data_map[iz,ix]/2.0 * avg_fact
                zdist = (iz + 1.0) * avg_fact
                #
                if (ix == 0):
                    self._verticies[iv] = [0.0, -ydist, zdist]
                    vert_map[iz, ix, 3] = iv
                    vert_map[iz+1, ix, 0] = iv
                    iv += 1
                    self._verticies[iv] = [0.0, ydist, zdist]
                    iv += 1
                #
                if (iz == 0):
                    self._verticies[iv] = [xdist, -ydist, 0.0]
                    vert_map[iz, ix, 1] = iv
                    vert_map[iz, ix+1, 0] = iv
                    iv += 1
                    self._verticies[iv] = [xdist, ydist, 0.0]
                    iv += 1
                #
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
                self._blocks[ib, 0] = vert_map[iz, ix, 0]     # back bottom left
                self._blocks[ib, 1] = vert_map[iz, ix, 1]     # back bottom right
                self._blocks[ib, 2] = vert_map[iz, ix, 1] + 1 # front bottom right
                self._blocks[ib, 3] = vert_map[iz, ix, 0] + 1 # front bottom left
                self._blocks[ib, 4] = vert_map[iz, ix, 3]     # back top left
                self._blocks[ib, 5] = vert_map[iz, ix, 2]     # back top right
                self._blocks[ib, 6] = vert_map[iz, ix, 2] + 1 # front top right
                self._blocks[ib, 7] = vert_map[iz, ix, 3] + 1 # front top left
        #
        # building face arrays
        i = 0
        for iz in range(self.nz):
            ib = iz * self.nx
            self._faces[i] = self._blocks[ib,[0,3,7,4]]
            self['boundary.left'][i] = True
            i += 1
        for iz in range(self.nz):
            ib = iz * self.nx + (self.nx - 1)
            self._faces[i] = self._blocks[ib,[1,2,6,5]]
            self['boundary.right'][i] = True
            i += 1
        for ix in range(self.nx):
            ib =  (self.nz - 1)*self.nx + ix
            self._faces[i] = self._blocks[ib,[4,5,6,7]]
            self['boundary.top'][i] = True
            i += 1
        for ix in range(self.nx):
            ib = ix
            self._faces[i] = self._blocks[ib,[0,1,2,3]]
            self['boundary.bottom'][i] = True
            i += 1
        for iz in range(self.nz):
            for ix in range(self.nx):
                ib = iz * self.nx + ix
                self._faces[i] = self._blocks[ib,[3,2,6,7]]
                self['boundary.front'][i] = True
                i += 1
        for iz in range(self.nz):
            for ix in range(self.nx):
                ib = iz * self.nx + ix
                self._faces[i] = self._blocks[ib,[0,1,5,4]]
                self['boundary.back'][i] = True
                i += 1

    #
#
########################################################################
#
# Function Definitions
#
def export_aperture_map(map_file):
    pass

#
# Test area
infile = r'M:\Desktop\AP_MAP_FLOW\Fracture1ApertureMap-100avg.txt'
export_params = {
    'convertToMeters' : '1E-6',
    'numbersOfCells' : '(5 5 5)',
    'cellExpansionRatios' : 'simpleGrading (1 2 3)',
    #
    'boundary.left.type' : 'empty',
    'boundary.right.type' : 'empty',
    'boundary.top.type' : 'wall',
    'boundary.bottom.type' : 'wall',
    'boundary.front.type' : 'wall',
    'boundary.back.type' : 'wall'
}
field = DataFieldNew(infile)
export = OpenFoamExport(field, 10.0, export_params)
self = export





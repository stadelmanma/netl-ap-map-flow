"""
This stores the basic classes and functions needed to interact with OpenFoam
files.
#
Written By: Matthew Stadelman
Date Written: 2016/03/22
Last Modifed: 2016/08/08
#
"""
#
from collections import OrderedDict
import os
import re
#
########################################################################
#


class OpenFoamObject(object):
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
        if values is not None:
            init_vals = values
        #
        super().__init__(init_vals)
        self.name = name.strip()

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
        if values is not None:
            init_vals = values
        #
        super().__init__(init_vals)
        self.name = name.strip()

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
        ('class', None),
        ('location', None),
        ('object', None)
    ])
    # trimming off leading newlines
    FOAM_HEADER = FOAM_HEADER[1:]
    FOAM_SPACER = FOAM_SPACER[1:]

    def __init__(self, *args, **kwargs):
        r"""
        Creates and instance of the class passing the first three arguments
        to the FileFile header dict and the final argument can be used to
        initialize the OpenFoamFile object with entries.

        location : string, sets the subdirectory location of the file
            during output.
        object_name : string, sets initial value of self.name attribute used
            to name the output file and the 'object' key in the FoamFile dict
        class_name : string, optional, sets the 'class' key in the FoamFile
            dict, it defaults to 'dictionary'
        values : iterable, optional, any valid iterable that can be used to
            initialize a regular Python dictionary
        """
        # choosing initialization method based on number of args
        if len(args) == 1:
            foam_file = OpenFoamFile._init_from_file(args[0])
            #
            location = foam_file.head_dict['location'].replace('"', "")
            object_name = foam_file.head_dict['object']
            class_name = foam_file.head_dict.get('class', 'dictionary')
            values = foam_file.items()
        else:
            location = args[0]
            object_name = args[1]
            class_name = kwargs.get('class_name', 'dictionary')
            values = kwargs.get('values', {})
        #
        # initializing class and head_dict
        super().__init__(values)
        self.name = object_name
        self.head_dict = OpenFoamDict(OpenFoamFile.HEAD_DICT.name,
                                      OpenFoamFile.HEAD_DICT.items())
        #
        # setting head dict values
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
        return str_rep

    @staticmethod
    def _init_from_file(filename):
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
            while not re.match(r'^}', content) and content:
                content = add_param(content, ofdict)
            #
            content = re.sub(r'^}\n', '', content)
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
            while not re.match(r'^\);', content) and content:
                content = add_param(content, oflist)
            #
            content = re.sub(r'^\);\n', '', content)
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
                line = re.match(r'.*\n', content).group()
                line = re.sub(r';', '', line)
                line = line.strip()
                try:
                    key, value = re.split(r'\s+', line, maxsplit=1)
                except ValueError:
                    key, value = line, ''
                #
                # removing line from content
                content = re.sub(r'^.*\n', '', content)
                if isinstance(out_obj, list):
                    out_obj.append(line)
                else:
                    out_obj[key] = value
            #
            return content
        #
        # reading file
        with open(filename, 'r') as infile:
            content = infile.read()
        #
        if not re.search('FoamFile', content):
            msg = 'Invalid OpenFoam input file, no FoamFile dict'
            raise ValueError(msg)
        #
        # removing comments and other characters
        inline_comment = re.compile(r'(//.*)')
        block_comment = re.compile(r'(/[*].*?[*]/)', flags=re.S)
        content = inline_comment.sub('', content)
        content = block_comment.sub('', content)
        content = re.sub(r'\s*$', '\n', content, flags=re.M)
        content = re.sub(r'^\s*', '', content, flags=re.M)
        #
        # parsing content of file
        foam_file_params = OrderedDict()
        while content:
            content = add_param(content, foam_file_params)
        #
        # generating OpenFoamFile
        head_dict = foam_file_params.pop('FoamFile', {})
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

=========================
Using the OpenFoam Module
=========================

.. contents::

Description
===========
The OpenFoam Module is designed to allow easy modification and creation of OpenFoam files in a Python interface. The main motivation for writing the code was to create a work flow that would allow results from the Local Cubic Law (LCL) model to be quickly compared to OpenFoam results on the same geometry. The module has routines to load and parse basic OpenFoam files as well as generate a blockMeshDict file from a 2-D aperture map. There are three primary classes and three additional helper classes used in the module, all of which will be gone over next. The apm_open_foam_export.py script wraps all of the functionality present in the module into a program that can generate a complete OpenFoam simulation by modifying an existing set of OpenFoam files. 

OpenFoamFile Class
==================
The OpenFoamFile class is one of the central objects of the OpenFoam module allowing the reading of an existing OpenFoamFile or creating one from scratch. It inherits from the OpenFoamObject and the OrderedDict classes. All OpenFoam files have a dictionary-like structure and as such data is stored on the OpenFoamFile object in the same format as a regular Python dictionary. It has one method, :code:`write_foam_file(*args, **kwargs)`. The class can be instantiated by directly providing values or giving a filename to read instead. Direct creation of an OpenFoamFile instance has two required positional arguments and 2 optional keyword arguments. :code:`OpenFoamFile(location, object_name, class_name=None, values=None)`. The first three correspond to entries in the FoamFile dictionary at the top of all OpenFoam files and the final argument is a set of key, value pairs to load onto the object. Because the class inherits from the OrderedDict class any valid dictionary iterable in Python can be used however a list of key,value pairs works best because order is maintained.

.. code-block:: python
	
	# loading modules
	import os
	from ApertureMapModelTools import OpenFoam as of
	
	# directly creating an OpenFoamFile object
	init_vals = [
	    ('numberOfSubdomains', '2'),
	    ('method', 'scotch'),
	    ('distributed', 'no')
	]
	of_file = of.OpenFoamFile('system', # goes in the system directory 
	                          'decomposeParDict', # OpenFoam object name
	                          class_name='dictionary, # showing default value
	                          values=init_vals) 

	# checking value and resetting
	print(of_file['numberOfSubdomains']) # prints '2'
	of_file['numberOfSubdomains'] = '4'

	# creating instance of OpenFoamFile by reading an existing file
	filename = 'path/to/OpenFoamFile'
	of_file = of.OpenFoamFile(filename)

Once an instance has been created and contains the desired values a file can be easily written to a specified location by calling :code:`write_foam_file(path='.', create_dirs=True, overwrite=False)` instance method. By default a file is written to the following path and name './location/object' where location and object are values stored in the :code:`head_dict` attribute of the class object. In the above example location is the 'system' directory and object is 'decomposeParDict'. An alternative output name, for example 'decomposeParDict-np4' can be defined by setting the :code:`name` attribute of the object. The example below will show a few examples of writing files. 

When using an instance produced from an existing file the location and name attribute can differ from the defaults. The code will attempt to pull the 'location' value from the FoamFile dict in the file being read, if that fails then it will use the name of the directory the file was stored in. The initial value of the :code:`name` attribute is always the name of the file being read. This was done to allow different versions of the same file to coexist when creating an export.

.. code-block:: python
	
	# writing file to './system/decomposeParDict'
	of_file.write_foam_file()

	# writing file to a FOAM_RUN case directory (may not work correctly in Spyder)
	foam_run = os.getenv('FOAM_RUN')
	case_dir = os.path.join(foam_run, 'LCL-test')
	of_file.write_foam_file(path=case_dir)

	# writing file to './decomposeParDict'
	of_file.write_foam_file(create_dirs=False)

	# writing file to './system/decomposeParDict-np4'
	of_file.name = 'decomposeParDict-np4'
	of_file.write_foam_file()
	  

OpenFoamObject Class
--------------------
This class is not intended for direct use and has no methods of its own. It is used to identify any objects descended from it because they have specialized :code:`__str__` methods that need called directly. Any future methods that need applied to the entire gamut of OpenFoam objects will also be added here.

OpenFoamDict Class
------------------
Along with the OpenFoamList class this is a primary building block of an OpenFoam file. It is descended from the OpenFoamObject and OrderedDict classes. The primary feature of the class is a specialized :code:`__str__` method that produces a nicely formatted dictionary structure in an OpenFoam file with proper indentation. Instantiation is done in the same way as a regular dict with one exception, the first argument is the 'name' to be used in output and is required. The second argument is optional and can be any valid iterable used to initialize a regular dictionary. Any number of OpenFoamDicts and OpenFoamLists can be mixed and nested into each other.

OpenFoamList Class
------------------
This is the second core building block used in OpenFoam files and mainly in blockMeshDict generation. It is descended from the OpenFoamObject and list classes. This class also has a specialized :code:`__str__` method that produces an output considerably different than calling :code:`str()` on a regular Python list and honors indentation from nesting. Instantiation is similar to the OpenFoamDict class where the first parameter is the required named attribute of the class and the second is optional but can be any valid iterable used to initialize a regular list. As above any number of OpenFoamDicts and OpenFoamLists can be mixed and nested into each other.

BlockMeshDict Class
===================
The BlockMeshDict class is used to generate a mesh file from a provided 2-D aperture map data field. It descends from the OpenFoamFile class however has significantly different usage and the only method it shares from the parent class is :code:`write_foam_file`. If :code:`create_dirs=true` then it will automatically generate the 'constant/polyMesh' sub-directories on the desired path. Full explanation of mesh generation is beyond the scope of this example and is covered in depth in the `blockMeshDict example <blockmeshdict-generation-example.rst>`_

OpenFoamExport Class
====================
The OpenFoamExport class is designed to act as a central location to manage and write OpenFoam files. This class has a few public methods that allow it to interact with OpenFoam objects. It can be initialized either with no arguments or supplying the optional arguments to pass along to the BlockMeshDict class. The latter case generates and stores a BlockMeshDict class instance on the :code:`block_mesh_dict` attribute other wise that attribute is 'None'. The second primary attribute of the class is a foam_files dictionary where each key-value pair represents an OpenFoamFile instance. Each key has the format of 'location.name' where location is the value of the 'location' key in the file's head_dict and name is the file's 'name' attribute.

BlockMesh Related Methods
-------------------------
As stated above this class is able to call some methods of its internally stored BlockMeshDict instance. An instance of the BlockMeshDict is created by calling the :code:`generate_block_mesh_dict(field, avg_fact=1.0, mesh_params=None)` method. The arguments are exactly the same as and passed on to the BlockMeshDict constructor. These arguments can also be supplied during instantiation of the OpenFoamExport class and a BlockMeshDict instance will automatically be created. The other two methods available are :code:`write_symmetry_plane(path='.', create_dirs=True, overwrite=False)` and :code:`write_mesh_file(path='.', create_dirs=True, overwrite=False)`. Any other BlockMeshDict methods such as :code:`generate_threshold_mesh` need to be called directly from the :code:`block_mesh_dict` attribute. Additionally the :code:`write_foam_files` method of the OpenFoamExport call will not write a mesh file, one of the above methods will need to be called to output one.

OpenFoamFile Related Methods
----------------------------
There are two methods associated with OpenFoamFile instances, they are :code:`generate_foam_files(*args)` and :code:`write_foam_files(path='.', overwrite=False)`. The first method accepts any number of arguments where each argument is one of the following three forms.

 1. An existing instance of the OpenFoamFile class
 2. A filename to read from
 3. A valid dictionary iterable with at minimum a 'location' and 'object' key.

The two required keys and an optional 'class_name' key are passed onto the OpenFoamFile constructor. Any remaining values are sent along in the 'values' keyword argument. All OpenFoamFile instances are stored on the 'foam_files' attribute of the OpenFoamExport class. That attribute is a python dictionary and the format of keywords are 'location.name' where location is the 'location' key in the stored file's head dict and 'name' is the value of the 'name' attribute of the stored file.

The final method is :code:`write_foam_files(path='.', overwrite=False)` which writes every file stored in the foam_files dict to :code:`path/location/name`. The blockMeshDict is not generated using this method, one of the methods listed in the above section needs to be used as well.

The apm_open_foam_export.py Script
==================================

Usage
-----
Located in the `scripts <../scripts>`_ directory, it is designed to help automate the process of taking input files from the LCL model and creating a full OpenFoam simulation case to run. The script is meant to be run from the command line and accepts several arguments and flags. The script only modifies or creates four files including the blockMesh, all other files will either need to be created or exist in the directory read from.

Arguments and Flags
-------------------
The export command line utility accepts several flags and a useful help message can be generated by running the command :code:`apm_open_foam_export.py --help`. The command needs to be run from the scripts folder unless a valid path to the script is used or you make the scripts folder visible on the :code:`$PATH` environment variable. Basic syntax of the command is:

.. code-block:: bash
	
	apm_open_foam_export.py [-ivf] [-r READ_DIR] [-o OUTPUT_DIR] [input_file]

All arguments are optional, the default values for READ_DIR and OUTPUT_DIR is the current working directory. When reading from a directory the command will not recursively search all subdirectories, only the constant, system and 0 directories will be searched if they exist. Sub directories of those directories are also not searched, for example nothing in the constant/polyMesh directory will be found unless that is explicitly stated as the directory to read from. Note, blockMeshDict files are not directly excluded but should not be intentionally read due to their length and likelihood of parsing errors due to different formatting.

Flag and Argument description
 * -i, --interactive : interactive mode, explained below
 * -v, --verbose : verbose logging messages
 * -f, --force : overwrite mode, allows any existing files to be replaced
 * -r [dir], --read-dir [dir] : specifies a directory to read files from
 * -o [dir], --output-dir [dir] : specifies a directory to output the files to. 
 * input_file : LCL Model input file to pull information from


Automatic BlockMesh Generation
------------------------------
By suppling a LCL input_file in the command's args an instance of the BlockMeshDict class is created and automatically linked to the internal export variable. Several pieces of information are pulled from the input_file. However, the five of note for blockMeshDict generation are APER-MAP, AVG_FACT, VOXEL, ROUGHNESS, HIGH-MASK and LOW-MASK. The latter three are applied as geometric adjustments to the aperture map data read from the APER-MAP keyword. The value of AVG_FACT is passed on to the BlockMeshDict constructor as the avg_fact argument, voxel-size and the BC's determined are stored in the mesh_params dictionary. Also, a default cell-grading of (5 5 5) is used.

Automatic File Generation
-------------------------
The three files below are generated by the script or modified from existing files found and read. A U file is only created/modified if an aperture map is found at the path specified by the APER-MAP keyword in the input file.

p File
~~~~~~
The script will check the foam_files dict for a '0.p' key to update and if one is not found then it will create a new OpenFoamFile instance for that key. The only dictionary updated in the p file is the boundaryField dict. It will attempt to pull patch names from the blockMeshDict object but if it does not exist then the standard 6 faces are used: left, right, bottom, top, front and back. Initially all patches have a 'zeroGradient' boundary condition defined. If any pressure BC's were found in the LCL model input file then a kinematic pressure condition is created for that BC.

U File
~~~~~~
The U file is generated in much the same way as the p file, if there is not a value for the '0.U' key in the foam_files dictionary one is created. All patches are initially defined as no-slip walls. If a pressure BC was defined for a side then that side is changed from a no-slip wall to the zeroGradient BC type. If a fixed rate condition was defined for the LCL model then average cross-sectional area of the BC side is used to calculate a uniform U field value from the volumetric flow.

transportProperties File
~~~~~~~~~~~~~~~~~~~~~~~~
The transport properties file only has two keys updated 'nu' and 'rho' with the values defined in the input file. Any additional coefficients defined will need to be manually updated. If a viscosity or density is not supplied by the LCL model input file then the standard values for water are used 1.0 cP and 1000 kg/m^3. Only a file stored on the 'constant.transportProperties' key of the foam_files dictionary is modified or created if it doesn't exist.

Interactive Mode
----------------
Interactive mode is activated by using the -i flag. When interactive mode is used the script recalls itself using :code:`python3 -i (script and args passed)` which essentially causes the script to be executed in an interactive python interpreter. Anything that exists on the main namespace in the script is visible and defined in the interactive session such as variables, functions, module imports, etc. Using the command :code:`apm_open_foam_export.py -iv` will begin an interactive mode session. 

Files are not automatically written in interactive mode. To write all files based on the command line args used call the function :code:`write_all_files(overwrite=False)`. If the -f flag was used :code:`overwrite=False` is ignored, alternatively :code:`overwrite=True` can be used to mimic the effects of the -f flag. This command will write the blockMeshDict file as well.

Several global variables are defined to ease the use of interactive mode. For a more complete understanding of what is available in terms of functions and globals it recommended to review the code in `apm_open_foam_export.py <../scripts/apm_open_foam_export.py>`_.

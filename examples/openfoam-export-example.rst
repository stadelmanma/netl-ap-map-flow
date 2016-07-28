
Using the OpenFoamExport class
==============================
.. contents::

Description
-----------
This describes the basic process of how to convert a vertical aperture map into an OpenFOAM readable blockMeshDict. Using the OpenFoamExport class is a very simple and all the heavy lifting is done internally unless additional customizations are needed. Additional customizations can include setting up your own edges and patches to merge as well as apply more than just the standard boundary face labels. The routine can also create the two sub directories OpenFOAM requires the mesh file to be in if desired. The template at the bottom of the file can be used to base simple exports off of by simply copying and pasting it into a file and running it as a python script. **Currently there is not a good method to add custom face labels that is in the works.**

There are three steps required to do an export:
  1. Create a DataField object to store the aperture map data
  2. Create the OpenFoamExport class
  3. Write the export to your desired location

Setting up the Export
---------------------
As mentioned the first step is creating a data field object, the only required argument is the path to the aperture map file. However first we need to import the modules.

.. code-block:: python

    from ApertureMapModelTools import DataField
    from ApertureMapModelTools.OpenFoamExport import OpenFoamExport

Next we can instantiate the data field class.

.. code-block:: python

    aper_map_file = r'./examples/Fractures/Fracture1ApertureMap-10avg.txt'
    aper_map_field = DataField(aper_map_file)

With the DataField for the aperture map file created we can now instantiate the OpenFoamExport class. The class accepts three arguments, :code:`OpenFoamExport(field, avg_fact=1.0, mesh_params=None)`. The first argument :code:`field` is a :code:`DataField` object, in this case :code:`aper_map_field` will go there. :code:`avg_fact` is the horizontal averaging or scale factor of the map. It defaults to assume that each cell in the map has a 1 voxel by 1 voxel square base. The final argument :code:`mesh_params` is a dictionary used to populate several aspects of the blockMeshDict file. Below I have listed the default params for the export class, these will be overwritten by anything you define.

.. code-block:: python

    default_mesh_params = {
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

:code:`convertToMeters` is where you specify the voxel to meters conversion factor. The :code:`boundary.*.type` entries set the types for each defined face label. Any additional face labels you create would need their type specified here. Next we will create the export class for our aperture map defining the parameters required to replicate a 2-D LCL simulation.

.. code-block:: python

    my_mesh_params = {
        'convertToMeters': '2.680E-5',
        #
        'boundary.left.type': 'empty',
        'boundary.right.type': 'empty',
        'boundary.top.type': 'wall',
        'boundary.bottom.type': 'wall',
        'boundary.front.type': 'wall',
        'boundary.back.type': 'wall'
    }

    export = OpenFoamExport(aper_map_field, avg_fact=10.0, mesh_params=my_mesh_params)

The export stores the verticies, blocks, faces, edges and mergePatchPairs in scipy ndarrays as attributes of the BlockMeshDict class which is stored on the export object as export.block_mesh_dict. They are accessible by typing :code:`export.block_mesh_dict._verticies` or :code:`export.block_mesh_dict._edges`, etc. The :code:`._edges` and :code:`._mergePatchPairs` arrays are not initialized by default and would need to be created. Face labels are stored as keys on the BlockMeshDict class in a dictionary named :code:`face_labels` each key has the format boundary.side for example :code:`face_labels['boundary.bottom']` would return a boolean array and all indicies that are :code:`True` correspond to a 'bottom' face. If you need to add custom edges or mergePatchPairs then a valid list of strings representing them will need to be stored in the :code:`export.block_mesh_dict._edges` and :code:`export.block_mesh_dict._mergePatchPairs` arrays. The export does no additional processing on them so what you put is is exactly what will be output in those sections of the blockMeshDict file. For example to add in arc shaped edges you would need to store strings like this  :code:`'arc 1 5 (1.1 0.0 0.5)'` in the :code:`._edges` array. Each entry in the :code:`._edges` array should describe a single edge.

Creating the blockMeshdict File
-------------------------------
All of the work mainly takes place in the setup steps and the user just needs to call :code:`export.write_mesh_file()` to use the defaults and output a mesh file in the local directory. The output function also takes three optional parameters as well, :code:`export.write_mesh_file(path='.', create_dirs=True, overwrite=False)`. The first allows for an alternate output location, say in the 'run' folder of OpenFOAM, relative and absolute paths are valid. `create_dirs` tells the export whether or not to create the :code:`constants/polyMesh` directories for you, if this is true and they already exist the file will be output in that location preserving the contents of those directories. The final parameter `overwrite` prevents or enables the program to replace an existing blockMeshDict file in the chosen location.

Template Code for Simple Exports
--------------------------------
The template below can be used with some minor customization for simple exports.

.. code-block:: python

    import os
    from ApertureMapModelTools import DataField
    from ApertureMapModelTools.OpenFoamExport import OpenFoamExport
    #
    # The path to the aperture map needs to be updated to match the file you want to export
    aper_map_file = os.path.join('path', 'to', 'aperture_map_file.txt')
    aper_map_field = DataField(aper_map_file)
    #
    # convertToMeters needs to be updated to match your data
    # numbersOfCells needs to be updated to match your desired internal block meshing
    my_mesh_params = {
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
    #
    export = OpenFoamExport(field=aper_map_field, avg_fact=1.0, mesh_params=my_mesh_params)
    export.write_mesh_file(path='.', create_dirs=True, overwrite=False)


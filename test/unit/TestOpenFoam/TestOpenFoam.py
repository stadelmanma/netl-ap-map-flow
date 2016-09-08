"""
Handles testing of the OpenFOAM export module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/08/15
#
"""
#
import os
import pytest
import scipy as sp
from ApertureMapModelTools.OpenFoam.__openfoam_core__ import OpenFoamObject
from ApertureMapModelTools import OpenFoam


class TestOpenFoam:
    r"""
    Executes a set of functions to handle testing of the export routines
    """
    def setup_class(self):
        pass

    def test_open_foam_object(self):
        of_object = OpenFoamObject()
        with pytest.raises(NotImplementedError):
            print(of_object)

    def test_openfoam_dict(self):
        init_vals = [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')]
        of_dict = OpenFoam.OpenFoamDict('testDict', values=init_vals)
        assert of_dict.name == 'testDict'
        assert list(of_dict.items()) == init_vals
        #
        # adding a nested dict
        of_dict['nestedDict'] = OpenFoam.OpenFoamDict('nestedDict', of_dict)
        #
        print(of_dict)

    def test_openfoam_list(self):
        init_vals = ['val1', 'val2', 'val3']
        of_list = OpenFoam.OpenFoamList('testList', values=init_vals)
        assert of_list.name == 'testList'
        assert of_list == init_vals
        #
        # adding a nested list
        of_list.append(OpenFoam.OpenFoamList('nestedList', of_list))
        #
        print(of_list)

    def test_open_foam_file(self):
        init_vals = [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')]
        of_file = OpenFoam.OpenFoamFile('test_location', 'test_object', class_name='test_class', values=init_vals)
        #
        # checking initialization
        assert of_file.head_dict['class'] == 'test_class'
        assert of_file.head_dict['location'] == '"test_location"'
        assert of_file.head_dict['object'] == 'test_object'
        assert list(of_file.items()) == init_vals
        #
        # adding  dict and list
        of_file['dict'] = OpenFoam.OpenFoamDict('dict', init_vals)
        of_file['list'] = OpenFoam.OpenFoamList('list', ['val1', 'val2', 'val3'])
        print(of_file)
        #
        # writing file
        of_file.write_foam_file(TEMP_DIR, create_dirs=True, overwrite=False)
        with pytest.raises(FileExistsError):
            of_file.write_foam_file(TEMP_DIR, create_dirs=True, overwrite=False)
        #
        # reading a file
        path = os.path.join(FIXTURE_DIR, 'testFoamFile')
        of_file = OpenFoam.OpenFoamFile(path)
        print(of_file)
        #
        assert of_file.head_dict['object'] == 'testFoamFile'
        assert of_file['keyword1'] == 'value1'
        assert isinstance(of_file['toplevel_dict'], OpenFoam.OpenFoamDict)
        assert isinstance(of_file['toplevel_list'], OpenFoam.OpenFoamList)
        assert len(of_file['toplevel_dict'].keys()) == 6
        assert len(of_file['toplevel_list']) == 5
        assert of_file['toplevel_dict']['nest_dict3']['n3keyword3'] == 'n3value3'
        assert of_file['toplevel_list'][3][1] == 'n4value2'
        #
        # commented out stuff
        with pytest.raises(KeyError):
            of_file['inline_cmt_keyword'] is not None
        with pytest.raises(KeyError):
            of_file['toplevel_dict2'] is not None
        #
        # invalid file
        with pytest.raises(ValueError):
            path = os.path.join(FIXTURE_DIR, 'TEST_INIT.INP')
            of_file = OpenFoam.OpenFoamFile(path)

    def test_block_mesh_dict(self, data_field_class):
        field = data_field_class()
        offsets = data_field_class()
        #
        params = {
            'convertToMeters': '0.000010000',
            'numbersOfCells': '(5 10 15)',
            'cellExpansionRatios': 'simpleGrading (1 2 3)',
            #
            'boundary.left.type': 'empty',
            'boundary.right.type': 'empty',
            'boundary.top.type': 'wall',
            'boundary.bottom.type': 'wall',
            'boundary.front.type': 'wall',
            'boundary.back.type': 'wall'
        }
        mesh = OpenFoam.BlockMeshDict(field, avg_fact=10.0, mesh_params=params, offset_field=offsets)
        mesh._edges = ['placeholder']
        mesh._mergePatchPairs = ['placeholder']
        mesh.write_foam_file(TEMP_DIR, overwrite=True)
        #
        # attempting to overwrite existing mesh file
        with pytest.raises(FileExistsError):
            mesh.write_mesh_file(TEMP_DIR, overwrite=False)
        #
        # writing out a symmetry plane
        mesh.write_symmetry_plane(TEMP_DIR, overwrite=True)
        #
        # testing generation of a thresholded mesh
        mesh.generate_threshold_mesh(min_value=9, max_value=90)
        assert sp.all(mesh.data_map[0, :] == 0)
        assert sp.all(mesh.data_map[9, :] == 0)
        assert len(mesh._blocks) == 80

    def test_open_foam_export(self, data_field_class, openfoam_file_class):
        self._field = data_field_class()
        #
        export = OpenFoam.OpenFoamExport(field=self._field)
        #
        path_param = os.path.join(FIXTURE_DIR, 'testFoamFile')
        iter_param = [
            ('location', 'test'),
            ('object', 'iterFile'),
            ('key1', 'val1'),
            ('key2', 'val2'),
        ]
        #
        export.generate_foam_files(path_param, iter_param, openfoam_file_class())
        assert export.foam_files['test.iterFile']
        assert export.foam_files['test.iterFile']['key1'] == 'val1'
        assert list(export.foam_files['test.iterFile'].keys()) == ['key1', 'key2']
        assert export.foam_files['fixtures.testFoamFile']
        assert export.foam_files['conftest.pseduoOpenFoamFile']
        #
        export.write_mesh_file(TEMP_DIR, create_dirs=True, overwrite=True)
        export.write_symmetry_plane(TEMP_DIR, create_dirs=True, overwrite=True)
        export.write_foam_files(TEMP_DIR, overwrite=True)
        with pytest.raises(FileExistsError):
            export.write_foam_files(TEMP_DIR, overwrite=False)

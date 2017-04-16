"""
Handles testing of the script files when running setup.py
#
Written By: Matthew Stadelman
Date Written: 2017/04/09
Last Modifed: 2017/04/09
#
"""
from glob import glob
import os
import pytest
from subprocess import Popen, PIPE, check_output
import yaml


class TestScripts:
    r"""
    Manages running the test suite
    """
    def setup_class(cls):
        # determine top of repository and location of scripts folder
        cmd = ['git', 'rev-parse', '--show-toplevel']
        cls.repo_top = check_output(cmd, universal_newlines=True).strip()

        # get all script files and set basename as key
        script_path = os.path.join(cls.repo_top, 'scripts')
        cls.script_files = glob(os.path.join(script_path, 'apm-*'))
        cls.script_files = {os.path.basename(s): s for s in cls.script_files}

    def run_script(cls, script, args):
        r"""
        runs the set of args provided for the script
        """
        script = cls.script_files[script]
        cmd = ['python', script] + args
        proc = Popen(cmd)
        print('Running command: ', cmd)
        assert not proc.wait()

    def test_apm_bulk_run(cls):
        # load bulk run file for pre-processing
        bulkrun_inp_file = os.path.join(FIXTURE_DIR, 'test-bulk-run.yaml')
        with open(bulkrun_inp_file, 'r') as f:
            bulk_run_inps = yaml.load(f)
        #
        # update paths to be platform independent
        file_path = bulk_run_inps['initial_input_file']
        bulk_run_inps['initial_input_file'] = os.path.join(FIXTURE_DIR, file_path)
        for key, file_path in bulk_run_inps['default_file_formats'].items():
            if key == 'APER-MAP':
                file_path = os.path.join(FIXTURE_DIR, 'maps', file_path)
            else:
                file_path = os.path.join(TEMP_DIR, file_path)
            #
            bulk_run_inps['default_file_formats'][key] = file_path
        #
        # output the file
        bulkrun_inp_file = os.path.join(TEMP_DIR, 'test-bulk-run.yaml')
        with open(bulkrun_inp_file, 'w') as f:
            f.write(yaml.dump(bulk_run_inps))
        #
        # run dry run
        args = ['-v', bulkrun_inp_file]
        cls.run_script('apm-bulk-run.py', args)
        #
        # actually perform bulk run
        args = ['-v', '--start', bulkrun_inp_file]
        cls.run_script('apm-bulk-run.py', args)
        #
        # checking that some files were created
        assert os.path.isfile(os.path.join(TEMP_DIR,
                              'parallel-plate-01vox-RF1.00-400PA-STAT.csv'))
        assert os.path.isfile(os.path.join(TEMP_DIR,
                              'parallel-plate-01vox-RF1.00-400PA-STAT.yaml'))
        assert os.path.isfile(os.path.join(TEMP_DIR,
                              'parallel-plate-10vox-RF1.00-700PA-LOG.TXT'))
        assert os.path.isfile(os.path.join(TEMP_DIR,
                              'Fracture1ApertureMap-10avg-RF0.00-300PA-INIT.INP'))

    def test_fracture_df(cls):
        # run dry run -xz --bot --mid --top
        infile = os.path.join(FIXTURE_DIR, 'binary-fracture-small.tif')
        args = ['-xz', '--bot', '--mid', '--top', infile, '-o', TEMP_DIR]
        cls.run_script('apm-fracture-df.py', args)
        #
        # check that file was created
        assert os.path.isfile(os.path.join(TEMP_DIR, 'binary-fracture-small-df.txt'))

    def test_convert_csv_stats_file(cls):
        #
        # run dry run -xz --bot --mid --top
        infile = os.path.join(FIXTURE_DIR, 'legacy-stats-file.csv')
        args = ['-v', infile, '-o', TEMP_DIR]
        cls.run_script('apm-convert-csv-stats-file.py', args)
        #
        assert os.path.isfile(os.path.join(TEMP_DIR, 'legacy-stats-file.yaml'))

    def test_generate_aperture_map(cls):
        #
        infile = os.path.join(FIXTURE_DIR, 'binary-fracture.tif')
        args = ['-v', '--gen-colored-stack', infile, '-o', TEMP_DIR]
        cls.run_script('apm-generate-aperture-map.py', args)
        #
        # test for file existance
        filename = 'binary-fracture-aperture-map.txt'
        assert os.path.isfile(os.path.join(TEMP_DIR, filename))
        filename = 'binary-fracture-colored.tif'
        assert os.path.isfile(os.path.join(TEMP_DIR, filename))

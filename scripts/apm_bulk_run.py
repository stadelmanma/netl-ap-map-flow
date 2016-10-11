#!/usr/bin/env python3
r"""
Parses a YAML formatted file to automatically setup a bulk run of the
LCL model.
"""
import yaml
import sys
from ApertureMapModelTools.RunModel import BulkRun, InputFile

# loading yaml file and parsing input file
inputs = yaml.load(open(sys.argv[1], 'r'))
inp_file = InputFile(inputs['initial_input_file'])

# Creating class with provided kwargs
bulk_run = BulkRun(inp_file, **inputs['bulk_run_keyword_args'])

# Generating the InputFile list
bulk_run.generate_input_files(inputs['default_run_parameters'],
                              inputs['default_file_formats'],
                              case_identifer=inputs['case_identifier'],
                              case_params=inputs['case_parameters'])

# testing simulations (replace 'dry_run' with 'bulk_run' to actually run sims)
bulk_run.dry_run()

# the start() method actually begins the simulations
# bulk_run.start()

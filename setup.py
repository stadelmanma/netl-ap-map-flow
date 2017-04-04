from glob import glob
import os
import sys
from distutils.util import convert_path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Check Python version
if sys.version_info < (3, 4):
    raise Exception('ApertureMapModelTools requires Python 3.4 or greater to run')

main_ = {}
ver_path = convert_path('ApertureMapModelTools/__init__.py')
with open(ver_path) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, main_)

setup(
    name='ApertureMapModelTools',
    description = ' A fracture flow modeling package utilizing a modified local cubic law approach with OpenFoam and ParaView compatibility.',
    version=main_['__version__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Fortran',
        'Intended Audience :: Science/Research'
        'Topic :: Scientific/Engineering :: Physics',
    ],
    packages=[
        'ApertureMapModelTools',
        'ApertureMapModelTools.DataProcessing',
        'ApertureMapModelTools.OpenFoam',
        'ApertureMapModelTools.RunModel',
    ],
    scripts=glob('scripts/apm-*'),
    install_requires=[
        'numpy',
        'scipy',
        'pillow>=3.4.0',
        'pyyaml'
    ],
    author='Matthew A. Stadelman',
    author_email='stadelmanma@gmail.com',
    download_url='https://github.com/stadelmanma/netl-AP_MAP_FLOW',
    url='https://github.com/stadelmanma/netl-AP_MAP_FLOW'
)

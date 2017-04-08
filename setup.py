from glob import glob
import os
import sys

try:
    from setuptools import setup
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)

# Check Python version
if sys.version_info < (3, 4):
    print('ApertureMapModelTools requires Python 3.4 or greater to run')
    sys.exit(1)

# pull long description from README
with open('README.rst', 'r') as f:
    long_desc = f.read()

# pull out version and default name from module
main_ = {}
ver_path = os.path.join('ApertureMapModelTools', '__init__.py')
with open(ver_path) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, main_)

# call setup
setup(
    name='ApertureMapModelTools',
    description=' A fracture flow modeling package utilizing a modified local cubic law approach with OpenFoam and ParaView compatibility.',
    long_description=long_desc,
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
    include_package_data=True,
    package_data={
        'ApertureMapModelTools': ['logging.conf', 'src/*.F', 'src/makefile']
    },
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
    url='https://github.com/stadelmanma/netl-AP_MAP_FLOW',
    license='GPLv3',
    keywords=['Local Cubic Law', 'Paraview', 'OpenFoam']
)

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
    print('apmapflow requires Python 3.4 or greater to run')
    sys.exit(1)

# pull long description from README
with open('README.rst', 'r') as f:
    long_desc = f.read()

# pull out version and default name from module
main_ = {}
ver_path = os.path.join('apmapflow', '__init__.py')
with open(ver_path) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, main_)

# get all scripts
scripts = glob(os.path.join('apmapflow', 'scripts', '*'))
fmt = '{0} = apmapflow.scripts.{0}:main'
for i, script in enumerate(scripts):
    scripts[i] = fmt.format(os.path.splitext(os.path.basename(script))[0])

# call setup
setup(
    name='apmapflow',
    description='A fracture flow modeling package utilizing a modified local ' +
                'cubic law approach with OpenFoam and ParaView compatibility.',
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
        'apmapflow',
        'apmapflow.data_processing',
        'apmapflow.openfoam',
        'apmapflow.run_model',
        'apmapflow.scripts'
    ],
    entry_points={
        'console_scripts': scripts
    },
    include_package_data=True,
    package_data={
        'apmapflow': ['logging.conf', 'src/*.F', 'src/makefile']
    },
    install_requires=[
        'numpy',
        'scipy',
        'pillow>=3.4.0',
        'pint',
        'pyyaml'
    ],
    author='Matthew A. Stadelman',
    author_email='stadelmanma@gmail.com',
    download_url='https://github.com/stadelmanma/netl-ap-map-flow',
    url='https://github.com/stadelmanma/netl-ap-map-flow',
    license='GPLv3',
    keywords=['Local Cubic Law', 'Paraview', 'OpenFoam']
)

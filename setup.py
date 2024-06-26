from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('rtd/properties.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

VERSION = main_ns['__version__']
DESCRIPTION = ''
LONG_DESCRIPTION = ''

# Setting up
setup(
        name="rtd-code-python", 
        version=VERSION,
        author="",
        author_email="",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
                'mergedeep>=1.3',
                'numpy>=1.24',
                'nptyping>=2.5.0',
                'matplotlib>=3.7',
                'trimesh>=3.21',
                'python-fcl>=0.7',
                'scipy>=1.10',
                'urchin>=0.0.27',
                'pyvista>=0.39.0',
                'websockets>=12.0',
        ],
)
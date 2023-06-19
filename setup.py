from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = ''
LONG_DESCRIPTION = ''

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="rtd-code-python", 
        version=VERSION,
        author="",
        author_email="",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
)
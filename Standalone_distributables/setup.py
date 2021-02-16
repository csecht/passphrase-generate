"""
The standalone executables included in this distribution were created
using a version of this script.

USAGE: Place setup.py in the passphrase-generate-master folder and run it
from a Terminal.
MacOS command:
    python3 setup.py py2app
Windows command:
    python setup.py py2exe

For all systems, the wordlists folder and the passphrase.py file from the
passphrase-generate repository must be in the parent folder where this is executed.

You will also need to install one of these programs:
py2app installation: https://pypi.org/project/py2app/
py2exe installation: https://pypi.org/project/py2exe/

Additional information: https://pythonhosted.org/an_example_pypi_project/setuptools.html
"""

import os
from setuptools import setup  # comment out for Windows
# from distutils.core import setup # uncomment for Windows

DATA_FILES = []
for files in os.listdir('/Users/path/to/passphrase-generate-master/wordlists/'):
    f1 = './wordlists/' + files
    if os.path.isfile(f1):  # skip directories
        f2 = 'wordlists', [f1]
        DATA_FILES.append(f2)

setup(
    app=['passphrase.py'],  # comment out for Windows
    # windows=['passphrase.py,],  # uncomment for Windows
    data_files=DATA_FILES,
    name='Passphrase',
    version='0.5.11',
    author='C.S. Echt',
    description=('A utility to create random passphrases and passwords'),
    license='GNU General Public License',
    keywords='passphrase password',
    url='https://github.com/csecht/passphrase-generate',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: GNU License',
        'Programming Language :: Python :: 3.8'
    ],
    # options={'py2app':{}}
    # options={'py2exe:{'unbuffered': True, 'optimize': 2}}
)

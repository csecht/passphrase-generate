from pass_utils import platform_check, vcheck

"""
These constants are used with the --about command line argument or button.
Program will exit here if any check fails when called at startup.
"""

platform_check.check_platform()
vcheck.minversion('3.6')

# Development status standards: https://pypi.org/classifiers/

__author__ = 'Craig S. Echt'
__version__ = '0.12.0'
__dev_status__ = 'Development Status :: 4 - Beta'
__copyright__ = 'Copyright (C) 2021- 2022 C.S. Echt, under GNU General Public License'

URL = 'github.com/csecht/passphrase-generate'

LICENSE = """
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program (the LICENCE.txt file). If not, see
    https://www.gnu.org/licenses/."""
"""
Startup validation of current OS platform. Is called from pass_utils.__init__.
Functions: check_platform()
MY_OS constant used in main script.
"""
# 'Copyright (C) 2021- 2022 C.S. Echt, under GNU General Public License'

import sys

MY_OS = sys.platform[:3]


def check_platform():
    if MY_OS not in 'lin, win, dar':
        print(f'Platform <{sys.platform}> is not supported.\n'
              'Windows, Linux, and MacOS (darwin) are supported.')
        sys.exit(1)

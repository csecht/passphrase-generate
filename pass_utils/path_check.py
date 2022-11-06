"""
Startup path validation and path-related attributes as constants.
Is called from pass_utils.__init__.
Functions: valid_path_to()
WORDDIR and SYSDICT_PATH are called from main script.
"""
# 'Copyright (C) 2021- 2022 C.S. Echt, under GNU General Public License'

import sys
from pathlib import Path


def valid_path_to(relative_path: str) -> Path:
    """
    Get correct path to program's directory/file structure
    depending on whether program invocation is a standalone app or
    the command line. Works with symlinks.
    _MEIPASS var is used by distribution programs from
    PyInstaller --onefile; e.g. for images dir.

    :param relative_path: Program's local dir/file name, as string.
    :return: Absolute path as pathlib Path object.
    """
    # Modified from: https://stackoverflow.com/questions/7674790/
    #    bundling-data-files-with-pyinstaller-onefile and PyInstaller manual.
    if getattr(sys, 'frozen', False):  # hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', Path(Path(__file__).resolve()).parent)
        valid_path = Path(base_path) / relative_path
    else:
        valid_path = Path(Path(__file__).parent, f'../{relative_path}').resolve()
    return valid_path


# Note: The optional wordlist files are referenced in PassModeler().
WORDDIR = valid_path_to('wordlists')
# System dictionary path is needed only for Linux and macOS, not Windows.
SYSDICT_PATH = Path('/usr/share/dict/words').resolve()

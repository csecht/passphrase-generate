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
    Get absolute path to files and directories.
    _MEIPASS var is used by distribution programs from
    PyInstaller --onefile; e.g. for images dir.

    :param relative_path: File or dir name path, as string.
    :return: Absolute path as pathlib Path object.
    """
    # Modified from: https://stackoverflow.com/questions/7674790/
    #    bundling-data-files-with-pyinstaller-onefile and PyInstaller manual.
    if getattr(sys, 'frozen', False):  # hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', Path(Path(__file__).resolve()).parent)
        return Path(base_path) / relative_path
    return Path(relative_path).resolve()


# Note: The optional wordlist files are referenced in PassModeler().
WORDDIR = valid_path_to('wordlists')
# System dictionary path is needed only for Linux and macOS, not Windows.
SYSDICT_PATH = Path('/usr/share/dict/words').resolve()

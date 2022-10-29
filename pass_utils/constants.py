"""
Constants and variables used in main script, passphrase.

SYMBOLS - string of acceptable symbols
VERY_RANDOM - a random float
W - default width of the results display fields
STRING_DATA - dictionary of string module constants
LIST_DATA - dictionary of word lists, populated in main script
"""
# 'Copyright (C) 2021- 2022 C.S. Echt, under GNU General Public License'

import random
from string import digits, punctuation, ascii_letters, ascii_uppercase

SYMBOLS = "~!@#$%^&*_-+="
# SYMBOLS = "~!@#$%^&*()_-+={}[]<>?"

# Number of characters for evaluating passphrase lengths and
#   setting pass-string results Entry widget widths.
# Depends on changes in app window minsize and PassFonts.set_fonts.
W = 52

STUBRESULT = 'Result can be copied and pasted.'

COLORS = {
    'master_fg': 'grey90',  # Used for row headers.
    'master_bg': 'RoyalBlue4',  # Also used for some labels.
    'dataframe_bg': 'grey30',  # Also background for data labels.
    'stubpass_fg': 'grey60',  # For initial pass-string stub.
    'pass_fg': 'brown4',  # Pass-string font color.
    'long_fg': 'blue',  # Long pass-string font color.
    'pass_bg': 'khaki2',  # Background of pass-string results cells.
}

# VERY_RANDOM = random.Random(time.time())  # Use epoch timestamp seed.
# VERY_RANDOM = random.SystemRandom()   # Use current system's random.
VERY_RANDOM = random.Random(random.random())

# These dictionaries can be placed as PassViewer class attributes.
#   Can not be used as PassViewer instance attributes b/c they can't be
#   reset each time Viewer is called.
STRING_DATA = {
    'symbols': SYMBOLS,
    'digi': digits,
    'caps': ascii_uppercase,
    'all_char': ascii_letters + digits + punctuation,
    'some_char': ascii_letters + digits + SYMBOLS,
    'all_unused': ''
}

LIST_DATA = {'word_list': [], 'short_list': []}

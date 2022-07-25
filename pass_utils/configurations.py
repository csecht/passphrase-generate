"""
Constants and variables used in main script, passphrase.

SYMBOLS - string of acceptable symbols
very_random - a random float
W - default width of the results display fields
string_data - dictionary of string module constants
list_data - dictionary of word lists, populated in main script
"""
# 'Copyright (C) 2021- 2022 C.S. Echt, under GNU General Public License'

import random
from string import digits, punctuation, ascii_letters, ascii_uppercase

SYMBOLS = "~!@#$%^&*_-+="
# SYMBOLS = "~!@#$%^&*()_-+={}[]<>?"

# Number of characters for evaluating passphrase lengths and
#   setting widget widths.
W = 52

# very_random = random.Random(time.time())  # Use epoch timestamp seed.
# very_random = random.SystemRandom()   # Use current system's random.
very_random = random.Random(random.random())

# These dictionaries can be placed as PassViewer class attributes.
#   Can not be used as PassViewer instance attributes b/c they can't be
#   reset each time Viewer is called.
string_data = {
    'symbols': SYMBOLS,
    'digi': digits,
    'caps': ascii_uppercase,
    'all_char': ascii_letters + digits + punctuation,
    'some_char': ascii_letters + digits + SYMBOLS,
    'all_unused': ''
}

list_data = {'word_list': [], 'short_list': []}

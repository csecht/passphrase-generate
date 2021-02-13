#!/usr/bin/env python3

"""
A utility to create random passphrases and passwords.
Inspired by code from @codehub.py via Instagram.
     Copyright (C) 2021 C.S. Echt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see https://www.gnu.org/licenses/.
"""

__version__ = '0.5.3'

import glob
import random
import sys
from math import log
from pathlib import Path
from string import digits, punctuation, ascii_letters, ascii_uppercase

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import messagebox
except (ImportError, ModuleNotFoundError) as error:
    print('GUI requires tkinter, which is included with Python 3.7 and higher'
          '\nInstall 3.7+ or re-install Python and include Tk/Tcl.'
          f'\nSee also: https://tkdocs.com/tutorial/install.html \n{error}')

PROJ_URL = 'github.com/csecht/passphrase-generate'
# MY_OS = sys.platform[:3]
MY_OS = 'win'  # TESTING
SYMBOLS = "~!@#$%^&*()_-+="
# SYMBOLS = "~!@#$%^&*()_-+={}[]<>?"
SYSDICT_PATH = Path('/usr/share/dict/words')
WORDDIR = './wordlists/'
VERY_RANDOM = random.Random(random.random())
# VERY_RANDOM = random.Random(time.time())  # Use epoch timestamp seed.
# VERY_RANDOM = random.SystemRandom()   # Use current system's random.
W = 60  # Default width of the results display fields.


class PassGenerator:
    """
    A GUI to specify lengths of reported passphrases and passwords.
    """
    def __init__(self, master):
        """Window widgets and default some variables are set up here.
        """
        self.master = master

        # tkinter widgets used in config_window(), in general order of appearance:
        # EFF checkbutton is not used in Windows b/c only EFF words are used.
        # self.eff =          tk.BooleanVar()
        self.choice = tk.StringVar()
        self.choose_wordlist = ttk.Combobox(state='readonly')
        # https://www.tcl.tk/man/tcl/TkCmd/ttk_combobox.htm

        # Passphrase section ##################################################
        self.numwords_label = tk.Label()
        self.numwords_entry = tk.Entry()

        self.l_and_h_header = tk.Label()
        self.passphrase_header = tk.Label()

        self.result_frame1 = tk.Frame()

        self.any_describe =      tk.Label()
        self.any_lc_describe =   tk.Label()
        self.some_describe =   tk.Label()

        self.length_any =        tk.IntVar()
        self.length_lc =         tk.IntVar()
        self.length_some =       tk.IntVar()
        self.length_any_label =  tk.Label(self.result_frame1,
                                          textvariable=self.length_any)
        self.length_lc_label =   tk.Label(self.result_frame1,
                                          textvariable=self.length_lc)
        self.length_some_label = tk.Label(self.result_frame1,
                                          textvariable=self.length_some)
        self.h_any =             tk.IntVar()
        self.h_lc =              tk.IntVar()
        self.h_some =            tk.IntVar()
        self.h_any_label =       tk.Label(self.result_frame1,
                                          textvariable=self.h_any)
        self.h_lc_label =        tk.Label(self.result_frame1,
                                          textvariable=self.h_lc)
        self.h_some_label =      tk.Label(self.result_frame1,
                                          textvariable=self.h_some)

        self.phrase_any =        tk.StringVar()
        self.phrase_lc =         tk.StringVar()
        self.phrase_some =       tk.StringVar()
        # Results are displayed in Entry() instead of Text() b/c
        # textvariable is easier to code than .insert(). Otherwise, identical.
        self.phrase_any_display =  tk.Entry(self.result_frame1,
                                            textvariable=self.phrase_any)
        self.phrase_lc_display =   tk.Entry(self.result_frame1,
                                            textvariable=self.phrase_lc)
        self.phrase_some_display = tk.Entry(self.result_frame1,
                                            textvariable=self.phrase_some)
        # End passphrase section ##############################################

        self.generate_btn = ttk.Button()

        # Password section ####################################################
        self.pw_header =      tk.Label()

        # There are problems of tk.Button text showing up on MacOS, so ttk.
        self.numchars_label =   tk.Label()
        self.numchars_entry =   tk.Entry()

        self.result_frame2 =    tk.Frame()

        self.pw_any_describe =  tk.Label()
        self.pw_some_describe = tk.Label()

        self.length_pw_any =    tk.IntVar()
        self.length_pw_some =   tk.IntVar()
        self.length_pw_any_l =  tk.Label(self.result_frame2,
                                         textvariable=self.length_pw_any)
        self.length_pw_some_l = tk.Label(self.result_frame2,
                                         textvariable=self.length_pw_some)
        self.h_pw_any =         tk.IntVar()
        self.h_pw_some =        tk.IntVar()
        self.h_pw_any_l =       tk.Label(self.result_frame2,
                                         textvariable=self.h_pw_any)
        self.h_pw_some_l =      tk.Label(self.result_frame2,
                                         textvariable=self.h_pw_some)

        self.pw_any =           tk.StringVar()
        self.pw_some =          tk.StringVar()
        self.pw_any_display =   tk.Entry(self.result_frame2,
                                         textvariable=self.pw_any, )
        self.pw_some_display =  tk.Entry(self.result_frame2,
                                         textvariable=self.pw_some)
        # End password section ################################################

        self.exclude_describe =  tk.Label()
        self.exclude_entry =     tk.Entry()
        self.exclude_info_b =    ttk.Button()
        self.reset_button =      ttk.Button()
        self.excluded =          tk.StringVar()
        self.excluded_display =  tk.Label(textvariable=self.excluded)

        # First used in get_words():
        self.wordfile =    []
        self.allwords =    []
        self.word_list =   []
        self.trim_words =  []
        self.wordlists =   {}
        self.choice =      ''

        # First used in set_passstrings()
        self.symbols =   SYMBOLS
        self.digi =      digits
        self.caps =      ascii_uppercase
        self.all_char =  ascii_letters + digits + punctuation
        self.some_char = ascii_letters + digits + self.symbols
        self.prior_unused = ''
        self.somewords =    ''
        self.all_unused =   ''
        self.passphrase1 =  ''
        self.passphrase2 =  ''
        self.password1 =    ''
        self.password2 =    ''

        # Used only in explain()
        self.system_list = []

        # Configure and grid all widgets & check for needed files.
        self.display_font = ''  # also used in config_results().
        self.pass_fg = ''  # also used in config_results().
        self.config_window()
        self.grid_window()
        self.check_files()

    def config_window(self) -> None:
        """Configure all tkinter widgets.

        :return: Easy to understand window labels and data.
        """

        self.master.minsize(850, 420)
        self.master.maxsize(1230, 420)

        master_bg = 'SkyBlue4'    # also used for some labels.
        master_fg = 'LightCyan2'
        frame_bg = 'grey40'       # background for data labels and frame
        stubresult_fg = 'grey60'  # used only for initial window
        pass_bg = 'khaki2'
        self.pass_fg = 'brown4'   # also used in config_results()
        # Use Courier b/c TKFixedFont does not monospace symbol characters.
        self.display_font = 'Courier', 12  # also used in config_results().

        # Widget configurations are generally listed top to bottom of window.
        self.master.bind("<Escape>", lambda q: quit_gui())
        self.master.bind("<Control-q>", lambda q: quit_gui())
        self.master.bind("<Control-g>", lambda q: self.set_passstrings())
        self.master.config(bg=master_bg)

        # Create menu instance and add pull-down menus
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Generate", command=self.set_passstrings,
                         accelerator="Ctrl+G")
        file.add_command(label="Quit", command=quit_gui, accelerator="Ctrl+Q")

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="What's going on here?",
                              command=self.explain)
        help_menu.add_command(label="About", command=self.about)

        # Configure and set initial values of user entry and control widgets:
        self.wordlists = {
            'System dictionary': SYSDICT_PATH,
            'EFF long wordlist': WORDDIR + 'eff_large_wordlist.txt',
            'US Constitution'  : WORDDIR + 'usconst_wordlist.txt',
            'Don Quijote'      : WORDDIR + 'don_quijote_wordlist.txt',
            'Frankenstein'     : WORDDIR + 'frankenstein_wordlist.txt'
            }
        if MY_OS in 'lin, dar':
            self.choose_wordlist['values'] = tuple(self.wordlists.keys())
        if MY_OS == 'win':
            nosys = list(self.wordlists.keys())
            del nosys[0]
            self.choose_wordlist['values'] = nosys
            # ^^ Removal of 'System dictionary' also in config_nosyswords().
        # Need to default to the 1st wordlist
        self.choose_wordlist.current(0)
        self.choose_wordlist.bind('<<ComboboxSelected>>', self.get_words)

        # Passphrase section ##################################################
        # Statements generally grouped by row number.
        self.passphrase_header.config(text='Passphrases', font=('default', 12),
                                      fg=pass_bg, bg=master_bg)
        # MacOS needs a larger font
        if MY_OS == 'dar':
            self.passphrase_header.config(font=('default', 16))

        # This header spans two columns, but much easier to align with grid
        #  in the results frame if "pad" it across columns with spaces.
        self.l_and_h_header.config(text=' L       H', width=10,
                                   fg=master_fg, bg=master_bg)

        self.result_frame1.config(borderwidth=3, relief='sunken',
                                  background=frame_bg)

        self.numwords_label.config(text='# words', fg=pass_bg, bg=master_bg)
        self.numwords_entry.config(width=2)
        self.numwords_entry.insert(0, '5')

        stubresult = 'Result can be copied and pasted from keyboard.'

        self.any_describe.config(text="Any words from dictionary",
                                 fg=master_fg, bg=master_bg)
        self.length_any.set(0)
        self.length_any_label.config(width=3)
        self.h_any.set(0)
        self.h_any_label.config(width=3)
        self.phrase_any.set(stubresult)
        self.phrase_any_display.config(width=W, font=self.display_font,
                                       fg=stubresult_fg, bg=pass_bg)

        self.any_lc_describe.config(text="... plus 3 characters",
                                    fg=master_fg, bg=master_bg)
        self.length_lc.set(0)
        self.length_lc_label.config(width=3)
        self.h_lc.set(0)
        self.h_lc_label.config(width=3)
        self.phrase_lc.set(stubresult)
        self.phrase_lc_display.config(width=W, font=self.display_font,
                                      fg=stubresult_fg, bg=pass_bg)

        self.some_describe.config(text="...with words of 3 to 8 letters",
                                  fg=master_fg, bg=master_bg)
        self.length_some.set(0)
        self.length_some_label.config(width=3)
        self.h_some.set(0)
        self.h_some_label.config(width=3)
        self.phrase_some.set(stubresult)
        self.phrase_some_display.config(width=W, font=self.display_font,
                                        fg=stubresult_fg, bg=pass_bg)
        # End passphrase section ##############################################

        # Explicit styles are needed for buttons to show properly on MacOS.
        #  ... even then, background and pressed colors won't be recognized.
        style = ttk.Style()
        style.map("G.TButton",
                  foreground=[('active', self.pass_fg)],
                  background=[('pressed', frame_bg),
                              ('active', pass_bg)])
        self.generate_btn.configure(style="G.TButton", text='Generate!',
                                    command=self.set_passstrings)
        self.generate_btn.focus()

        self.result_frame2.config(borderwidth=3, relief='sunken',
                                  background=frame_bg)

        # Password section ####################################################
        # Statements generally grouped by row number.
        self.pw_header.config(text='Passwords', font=('default', 12),
                              fg=pass_bg, bg=master_bg)
        if MY_OS == 'dar':
            self.pw_header.config(font=('default', 16))

        self.numchars_label.config(text='# characters',
                                   fg=pass_bg, bg=master_bg)
        self.numchars_entry.config(width=3)
        self.numchars_entry.insert(0, 0)

        self.pw_any_describe.config(text="Any characters",
                                    fg=master_fg, bg=master_bg)
        self.length_pw_any.set(0)
        self.length_pw_any_l.config(width=3)
        self.h_pw_any.set(0)
        self.h_pw_any_l.config(width=3)
        self.pw_any.set(stubresult)
        self.pw_any_display.config(width=W, font=self.display_font,
                                   fg=stubresult_fg, bg=pass_bg)

        self.pw_some_describe.config(text="More likely usable characters",
                                     fg=master_fg, bg=master_bg)
        self.length_pw_some.set(0)
        self.length_pw_some_l.config(width=3)
        self.h_pw_some.set(0)
        self.h_pw_some_l.config(width=3)
        self.pw_some.set(stubresult)
        self.pw_some_display.config( width=W, font=self.display_font,
                                     fg=stubresult_fg, bg=pass_bg)

        # Excluded character section ##########################################
        self.exclude_describe.config(text='Exclude character(s)',
                                     fg=pass_bg, bg=master_bg)
        self.exclude_entry.config(width=3)
        self.reset_button.configure(style="G.TButton", text='Reset',
                                    width=0,
                                    command=self.reset_exclusions)
        self.excluded_display.config(fg='orange', bg=master_bg)
        self.exclude_info_b.configure(style="G.TButton", text="?",
                                      width=0,
                                      command=self.exclude_msg)

    def grid_window(self) -> None:
        """Grid all tkinter widgets.

        :return: A nice looking interactive window.
        """
        ############## sorted by row number #################
        # Passphrase widgets ##################################################
        self.choose_wordlist.grid(column=1, row=0, pady=(10, 5), padx=5,
                                  columnspan=2, sticky=tk.W)

        self.passphrase_header.grid( column=0, row=0, pady=(10, 5), padx=5,
                                     sticky=tk.W)
        self.l_and_h_header.grid(    column=1, row=1, padx=0, sticky=tk.W)

        self.numwords_label.grid(    column=0, row=1, padx=5, sticky=tk.W)
        self.numwords_entry.grid(    column=0, row=1, padx=(5, 100),
                                     sticky=tk.E)

        self.result_frame1.grid(     column=1, row=2, padx=(5, 10),
                                     columnspan=3, rowspan=3, sticky=tk.EW)

        # Result _displays will maintain equal widths with sticky=tk.EW.
        self.any_describe.grid(      column=0, row=2, pady=(5, 0), sticky=tk.E)
        self.length_any_label.grid(  column=1, row=2, pady=(5, 3), padx=(4, 0))
        self.h_any_label.grid(       column=2, row=2, pady=(5, 3), padx=(4, 0))
        self.phrase_any_display.grid(column=3, row=2, pady=(5, 3), padx=5,
                                     ipadx=5, sticky=tk.EW)
        self.any_lc_describe.grid(   column=0, row=3, pady=(0, 0), sticky=tk.E)
        self.length_lc_label.grid(   column=1, row=3, pady=(5, 3), padx=(4, 0))
        self.h_lc_label.grid(        column=2, row=3, pady=(5, 3), padx=(4, 0))
        self.phrase_lc_display.grid( column=3, row=3, pady=(5, 3), padx=5,
                                     ipadx=5, sticky=tk.EW)
        self.some_describe.grid(column=0, row=4, pady=(0, 3), sticky=tk.E)
        self.length_some_label.grid( column=1, row=4, pady=3, padx=(4, 0))
        self.h_some_label.grid(      column=2, row=4, pady=3, padx=(4, 0))
        self.phrase_some_display.grid(column=3, row=4, pady=6, padx=5, ipadx=5,
                                      sticky=tk.EW)

        # Need to pad and span to center the button between two results frames.
        self.generate_btn.grid(   column=3, row=5, pady=(10, 5), padx=(0, 250),
                                  rowspan=2, sticky=tk.W)
        if MY_OS == 'dar':
            self.generate_btn.grid(column=3, row=5, pady=(10, 5), padx=(0, 150),
                                   rowspan=2, sticky=tk.W)

        # Password widgets ####################################################
        self.pw_header.grid(       column=0, row=5, pady=(12, 6), padx=5,
                                   sticky=tk.W)
        self.numchars_label.grid(  column=0, row=6, padx=5, sticky=tk.W)
        self.numchars_entry.grid(  column=0, row=6, padx=(0, 65),
                                   sticky=tk.E)

        self.result_frame2.grid(   column=1, row=7, padx=(5, 10),
                                   columnspan=3, rowspan=2, sticky=tk.EW)

        self.pw_any_describe.grid( column=0, row=7, pady=(6, 0),
                                   sticky=tk.E)
        self.length_pw_any_l.grid( column=1, row=7, pady=(6, 3), padx=(4, 0))
        self.h_pw_any_l.grid(      column=2, row=7, pady=(6, 3), padx=(4, 0))
        self.pw_any_display.grid(  column=3, row=7, pady=(6, 3), padx=5,
                                   columnspan=2, ipadx=5, sticky=tk.EW)
        self.pw_some_describe.grid(column=0, row=8, pady=(0, 6), padx=(5, 0),
                                   sticky=tk.E)
        self.length_pw_some_l.grid(column=1, row=8, pady=3, padx=(4, 0))
        self.h_pw_some_l.grid(     column=2, row=8, pady=3, padx=(4, 0))
        self.pw_some_display.grid( column=3, row=8, pady=6, padx=5,
                                   columnspan=2, ipadx=5, sticky=tk.EW )

        # Excluded character widgets ##########################################
        self.exclude_describe.grid(column=0, row=9, pady=(20, 0), padx=5,
                                   sticky=tk.W)
        self.exclude_entry.grid(   column=0, row=9, pady=(20, 5), padx=(0, 10),
                                   sticky=tk.E)
        self.reset_button.grid(    column=1, row=9, pady=(20, 5), padx=(0, 0),
                                   sticky=tk.W)
        self.exclude_info_b.grid(  column=1, row=9, pady=(20, 5), padx=(70, 0),
                                   sticky=tk.W)
        if MY_OS == 'dar':
            self.exclude_info_b.grid(column=1, row=9, pady=(20, 5), padx=(78, 0),
                                     sticky=tk.W)

        self.excluded_display.grid( column=0, row=10, padx=5, sticky=tk.W)

    def check_files(self) -> object:
        """Confirm whether required files are present, exit if not.

        :return: quit_gui() or self.get_words()
        """
        fnf_msg = (
            '\nHmmm. Cannot locate system dictionary\n'
            ' words nor any custom wordlist files\n'
            ' (*_wordlist.txt). Wordlist files should be\n'
            ' in a folder called "wordfiles" included\n'
            ' with the repository downloaded from:\n'
            f'{PROJ_URL}\nWill exit program now...')

        wordfiles = glob.glob(WORDDIR + '*_wordlist.txt')
        # This covers OS with and w/o system dictionary.
        if Path.is_file(SYSDICT_PATH) is False:
            if len(wordfiles) == 0:
                print(fnf_msg)
                messagebox.showinfo(title='Files not found',
                                    detail=fnf_msg)
                return quit_gui()
            if len(wordfiles) > 0:
                return self.config_nosyswords()
        elif Path.is_file(SYSDICT_PATH) is True:
            if len(wordfiles) == 0:
                return self.config_no_options()

        # As long as necessary files are present, proceed...
        return self.get_words()

    def get_words(self, event = None) -> None:
        """
        Populate lists with words to randomize in set_passstrings().

        :param: event is a call from <<ComboboxSelected>>.

        :return: Word lists or pop-up msg if some files are missing.
        """

        # The *_wordlist.txt files were pre-compiled to have only unique words.
        # Use set() and split() here to generalize for any text file.
        self.choice = self.choose_wordlist.get()
        self.wordfile = self.wordlists[self.choice]
        self.allwords =  set(Path(self.wordfile).read_text(encoding='utf8').split())
        # Need to remove words having the possessive form ('s) b/c they
        #   duplicate many nouns in an English system dictionary.
        #   Also removes hyphenated words; EFF large wordlist has 4.
        self.word_list = [word for word in self.allwords if word.isalpha()]
        self.trim_words = [word for word in self.word_list if 8 >= len(word) >= 3]

    def set_passstrings(self) -> None:
        """Generate and set random pass-strings.
        Called from keybinding, menu, or button.

        :return: Calls to self.set_entropy() and self.config_results().
        """

        # Need to filter words and strings containing characters to be excluded.
        unused = self.exclude_entry.get().strip()

        if len(unused) > 0:
            self.word_list = [
                word for word in self.word_list if unused not in word]
            self.trim_words = [
                word for word in self.trim_words if unused not in word]
            self.symbols = [char for char in self.symbols if unused not in char]
            self.digi = [num for num in self.digi if unused not in num]
            self.caps = [letter for letter in self.caps if unused not in letter]
            self.all_char = [char for char in self.all_char if unused not in char]
            self.some_char = [char for char in self.some_char if unused not in char]

            self.prior_unused = unused
        # Need to reset lists if user removes prior excluded character(s).
        # These lists are initially defined with default values in get_words().
        #   Don't repopulate lists if they are unchanged between calls.
        elif len(unused) == 0 and self.prior_unused != unused:
            self.reset_exclusions()
            self.prior_unused = unused

        # Need to display all characters that have been excluded by user.
        if unused not in self.all_unused:
            self.all_unused = ' '.join([unused, self.all_unused])
        self.excluded.set(self.all_unused)

        # Need to correct invalid user entries for number of words & characters.
        numwords = str(self.numwords_entry.get()).strip()
        if numwords == '':
            self.numwords_entry.insert(0, '0')
        elif numwords.isdigit() is False:
            self.numwords_entry.delete(0, 'end')
            self.numwords_entry.insert(0, '0')
        numwords = int(self.numwords_entry.get())

        numchars = str(self.numchars_entry.get()).strip()
        if numchars == '':
            self.numchars_entry.insert(0, '0')
        if numchars.isdigit() is False:
            self.numchars_entry.delete(0, 'end')
            self.numchars_entry.insert(0, '0')
        numchars = int(self.numchars_entry.get())

        # Randomly select user-specified number of words.
        self.allwords = "".join(VERY_RANDOM.choice(self.word_list) for
                                _ in range(numwords))
        self.somewords = "".join(VERY_RANDOM.choice(self.trim_words) for
                                 _ in range(numwords))

        # Randomly select symbols to append; number is not user-specified.
        addsymbol = "".join(VERY_RANDOM.choice(self.symbols) for _ in range(1))
        addnum = "".join(VERY_RANDOM.choice(self.digi) for _ in range(1))
        addcaps = "".join(VERY_RANDOM.choice(self.caps) for _ in range(1))

        # Build the pass-strings.
        self.passphrase1 = self.allwords + addsymbol + addnum + addcaps
        self.passphrase2 = self.somewords + addsymbol + addnum + addcaps
        self.password1 = "".join(VERY_RANDOM.choice(self.all_char) for
                                 _ in range(numchars))
        self.password2 = "".join(VERY_RANDOM.choice(self.some_char) for
                                 _ in range(numchars))

        # Set all pass-strings for display in results frames.
        self.phrase_any.set(self.allwords)
        self.length_any.set(len(self.allwords))
        self.phrase_lc.set(self.passphrase1)
        self.length_lc.set(len(self.passphrase1))
        self.phrase_some.set(self.passphrase2)
        self.length_some.set(len(self.passphrase2))
        self.pw_any.set(self.password1)
        self.length_pw_any.set(len(self.password1))
        self.pw_some.set(self.password2)
        self.length_pw_some.set(len(self.password2))

        # Finally, set H values for each pass-string and configure results.
        self.set_entropy(numwords, numchars)
        self.config_results()

    def set_entropy(self, numwords: int, numchars: int) -> None:
        """Calculate and set values for information entropy, H.

        :param numwords: User-defined number of passphrase words.
        :param numchars: User-defined number of password characters.
        :return: self.config_results()
        """
        # https://en.wikipedia.org/wiki/Password_strength
        # For +3 characters, we use only 1 character each from each set of
        # symbols, numbers, caps, so only need P of selecting one element
        # from a set to obtain H, then sum all P.
        # https://en.wikipedia.org/wiki/Entropy_(information_theory)
        # Note that length of these string may reflect excluded characters.
        h_symbol =  -log(1 / len(self.symbols), 2)
        h_digit = -log(1/len(self.digi), 2)
        h_cap = -log(1/len(self.caps), 2)
        h_add3 = int(h_symbol + h_cap + h_digit)  # H ~= 11

        # Calculate information entropy, H = L * log N / log 2, where N is the
        #   number of possible characters or words and L is the number of characters
        #   or words in the pass-string. Log can be any base, but needs to be
        #   the same base in numerator and denominator.
        # Note that N is corrected for any excluded words from set_passstrings().
        # Note that the label names for 'h_any' and 'h_some' are recycled
        #   between system dict and eff wordlist options.
        self.h_any.set(int(numwords * log(len(self.word_list)) / log(2)))
        h_some = int(numwords * log(len(self.trim_words)) / log(2))
        self.h_some.set(h_some + h_add3)

        self.h_lc.set(self.h_any.get() + h_add3)
        self.h_pw_any.set(int(numchars * log(len(self.all_char)) / log(2)))
        self.h_pw_some.set(int(numchars * log(len(self.some_char)) / log(2)))

        # return self.config_results()

    def config_results(self) -> None:
        """
        Configure fonts and display widths in results frames.

        :return: A more readable display of results.
        """
        # Change font colors of results from the initial self.passstub_fg.
        # pass_fg does not change after first call to set_passstrings().
        self.phrase_any_display.config( fg=self.pass_fg)
        self.phrase_lc_display.config(  fg=self.pass_fg)
        self.phrase_some_display.config(fg=self.pass_fg)
        self.pw_any_display.config(     fg=self.pass_fg)
        self.pw_some_display.config(    fg=self.pass_fg)

        # Need to reduce font size of long pass-string length to keep
        #   window on screen, then reset to default font size when pass-string
        #   length is shortened.
        # Adjust width of results display widgets to THE longest result string.
        # B/c 'width' is character units, not pixels, length may change
        #   as font sizes and string lengths change.
        small_font = 'Courier', 10
        if len(self.passphrase1) > W:
            self.phrase_any_display.config( font=small_font,
                                            width=len(self.passphrase1))
            self.phrase_lc_display.config(  font=small_font)
            self.phrase_some_display.config(font=small_font)
        elif len(self.passphrase1) <= W:
            self.phrase_any_display.config( font=self.display_font, width=W)
            self.phrase_lc_display.config(  font=self.display_font, width=W)
            self.phrase_some_display.config(font=self.display_font, width=W)

        if len(self.password1) > W:
            self.pw_any_display.config(     font=small_font,
                                            width=len(self.password1))
            self.pw_some_display.config(    font=small_font,
                                            width=len(self.password2))
        elif len(self.password1) <= W:
            self.pw_any_display.config(     font=self.display_font, width=W)
            self.pw_some_display.config(    font=self.display_font, width=W)

    def config_nosyswords(self) -> None:
        """
        Warn if the Linux/MacOX system dictionary cannot be found.
        Warns by default on Windows.

        :return: A notice and updated Combobox.
        """
        notice = ('Hmmm. The system dictionary cannot be found.\n'
                  'Using only custom wordlists ...')
        # print(notice)
        messagebox.showinfo(title='File not found', detail=notice)
        nosys = list(self.wordlists.keys())
        del nosys[0]
        self.choose_wordlist['values'] = nosys
        self.choose_wordlist.current(0)
        return self.get_words()

    def config_no_options(self) -> None:
        """
        Warn that optional wordlists cannot be found.

        :return: A text window notice and an updated Combobox.
        """
        # This will not be called in the standalone app or executable.
        notice = ('Oops! Optional wordlists are missing.\n'
                  'Wordlist files should be in a folder\n'
                  ' called "wordfiles" included with'
                  ' the repository downloaded from:\n'
                  f'{PROJ_URL}\n'
                  'Using system dictionary words...\n')
        self.choose_wordlist.config(state='disabled')
        # print(notice)
        messagebox.showinfo(title='File not found', detail=notice)
        self.choose_wordlist['values'] = ('System dictionary',)
        self.choose_wordlist.current(0)
        return self.get_words()

    def explain(self) -> None:
        """Provide information about words used to create passphrases.

        :return: An text window notice with current wordlist data.
        """
        # B/c system dictionary is not accessible in Windows, need to redefine
        #   lists so that they sum to zero words.
        if MY_OS == 'win' or Path.is_file(SYSDICT_PATH) is False:
            self.system_list = self.word_list = self.trim_words = []

        # Formatting this is a pain.  There must be a better way.
        info = (
"""A passphrase is a random string of words that can be more secure and
easier to remember than a password of random characters. For more 
information on passphrases, see, for example, a discussion of word lists
and word selection at the Electronic Frontier Foundation (EFF):
https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases 

On MacOS and Linux systems, the system dictionary wordlist is used by 
default to provide words, though optional wordlists are available. 
Windows users can use only the optional wordlists.

"""
f'There are {len(self.word_list)} words available to construct passphrases'
f' from the\ncurrently selected wordlist, {self.choice}.\n'
"""
There is an option to exclude any character or string of characters 
from passphrase words and passwords. Words with excluded letters are not 
available nor counted above. You may need to click the Generate! button 
(or use Ctrl C) to update the non-excluded word count. Multiple windows 
can remain open to compare the counts and lists reported above.

Optional wordlists were derived from texts obtained from these sites:
    https://www.gutenberg.org
    https://www.archives.gov/founding-docs/constitution-transcript
    https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt
Although the EFF list contains 7776 selected words, only 7772 are used 
here because hyphenated word are excluded.

Words with less than 3 letters are not used in any wordlist.

To accommodate some password requirements, a choice is provided that 
adds three characters : 1 symbol, 1 number, and 1 upper case letter.
"""
f'The symbols used are: {self.symbols}\n'
"""
In the results fields, L is the character length of each pass-string.
H, as used here, is for comparing relative pass-string strengths.
Higher is better; each increase of 1 doubles the relative strength. 
H is actually the information entropy (Shannon entropy) value and is 
equivalent to bits of entropy. For more information see: 
    https://explainxkcd.com/wiki/index.php/936:_Password_Strength 
    https://en.wikipedia.org/wiki/Password_strength
    https://en.wikipedia.org/wiki/Entropy_(information_theory)
"""
)
        infowin = tk.Toplevel()
        infowin.title('A word about words and characters')
        num_lines = info.count('\n')
        infotext = tk.Text(infowin, width=75, height=num_lines + 1,
                           background='grey40', foreground='grey98',
                           relief='groove', borderwidth=8, padx=20, pady=10)
        infotext.insert('1.0', info)
        infotext.pack()

    def reset_exclusions(self) -> None:
        """Restore original word and character lists.

        :return: Wordlists and characters with no exclusions.
        """
        self.get_words()
        self.symbols =   SYMBOLS
        self.digi =      digits
        self.caps =      ascii_uppercase
        self.all_char =  ascii_letters + digits + punctuation
        self.some_char = ascii_letters + digits + SYMBOLS

        self.exclude_entry.delete(0, 'end')
        self.all_unused = ''
        self.excluded.set(self.all_unused)

    @staticmethod
    def exclude_msg() -> None:
        """A pop-up explaining how to use excluded characters.
        Called  from a Button.

        :return: A message text window.
        """
        msg = (
"""
The character(s) you enter will not appear in passphrase 
words or passwords. Multiple characters are treated as a 
unit. For example, "es" will exclude "trees", not "eye" 
and  "says". To exclude all three words, enter "e", then
Generate!, enter "s", then Generate!. 
The Reset button removes exclusions and restores original  
words, characters, numbers, and symbols.
"""
)
        exclwin = tk.Toplevel()
        exclwin.title('Exclude from what?')
        num_lines = msg.count('\n')
        infotext = tk.Text(exclwin, width=62, height=num_lines + 1,
                           background='grey40', foreground='grey98',
                           relief='groove', borderwidth=8, padx=20, pady=10)
        infotext.insert('1.0', msg)
        infotext.pack()

    @staticmethod
    def about() -> None:
        """Basic information about the script; called from GUI Help menu.

        :return: Information window.
        """
        # msg separators use em dashes.
        boilerplate = ("""
passphrase.py and its stand-alones generate passphrases and passwords.
Download the most recent version from:
""" 
f'{PROJ_URL}'
"""
————————————————————————————————————————————————————————————————————
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.\n
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.\n
You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/
————————————————————————————————————————————————————————————————————\n
                   Author:     cecht
                   Copyright:  Copyright (C) 2021 C.S. Echt
                   Development Status: 4 - Beta
                   Version:    """)  # __version__ is appended here.

        num_lines = boilerplate.count('\n')
        aboutwin = tk.Toplevel()
        aboutwin.title('About Passphrase')
        colour = ['SkyBlue4', 'DarkSeaGreen4', 'DarkGoldenrod4', 'DarkOrange4',
                  'grey40', 'blue4', 'navy', 'DeepSkyBlue4', 'dark slate grey',
                  'dark olive green', 'grey2', 'grey25', 'DodgerBlue4',
                  'DarkOrchid4']
        bkg = random.choice(colour)
        abouttxt = tk.Text(aboutwin, width=75, height=num_lines + 2,
                           background=bkg, foreground='grey98',
                           relief='groove', borderwidth=8, padx=5)
        abouttxt.insert('0.0', boilerplate + __version__)
        # Center text preceding the Author, etc. details.
        abouttxt.tag_add('text1', '0.0', float(num_lines - 3))
        abouttxt.tag_configure('text1', justify='center')
        abouttxt.pack()


def quit_gui() -> None:
    """Safe and informative exit from the program.
    """
    print('\n  *** User has quit the program. Exiting...\n')
    root.destroy()
    sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Passphrase Generator")
    PassGenerator(root)
    root.mainloop()

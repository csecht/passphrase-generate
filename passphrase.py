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

__version__ = '0.4.1'

import random
import sys
from math import log
from pathlib import Path
from string import digits, punctuation, ascii_letters, ascii_uppercase

try:
    import tkinter as tk
    from tkinter import messagebox
    import tkinter.ttk as ttk
except (ImportError, ModuleNotFoundError) as error:
    print('GUI requires tkinter, which is included with Python 3.7 and higher'
          '\nInstall 3.7+ or re-install Python and include Tk/Tcl.'
          f'\nSee also: https://tkdocs.com/tutorial/install.html \n{error}')

# PROGRAM_VER = '0.4.1'
PROJ_URL = 'https://github.com/csecht/passphrase-generate'
SYMBOLS = "~!@#$%^&*_-+=(){}[]<>?"
MY_OS = sys.platform[:3]
# MY_OS = 'win'  # TESTING
SYSWORDS_PATH = Path('/usr/share/dict/words')
EFFWORDS_PATH = Path('eff_large_wordlist.txt')

# Need to confirm that required files are present.
fnf_msg = ('\n*** Cannot locate either the system dictionary or EFF wordlist\n'
           'At a minimum, the file eff_large_wordlist.txt should be in '
           'the master directory.\nThat file can is included with:\n'
           f'{PROJ_URL}\n'
           'Exiting now...')
if MY_OS in 'lin, dar':
    if Path.is_file(SYSWORDS_PATH) is False:
        if Path.is_file(EFFWORDS_PATH) is False:
            print(fnf_msg)
            sys.exit(1)
elif MY_OS == 'win' and Path.is_file(EFFWORDS_PATH) is False:
    print(fnf_msg)
    sys.exit(1)


class Generator:
    """
    A GUI to specify lengths of reported passphrases and passwords.
    """
    def __init__(self, master):
        """Window layout and default values are set up here.
        """
        self.master = master
        self.master.bind("<Escape>", lambda q: quit_gui())
        self.master.bind("<Control-q>", lambda q: quit_gui())
        self.master.bind("<Control-g>", lambda q: self.make_pass())

        self.master_bg = 'SkyBlue4'  # also used for some labels.
        self.master_fg = 'LightCyan2'  # foreground for user entry labels
        self.frame_bg = 'grey40'  # background for data labels and frame
        self.frame_fg = 'grey90'
        self.stubresult_fg = 'grey60'
        self.pass_fg = 'brown4'
        self.pass_bg = 'khaki2'
        # Use courier b/c TKFixedFont does not monospace symbol characters.
        self.display_font = 'Courier', 12
        self.small_font = 'Courier', 10

        self.stubresult = 'Result can be copied and pasted from keyboard.'

        # Variables used in setup_window(), in general order of appearance:
        # EFF checkbutton is not used in Windows b/c EFF words are default.
        self.eff =          tk.BooleanVar()
        self.eff_checkbtn = tk.Checkbutton()

        self.numwords_label = tk.Label()
        self.numwords_entry = tk.Entry()
        self.numchars_label = tk.Label()
        self.numchars_entry = tk.Entry()
        self.exclude_label =  tk.Label()
        self.exclude_entry =  tk.Entry()

        # There are problems of tk.Button text showing up on MacOS, so ttk
        self.exclude_btn =  ttk.Button()
        self.generate_btn = ttk.Button()

        self.result_frame1 = tk.Frame()
        self.result_frame2 = tk.Frame()

        self.l_and_h_header =    tk.Label()
        self.passphrase_header = tk.Label()
        self.any_describe =      tk.Label()
        self.any_lc_describe =   tk.Label()
        self.select_describe =   tk.Label()
        self.length_any =        tk.IntVar()
        self.length_lc =         tk.IntVar()
        self.length_some =       tk.IntVar()
        self.length_pw_any =     tk.IntVar()
        self.length_pw_some =    tk.IntVar()
        self.h_any =             tk.IntVar()
        self.h_lc =              tk.IntVar()
        self.h_some =            tk.IntVar()
        self.h_pw_any =          tk.IntVar()
        self.h_pw_some =         tk.IntVar()
        self.length_any_label =  tk.Label(self.result_frame1)
        self.length_lc_label =   tk.Label(self.result_frame1)
        self.length_some_label = tk.Label(self.result_frame1)
        self.length_pw_any_l =   tk.Label(self.result_frame2)
        self.length_pw_some_l =  tk.Label(self.result_frame2)
        self.h_any_label =       tk.Label(self.result_frame1)
        self.h_lc_label =        tk.Label(self.result_frame1)
        self.h_some_label =      tk.Label(self.result_frame1)
        self.h_pw_any_l =        tk.Label(self.result_frame2)
        self.h_pw_some_l =       tk.Label(self.result_frame2)
        self.phrase_any =        tk.StringVar()
        self.phrase_lc =         tk.StringVar()
        self.phrase_some =       tk.StringVar()
        # Results are displayed in Entry() instead of Text() b/c
        # textvariable is easier to code than .insert(). Otherwise, identical.
        self.phrase_any_display = tk.Entry(self.result_frame1,
                                           textvariable=self.phrase_any)
        self.phrase_lc_display =  tk.Entry(self.result_frame1,
                                           textvariable=self.phrase_lc)
        self.phrase_some_display = tk.Entry(self.result_frame1,
                                            textvariable=self.phrase_some)
        self.pw_header =          tk.Label()
        self.pw_any_describe =    tk.Label()
        self.pw_some_describe =   tk.Label()

        self.pw_any =             tk.StringVar()
        self.pw_some =            tk.StringVar()
        self.pw_any_display =     tk.Entry(self.result_frame2,
                                           textvariable=self.pw_any, )
        self.pw_some_display =    tk.Entry(self.result_frame2,
                                           textvariable=self.pw_some)
        # First used in get_words():
        self.use_effwords = True
        self.system_words = 'Null'
        self.eff_wordlist = 'None'
        self.eff_list = ['None']
        self.system_list = ['None']

        # First used in make_pass()
        self.uniq_words = []
        self.trim_words = []
        self.eff_words = []
        self.caps = []
        self.string1 = []
        self.string2 = []
        self.numwords = 0
        self.numchars = 0

        # Used in set_entropy()
        self.h_symbol = 0.0
        self.h_cap = 0.0
        self.h_digit = 0.0
        self.h_add3 = 0

        # Now put the widgets in the main window.
        self.setup_window()

    def setup_window(self) -> None:
        """
        Layout the main window and assign starting values to labels.

        :return: A nice looking interactive graphic.
        """
        if MY_OS == 'win':
            self.master.minsize(850, 360)
            self.master.maxsize(1230, 360)
        elif MY_OS in 'lin, dar':
            self.master.minsize(850, 390)
            self.master.maxsize(1230, 390)

        # Widget configurations are generally listed as top to bottom of window.
        self.master.config(bg=self.master_bg)

        self.result_frame1.config(borderwidth=3, relief='sunken',
                                  background=self.frame_bg)
        self.result_frame2.config(borderwidth=3, relief='sunken',
                                  background=self.frame_bg)

        # Create menu instance and add pull-down menus
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Generate", command=self.make_pass,
                         accelerator="Ctrl+G")
        file.add_command(label="Quit", command=quit_gui, accelerator="Ctrl+Q")

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="What's going on here?",
                              command=self.explain)
        help_menu.add_command(label="About", command=about)

        # Configure and set initial values of user entry and control widgets:
        if MY_OS in 'lin, dar':
            self.eff_checkbtn.config(text='Use EFF word list ',
                                     variable=self.eff,
                                     fg=self.master_fg, bg=self.master_bg,
                                     activebackground='grey80',
                                     selectcolor=self.frame_bg)
        if self.use_effwords is False:
            self.eff_checkbtn.config(state='disabled')

        self.passphrase_header.config(text='Passphrases', font=('default', 12),
                                      fg=self.pass_bg, bg=self.master_bg)
        if MY_OS == 'dar':
            self.passphrase_header.config(font=('default', 16))

        # This header spans two columns, but much easier to align with grid
        #  in the results frame if "pad" it across columns with spaces.
        self.l_and_h_header.config(text=' L       H', width=10,
                                   fg=self.master_fg, bg=self.master_bg)

        # Passphrase results section:
        # Set up OS-specific widgets.
        if MY_OS in 'lin, dar':
            self.any_describe.config(   text="Any words from dictionary",
                                        fg=self.master_fg, bg=self.master_bg)
            self.any_lc_describe.config(text="...+3 characters & lower case",
                                        fg=self.master_fg, bg=self.master_bg)
            self.select_describe.config(text="...with words of 3 to 8 letters",
                                        fg=self.master_fg, bg=self.master_bg)
            self.length_some.set(0)
            self.length_some_label.config(textvariable=self.length_some,
                                          width=3)
            self.h_some.set(0)
            self.h_some_label.config(     textvariable=self.h_some,
                                          width=4)
            self.phrase_some.set(self.stubresult)
            self.phrase_some_display.config(width=60, font=self.display_font,
                                            fg=self.stubresult_fg,
                                            bg=self.pass_bg)
        elif MY_OS == 'win':
            self.any_describe.config(   text="Any words from EFF wordlist",
                                        fg=self.master_fg, bg=self.master_bg)
            self.any_lc_describe.config(text="...add 3 characters",
                                        fg=self.master_fg, bg=self.master_bg)
            self.select_describe.config(text=" ",
                                        fg=self.master_fg, bg=self.master_bg)

        # Passphrase widgets used by all OS.
        self.numwords_label.config(text='# words',
                                   fg=self.pass_bg, bg=self.master_bg)
        self.numwords_entry.config(width=2)
        self.numwords_entry.insert(0, '5')

        self.length_any.set(0)
        self.length_lc.set(0)
        self.length_pw_any.set(0)
        self.length_pw_some.set(0)
        self.length_any_label.config(textvariable=self.length_any, width=3)
        self.length_lc_label.config( textvariable=self.length_lc, width=3)
        self.length_pw_any_l.config( textvariable=self.length_pw_any, width=3)
        self.length_pw_some_l.config(textvariable=self.length_pw_some, width=3)
        self.h_any.set(0)
        self.h_lc.set(0)
        self.h_pw_any.set(0)
        self.h_pw_some.set(0)
        self.h_any_label.config(textvariable=self.h_any, width=4)
        self.h_lc_label.config( textvariable=self.h_lc, width=4)
        self.h_pw_any_l.config( textvariable=self.h_pw_any, width=4)
        self.h_pw_some_l.config(textvariable=self.h_pw_some, width=4)
        self.phrase_any.set(self.stubresult)
        self.phrase_lc.set(self.stubresult)
        self.phrase_any_display.config(width=60, font=self.display_font,
                                       fg=self.stubresult_fg, bg=self.pass_bg)
        self.phrase_lc_display.config( width=60, font=self.display_font,
                                       fg=self.stubresult_fg, bg=self.pass_bg)

        # Explicit styles are needed for buttons to show properly on MacOS.
        #  ... even then, background and pressed colors won't be recognized.
        style = ttk.Style()
        style.map("G.TButton",
                  foreground=[('active', self.pass_fg)],
                  background=[('pressed', self.frame_bg),
                              ('active', self.pass_bg)])
        self.generate_btn.configure(style="G.TButton", text='Generate!',
                                    command=self.make_pass)
        self.generate_btn.focus()
        self.exclude_btn.configure(style="G.TButton", text="?", width=0,
                                   command=exclude_msg)

        # Password results section:
        self.pw_header.config(         text='Passwords', font=('default', 12),
                                       fg=self.pass_bg, bg=self.master_bg)
        if MY_OS == 'dar':
            self.pw_header.config(font=('default', 16))

        self.numchars_label.config(    text='# characters',
                                       fg=self.pass_bg, bg=self.master_bg)
        self.numchars_entry.config(    width=3)
        self.numchars_entry.insert(0, 0)

        self.pw_any_describe.config(   text="Any characters",
                                       fg=self.master_fg, bg=self.master_bg)
        self.pw_some_describe.config(  text="More likely usable characters",
                                       fg=self.master_fg, bg=self.master_bg)
        self.pw_any.set(self.stubresult)
        self.pw_some.set(self.stubresult)
        self.pw_any_display.config(   width=60, font=self.display_font,
                                      fg=self.stubresult_fg, bg=self.pass_bg)
        self.pw_some_display.config(  width=60, font=self.display_font,
                                      fg=self.stubresult_fg, bg=self.pass_bg)

        self.exclude_label.config(    text='Exclude character(s)',
                                      fg=self.pass_bg, bg=self.master_bg)
        self.exclude_entry.config(    width=3)

        #### GRID all widgets: ############# sorted by row number #############
        # Passphrase widgets grid:
        self.eff_checkbtn.grid(      column=1, row=0, pady=(10, 5), padx=5,
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
        self.select_describe.grid(   column=0, row=4, pady=(0, 3), sticky=tk.E)
        self.length_some_label.grid( column=1, row=4, pady=3, padx=(4, 0))
        self.h_some_label.grid(      column=2, row=4, pady=3, padx=(4, 0))
        self.phrase_some_display.grid(column=3, row=4, pady=6, padx=5, ipadx=5,
                                      sticky=tk.EW)
        # Don't show system dictionary or EFF-specific widgets on Windows.
        # Need to adjust padding to keep row headers aligned with results b/c
        #  of deletion of those widgets. (?)
        if MY_OS == 'win':
            self.eff_checkbtn.grid_forget()
            self.any_describe.grid(column=0, row=2, pady=(6, 0), sticky=tk.E)
            self.select_describe.grid_forget()
            self.length_some_label.grid_forget()
            self.h_some_label.grid_forget()
            self.phrase_some_display.grid_forget()

        # Need to pad and span to center the button between two results frames.
        self.generate_btn.grid(      column=3, row=5, pady=(10, 5),
                                     padx=(0, 200), sticky=tk.W,
                                     rowspan=2)

        # Password widgets grid:
        self.pw_header.grid(         column=0, row=5, pady=(12, 6), padx=5,
                                     sticky=tk.W)
        self.numchars_label.grid(    column=0, row=6, padx=5, sticky=tk.W)
        self.numchars_entry.grid(    column=0, row=6, padx=(0, 65),
                                     sticky=tk.E)

        self.result_frame2.grid(     column=1, row=7, padx=(5, 10),
                                     columnspan=3, rowspan=2, sticky=tk.EW)

        self.pw_any_describe.grid(   column=0, row=7, pady=(6, 0),
                                     sticky=tk.E)
        self.length_pw_any_l.grid(   column=1, row=7, pady=(6, 3), padx=(4, 0))
        self.h_pw_any_l.grid(        column=2, row=7, pady=(6, 3), padx=(4, 0))
        self.pw_any_display.grid(    column=3, row=7, pady=(6, 3), padx=5,
                                     columnspan=2, ipadx=5, sticky=tk.EW)
        self.pw_some_describe.grid(  column=0, row=8, pady=(0, 6), padx=(5, 0),
                                     sticky=tk.E)
        self.length_pw_some_l.grid(  column=1, row=8, pady=3, padx=(4, 0))
        self.h_pw_some_l.grid(       column=2, row=8, pady=3, padx=(4, 0))
        self.pw_some_display.grid(   column=3, row=8, pady=6, padx=5,
                                     columnspan=2, ipadx=5, sticky=tk.EW)

        self.exclude_label.grid(     column=0, row=9, pady=(20, 5), padx=5,
                                     sticky=tk.W)
        self.exclude_entry.grid(     column=0, row=9, pady=(20, 5), padx=(0, 10),
                                     sticky=tk.E)
        self.exclude_btn.grid(       column=1, row=9, pady=(20, 5), padx=5,
                                     sticky=tk.W)

    def get_words(self) -> None:
        """
        Populate lists with words to randomize in make_pass().
        """
        if MY_OS == 'win':
            self.eff_wordlist = Path(EFFWORDS_PATH).read_text()

        if MY_OS in 'lin, dar':
            if Path.is_file(SYSWORDS_PATH):
                self.system_words = Path(SYSWORDS_PATH).read_text()
            elif Path.is_file(SYSWORDS_PATH) is False:
                notice = ('*** NOTICE: The system dictionary cannot be found.\n'
                          'Using EFF word list ... ***')
                self.system_words = 'Null'
                self.eff_checkbtn.config(state='disabled')
                print(notice)
                messagebox.showinfo(title='File not found',
                                    detail=notice)
            if Path.is_file(EFFWORDS_PATH):
                self.eff_wordlist = Path(EFFWORDS_PATH).read_text()
            elif Path.is_file(EFFWORDS_PATH) is False:
                self.use_effwords = False  # Used in window_setup().
                notice = (
                    '*** EFF large wordlist cannot be found.\n'
                    'That file is included with:\n'
                    f'{PROJ_URL}\n'
                    'Using system dictionary... ***\n'
                )
                self.eff_checkbtn.config(state='disabled')
                print(notice)
                messagebox.showinfo(title='File not found',
                                    detail=notice)
            self.system_list = self.system_words.split()

        self.eff_list = self.eff_wordlist.split()

    def make_pass(self) -> None:
        """Provide pass-string results each time Generate! is evoked.
        """
        # Need different passphrase descriptions for sys dict and EEF list.
        # Initial label texts are for sys. dict. and are set in
        # window_setup(), but are modified here if EFF option is used.
        # OS label descriptors are written each time "Generate" command is run.
        if MY_OS in 'lin, dar':
            if self.eff.get() is False:
                self.any_describe.config(   text="Any words from dictionary",
                                            fg=self.master_fg, bg=self.master_bg)
                self.any_lc_describe.config(text="...+3 characters & lower case",
                                            fg=self.master_fg, bg=self.master_bg)
                self.select_describe.config(text="...with words of 3 to 8 letters",
                                            fg=self.master_fg, bg=self.master_bg)
            elif self.eff.get() is True:
                self.any_describe.config(   text="Any words from EFF wordlist",
                                            fg=self.master_fg, bg=self.master_bg)
                self.any_lc_describe.config(text="...+3 characters",
                                            fg=self.master_fg, bg=self.master_bg)
                self.select_describe.config(text=" ",
                                            fg=self.master_fg, bg=self.master_bg)
                self.length_some.set(' ')
                self.phrase_some.set(' ')

        # Need to correct invalid user entries.
        if self.numwords_entry.get() == '':
            self.numwords_entry.insert(0, '0')
        elif self.numwords_entry.get().isdigit() is False:
            self.numwords_entry.delete(0, 'end')
            self.numwords_entry.insert(0, '0')

        if self.numchars_entry.get() == '':
            self.numchars_entry.insert(0, '0')
        elif self.numchars_entry.get().isdigit() is False:
            self.numchars_entry.delete(0, 'end')
            self.numchars_entry.insert(0, '0')

        # Need to remove words having the possessive form ('s, English).
        # Remove hyphenated words (4) from EFF wordlist (are not alpha).
        self.uniq_words = [word for word in self.system_list if word.isalpha()]
        self.trim_words = [word for word in self.uniq_words if 8 >= len(word) >= 3]
        self.eff_words = [word for word in self.eff_list if word.isalpha()]

        self.caps = ascii_uppercase
        self.string1 = ascii_letters + digits + punctuation
        self.string2 = ascii_letters + digits + SYMBOLS

        # Filter out words and strings containing characters to be excluded.
        unused = str(self.exclude_entry.get().strip(' '))
        if len(unused) != 0:
            self.uniq_words = [word for word in self.uniq_words if unused not in word]
            self.trim_words = [word for word in self.trim_words if unused not in word]
            self.eff_words = [word for word in self.eff_words if unused not in word]
            self.caps = [letter for letter in self.caps if unused not in letter]
            self.string1 = [char for char in self.string1 if unused not in char]
            self.string2 = [char for char in self.string2 if unused not in char]

        # very_random = random.Random(time.time())  # Use epoch timestamp seed.
        # very_random = random.SystemRandom()   # Use current system's random.
        very_random = random.Random(random.random())
        self.numwords = int(self.numwords_entry.get().strip(' '))
        self.numchars = int(self.numchars_entry.get().strip(' '))

        # Select user-specified number of words.
        allwords = "".join(very_random.choice(self.uniq_words) for
                           _ in range(self.numwords))
        somewords = "".join(very_random.choice(self.trim_words) for
                            _ in range(self.numwords))
        effwords = "".join(very_random.choice(self.eff_words) for
                           _ in range(self.numwords))

        # Select symbols to append, as a convenience; is not user-specified.
        addsymbol = "".join(very_random.choice(SYMBOLS) for _ in range(1))
        addcaps = "".join(very_random.choice(self.caps) for _ in range(1))
        addnum = "".join(very_random.choice(digits) for _ in range(1))

        # 1st condition evaluates eff checkbutton on, 2nd if no sys dict found.
        #   3rd, if EFF is only choice in Linux/Mac, disable eff checkbutton.
        #   There is probably a clearer way to work these conditions.
        if MY_OS in 'lin, dar' and self.eff.get() is True:
            allwords = effwords
            somewords = effwords
        elif MY_OS == 'win' or self.system_words == 'Null':
            allwords = effwords
            somewords = effwords
            if MY_OS in 'lin, dar':
                self.eff_checkbtn.config(state='disabled')

        # Build the pass-strings.
        passphrase1 = allwords.lower() + addsymbol + addnum + addcaps
        passphrase2 = somewords.lower() + addsymbol + addnum + addcaps
        password1 = "".join(very_random.choice(self.string1) for
                            _ in range(self.numchars))
        password2 = "".join(very_random.choice(self.string2) for
                            _ in range(self.numchars))

        # Need to reduce font size of long pass-string length to keep
        # window on screen, then reset to default font size when pass-string
        # length is shortened. On MacOS, fonts can be too small.
        # Adjust width of results entry widgets to THE longest result string.
        # B/c 'width' is character units, not pixels, length is not perfect
        #   fit when font sizes change.
        if len(passphrase1) > 60:
            self.phrase_any_display.config(font=self.small_font,
                                           width=len(passphrase1))
            self.phrase_lc_display.config(font=self.small_font)
            self.phrase_some_display.config(font=self.small_font)
        elif len(passphrase1) <= 60:
            self.phrase_any_display.config(font=self.display_font,
                                           width=len(passphrase1))
            self.phrase_lc_display.config(font=self.display_font)
            self.phrase_some_display.config(font=self.display_font)

        if len(password1) > 60:
            self.pw_any_display.config(font=self.small_font,
                                       width=len(password1))
            self.pw_some_display.config(font=self.small_font,
                                        width=len(password2))
        elif len(password1) <= 60:
            self.pw_any_display.config(font=self.display_font, width=60)
            self.pw_some_display.config(font=self.display_font, width=60)

        # Set all pass-strings for display.
        #   No need to set sys dictionary vars or provide eff checkbutton
        #     condition for Windows b/c no system dictionary is available.
        if MY_OS in 'lin, dar':
            if self.eff.get() is False:
                self.phrase_some.set(passphrase2)
                self.length_some.set(len(passphrase2))
            elif self.eff.get() is True:
                self.phrase_some.set(' ')
                self.length_some.set(' ')

        elif MY_OS == 'win':
            self.phrase_some.set(' ')
            self.length_some.set(' ')

        # Set statements common to all OS eff conditions:
        self.phrase_any.set(allwords)
        self.phrase_lc.set(passphrase1)
        self.length_any.set(len(allwords))
        self.length_lc.set(len(passphrase1))
        self.length_pw_any.set(len(password1))
        self.length_pw_some.set(len(password2))
        self.pw_any.set(password1)
        self.pw_some.set(password2)

        # Change font colors of results from the initial self.passstub_fg.
        self.phrase_any_display.config(fg=self.pass_fg)
        self.phrase_lc_display.config(fg=self.pass_fg)
        self.phrase_some_display.config(fg=self.pass_fg)
        self.pw_any_display.config(fg=self.pass_fg)
        self.pw_some_display.config(fg=self.pass_fg)

        # Finally, fill in H values for each pass-string.
        self.set_entropy(unused, self.string1, self.string2)

    def set_entropy(self, excl_char: str, all_char: list, some_char: list) -> None:
        """Calculate and set values for information entropy, H.

        :param excl_char: The user-defined character(s) to be excluded.
        :param all_char: All usable password characters, from import string.
        :param some_char: all_char but with customized SYMBOLS.
        """
        # https://en.wikipedia.org/wiki/Password_strength
        # We use only 1 character each from each set of symbols, numbers, caps.
        #  so only need P for selecting one from a set to calc H.
        # https://en.wikipedia.org/wiki/Entropy_(information_theory)
        self.h_symbol =  -log(1/len(SYMBOLS), 2)
        self.h_cap = -log(1/len(self.caps), 2)
        self.h_digit = -log(1/len(digits), 2)
        self.h_add3 = int(self.h_symbol + self.h_cap + self.h_digit)  # H ~= 12

        # Need to correct H for excluded characters in passwords (lower the N).
        # This accurately corrects H only when 1 char is excluded.
        # There are too many combinations of multi-char strings to easily code.
        # -1 is good approx. b/c of v. low P of existence of multi-char strings,
        #   so 1 is the maximum likely reduction of N. (true?)
        # Cannot use string1 and string2 from make_pass() b/c those lists
        #  are shortened by the excluded character.
        #  We need full sets of possible characters for N here.
        if len(excl_char) != 0:
            if excl_char in SYMBOLS:
                self.h_symbol = -log(1 / (len(SYMBOLS) - 1), 2)
            if excl_char in self.caps:
                self.h_cap = -log(1 / (len(self.caps) - 1), 2)
            if excl_char in digits:
                self.h_digit = -log(1 / (len(digits) - 1), 2)
            self.h_add3 = int(self.h_symbol + self.h_cap + self.h_digit)
            if excl_char in all_char:
                self.h_pw_any.set(
                    int(self.numchars * log(len(all_char) - 1) / log(2)))
            if excl_char in some_char:
                self.h_pw_some.set(
                    int(self.numchars * log(len(some_char) - 1) / log(2)))

        # Calculate information entropy, H = L * log N / log 2, where N is the
        # number of possible characters or words and L is the number of characters
        # or words in the pass-string. Log can be any base, but needs to be the
        # same in numerator and denominator.
        self.h_any.set(int(self.numwords * log(len(self.uniq_words)) / log(2)))
        self.h_lc.set(self.h_any.get() + self.h_add3)
        h_some = int(self.numwords * log(len(self.trim_words)) / log(2))
        self.h_some.set(h_some + self.h_add3)
        self.h_pw_any.set(int(self.numchars * log(len(self.string1)) / log(2)))
        self.h_pw_some.set(int(self.numchars * log(len(self.string2)) / log(2)))

        # Note that N is already corrected for excluded words from make_pass().
        # Note that the label names for 'any' and 'lc' are recycled between
        #  system dict and eff wordlist options; in retrospect, not smart.
        if MY_OS in 'lin, dar' and self.eff.get() is True:
            self.h_any.set(
                int(self.numwords * log(len(self.eff_words)) / log(2)))
            self.h_lc.set(self.h_any.get() + self.h_add3)
            self.h_some.set(' ')
        elif MY_OS == 'win' or self.system_words == 'Null':
            self.h_any.set(
                int(self.numwords * log(len(self.eff_words)) / log(2)))
            self.h_lc.set(self.h_any.get() + self.h_add3)
            self.h_some.set(' ')

    def explain(self) -> None:
        """Provide information about words used to create passphrases.
        """
        # These variables are only valid for Linux and MacOS system dictionary.
        word_num = self.system_words.split()
        unique = [word for word in self.system_list if word.isalpha()]
        trimmed = [word for word in unique if 8 >= len(word) >= 3]

        # Need to redefine lists for the Windows system dictionary b/c it is
        # not accessible. The initial value of self.system_words from __init__
        # is 'None', which gives a list length of 1 when the length should be
        # 0; but can't set the __init__ value to null, [], b/c errors arise.
        if MY_OS == 'win':
            word_num = unique = trimmed = []

        # Formatting this is a pain.  There must be a better way.
        info = (
"""A passphrase is a random string of words that can be more secure and
easier to remember than a shorter or complicated password.
For more information on passphrases, see, for example, a discussion of
word lists and selection at the Electronic Frontier Foundation (EFF):
https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases 

While MacOS and Linux users have an option to use an EFF wordlist, by 
default the system dictionary is used. Windows users, however, by default
can use only the EFF wordlist. Your system dictionary provides:
"""
f"    {len(word_num)} words of any length, of which...\n"
f"    {len(unique)} are unique (no possessive forms of nouns) and... \n"
f"    {len(trimmed)} of unique words that have 3 to 8 letters."
"""
Only the unique and length-limited word subsets are used for passphrases
if the EFF word list option is not selected. Passphrases built from the
system dictionary may include proper names and diacritics.

Proper names or diacritics are not in EFF large word list used here,
https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt. Its words 
(English) are generally shorter and easier to remember than those from a
system dictionary. Although the EFF list contains 7776 selected words,
only 7772 are used here because hyphenated word are excluded.

To accommodate password policies of some web sites and applications, a 
choice is provided that adds three characters : 1 symbol, 1 number, 
and 1 upper case letter. Symbols used are restricted to these: """
f'\n{SYMBOLS}\n'
"""
There is an option to exclude any character or string of characters
from your passphrase words and passwords (together called pass-strings).

In the results boxes, L is the character length of each pass-string.
H, as used here, is for comparing relative pass-string strengths. Higher
is better; each increase of 1 doubles the relative strength. H is 
actually the information entropy (Shannon entropy) value and is 
equivalent to bits of entropy. For more information see: 
https://explainxkcd.com/wiki/index.php/936:_Password_Strength 
https://en.wikipedia.org/wiki/Password_strength
https://en.wikipedia.org/wiki/Entropy_(information_theory)
"""
)

        infowin = tk.Toplevel()
        infowin.title('A word about words and characters')
        num_lines = info.count('\n')
        infotxt = tk.Text(infowin, width=75, height=num_lines + 1,
                          background='dark slate grey', foreground='grey94',
                          relief='groove', borderwidth=10, padx=20, pady=10)
        infotxt.insert('1.0', info)
        infotxt.pack()


def exclude_msg() -> None:
    """A pop-up explaining how to use excluded characters.
    """
    msg = 'The character(s) you enter...'
    detail = ('will not appear in passphrase words, nor appear in '
              'passwords. Multiple characters are treated as a '
              'unit. For example, "es" will exclude "trees", not "eye" '
              'and "says". Only these symbols are used in "+3 characters"'
              f' and "More likely usable" passwords: {SYMBOLS}'
              " (all other symbols and punctuation are excluded).")
    messagebox.showinfo(title='Excluded from what?', message=msg, detail=detail)


def about() -> None:
    """
    Basic information for the script; called from GUI Help menu.

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
            Copyright:  Copyright (C) 2021 C. Echt
            Development Status: 4 - Beta
            Version:    """)  # The version number is appended here.

    num_lines = boilerplate.count('\n')
    aboutwin = tk.Toplevel()
    aboutwin.title('About Passphrase')
    colour = ['SkyBlue4', 'DarkSeaGreen4', 'DarkGoldenrod4', 'DarkOrange4',
              'grey40', 'blue4', 'navy', 'DeepSkyBlue4', 'dark slate grey',
              'dark olive green', 'grey2', 'grey25', 'DodgerBlue4',
              'DarkOrchid4']
    bkg = random.choice(colour)
    abouttxt = tk.Text(aboutwin, width=72, height=num_lines + 2,
                       background=bkg, foreground='grey98',
                       relief='groove', borderwidth=5, padx=5)
    abouttxt.insert('1.0', boilerplate + __version__)
    # Center text preceding the Author, etc. details.
    abouttxt.tag_add('text1', '1.0', float(num_lines - 5))
    abouttxt.tag_configure('text1', justify='center')
    abouttxt.pack()


def quit_gui() -> None:
    """Safe and informative exit from the program.
    """
    print('\n  *** User has quit the program. Exiting...\n')
    root.destroy()
    sys.exit(0)


if __name__ == "__main__":
    # os.chdir(os.path.dirname(os.path.realpath(__file__)))
    root = tk.Tk()
    root.title("Passphrase Generator")
    Generator(root).get_words()
    root.mainloop()

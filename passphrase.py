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

__version__ = '0.4.11'

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

PROJ_URL = 'https://github.com/csecht/passphrase-generate'
MY_OS = sys.platform[:3]
# MY_OS = 'win'  # TESTING
SYMBOLS = "~!@#$%^&*()_-+="
# SYMBOLS = "~!@#$%^&*()_-+={}[]<>?"
SYSWORDS_PATH = Path('/usr/share/dict/words')
EFFWORDS_PATH = Path('eff_large_wordlist.txt')
VERY_RANDOM = random.Random(random.random())
# VERY_RANDOM = random.Random(time.time())  # Use epoch timestamp seed.
# VERY_RANDOM = random.SystemRandom()   # Use current system's random.


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
        self.eff =          tk.BooleanVar()
        self.eff_checkbtn = tk.Checkbutton()

        self.numwords_label = tk.Label()
        self.numwords_entry = tk.Entry()
        self.numchars_label = tk.Label()
        self.numchars_entry = tk.Entry()

        # There are problems of tk.Button text showing up on MacOS, so ttk.
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
        self.length_any_label =  tk.Label(self.result_frame1,
                                          textvariable=self.length_any)
        self.length_lc_label =   tk.Label(self.result_frame1,
                                          textvariable=self.length_lc)
        self.length_some_label = tk.Label(self.result_frame1,
                                          textvariable=self.length_some)
        self.length_pw_any_l =   tk.Label(self.result_frame2,
                                          textvariable=self.length_pw_any)
        self.length_pw_some_l =  tk.Label(self.result_frame2,
                                          textvariable=self.length_pw_some)
        self.h_any_label =       tk.Label(self.result_frame1,
                                          textvariable=self.h_any)
        self.h_lc_label =        tk.Label(self.result_frame1,
                                          textvariable=self.h_lc)
        self.h_some_label =      tk.Label(self.result_frame1,
                                          textvariable=self.h_some)
        self.h_pw_any_l =        tk.Label(self.result_frame2,
                                          textvariable=self.h_pw_any)
        self.h_pw_some_l =       tk.Label(self.result_frame2,
                                          textvariable=self.h_pw_some)
        self.phrase_any =        tk.StringVar()
        self.phrase_lc =         tk.StringVar()
        self.phrase_some =       tk.StringVar()
        # Results are displayed in Entry() instead of Text() b/c
        # textvariable is easier to code than .insert(). Otherwise, identical.
        self.phrase_any_display = tk.Entry( self.result_frame1,
                                            textvariable=self.phrase_any)
        self.phrase_lc_display =  tk.Entry( self.result_frame1,
                                            textvariable=self.phrase_lc)
        self.phrase_some_display = tk.Entry(self.result_frame1,
                                            textvariable=self.phrase_some)
        self.pw_header =          tk.Label()
        self.pw_any_describe =    tk.Label()
        self.pw_some_describe =   tk.Label()

        self.pw_any =             tk.StringVar()
        self.pw_some =            tk.StringVar()
        self.pw_any_display =     tk.Entry( self.result_frame2,
                                            textvariable=self.pw_any, )
        self.pw_some_display =    tk.Entry( self.result_frame2,
                                            textvariable=self.pw_some)

        self.exclude_describe =  tk.Label()
        self.exclude_entry =     tk.Entry()
        self.exclude_info_b =    ttk.Button()
        self.reset_button =      ttk.Button()
        self.excluded =          tk.StringVar()
        self.excluded_display =  tk.Label(textvariable=self.excluded)

        # First used in get_words():
        self.eff_list =     []
        self.system_list =  []
        self.passphrase1 =  ''
        self.passphrase2 =  ''
        self.password1 =    ''
        self.password2 =    ''
        self.symbols =   SYMBOLS
        self.digi =      digits
        self.caps =      ascii_uppercase
        self.all_char =  ascii_letters + digits + punctuation
        self.some_char = ascii_letters + digits + self.symbols

        # First used in set_passstrings()
        self.uniq_words =   []
        self.trim_words =   []
        self.eff_words =    []
        self.allwords =     ''
        self.somewords =    ''
        self.effwords =     ''
        self.prior_unused = ''
        self.all_unused = ''


        # Now configure widgets for the main window.
        self.display_font = ''  # also used in config_results().
        self.pass_fg = ''  # also used in config_results().
        self.config_window()

    def config_window(self) -> None:
        """Configure all tkinter widgets.

        :return: Easy to understand window labels and data.
        """
        if MY_OS == 'win':
            self.master.minsize(850, 390)
            self.master.maxsize(1230, 390)
        elif MY_OS in 'lin, dar':
            self.master.minsize(850, 420)
            self.master.maxsize(1230, 420)

        master_bg = 'SkyBlue4'  # also used for some labels.
        master_fg = 'LightCyan2'
        frame_bg = 'grey40'  # background for data labels and frame
        stubresult_fg = 'grey60'  # used only for initial window
        pass_bg = 'khaki2'
        self.pass_fg = 'brown4'  # also used in config_results()
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
        stubresult = 'Result can be copied and pasted from keyboard.'

        if MY_OS in 'lin, dar':
            self.eff_checkbtn.config(text='Use EFF word list ',
                                     variable=self.eff,
                                     fg=master_fg, bg=master_bg,
                                     activebackground='grey80',
                                     selectcolor=frame_bg)

        self.passphrase_header.config(text='Passphrases', font=('default', 12),
                                      fg=pass_bg, bg=master_bg)
        if MY_OS == 'dar':
            self.passphrase_header.config(font=('default', 16))

        # This header spans two columns, but much easier to align with grid
        #  in the results frame if "pad" it across columns with spaces.
        self.l_and_h_header.config(text=' L       H', width=10,
                                   fg=master_fg, bg=master_bg)

        self.result_frame1.config(borderwidth=3, relief='sunken',
                                  background=frame_bg)
        self.result_frame2.config(borderwidth=3, relief='sunken',
                                  background=frame_bg)

        # Passphrase results section ##########################
        # Set up OS-specific widgets.
        if MY_OS in 'lin, dar':
            self.any_describe.config(   text="Any words from dictionary",
                                        fg=master_fg, bg=master_bg)
            self.any_lc_describe.config(text="... +3 characters & lower case",
                                        fg=master_fg, bg=master_bg)
            self.select_describe.config(text="...with words of 3 to 8 letters",
                                        fg=master_fg, bg=master_bg)
            self.length_some.set(0)
            self.length_some_label.config(width=3)
            self.h_some.set(0)
            self.h_some_label.config(     width=4)
            self.phrase_some.set(stubresult)
            self.phrase_some_display.config(width=60, font=self.display_font,
                                            fg=stubresult_fg, bg=pass_bg)
        elif MY_OS == 'win':
            self.any_describe.config(   text="Any words from EFF wordlist",
                                        fg=master_fg, bg=master_bg)
            self.any_lc_describe.config(text="...add 3 characters",
                                        fg=master_fg, bg=master_bg)
            self.select_describe.config(text=" ",
                                        fg=master_fg, bg=master_bg)

        # Passphrase widgets used by all OS.
        self.numwords_label.config(text='# words',
                                   fg=pass_bg, bg=master_bg)
        self.numwords_entry.config(width=2)
        self.numwords_entry.insert(0, '5')

        self.length_any.set(0)
        self.length_lc.set(0)
        self.length_pw_any.set(0)
        self.length_pw_some.set(0)
        self.length_any_label.config(width=3)
        self.length_lc_label.config( width=3)
        self.length_pw_any_l.config( width=3)
        self.length_pw_some_l.config(width=3)
        self.h_any.set(0)
        self.h_lc.set(0)
        self.h_pw_any.set(0)
        self.h_pw_some.set(0)
        self.h_any_label.config(width=4)
        self.h_lc_label.config( width=4)
        self.h_pw_any_l.config( width=4)
        self.h_pw_some_l.config(width=4)
        self.phrase_any.set(stubresult)
        self.phrase_lc.set(stubresult)
        self.phrase_any_display.config(width=60, font=self.display_font,
                                       fg=stubresult_fg, bg=pass_bg)
        self.phrase_lc_display.config( width=60, font=self.display_font,
                                       fg=stubresult_fg, bg=pass_bg)

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

        # Password results section ##########################
        self.pw_header.config(       text='Passwords', font=('default', 12),
                                     fg=pass_bg, bg=master_bg)
        if MY_OS == 'dar':
            self.pw_header.config(font=('default', 16))

        self.numchars_label.config(  text='# characters',
                                     fg=pass_bg, bg=master_bg)
        self.numchars_entry.config(  width=3)
        self.numchars_entry.insert(0, 0)

        self.pw_any_describe.config( text="Any characters",
                                     fg=master_fg, bg=master_bg)
        self.pw_some_describe.config(text="More likely usable characters",
                                     fg=master_fg, bg=master_bg)
        self.pw_any.set(stubresult)
        self.pw_some.set(stubresult)
        self.pw_any_display.config(  width=60, font=self.display_font,
                                     fg=stubresult_fg, bg=pass_bg)
        self.pw_some_display.config( width=60, font=self.display_font,
                                     fg=stubresult_fg, bg=pass_bg)

        self.exclude_describe.config(text='Exclude character(s)',
                                     fg=pass_bg, bg=master_bg)
        self.exclude_entry.config(   width=3)

        self.reset_button.configure(    style="G.TButton", text='Reset',
                                        width=6,
                                        command=self.reset_exclusions)
        if MY_OS == 'dar':
            self.reset_button.configure(style="G.TButton", text='Reset',
                                        width=4,
                                        command=self.reset_exclusions)

        self.exclude_info_b.configure(  style="G.TButton", text="?", width=0,
                                        command=self.exclude_msg)
        self.excluded_display.config(fg='orange', bg=master_bg)
        #####################################################

        self.grid_window()

    def grid_window(self) -> None:
        """Grid all tkinter widgets.

        :return: A nice looking interactive window.
        """
        ############## sorted by row number #################
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
        self.generate_btn.grid(   column=3, row=5, pady=(10, 5), padx=(0, 250),
                                  rowspan=2, sticky=tk.W)
        if MY_OS == 'dar':
            self.generate_btn.grid(column=3, row=5, pady=(10, 5), padx=(0, 150),
                                   rowspan=2, sticky=tk.W)

        # Password widgets grid:
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
                                   columnspan=2, ipadx=5, sticky=tk.EW)

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

        self. excluded_display.grid( column=0, row=10, padx=5, sticky=tk.W)

    def check_files(self) -> None:
        """Confirm whether required files are present, exit if not.

        :return: A graceful exit or pass through.
        """
        fnf_msg = (
            f'\nHmmm. Cannot locate the system dictionary or {EFFWORDS_PATH} '
            f'\n'
            f'At a minimum, the file {EFFWORDS_PATH} should be in '
            'the master directory.\nThat file is in the repository:\n'
            f'{PROJ_URL}\n...Will exit program now...')
        if MY_OS in 'lin, dar':
            if Path.is_file(SYSWORDS_PATH) is False:
                if Path.is_file(EFFWORDS_PATH) is False:
                    print(fnf_msg)
                    messagebox.showinfo(title='Files not found',
                                        detail=fnf_msg)
                    quit_gui()
        elif MY_OS == 'win' and Path.is_file(EFFWORDS_PATH) is False:
            print(fnf_msg)
            messagebox.showinfo(title='Files not found', detail=fnf_msg)
            quit_gui()

        # As long as necessary files are present, proceed...
        self.get_words()

    def get_words(self) -> None:
        """
        Populate lists with words to randomize in set_passstrings().

        :return: Large word lists; pop-up msg if some files are missing.
        """

        # If pass the check, then at least one file exists, so proceed to
        #   populate word list(s).
        if MY_OS == 'win':
            self.eff_list = Path(EFFWORDS_PATH).read_text().split()
            self.eff_words = [word for word in self.eff_list if word.isalpha()]
        if MY_OS in 'lin, dar':
            if Path.is_file(SYSWORDS_PATH):
                self.system_list = Path(SYSWORDS_PATH).read_text().split()
            elif Path.is_file(SYSWORDS_PATH) is False:
                self.config_nosyswords()

            if Path.is_file(EFFWORDS_PATH):
                self.eff_list = Path(EFFWORDS_PATH).read_text().split()
                self.eff_words = [word for word in self.eff_list if
                                  word.isalpha()]
            elif Path.is_file(EFFWORDS_PATH) is False:
                self.config_noeffwords()

            # Need to remove words having the possessive form ('s, English)
            # Remove hyphenated words (4) from EFF wordlist (are not alpha).
            self.uniq_words = [word for word in self.system_list if word.isalpha()]
            self.trim_words = [word for word in self.uniq_words if 8 >= len(word) >= 3]

    def set_passstrings(self) -> None:
        """Generate and set pass-strings.
        Called from keybind, menu, or button.

        :return: Random pass-strings of specified length.
        """
        # Need different passphrase descriptions for sys dict and EEF list
        # to be re-configured here b/c EFF option may be used between calls.
        if MY_OS in 'lin, dar':
            if self.eff.get() is False:
                self.any_describe.config(   text="Any words from dictionary")
                self.any_lc_describe.config(text="... +3 characters & lower case")
                self.select_describe.config(text="...with words of 3 to 8 letters")
            elif self.eff.get() is True:
                self.any_describe.config(   text="Any words from EFF wordlist")
                self.any_lc_describe.config(text="... +3 characters")
                self.select_describe.config(text=" ")
                self.length_some.set(' ')
                self.phrase_some.set(' ')

        # Need to filter words and strings containing characters to be excluded.
        unused = self.exclude_entry.get().strip()

        if len(unused) > 0:
            if MY_OS in 'lin, dar' and self.system_list:
                self.uniq_words = [
                    word for word in self.uniq_words if unused not in word]
                self.trim_words = [
                    word for word in self.trim_words if unused not in word]
            # Remaining statements apply to all OS.
            self.eff_words = [
                word for word in self.eff_words if unused not in word]
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
        if self.numwords_entry.get() == '':
            self.numwords_entry.insert(0, '0')
        elif self.numwords_entry.get().isdigit() is False:
            self.numwords_entry.delete(0, 'end')
            self.numwords_entry.insert(0, '0')
        numwords = int(self.numwords_entry.get().strip())

        if self.numchars_entry.get() == '':
            self.numchars_entry.insert(0, '0')
        elif self.numchars_entry.get().isdigit() is False:
            self.numchars_entry.delete(0, 'end')
            self.numchars_entry.insert(0, '0')
        numchars = int(self.numchars_entry.get().strip())

        # Randomly select user-specified number of words.
        if MY_OS in 'lin, dar' and self.system_list:
            self.allwords = "".join(VERY_RANDOM.choice(self.uniq_words) for
                                    _ in range(numwords))
            self.somewords = "".join(VERY_RANDOM.choice(self.trim_words) for
                                     _ in range(numwords))
        # Windows only uses EFF file, Linux/MacOS uses it as an option.
        if Path.is_file(EFFWORDS_PATH):
            self.effwords = "".join(VERY_RANDOM.choice(self.eff_words) for
                                    _ in range(numwords))

        # 1st condition evaluates whether eff checkbutton state is on,
        # 2nd if no sys dict found,
        # 3rd if only EFF found in Linux/Mac, then disable eff checkbutton.
        if MY_OS in 'lin, dar' and self.eff.get() is True:
            self.allwords = self.effwords
            self.somewords = self.effwords
        elif MY_OS == 'win' or not self.system_list:
            self.allwords = self.effwords
            self.somewords = self.effwords
            if MY_OS in 'lin, dar':
                self.eff_checkbtn.config(state='disabled')

        # Randomly select symbols to append; number is not user-specified.
        addsymbol = "".join(VERY_RANDOM.choice(self.symbols) for _ in range(1))
        addnum = "".join(VERY_RANDOM.choice(self.digi) for _ in range(1))
        addcaps = "".join(VERY_RANDOM.choice(self.caps) for _ in range(1))

        # Build the pass-strings.
        self.passphrase1 = self.allwords.lower() + addsymbol + addnum + addcaps
        self.passphrase2 = self.somewords.lower() + addsymbol + addnum + addcaps
        self.password1 = "".join(VERY_RANDOM.choice(self.all_char) for
                                 _ in range(numchars))
        self.password2 = "".join(VERY_RANDOM.choice(self.some_char) for
                                 _ in range(numchars))

        # Set all pass-strings for display in results frames.
        # Set OS-independent and eff-independent StringVar():
        self.phrase_any.set(self.allwords)
        self.phrase_lc.set(self.passphrase1)
        self.length_any.set(len(self.allwords))
        self.length_lc.set(len(self.passphrase1))
        self.length_pw_any.set(len(self.password1))
        self.length_pw_some.set(len(self.password2))
        self.pw_any.set(self.password1)
        self.pw_some.set(self.password2)
        # Set OS-specific and eff-dependent StringVar()
        if MY_OS in 'lin, dar':
            if self.eff.get() is False:
                self.phrase_some.set(self.passphrase2)
                self.length_some.set(len(self.passphrase2))
            elif self.eff.get() is True:
                self.phrase_some.set(' ')
                self.length_some.set(' ')
        #  ^^No need to set sys dictionary vars or evaluate eff checkbutton
        #    state for Windows b/c no system dictionary is available.

        # Finally, set H values for each pass-string.
        self.set_entropy(numwords, numchars)

    def set_entropy(self, numwords: int, numchars: int) -> None:
        """Calculate and set values for information entropy, H.

        :param numwords: User-defined number of passphrase words.
        :param numchars: User-defined number of password characters.
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
        # These are complicated conditions, but it works concisely.
        if MY_OS in 'lin, dar' and self.system_list:
            self.h_any.set(int(numwords * log(len(self.uniq_words)) / log(2)))
            h_some = int(numwords * log(len(self.trim_words)) / log(2))
            self.h_some.set(h_some + h_add3)
            if self.eff.get() is True:
                self.h_any.set(
                    int(numwords * log(len(self.eff_words)) / log(2)))
                self.h_some.set(' ')
        elif MY_OS == 'win' or not self.system_list:
            self.h_any.set(
                int(numwords * log(len(self.eff_words)) / log(2)))

        # Calculate H used for all OS.
        self.h_lc.set(self.h_any.get() + h_add3)
        self.h_pw_any.set(int(numchars * log(len(self.all_char)) / log(2)))
        self.h_pw_some.set(int(numchars * log(len(self.some_char)) / log(2)))

        self.config_results()

    def config_results(self) -> None:
        """
        Configure fonts and display widths in results frames.

        :return: A more readable display of results.
        """
        # Change font colors of results from the initial self.passstub_fg.
        # pass_fg does not change after first call to set_passstrings().
        #   So, make it conditional with a counter in set_passstrings()
        #   or is it okay to .config() on every call?
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
        if len(self.passphrase1) > 60:
            self.phrase_any_display.config( font=small_font,
                                            width=len(self.passphrase1))
            self.phrase_lc_display.config(  font=small_font)
            self.phrase_some_display.config(font=small_font)
        elif len(self.passphrase1) <= 60:
            self.phrase_any_display.config( font=self.display_font, width=60)
            self.phrase_lc_display.config(  font=self.display_font, width=60)
            self.phrase_some_display.config(font=self.display_font, width=60)

        if len(self.password1) > 60:
            self.pw_any_display.config(     font=small_font,
                                            width=len(self.password1))
            self.pw_some_display.config(    font=small_font,
                                            width=len(self.password2))
        elif len(self.password1) <= 60:
            self.pw_any_display.config(     font=self.display_font, width=60)
            self.pw_some_display.config(    font=self.display_font, width=60)

    def config_nosyswords(self) -> None:
        """
        Warn that the Linux/MacOX system dictionary cannot be found.
        Call from get_words().

        :return: Pop-up message.
        """
        notice = ('Hmmm. The system dictionary cannot be found.\n'
                  f'Using only {EFFWORDS_PATH} ...')
        self.eff_checkbtn.toggle()
        self.eff_checkbtn.config(state='disabled')
        print(notice)
        messagebox.showinfo(title='File not found', detail=notice)
        # Remove widgets specific to EFF results; as if Windows.
        # Statements are duplicated from config_window() & grid_window().
        self.any_describe.config(text="Any words from EFF wordlist")
        self.any_lc_describe.config(text="...add 3 characters")
        self.select_describe.config(text=" ")
        self.any_describe.grid(column=0, row=2, pady=(6, 0), sticky=tk.E)
        self.select_describe.grid_forget()
        self.length_some_label.grid_forget()
        self.h_some_label.grid_forget()
        self.phrase_some_display.grid_forget()

    def config_noeffwords(self) -> None:
        """
        Warn that EFF wordlist cannot be found. Call from get_words().

        :return: Pop-up message.
        """
        # This will not be called in the standalone app or executable.
        notice = (f'Oops! {EFFWORDS_PATH} is missing.\n'
                  'It should be in master directory and is'
                  f' included with the repository\n'
                  'Using system dictionary...\n')
        self.eff_checkbtn.config(state='disabled')
        print(notice)
        messagebox.showinfo(title='File not found', detail=notice)

    def explain(self) -> None:
        """Provide information about words used to create passphrases.
        """
        # B/c system dictionary is not accessible in Windows, need to redefine
        #   lists so that they sum to zero words.
        if MY_OS == 'win':
            self.system_list = self.uniq_words = self.trim_words = []

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
f"    {len(self.system_list)} words of any length, of which...\n"
f"    {len(self.uniq_words)} are unique (no possessive forms of nouns) and... \n"
f"    {len(self.trim_words)} of unique words that have 3 to 8 letters."
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
f'\n{self.symbols}\n'
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
        infotext = tk.Text(infowin, width=75, height=num_lines + 1,
                           background='dark slate grey', foreground='grey94',
                           relief='groove', borderwidth=10, padx=20, pady=10)
        infotext.insert('1.0', info)
        infotext.pack()

    def reset_exclusions(self) -> None:
        """Restore original word and character lists.

        :return: Words and characters without exclusions.
        """
        if MY_OS == 'win':
            self.eff_words = [
                word for word in self.eff_list if word.isalpha()]
        elif MY_OS in 'lin, dar':
            self.eff_words = [
                word for word in self.eff_list if word.isalpha()]
            self.uniq_words = [
                word for word in self.system_list if word.isalpha()]
            self.trim_words = [
                word for word in self.uniq_words if 8 >= len(word) >= 3]
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
        """A pop-up explaining how to use excluded characters. Called
        from a Button.
        """
        msg = (
"""
The character(s) you enter will not appear in passphrase 
words or passwords. Multiple characters are treated as a 
unit. For example, "es" will exclude "trees", not "eye" 
and  "says". To exclude all three words, enter "e", then
Generate!, enter "s", then Generate!. 
The Reset button removes exclusions and restores all  
words, characters, numbers, and symbols.
"""
)
        exclwin = tk.Toplevel()
        exclwin.title('Exclude from what?')
        num_lines = msg.count('\n')
        infotext = tk.Text(exclwin, width=62, height=num_lines + 1,
                           background='dark slate grey', foreground='grey94',
                           relief='groove', borderwidth=10, padx=20, pady=10)
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
                           relief='groove', borderwidth=5, padx=5)
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
    PassGenerator(root).check_files()
    root.mainloop()

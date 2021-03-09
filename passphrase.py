#!/usr/bin/env python3

"""
A passphrase and password generator using MVC architecture, which is
structured in three main classes of Model, View, and Controller; based
on posts by Brian Oakley;  https://stackoverflow.com/questions/32864610/

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

__version__ = '0.7.8'

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
    from tkinter.scrolledtext import ScrolledText
except (ImportError, ModuleNotFoundError) as error:
    print('GUI requires tkinter, which is included with Python 3.7 and higher'
          '\nInstall 3.7+ or re-install Python and include Tk/Tcl.'
          f'\nSee also: https://tkdocs.com/tutorial/install.html \n{error}')

PROJ_URL = 'github.com/csecht/passphrase-generate'
MY_OS = sys.platform[:3]
# MY_OS = 'win'  # TESTING
SYMBOLS = "~!@#$%^&*_-+="
# SYMBOLS = "~!@#$%^&*()_-+={}[]<>?"
SYSDICT_PATH = Path('/usr/share/dict/words')
WORDDIR = './wordlists/'
# Note: The optional wordlist files are referenced in PassModeler().
VERY_RANDOM = random.Random(random.random())
# VERY_RANDOM = random.Random(time.time())  # Use epoch timestamp seed.
# VERY_RANDOM = random.SystemRandom()   # Use current system's random.
W = 65  # Default width of the results display fields.


# Functions independent of, but used by, passphrase MVC %%%%%%%%%%%%%%%%%%%%%%%
def quit_gui() -> None:
    """Safe and informative exit from the program.
    """
    print('\n  *** User has quit the program. Exiting...\n')
    app.destroy()
    sys.exit(0)


class RightClickEdit:
    """
    Right-click pop-up option to edit selected text; call as a Button-2
    or Button-3 binding in Text or window that needs the function.
    """
    # Based on: https://stackoverflow.com/questions/57701023/
    def __init__(self, event):
        right_click_menu = tk.Menu(None, tearoff=0, takefocus=0)
        right_click_menu.add_command(
            label='Copy', command=lambda: self.right_click_command(event, 'Copy'))
        right_click_menu.add_command(
            label='Paste', command=lambda: self.right_click_command(event, 'Paste'))
        right_click_menu.add_command(
            label='Cut', command=lambda: self.right_click_command(event, 'Cut'))

        right_click_menu.tk_popup(event.x_root + 10, event.y_root + 15)

    @staticmethod
    def right_click_command(event, cmd):
        event.widget.event_generate(f'<<{cmd}>>')
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# Main MVC Classes. %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class PassModeler:
    """The modeler crunches input from Viewer, then sends results back, via
    shared 'share' objects that are handled through the Controller class.
    """
    # Need Class variables here so they aren't reset in __init__ each time
    #   make_pass() is called.
    strdata = {
        'symbols'     : SYMBOLS,
        'digi'        : digits,
        'caps'        : ascii_uppercase,
        'all_char'    : ascii_letters + digits + punctuation,
        'some_char'   : ascii_letters + digits + SYMBOLS,
        'all_unused'  : '',
        'prior_unused': ''}

    listdata = {'word_list': [], 'short_list': []}

    def __init__(self, share):
        self.share = share

        self.share.word_files = {
            'System dictionary'      : SYSDICT_PATH,
            'EFF long wordlist'      : WORDDIR + 'eff_large_wordlist.txt',
            'US Constitution'        : WORDDIR + 'usconst_wordlist.txt',
            'Don Quijote'            : WORDDIR + 'don_quijote_wordlist.txt',
            'Frankenstein'           : WORDDIR + 'frankenstein_wordlist.txt',
            '此開卷第 Story of the Stone': WORDDIR + 'red_chamber_wordlist.txt'}

    def check_files(self) -> None:
        """
        Confirm whether required files are present, exit if not.
        Update wordlist options based on availability.
        """

        all_lists = list(self.share.word_files.keys())
        if MY_OS in 'lin, dar':
            self.share.choose_wordlist['values'] = all_lists
        # Need to remove 'System dictionary' from Windows usage.
        elif MY_OS == 'win':
            all_lists.remove('System dictionary')
            self.share.choose_wordlist['values'] = all_lists

        fnf_msg = ('\nHmmm. Cannot locate system dictionary\n'
                   'words nor any custom wordlist files\n'
                   '(*_wordlist.txt). Wordlist files should be\n'
                   'in a folder called "wordlists" included\n'
                   'with the repository downloaded from:\n'
                   f'{PROJ_URL}\nWill exit program now...')

        wordfile_list = glob.glob(WORDDIR + '*_wordlist.txt')
        # This covers platforms with and w/o system dictionary.
        if Path.is_file(SYSDICT_PATH) is False:
            if len(wordfile_list) == 0:
                print(fnf_msg)
                messagebox.showinfo(title='Files not found', detail=fnf_msg)
                quit_gui()

            if len(wordfile_list) > 0 and MY_OS != 'win':
                notice = ('Hmmm. The system dictionary cannot be found.\n'
                          'Using only custom wordlists ...')
                # print(notice)
                messagebox.showinfo(title='File not found', detail=notice)
                # Need to remove 'System dictionary' as an option.
                all_lists = list(self.share.word_files.keys())
                all_lists.remove('System dictionary')
                self.share.choose_wordlist['values'] = all_lists

        elif Path.is_file(SYSDICT_PATH) is True and len(wordfile_list) == 0:
            notice = ('Oops! Optional wordlists are missing.\n'
                      'Wordlist files should be in a folder\n'
                      'called "wordlists" included with\n'
                      'the repository downloaded from:\n'
                      f'{PROJ_URL}\n'
                      'Using system dictionary words...\n')
            self.share.choose_wordlist.config(state='disabled')
            # print(notice)
            messagebox.showinfo(title='File not found', detail=notice)
            self.share.choose_wordlist['values'] = ('System dictionary',)

        # Default in combobox is the 1st available wordlist.
        self.share.choose_wordlist.current(0)

    def get_words(self, *args) -> None:
        """
        Populate lists with words to randomize in make_pass(); needs to
        run at start and each time a new wordlist is selected by user.

        :param args: a virtual event call from choose_wordlist Combobox.
        """

        # Need to remove displayed excluded characters when a new wordlist
        #  is selected because no characters are excluded from a new list.
        self.share.exclude_entry.delete(0, 'end')
        self.share.tkdata['excluded'].set('')

        # The *_wordlist.txt files have only unique words, but...
        #   use set() and split() here to generalize for any text file.
        # Need read_text(encoding) for Windows to read all wordlist fonts.
        choice = self.share.choose_wordlist.get()
        wordfile = self.share.word_files[choice]
        all_words = set(Path(wordfile).read_text(encoding='utf-8').split())

        # Need to remove words having the possessive form ('s) b/c they
        #   duplicate many nouns in an English system dictionary.
        #   isalpha() also removes hyphenated words; EFF large wordlist has 4.
        # NOTE that all wordfiles were constructed with make_wordlist,
        # https://github.com/csecht/make_wordlist, and so contain only words
        # of 3 or more characters.
        longlist = self.listdata['word_list'] = [
            word for word in all_words if word.isalpha()]
        self.listdata['short_list'] = [
            word for word in longlist if len(word) <= 8]

        # This is used only as a PassFyi.explain() parameter, which is called
        #   only from the PassViewer.config_master Help menu.
        self.share.longlist_len = len(longlist)

    def make_pass(self) -> None:
        """
        Generate and set random pass-strings.
        Called through Controller from keybinding, menu, or button.
        Calls set_entropy() and config_results().
        """

        # Need to correct invalid user entries for number of words & characters.
        numwords = self.share.numwords_entry.get().strip()
        if numwords == '':
            self.share.numwords_entry.insert(0, '0')
        elif numwords.isdigit() is False:
            self.share.numwords_entry.delete(0, 'end')
            self.share.numwords_entry.insert(0, '0')
        numwords = int(self.share.numwords_entry.get())

        numchars = self.share.numchars_entry.get().strip()
        if numchars == '':
            self.share.numchars_entry.insert(0, '0')
        if numchars.isdigit() is False:
            self.share.numchars_entry.delete(0, 'end')
            self.share.numchars_entry.insert(0, '0')
        numchars = int(self.share.numchars_entry.get())

        # Need to filter words and strings containing characters to be excluded.
        unused = self.share.exclude_entry.get().strip()
        # No need to repopulate lists or duplicate display of excluded characters
        #   if unchanged between calls.
        if unused != self.strdata['prior_unused']:
            if len(unused) > 0:
                self.listdata['word_list'] = [
                    word for word in self.listdata['word_list'] if unused not in word]
                self.listdata['short_list'] = [
                    word for word in self.listdata['short_list'] if unused not in word]
                self.strdata['symbols'] = [
                    _s for _s in self.strdata['symbols'] if unused not in _s]
                self.strdata['digi'] = [
                    _d for _d in self.strdata['digi'] if unused not in _d]
                self.strdata['caps'] = [
                    _uc for _uc in self.strdata['caps'] if unused not in _uc]
                self.strdata['all_char'] = [
                    _ch for _ch in self.strdata['all_char'] if unused not in _ch]
                self.strdata['some_char'] = [
                    _ch for _ch in self.strdata['some_char'] if unused not in _ch]

                # Display all currently excluded characters
                self.strdata['all_unused'] = self.strdata['all_unused'] + ' ' + unused
                self.share.tkdata['excluded'].set(self.strdata['all_unused'])

                self.strdata['prior_unused'] = unused

            # Need to reset to default values if user deletes prior entry.
            elif len(unused) == 0:
                self.reset_exclusions()

        # Do not accept entries with space between characters.
        if ' ' in unused:
            self.reset_exclusions()

        # Build pass-strings.
        passphrase = "".join(VERY_RANDOM.choice(self.listdata['word_list']) for
                             _ in range(numwords))
        shortphrase = "".join(VERY_RANDOM.choice(self.listdata['short_list']) for
                              _ in range(numwords))
        password1 = "".join(VERY_RANDOM.choice(self.strdata['all_char']) for
                            _ in range(numchars))
        password2 = "".join(VERY_RANDOM.choice(self.strdata['some_char']) for
                            _ in range(numchars))

        # Randomly select 1 of each symbol to append; length not user-specified.
        addsymbol = "".join(VERY_RANDOM.choice(self.strdata['symbols']) for _ in range(1))
        addnum = "".join(VERY_RANDOM.choice(self.strdata['digi']) for _ in range(1))
        addcaps = "".join(VERY_RANDOM.choice(self.strdata['caps']) for _ in range(1))

        # Build final passphrase alternatives.
        phraseplus = passphrase + addsymbol + addnum + addcaps
        phraseshort = shortphrase + addsymbol + addnum + addcaps

        # Set all pass-strings for display in results frames.
        self.share.tkdata['phrase_raw'].set(passphrase)
        self.share.tkdata['pp_raw_len'].set(len(passphrase))
        self.share.tkdata['phrase_plus'].set(phraseplus)
        self.share.tkdata['pp_plus_len'].set(len(phraseplus))
        self.share.tkdata['phrase_short'].set(phraseshort)
        self.share.tkdata['pp_short_len'].set(len(phraseshort))
        self.share.tkdata['pw_any'].set(password1)
        self.share.tkdata['pw_any_len'].set(len(password1))
        self.share.tkdata['pw_some'].set(password2)
        self.share.tkdata['pw_some_len'].set(len(password2))

        # Finally, set H values for each pass-string and configure results.
        self.set_entropy(numwords, numchars)
        self.config_results()

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
        h_symbol =  -log(1 / len(self.strdata['symbols']), 2)
        h_digit = -log(1 / len(self.strdata['digi']), 2)
        h_cap = -log(1 / len(self.strdata['caps']), 2)
        h_add3 = int(h_symbol + h_cap + h_digit)  # H ~= 11

        # Calculate information entropy, H = L * log N / log 2, where N is the
        #   number of possible characters or words and L is the number of characters
        #   or words in the pass-string. Log can be any base, but needs to be
        #   the same base in numerator and denominator.
        # Note that N is corrected for any excluded words from set_pstrings().
        # Need to display H as integer, not float.
        self.share.tkdata['pp_raw_h'].set(
            int(numwords * log(len(self.listdata['word_list'])) / log(2)))
        self.share.tkdata['pp_plus_h'].set(
            self.share.tkdata['pp_raw_h'].get() + h_add3)
        h_some = int(numwords * log(len(self.listdata['short_list'])) / log(2))
        self.share.tkdata['pp_short_h'].set(
            h_some + h_add3)
        self.share.tkdata['pw_any_h'].set(
            int(numchars * log(len(self.strdata['all_char'])) / log(2)))
        self.share.tkdata['pw_some_h'].set(
            int(numchars * log(len(self.strdata['some_char'])) / log(2)))

    def config_results(self) -> None:
        """
        Configure fonts and display widths in results frames to provide
        a more readable display of results.
        """
        # Change font colors of results from the initial self.passstub_fg.
        # pass_fg does not change after first call to set_pstrings().
        self.share.pp_raw_show.config(  fg=self.share.pass_fg)
        self.share.pp_plus_show.config( fg=self.share.pass_fg)
        self.share.pp_short_show.config(fg=self.share.pass_fg)
        self.share.pw_any_show.config(  fg=self.share.pass_fg)
        self.share.pw_some_show.config( fg=self.share.pass_fg)

        # Need to reduce font size of long pass-string length to keep
        #   window on screen, then reset to default font size when pass-string
        #   length is shortened.
        # Use pp_plus_len, the likely longest passstring, to trigger font change.
        # B/c 'width' is character units, not pixels, length may change
        #   as font sizes and string lengths change.
        small_font = 'Courier', 10
        if MY_OS == 'dar':
            small_font = 'Courier', 12
        if self.share.tkdata['pp_plus_len'].get() > W:
            self.share.pp_raw_show.config(
                font=small_font,
                width=self.share.tkdata['pp_plus_len'].get())
            self.share.pp_plus_show.config(font=small_font)
            self.share.pp_short_show.config(font=small_font)

        elif self.share.tkdata['pp_plus_len'].get() <= W:
            self.share.pp_raw_show.config(font=self.share.display_font, width=W)
            self.share.pp_plus_show.config(font=self.share.display_font, width=W)
            self.share.pp_short_show.config(font=self.share.display_font, width=W)

        if self.share.tkdata['pw_any_len'].get() > W:
            self.share.pw_any_show.config(
                font=small_font,
                width=self.share.tkdata['pw_any_len'].get())
            self.share.pw_some_show.config(font=small_font)

        elif self.share.tkdata['pw_any_len'].get() <= W:
            self.share.pw_any_show.config(font=self.share.display_font, width=W)
            self.share.pw_some_show.config(font=self.share.display_font, width=W)

    def reset_exclusions(self) -> None:
        """
        Restore original word and character lists with default values.
        Call get_words() to restore full word lists.
        """
        self.share.exclude_entry.delete(0, 'end')
        self.share.tkdata['excluded'].set('')

        self.strdata['all_unused'] = ''
        self.strdata['symbols'] = SYMBOLS
        self.strdata['digi'] = digits
        self.strdata['caps'] = ascii_uppercase
        self.strdata['all_char'] = ascii_letters + digits + punctuation
        self.strdata['some_char'] = ascii_letters + digits + SYMBOLS

        self.get_words()


class PassViewer(tk.Frame):
    """
    The Viewer communicates with Modeler via 'share' objects handled
    through the Controller class. All GUI widgets go here.
    """
    def __init__(self, master, share):
        super().__init__(master)
        self.share = share

        # Colors and fonts:
        self.master_fg =    'LightCyan2'  # Used for row headers.
        self.master_bg =    'SkyBlue4'  # Also used for some labels.
        self.dataframe_bg = 'grey40'  # Also background for data labels.
        self.stubresult_fg = 'grey60'  # For initial pass-string stub.
        self.share.pass_fg = 'brown4'  # Pass-string font color.
        self.pass_bg =       'khaki2'  # Background of pass-string results cells.

        # Use Courier b/c TKFixedFont does not monospace symbol characters.
        self.share.display_font =  'Courier', 12  # Used for pass-string results.
        if MY_OS == 'dar':
            self.share.display_font = 'Courier', 14
        self.stubresult = 'Result can be copied and pasted from keyboard.'

        # All data variables that are passed(shared) between Modeler and Viewer.
        self.share.tkdata = {
            "pp_raw_len"    : tk.IntVar(),
            "pp_plus_len"   : tk.IntVar(),
            "pp_short_len"  : tk.IntVar(),
            "pp_raw_h"      : tk.IntVar(),
            "pp_plus_h"     : tk.IntVar(),
            "pp_short_h"    : tk.IntVar(),
            "phrase_raw"    : tk.StringVar(),
            "phrase_plus"   : tk.StringVar(),
            "phrase_short"  : tk.StringVar(),
            "pw_any_len"    : tk.IntVar(),
            "pw_some_len"   : tk.IntVar(),
            "pw_any_h"      : tk.IntVar(),
            "pw_some_h"     : tk.IntVar(),
            "pw_any"        : tk.StringVar(),
            "pw_some"       : tk.StringVar(),
            "excluded"      : tk.StringVar()
        }

        # Passphrase section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #  Generally sorted by row order.
        self.share.choose_wordlist = ttk.Combobox(state='readonly', width=24)
        self.share.choose_wordlist.bind('<<ComboboxSelected>>', self.share.getwords)

        self.numwords_label = tk.Label(text='# words',
                                       fg=self.pass_bg, bg=self.master_bg)
        self.share.numwords_entry = tk.Entry(width=2)
        self.share.numwords_entry.insert(0, '5')

        self.l_and_h_header =  tk.Label(text=' H      L', width=10,
                                        fg=self.master_fg, bg=self.master_bg)
        self.pp_section_head = tk.Label(text='Passphrase wordlists',
                                        font=('default', 12),
                                        fg=self.pass_bg, bg=self.master_bg)
        # MacOS needs a larger font
        if MY_OS == 'dar':
            self.pp_section_head.config(font=('default', 16))

        self.result_frame1 = tk.Frame(master, borderwidth=3, relief='sunken',
                                      background=self.dataframe_bg)
        self.result_frame2 = tk.Frame(master, borderwidth=3, relief='sunken',
                                      background=self.dataframe_bg)

        self.pp_raw_head =   tk.Label(text="Any word from list",
                                      fg=self.master_fg, bg=self.master_bg)
        self.pp_plus_head =  tk.Label(text="... plus 3 characters",
                                      fg=self.master_fg, bg=self.master_bg)
        self.pp_short_head = tk.Label(text="...but fewer than 9 letters",
                                      fg=self.master_fg, bg=self.master_bg)

        self.share.tkdata['pp_raw_len'].set(0)
        self.share.tkdata['pp_plus_len'].set(0)
        self.share.tkdata['pp_short_len'].set(0)
        self.pp_raw_len_lbl =   tk.Label(self.result_frame1, width=3,
                                         textvariable=self.share.tkdata[
                                             'pp_raw_len'])
        self.pp_plus_len_lbl =  tk.Label(self.result_frame1, width=3,
                                         textvariable=self.share.tkdata[
                                             'pp_plus_len'])
        self.pp_short_len_lbl = tk.Label(self.result_frame1, width=3,
                                         textvariable=self.share.tkdata[
                                             'pp_short_len'])

        self.share.tkdata['pp_raw_h'].set(0)
        self.share.tkdata['pp_plus_h'].set(0)
        self.share.tkdata['pp_short_h'].set(0)
        self.pp_raw_h_lbl =   tk.Label(self.result_frame1, width=3,
                                       textvariable=self.share.tkdata[
                                           'pp_raw_h'])
        self.pp_plus_h_lbl =  tk.Label(self.result_frame1, width=3,
                                       textvariable=self.share.tkdata[
                                           'pp_plus_h'])
        self.pp_short_h_lbl = tk.Label(self.result_frame1, width=3,
                                       textvariable=self.share.tkdata[
                                           'pp_short_h'])

        self.share.tkdata['phrase_raw'].set(self.stubresult)
        self.share.tkdata['phrase_plus'].set(self.stubresult)
        self.share.tkdata['phrase_short'].set(self.stubresult)
        # Results are displayed in Entry() instead of Text() b/c
        # textvariable is easier to code than .insert(). Otherwise, identical.
        self.share.pp_raw_show = tk.Entry(self.result_frame1, width=W,
                                          textvariable=self.share.tkdata[
                                              'phrase_raw'],
                                          fg=self.stubresult_fg, bg=self.pass_bg,
                                          font=self.share.display_font)
        self.share.pp_plus_show = tk.Entry(self.result_frame1, width=W,
                                           textvariable=self.share.tkdata[
                                               'phrase_plus'],
                                           fg=self.stubresult_fg, bg=self.pass_bg,
                                           font=self.share.display_font)
        self.share.pp_short_show = tk.Entry(self.result_frame1, width=W,
                                            textvariable=self.share.tkdata[
                                                'phrase_short'],
                                            fg=self.stubresult_fg,
                                            bg=self.pass_bg,
                                            font=self.share.display_font)
        # End passphrase section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        self.generate_btn = ttk.Button()

        # Password section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.pw_section_head = tk.Label(text='Passwords', font=('default', 12),
                                        fg=self.pass_bg, bg=self.master_bg)
        if MY_OS == 'dar':
            self.pw_section_head.config(font=('default', 16))

        self.numchars_label = tk.Label(text='# characters', fg=self.pass_bg,
                                       bg=self.master_bg)
        self.share.numchars_entry = tk.Entry(width=3)
        self.share.numchars_entry.insert(0, 0)

        self.l_and_h_header2 =  tk.Label(text=' H      L', width=10,
                                         fg=self.master_fg, bg=self.master_bg)

        self.pw_any_head = tk.Label(   text="Any characters", fg=self.master_fg,
                                       bg=self.master_bg)
        self.pw_some_head = tk.Label(  text="More likely usable characters",
                                       fg=self.master_fg, bg=self.master_bg)

        self.share.tkdata['pw_any_len'].set(0)
        self.share.tkdata['pw_some_len'].set(0)
        self.pw_any_len_lbl =  tk.Label(self.result_frame2, width=3,
                                        textvariable=self.share.tkdata[
                                            'pw_any_len'])
        self.pw_some_len_lbl = tk.Label(self.result_frame2, width=3,
                                        textvariable=self.share.tkdata[
                                            'pw_some_len'])
        self.share.tkdata['pw_any_h'].set(0)
        self.share.tkdata['pw_some_h'].set(0)
        self.pw_any_h_lbl =    tk.Label(self.result_frame2, width=3,
                                        textvariable=self.share.tkdata[
                                            'pw_any_h'])
        self.pw_some_h_lbl =   tk.Label(self.result_frame2, width=3,
                                        textvariable=self.share.tkdata[
                                            'pw_some_h'])

        self.share.tkdata['pw_any'].set(self.stubresult)
        self.share.tkdata['pw_some'].set(self.stubresult)
        self.share.pw_any_show = tk.Entry(self.result_frame2,
                                          textvariable=self.share.tkdata[
                                            'pw_any'],
                                          width=W, font=self.share.display_font,
                                          fg=self.stubresult_fg, bg=self.pass_bg)
        self.share.pw_some_show = tk.Entry(self.result_frame2,
                                           textvariable=self.share.tkdata[
                                            'pw_some'],
                                           width=W, font=self.share.display_font,
                                           fg=self.stubresult_fg, bg=self.pass_bg)
        # End password section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        # Begin exclude character section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.exclude_head =   tk.Label(text='Exclude character(s)',
                                       fg=self.pass_bg, bg=self.master_bg)
        self.share.exclude_entry = tk.Entry(width=2)
        self.exclude_info_b = ttk.Button()
        self.reset_button =   ttk.Button()
        self.excluded_head =  tk.Label(text='Currently excluded:',
                                       fg=self.master_fg, bg=self.master_bg)
        self.excluded_show =  tk.Label(textvariable=self.share.tkdata[
                                            'excluded'],
                                       fg='orange', bg=self.master_bg)
        # End exclude character section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        self.config_master()
        self.config_buttons()
        self.grid_all()

        self.share.checkfiles()
        self.share.getwords()

    def config_master(self) -> None:
        """Set up main window geometry, keybindings, menus.
        """
        self.config(bg=self.master_bg)

        if MY_OS == 'dar':
            self.master.bind('<Button-2>', RightClickEdit)
        elif MY_OS in 'lin, win':
            self.master.bind('<Button-3>', RightClickEdit)

        # Need pass-string fields to stretch with window drag size.
        self.master.columnconfigure(3, weight=1)
        self.result_frame1.columnconfigure(3, weight=2)
        self.result_frame2.columnconfigure(3, weight=2)

        # Widget configurations are generally listed top to bottom of window.
        self.master.bind("<Escape>", lambda q: quit_gui())
        self.master.bind("<Control-q>", lambda q: quit_gui())
        self.master.bind("<Control-g>", lambda q: self.share.makepass())

        # Create menu instance and add pull-down menus
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Generate", command=self.share.makepass,
                         accelerator="Ctrl+G")
        file.add_command(label="Quit", command=quit_gui,
                         accelerator="Ctrl+Q")

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(     label="Help", menu=help_menu)
        help_menu.add_command(label="What's going on here?",
                              command=self.share.explain)
        help_menu.add_command(label="About", command=self.share.about)

    def config_buttons(self) -> None:
        """Set up all buttons used in master window.
        """
        # There are problems of tk.Button text showing up on MacOS, so ttk.
        # Explicit styles are needed for buttons to show properly on MacOS.
        #  ... even then, background and pressed colors won't be recognized.
        style = ttk.Style()
        style.map("G.TButton",
                  foreground=[('active', self.share.pass_fg)],
                  background=[('pressed', self.dataframe_bg),
                              ('active', self.pass_bg)])
        self.generate_btn.configure(  style="G.TButton", text='Generate!',
                                      command=self.share.makepass)

        self.generate_btn.focus()
        self.reset_button.configure(  style="G.TButton", text='Reset',
                                      width=0,
                                      command=self.share.reset)
        self.exclude_info_b.configure(style="G.TButton", text="?",
                                      width=0,
                                      command=self.share.excludemsg)

    def grid_all(self) -> None:
        """Grid all tkinter widgets.
        """
        # This self.grid fills out the inherited tk.Frame, padding gives border.
        # Padding depends on app.minsize/maxsize in if __name__ == "__main__"
        # Frame background color, self.master_bg, is set in config_master().
        self.grid(column=0, row=0, sticky=tk.NSEW, rowspan=11, columnspan=4,
                  padx=3, pady=(3, 4))

        # %%%%%%%%%%%%%%%%%%%%%%%% sorted by row number %%%%%%%%%%%%%%%%%%%%%%%
        # Passphrase widgets %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.pp_section_head.grid(column=0, row=0, pady=(10, 5), padx=5,
                                  sticky=tk.W)
        self.share.choose_wordlist.grid(
                                  column=1, row=0, pady=(10, 5), padx=5,
                                  columnspan=2, sticky=tk.W)

        self.numwords_label.grid( column=0, row=1, padx=5, sticky=tk.W)
        self.share.numwords_entry.grid(
                                  column=0, row=1, padx=(5, 100), sticky=tk.E)
        self.l_and_h_header.grid( column=1, row=1, padx=0, sticky=tk.W)

        self.result_frame1.grid(  column=1, row=2, padx=(5, 10),
                                  columnspan=3, rowspan=3, sticky=tk.EW)

        # Result _shows will maintain equal widths with sticky=tk.EW.
        self.pp_raw_head.grid(      column=0, row=2, pady=(6, 0), sticky=tk.E)
        self.pp_raw_h_lbl.grid(     column=1, row=2, pady=(5, 3), padx=(5, 0))
        self.pp_raw_len_lbl.grid(   column=2, row=2, pady=(5, 3), padx=(5, 0))
        self.share.pp_raw_show.grid(column=3, row=2, pady=(5, 3), padx=5,
                                    ipadx=5, sticky=tk.EW)

        self.pp_plus_head.grid(      column=0, row=3, pady=(3, 0), sticky=tk.E)
        self.pp_plus_h_lbl.grid(     column=1, row=3, pady=(5, 3), padx=(5, 0))
        self.pp_plus_len_lbl.grid(   column=2, row=3, pady=(5, 3), padx=(5, 0))
        self.share.pp_plus_show.grid(column=3, row=3, pady=(5, 3), padx=5,
                                     ipadx=5, sticky=tk.EW)

        self.pp_short_head.grid(     column=0, row=4, pady=(3, 6), sticky=tk.E)
        self.pp_short_h_lbl.grid(    column=1, row=4, pady=3, padx=(5, 0))
        self.pp_short_len_lbl.grid(  column=2, row=4, pady=3, padx=(5, 0))
        self.share.pp_short_show.grid(column=3, row=4, pady=6, padx=5,
                                      ipadx=5, sticky=tk.EW)

        # Need to pad and span to center the button between two results frames.
        #   ...with different padding to keep it aligned in MacOS.
        self.generate_btn.grid(   column=3, row=5, pady=(10, 5), rowspan=2,
                                  padx=(125, 0), sticky=tk.W)
        if MY_OS == 'dar':
            self.generate_btn.grid(padx=(40, 0))

        # Password widgets %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.pw_section_head.grid(column=0, row=5, pady=(12, 6), padx=5,
                                  sticky=tk.W)
        self.numchars_label.grid( column=0, row=6, pady=0, padx=5,
                                  sticky=tk.W)
        self.share.numchars_entry.grid(
                                  column=0, row=6, pady=0, padx=(0, 65),
                                  sticky=tk.E)
        self.l_and_h_header2.grid(column=1, row=6, pady=0, padx=0,
                                  sticky=tk.W)

        self.result_frame2.grid(  column=1, row=7, padx=(5, 10),
                                  columnspan=3, rowspan=2, sticky=tk.EW)

        self.pw_any_head.grid(    column=0, row=7, pady=(6, 0),
                                  sticky=tk.E)
        self.pw_any_h_lbl.grid(   column=1, row=7, pady=(6, 3), padx=(5, 0))
        self.pw_any_len_lbl.grid( column=2, row=7, pady=(6, 3), padx=(5, 0))
        self.share.pw_any_show.grid(column=3, row=7, pady=(6, 3), padx=5,
                                    columnspan=2, ipadx=5, sticky=tk.EW)

        self.pw_some_head.grid(   column=0, row=8, pady=(0, 6), padx=(5, 0),
                                  sticky=tk.E)
        self.pw_some_h_lbl.grid(  column=1, row=8, pady=3, padx=(5, 0))
        self.pw_some_len_lbl.grid(column=2, row=8, pady=3, padx=(5, 0))
        self.share.pw_some_show.grid(column=3, row=8, pady=6, padx=5,
                                     columnspan=2, ipadx=5, sticky=tk.EW)

        # Excluded character widgets %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.exclude_head.grid(  column=0, row=9, pady=(20, 0), padx=(17, 0),
                                 sticky=tk.W)
        self.share.exclude_entry.grid(
                                 column=0, row=9, pady=(20, 5), padx=(0, 15),
                                 sticky=tk.E)
        self.exclude_info_b.grid(column=1, row=9, pady=(20, 5), padx=(0, 0),
                                 sticky=tk.W)

        self.excluded_head.grid(column=0, row=10, pady=(0, 8), sticky=tk.E)
        self.reset_button.grid( column=0, row=10, pady=(0, 12), padx=(20, 0),
                                sticky=tk.W)
        self.excluded_show.grid(column=1, row=10, pady=(0, 8), sticky=tk.W)

        # Need to adjust padding for MacOS b/c of different character widths.
        if MY_OS == 'dar':
            self.exclude_head.grid(padx=(8, 0))
            self.reset_button.grid( columnspan=2, padx=(15, 0))
            self.excluded_head.grid(columnspan=2, padx=(90, 0), sticky=tk.W)
            self.excluded_show.grid(column=0, columnspan=2, padx=(218, 0))


class PassController(tk.Tk):
    """
    The Controller through which other Classes can interact.
    """
    def __init__(self):
        super().__init__()

        container = tk.Frame(self).grid(sticky=tk.NSEW)
        PassViewer(master=container, share=self)

    def checkfiles(self):
        """
        Is called from the Viewer __init__, which should be the only
        call to check_files(). Exits if needed files not found,
        otherwise populates choose_wordlist Combobox.
        """
        PassModeler(share=self).check_files()

    def getwords(self, *args):
        """Is called from the Viewer __init__.
        Populate lists with words to randomize in make_pass().

        :param args: a virtual event call from choose_wordlist Combobox.
        """
        PassModeler(share=self).get_words()

    def makepass(self) -> None:
        """Is called only from the Viewer for "Generate" commands.
        make_pass() creates random pass-strings, which then calls
        set_entropy() and config_results().
        """
        PassModeler(share=self).make_pass()

    def reset(self) -> None:
        """Is called only in response to reset button from the Viewer.
        """
        PassModeler(share=self).reset_exclusions()

    def explain(self):
        """
        Is called from Viewer Help menu. Parameters are live data feeds
        to the pop-up window.
        """
        PassFyi(share=self).explain(self.choose_wordlist.get(), self.longlist_len)

    def about(self):
        """Is called only from Viewer Help menu.
        """
        PassFyi(share=self).about()

    def excludemsg(self):
        """Is called only from the Viewer "?" button in exclude section.
        """
        PassFyi(share=self).exclude_msg()


class PassFyi:
    """Provide pop-up windows to answer user queries.
    """
    def __init__(self, share):
        self.share = share

    @staticmethod
    def explain(selection, wordcount) -> None:
        """Provide information about words used to create passphrases.

        :param selection: User selected wordlist name.
        :param wordcount: Length of full selected wordlist list.
        :return: An text window notice with current wordlist data.
        """

        info = (
"""A passphrase is a random string of words that can be more secure and
easier to remember than a password of random characters. For more
information on passphrases, see, for example, a discussion of word lists
and word selection at the Electronic Frontier Foundation (EFF):
https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases

On MacOS and Linux systems, the system dictionary wordlist is used by
default to provide words, though optional wordfiles are available.
Windows users can use only the optional wordfiles.

"""
f'There are {wordcount} words available to construct passphrases'
f' from the\ncurrently selected wordlist, {selection}.\n'
"""
There is an option to exclude any character or string of characters
from passphrase words and passwords. Words with excluded letters are not
available nor counted above. Multiple windows can remain open to compare
the counts of different wordlists.

Optional wordfiles were derived from texts obtained from these sites:
    https://www.gutenberg.org
    https://www.archives.gov/founding-docs/constitution-transcript
    https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt
Although the EFF list contains 7776 selected words, only 7772 are used
here because hyphenated words are excluded from all wordfiles.

Words with less than 3 letters are not used in any wordlist.

To accommodate some password requirements, a choice is provided that
adds three characters : 1 symbol, 1 number, and 1 upper case letter.
"""
f'The symbols used are: {SYMBOLS}\n'
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

        infotext = ScrolledText(infowin, width=75, height=25,
                                background='SkyBlue4', foreground='grey98',
                                relief='groove', borderwidth=8,
                                padx=20, pady=10)
        infotext.insert('1.0', info)
        infotext.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        if MY_OS in 'win':
            infowin.geometry('575x470')
            infowin.minsize(575, 200)
            infotext.configure(font=('default', 11))
            infotext.bind('<Button-3>', RightClickEdit)
        elif MY_OS == 'dar':
            infowin.geometry('575x500')
            infowin.minsize(575, 200)
            infotext.configure(font=('default', 14))
            infotext.bind('<Button-2>', RightClickEdit)
        elif MY_OS in 'lin':
            infowin.geometry('650x470')
            infowin.minsize(650, 200)
            infotext.bind('<Button-3>', RightClickEdit)


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
————————————————————————————————————————
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
————————————————————————————————————————\n
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

        if MY_OS == 'dar':
            abouttxt.bind('<Button-2>', RightClickEdit)
            abouttxt.configure(font=('default', 14), height=num_lines + 5)
        elif MY_OS == 'win':
            abouttxt.configure(font=('default', 10))

        if MY_OS in 'lin, win':
            abouttxt.bind('<Button-3>', RightClickEdit)

    @staticmethod
    def exclude_msg() -> None:
        """A pop-up describing how to use excluded characters.
        Called only from a Button.

        :return: A message text window.
        """
        msg = (
"""
Any character(s) you enter will not appear in passphrase
words or passwords. Multiple characters are treated as a
unit. For example, "es" will exclude "trees", not "eye"
and  "says". To exclude everything having "e" and "s",
enter "e", click Generate!, then enter "s" and Generate!

The Reset button removes all exclusions. A space entered
between characters will also trigger a reset.
"""
)
        exclwin = tk.Toplevel()
        exclwin.title('Exclude from what?')
        num_lines = msg.count('\n')
        infotext = tk.Text(exclwin, width=60, height=num_lines + 1,
                           background='grey40', foreground='grey98',
                           relief='groove', borderwidth=8, padx=20, pady=10)
        infotext.insert('1.0', msg)
        infotext.pack()

        if MY_OS == 'dar':
            infotext.configure(font=('default', 14), width=42)
        elif MY_OS == 'win':
            infotext.configure(font=('default', 10), width=50)


if __name__ == "__main__":
    app = PassController()
    app.title("Passphrase Generator")
    if MY_OS == 'lin':
        app.minsize(970, 425)
        app.maxsize(1230, 425)
    elif MY_OS == 'dar':
        app.minsize(850, 425)
        app.maxsize(1230, 425)
    elif MY_OS == 'win':
        app.minsize(950, 390)
        app.maxsize(1230, 390)
    app.mainloop()

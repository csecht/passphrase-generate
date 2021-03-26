#!/usr/bin/env python3

"""
A passphrase and passcode generator using MVC architecture, which is
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

__version__ = '0.9.18'

import glob
import random
import sys
from math import log
from pathlib import Path
from string import digits, punctuation, ascii_letters, ascii_uppercase
from typing import Dict, List, Any

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    # pylint: disable=unused-import
    import tkinter.font
    from tkinter import messagebox
    from tkinter.scrolledtext import ScrolledText
except (ImportError, ModuleNotFoundError) as error:
    print('Passphrase.py requires tkinter, which is included with Python 3.7+'
          '\nInstall 3.7+ or re-install Python and include Tk/Tcl.'
          f'\nSee also: https://tkdocs.com/tutorial/install.html \n{error}')

if sys.version_info < (3, 6):
    print('passphrase.py requires at least Python 3.6.')
    sys.exit(1)

MY_OS = sys.platform[:3]
# MY_OS = 'win'  # TESTING

PROJ_URL = 'github.com/csecht/passphrase-generate'

SYMBOLS = "~!@#$%^&*_-+="
# SYMBOLS = "~!@#$%^&*()_-+={}[]<>?"

SYSDICT_PATH = Path('/usr/share/dict/words')

VERY_RANDOM = random.Random(random.random())
# VERY_RANDOM = random.Random(time.time())  # Use epoch timestamp seed.
# VERY_RANDOM = random.SystemRandom()   # Use current system's random.

# Note: The optional wordlist files are referenced in PassModeler().
WORDDIR = './wordlists/'

W = 52  # Default width of the results display fields.


# Functions used by passphrase, but not part of MVC structure %%%%%%%%%%%%%%%%%
def quit_gui(event=None) -> None:
    """Safe and informative exit from the program.
    """
    print('\n  *** User has quit the program. Exiting...\n')
    app.destroy()
    sys.exit(0)


def close_toplevel(topwindow, event=None) -> None:
    """Close named toplevel window that has focus.
    Called from command/control W keybinding.

    :param topwindow: the tk.Toplevel() widget name.
    """
    topwindow.destroy()


def random_bkg() -> str:
    """Selects a random color; intended for Toplevel window backgrounds
    with a white or light grey foreground.

    :returns: A color name, as used in the tkinter color chart:
    http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
    :rtype: str
    """

    colour: List[str] = ['blue4', 'dark olive green', 'dark slate grey',
                         'DarkGoldenrod4', 'DarkOrange4', 'DarkOrchid4',
                         'DarkSeaGreen4', 'DeepSkyBlue4', 'DodgerBlue4',
                         'firebrick4', 'grey2', 'grey25', 'grey40',
                         'MediumOrchid4', 'MediumPurple4', 'navy',
                         'OrangeRed4', 'purple4', 'saddle brown',
                         'SkyBlue4'
                         ]
    return random.choice(colour)


class RightClickCmds:
    """
    Right-click pop-up option to edit text or close window;
    call as a Button-2 or Button-3 binding in Text or window
    that needs the commands.
    """
    # Based on: https://stackoverflow.com/questions/57701023/
    def __init__(self, event):
        right_click_menu = tk.Menu(None, tearoff=0, takefocus=0)

        right_click_menu.add_command(
            label='Select all',
            command=lambda: self.right_click_edit(event, 'SelectAll'))
        right_click_menu.add_command(
            label='Copy',
            command=lambda: self.right_click_edit(event, 'Copy'))
        right_click_menu.add_command(
            label='Paste',
            command=lambda: self.right_click_edit(event, 'Paste'))
        right_click_menu.add_command(
            label='Cut',
            command=lambda: self.right_click_edit(event, 'Cut'))
        right_click_menu.add(tk.SEPARATOR)
        right_click_menu.add_command(label='Bigger font',
                                     command=app.growfont)
        right_click_menu.add_command(label='Smaller font',
                                     command=app.shrinkfont)

        # Need to suppress 'Close window' option for master (app) window,
        #   which does not have .!toplevel instances.
        #   Show only for Toplevel windows and their children.
        if '.!toplevel' in str(app.focus_get()):
            right_click_menu.add(tk.SEPARATOR)
            right_click_menu.add_command(
                label='Close window',
                # pylint: disable=unnecessary-lambda
                command=lambda: self.close_window())

        right_click_menu.tk_popup(event.x_root + 10, event.y_root + 15)

    @staticmethod
    def right_click_edit(event, command):
        """
        Sets menu command to the selected predefined virtual event.
        Event is a unifying binding across multiple platforms.
        https://www.tcl.tk/man/tcl8.6/TkCmd/event.htm#M7
        """
        event.widget.event_generate(f'<<{command}>>')

    @staticmethod
    def close_window():
        """Close the Toplevel window where mouse has right-clicked.
        """
        # Based on https://stackoverflow.com/questions/66384144/
        # Need to cover all cases when the focus is on the toplevel window,
        #  or on a child of that window, i.e. .!text or .!frame.
        # There are many children in app and any toplevel window will be
        #   listed at or toward the end, so read children list in reverse
        #   Stop loop when the focus toplevel parent is found to prevent all
        #   toplevel windows from closing.
        for widget in reversed(app.winfo_children()):
            # pylint: disable=no-else-break
            if widget == app.focus_get():
                widget.destroy()
                break
            elif '.!text' in str(app.focus_get()):
                parent = str(app.focus_get())[:-6]
                if parent in str(widget):
                    widget.destroy()
                    break
            elif '.!frame' in str(app.focus_get()):
                parent = str(app.focus_get())[:-7]
                if parent in str(widget):
                    widget.destroy()
                    break

        # This closes ALL open Toplevel windows. Use as command?
        # for widget in app.winfo_children():
        #     if isinstance(widget, tk.Toplevel):
        #         widget.destroy()


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# MVC Classes %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class PassModeler:
    """The modeler crunches input from Viewer, then sends results back, via
    shared 'share' objects that are handled through the Controller class.
    """
    # Need Class variables here so they aren't reset in __init__ each time
    #   make_pass() is called.
    strdata: Dict[str, Any] = {
        'symbols'     : SYMBOLS,
        'digi'        : digits,
        'caps'        : ascii_uppercase,
        'all_char'    : ascii_letters + digits + punctuation,
        'some_char'   : ascii_letters + digits + SYMBOLS,
        'all_unused'  : ''
    }

    listdata: Dict[str, List[Any]] = {'word_list': [], 'short_list': []}

    def __init__(self, share):
        self.share = share

        self.share.word_files = {
            'System dictionary'      : SYSDICT_PATH,
            'EFF long wordlist'      : WORDDIR + 'eff_large_wordlist.txt',
            'US Constitution'        : WORDDIR + 'usconst_wordlist.txt',
            'Don Quijote'            : WORDDIR + 'don_quijote_wordlist.txt',
            'Frankenstein'           : WORDDIR + 'frankenstein_wordlist.txt',
            'Les Miserables'         : WORDDIR + 'les_miserables.txt',
            '此開卷第 Story of the Stone': WORDDIR + 'red_chamber_wordlist.txt'
        }

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

        # Need to have default .get() in combobox be the 1st available wordlist.
        self.share.choose_wordlist.current(0)

    # pylint: disable=unused-argument
    def get_words(self, *args) -> None:
        """
        Populate lists with words to randomize in make_pass(); needs to
        run at start and each time a new wordlist is selected by user.

        :param args: a virtual event call from choose_wordlist Combobox.
        """

        # Need to reset excluded characters and prior pass-strings when a new
        #   wordlist is selected.
        self.share.tkdata['pp_raw_h'].set(0)
        self.share.tkdata['pp_plus_h'].set(0)
        self.share.tkdata['pp_short_h'].set(0)
        self.share.tkdata['pp_raw_len'].set(0)
        self.share.tkdata['pp_plus_len'].set(0)
        self.share.tkdata['pp_short_len'].set(0)
        self.share.exclude_entry.delete(0, 'end')
        self.share.tkdata['excluded'].set('')
        self.strdata['all_unused'] = ''
        # Need to retain stub result only for startup, otherwise delete
        #   the results each time get_words() or share.getwords() is called.
        if self.share.tkdata['phrase_raw'].get() not in self.share.stubresult:
            self.share.tkdata['phrase_raw'].set('')
            self.share.tkdata['phrase_plus'].set('')
            self.share.tkdata['phrase_short'].set('')

        # The *_wordlist.txt files have only unique words, but...
        #   use set() and split() here to generalize for any text file.
        # Need read_text(encoding) so Windows can read all wordlist fonts.
        choice = self.share.choose_wordlist.get()
        wordfile = self.share.word_files[choice]
        all_words = set(Path(wordfile).read_text(encoding='utf-8').split())

        # Need to remove words having the possessive form ('s) b/c they
        #   duplicate many nouns in an English system dictionary.
        #   isalpha() also removes hyphenated words; EFF large wordlist has 4.
        # NOTE that all wordfiles were constructed with parser.py from
        # https://github.com/csecht/make_wordlist, and so contain only words
        # of 3 or more characters.
        longlist = self.listdata['word_list'] = [
            word for word in all_words if word.isalpha()]
        self.listdata['short_list'] = [
            word for word in longlist if len(word) < 7]

        # This is used as a PassFyi.explain() parameter, which is called
        #   only from the PassViewer.config_master Help menu. It is redefined
        #   in make_pass() if user excludes characters from passphrases.
        self.share.longlist_len = len(longlist)
        # This is used for live updates in the main window of selected wordlist
        #   length.
        self.share.tkdata['available'].set(len(longlist))

    def make_pass(self, event=None) -> None:
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
        # Do not accept entries with space between characters.
        # Need to reset to default values if user deletes the prior entry.
        if ' ' in unused or len(unused) == 0:
            self.reset_exclusions()

        if len(unused) > 0:
            self.listdata['word_list'] = [
                _w for _w in self.listdata['word_list'] if unused not in _w]
            self.listdata['short_list'] = [
                _w for _w in self.listdata['short_list'] if unused not in _w]
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

            # Display # of currently available words (in two different places).
            #   Used as arg in explain()
            self.share.longlist_len = len(self.listdata['word_list'])
            #   Used for live update in main window via share.available_show
            self.share.tkdata['available'].set(self.share.longlist_len)

            # Display all currently excluded characters,
            #   but not if already excluded.
            if unused not in self.strdata['all_unused'] and ' ' not in unused:
                self.strdata['all_unused'] = self.strdata['all_unused'] + ' ' + unused
                self.share.tkdata['excluded'].set(self.strdata['all_unused'])

        # Build pass-strings.
        passphrase = "".join(VERY_RANDOM.choice(self.listdata['word_list']) for
                             _ in range(numwords))
        shortphrase = "".join(VERY_RANDOM.choice(self.listdata['short_list']) for
                              _ in range(numwords))
        passcode1 = "".join(VERY_RANDOM.choice(self.strdata['all_char']) for
                            _ in range(numchars))
        passcode2 = "".join(VERY_RANDOM.choice(self.strdata['some_char']) for
                            _ in range(numchars))

        # Randomly select 1 of each symbol to append; length not user-specified.
        addsymbol = "".join(VERY_RANDOM.choice(self.strdata['symbols']) for _ in range(1))
        addnum = "".join(VERY_RANDOM.choice(self.strdata['digi']) for _ in range(1))
        addcaps = "".join(VERY_RANDOM.choice(self.strdata['caps']) for _ in range(1))

        # Build passphrase alternatives.
        phraseplus = passphrase + addsymbol + addnum + addcaps
        phraseshort = shortphrase + addsymbol + addnum + addcaps

        # Set all pass-strings for display in results frames.
        self.share.tkdata['phrase_raw'].set(passphrase)
        self.share.tkdata['pp_raw_len'].set(len(passphrase))
        self.share.tkdata['phrase_plus'].set(phraseplus)
        self.share.tkdata['pp_plus_len'].set(len(phraseplus))
        self.share.tkdata['phrase_short'].set(phraseshort)
        self.share.tkdata['pp_short_len'].set(len(phraseshort))
        self.share.tkdata['pc_any'].set(passcode1)
        self.share.tkdata['pc_any_len'].set(len(passcode1))
        self.share.tkdata['pc_some'].set(passcode2)
        self.share.tkdata['pc_some_len'].set(len(passcode2))

        # Finally, set H values for each pass-string and configure results.
        self.set_entropy(numwords, numchars)
        self.config_results()

    def set_entropy(self, numwords: int, numchars: int) -> None:
        """Calculate and set values for information entropy, H.

        :param numwords: User-defined number of passphrase words.
        :param numchars: User-defined number of passcode characters.
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
        self.share.tkdata['pp_short_h'].set(h_some + h_add3)
        self.share.tkdata['pc_any_h'].set(
            int(numchars * log(len(self.strdata['all_char'])) / log(2)))
        self.share.tkdata['pc_some_h'].set(
            int(numchars * log(len(self.strdata['some_char'])) / log(2)))

    def config_results(self) -> None:
        """
        Configure fonts and display widths in results frames to provide
        a more readable display of results. Called from make_pass().
        """
        # Change font colors of results from the initial self.passstub_fg.
        # pass_fg does not change after first call to set_pstrings().
        self.share.pp_raw_show.config(  fg=self.share.pass_fg)
        self.share.pp_plus_show.config( fg=self.share.pass_fg)
        self.share.pp_short_show.config(fg=self.share.pass_fg)
        self.share.pc_any_show.config(  fg=self.share.pass_fg)
        self.share.pc_some_show.config( fg=self.share.pass_fg)

        # Need to indicate when passphrases exceeds length of result field,
        #   then reset to default when pass-string length is shortened.
        # Use pp_plus_len, the likely longest passphrase, to trigger change.
        passphrase_len = self.share.tkdata['pp_plus_len'].get()

        # Need a special case for wider Chinese characters; 34 equivalent to 52
        #    Use 64% to generalize in case W changes.
        _w = W
        if self.share.choose_wordlist.get() == '此開卷第 Story of the Stone' \
                and passphrase_len > W * 0.64:
            _w = W * 0.64

        if passphrase_len > _w:
            self.share.pp_raw_show.config(fg=self.share.long_fg)
            self.share.pp_plus_show.config(fg=self.share.long_fg)
            self.share.pp_short_show.config(fg=self.share.long_fg)
        elif passphrase_len <= _w:
            self.share.pp_raw_show.config(fg=self.share.pass_fg)
            self.share.pp_plus_show.config(fg=self.share.pass_fg)
            self.share.pp_short_show.config(fg=self.share.pass_fg)

        # Need to show right-most of phrase in case length exceeds field width.
        self.share.pp_raw_show.xview_moveto(1)
        self.share.pp_plus_show.xview_moveto(1)
        self.share.pp_short_show.xview_moveto(1)

        # Need to also indicate long passcodes.
        passcode_len = int(self.share.numchars_entry.get())
        if passcode_len > W:
            self.share.pc_any_show.config(fg=self.share.long_fg)
            self.share.pc_some_show.config(fg=self.share.long_fg)
        elif passcode_len <= W:
            self.share.pc_any_show.config(fg=self.share.pass_fg)
            self.share.pc_some_show.config(fg=self.share.pass_fg)

        # Allow user to resize window for long strings.
        # Full-time resizing only for Windows. Resizing non-Windows at start-up
        #   is possible, but not after Generate! when length is "normal".
        # TODO: Figure out why .resizable() causes noticeable window redraw in Windows.
        # Comment out to allow default full-tim window resize on all OS.
        # if MY_OS != 'win':
        #     app.resizable(0, 0)
        #     if passphrase_len > _w or passcode_len > W:
        #         app.resizable(width=True, height=False)
        #     # Need to reset window to default size and state for shorter strings.
        #     if passphrase_len <= _w and passcode_len <= W:
        #         app.update_idletasks()
        #         app.geometry(f'{self.share.app_winwide}x{self.share.app_winhigh}')

    def reset_exclusions(self, event=None) -> None:
        """
        Restore original word and character lists with default values.
        Call get_words() to restore full word lists.
        """
        self.share.tkdata['pc_any'].set('')
        self.share.tkdata['pc_any_len'].set(0)
        self.share.tkdata['pc_any_h'].set(0)
        self.share.tkdata['pc_some'].set('')
        self.share.tkdata['pc_some_len'].set(0)
        self.share.tkdata['pc_some_h'].set(0)
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
        # self.master_fg =    'LightCyan2'  # Used for row headers.
        # self.master_bg =    'SkyBlue4'  # Also used for some labels.
        self.master_fg =    'grey90'  # Used for row headers.
        self.master_bg =    'LightSteelBlue4'  # Also used for some labels.
        self.dataframe_bg = 'grey40'  # Also background for data labels.
        self.stubpass_fg = 'grey60'  # For initial pass-string stub.
        self.share.pass_fg = 'brown4'  # Pass-string font color.
        self.share.long_fg = 'blue'  # Long pass-string font color.
        self.pass_bg =       'khaki2'  # Background of pass-string results cells.

        # Need to define as font.Font to configure in PassFonts().
        # For results Entry fields, need to use Courier family because
        #   TKFixedFont does not monospace symbol characters.
        # MacOS needs larger default fonts for easier readability.
        # 'default' is not a named font, therefore uses system default.
        if MY_OS == 'lin':
            self.share.text_font = tk.font.Font(font='TkDefaultFont')
            self.share.result_font = tk.font.Font(font='Courier')
        elif MY_OS == 'win':
            self.share.text_font = tk.font.Font(font='TkDefaultFont')
            self.share.result_font = tk.font.Font(family='Courier', size=10)
        elif MY_OS == 'dar':
            self.share.text_font = tk.font.Font(family='default', size=14)
            self.share.result_font = tk.font.Font(family='Courier', size=14)

        self.share.stubresult = 'Result can be copied and pasted.'

        # All data variables that are passed(shared) between Modeler and Viewer.
        self.share.tkdata = {
            'available'   : tk.IntVar(),
            'pp_raw_len'  : tk.IntVar(),
            'pp_plus_len' : tk.IntVar(),
            'pp_short_len': tk.IntVar(),
            'pp_raw_h'    : tk.IntVar(),
            'pp_plus_h'   : tk.IntVar(),
            'pp_short_h'  : tk.IntVar(),
            'phrase_raw'  : tk.StringVar(),
            'phrase_plus' : tk.StringVar(),
            'phrase_short': tk.StringVar(),
            'pc_any_len'  : tk.IntVar(),
            'pc_some_len' : tk.IntVar(),
            'pc_any_h'    : tk.IntVar(),
            'pc_some_h'   : tk.IntVar(),
            'pc_any'      : tk.StringVar(),
            'pc_some'     : tk.StringVar(),
            'excluded'    : tk.StringVar(),
        }

        # Passphrase section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #  Generally sorted by row order.
        self.share.choose_wordlist = ttk.Combobox(state='readonly', width=24)
        self.share.choose_wordlist.bind('<<ComboboxSelected>>', self.share.getwords)

        self.share.available_head = tk.Label(
            text='# available words:',
            fg=self.pass_bg, bg=self.master_bg)
        self.share.available_show = tk.Label(
            textvariable=self.share.tkdata['available'],
            fg=self.pass_bg, bg=self.master_bg)

        self.numwords_label = tk.Label(text='# words',
                                       fg=self.pass_bg, bg=self.master_bg)
        self.share.numwords_entry = tk.Entry(width=2)
        # Use 5 words as default passphrase length.
        self.share.numwords_entry.insert(0, '4')

        self.l_and_h_header =  tk.Label(text=' H      L', width=10,
                                        fg=self.master_fg, bg=self.master_bg)
        self.pp_section_head = tk.Label(text='Passphrase wordlists',
                                        font=('default', 12),
                                        fg=self.pass_bg, bg=self.master_bg)
        # MacOS needs a larger font and altered spacing
        if MY_OS == 'dar':
            self.pp_section_head.config(font=('default', 16))
            self.l_and_h_header.config(text='H       L')

        self.result_frame1 = tk.Frame(master, borderwidth=3, relief='sunken',
                                      background=self.dataframe_bg)
        self.result_frame2 = tk.Frame(master, borderwidth=3, relief='sunken',
                                      background=self.dataframe_bg)

        self.pp_raw_head =   tk.Label(text="Any words from list",
                                      fg=self.master_fg, bg=self.master_bg)
        self.pp_plus_head =  tk.Label(text="... plus 3 characters",
                                      fg=self.master_fg, bg=self.master_bg)
        self.pp_short_head = tk.Label(text="...words less than 7 letters",
                                      fg=self.master_fg, bg=self.master_bg)

        self.share.tkdata['pp_raw_h'].set(0)
        self.share.tkdata['pp_plus_h'].set(0)
        self.share.tkdata['pp_short_h'].set(0)
        self.pp_raw_h_lbl = tk.Label(self.result_frame1, width=3,
                                     fg=self.master_fg, bg=self.dataframe_bg,
                                     textvariable=self.share.tkdata[
                                         'pp_raw_h'])
        self.pp_plus_h_lbl = tk.Label(self.result_frame1, width=3,
                                      fg=self.master_fg, bg=self.dataframe_bg,
                                      textvariable=self.share.tkdata[
                                          'pp_plus_h'])
        self.pp_short_h_lbl = tk.Label(self.result_frame1, width=3,
                                       fg=self.master_fg,
                                       bg=self.dataframe_bg,
                                       textvariable=self.share.tkdata[
                                           'pp_short_h'])

        self.share.tkdata['pp_raw_len'].set(0)
        self.share.tkdata['pp_plus_len'].set(0)
        self.share.tkdata['pp_short_len'].set(0)
        self.pp_raw_len_lbl =   tk.Label(self.result_frame1, width=3,
                                         fg=self.master_fg, bg=self.dataframe_bg,
                                         textvariable=self.share.tkdata[
                                             'pp_raw_len'])
        self.pp_plus_len_lbl =  tk.Label(self.result_frame1, width=3,
                                         fg=self.master_fg, bg=self.dataframe_bg,
                                         textvariable=self.share.tkdata[
                                             'pp_plus_len'])
        self.pp_short_len_lbl = tk.Label(self.result_frame1, width=3,
                                         fg=self.master_fg, bg=self.dataframe_bg,
                                         textvariable=self.share.tkdata[
                                             'pp_short_len'])

        self.share.tkdata['phrase_raw'].set(self.share.stubresult)
        self.share.tkdata['phrase_plus'].set(self.share.stubresult)
        self.share.tkdata['phrase_short'].set(self.share.stubresult)
        # Results are displayed as Entry() instead of Text() b/c
        # textvariable is easier to code than .insert(). Otherwise, identical.
        self.share.pp_raw_show = tk.Entry(self.result_frame1, width=W,
                                          textvariable=self.share.tkdata[
                                              'phrase_raw'],
                                          fg=self.stubpass_fg, bg=self.pass_bg,
                                          font=self.share.result_font)
        self.share.pp_plus_show = tk.Entry(self.result_frame1, width=W,
                                           textvariable=self.share.tkdata[
                                               'phrase_plus'],
                                           fg=self.stubpass_fg, bg=self.pass_bg,
                                           font=self.share.result_font)
        self.share.pp_short_show = tk.Entry(self.result_frame1, width=W,
                                            textvariable=self.share.tkdata[
                                                'phrase_short'],
                                            fg=self.stubpass_fg, bg=self.pass_bg,
                                            font=self.share.result_font)
        # End passphrase section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        self.generate_btn = ttk.Button()

        # Passcode section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.pc_section_head = tk.Label(text='Passcodes', font=('default', 12),
                                        fg=self.pass_bg, bg=self.master_bg)

        self.numchars_label = tk.Label(text='# characters', fg=self.pass_bg,
                                       bg=self.master_bg)
        self.share.numchars_entry = tk.Entry(width=3)
        self.share.numchars_entry.insert(0, 0)

        self.l_and_h_header2 =  tk.Label(text=' H      L', width=10,
                                         fg=self.master_fg, bg=self.master_bg)
        # MacOS needs a larger font and altered spacing
        if MY_OS == 'dar':
            self.pc_section_head.config(font=('default', 16))
            self.l_and_h_header2.config(text='H       L')

        self.pc_any_head = tk.Label(   text="Any characters", fg=self.master_fg,
                                       bg=self.master_bg)
        self.pc_some_head = tk.Label(  text="More likely usable characters",
                                       fg=self.master_fg, bg=self.master_bg)

        self.share.tkdata['pc_any_len'].set(0)
        self.share.tkdata['pc_some_len'].set(0)
        self.pc_any_len_lbl =  tk.Label(self.result_frame2, width=3,
                                        fg=self.master_fg, bg=self.dataframe_bg,
                                        textvariable=self.share.tkdata[
                                            'pc_any_len'])
        self.pc_some_len_lbl = tk.Label(self.result_frame2, width=3,
                                        fg=self.master_fg, bg=self.dataframe_bg,
                                        textvariable=self.share.tkdata[
                                            'pc_some_len'])
        self.share.tkdata['pc_any_h'].set(0)
        self.share.tkdata['pc_some_h'].set(0)
        self.pc_any_h_lbl =    tk.Label(self.result_frame2, width=3,
                                        fg=self.master_fg, bg=self.dataframe_bg,
                                        textvariable=self.share.tkdata[
                                            'pc_any_h'])
        self.pc_some_h_lbl =   tk.Label(self.result_frame2, width=3,
                                        fg=self.master_fg, bg=self.dataframe_bg,
                                        textvariable=self.share.tkdata[
                                            'pc_some_h'])

        self.share.tkdata['pc_any'].set(self.share.stubresult)
        self.share.tkdata['pc_some'].set(self.share.stubresult)
        self.share.pc_any_show = tk.Entry(self.result_frame2,
                                          textvariable=self.share.tkdata[
                                              'pc_any'],
                                          width=W, font=self.share.result_font,
                                          fg=self.stubpass_fg, bg=self.pass_bg)
        self.share.pc_some_show = tk.Entry(self.result_frame2,
                                           textvariable=self.share.tkdata[
                                               'pc_some'],
                                           width=W, font=self.share.result_font,
                                           fg=self.stubpass_fg, bg=self.pass_bg)
        # End passcode section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        # Begin exclude character section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.exclude_head =   tk.Label(text='Exclude character(s)',
                                       fg=self.pass_bg, bg=self.master_bg)
        self.share.exclude_entry = tk.Entry(width=2)
        self.exclude_info_b = ttk.Button()
        self.reset_button =   ttk.Button()
        self.excluded_head =  tk.Label(text='Currently excluded:',
                                       fg=self.master_fg, bg=self.master_bg)
        self.excluded_show =  tk.Label(textvariable=self.share.tkdata['excluded'],
                                       fg='orange', bg=self.master_bg)
        self.quit_button = ttk.Button()
        # End exclude character section %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        self.config_master()
        self.config_buttons()
        self.grid_all()

        self.share.checkfiles()
        self.share.getwords()

        # Need to set window position here (not in config_master),so it doesn't
        #    shift when PassModeler.config_results() is called b/c different
        #    from app position.
        self.master.geometry('+120+100')
        # Need to get original/default window size to restore after size change.
        self.master.update_idletasks()
        self.share.app_winwide = self.master.winfo_width()
        self.share.app_winhigh = self.master.winfo_height()

    def config_master(self) -> None:
        """Set up main window configuration, keybindings, & menus.
        """
        self.config(bg=self.master_bg)

        # Need fields to stretch with window drag size and for the master
        #   frame to properly fill the app window.
        self.master.columnconfigure(3, weight=1)
        for _row in range(10):
            self.master.rowconfigure(_row, weight=1)
        self.result_frame1.columnconfigure(3, weight=1)
        self.result_frame2.columnconfigure(3, weight=1)
        self.result_frame1.rowconfigure(2, weight=1)
        self.result_frame1.rowconfigure(3, weight=1)
        self.result_frame1.rowconfigure(4, weight=1)
        self.result_frame2.rowconfigure(7, weight=1)
        self.result_frame2.rowconfigure(8, weight=1)

        self.master.bind('<Escape>', quit_gui)
        self.master.bind('<Control-q>', quit_gui)
        self.master.bind('<Control-g>', self.share.makepass)
        self.master.bind('<Return>', self.share.makepass)
        self.master.bind('<Control-o>', self.share.scratch)
        self.master.bind('<Control-r>', self.share.reset)
        self.master.bind('<Shift-Control-Up>', self.share.growfont)
        self.master.bind('<Shift-Control-Down>', self.share.shrinkfont)
        if MY_OS == 'dar':
            self.master.bind('<Command-q>', quit_gui)
            self.master.bind('<Command-g>', self.share.makepass)
            self.master.bind('<Command-o>', self.share.scratch)
            self.master.bind('<Command-r>', self.share.reset)

        # Need to specify Ctrl-A for Linux b/c in tkinter windows that key is
        #   bound to <<LineStart>>, not <<SelectAll>>, for some reason?
        if MY_OS in 'lin':
            def select_all():
                app.focus_get().event_generate('<<SelectAll>>')
            self.master.bind('<Control-a>', lambda q: select_all())

        # Need to specify OS-specific right-click mouse button only in results
        #   fields of master window.
        if MY_OS in 'lin, win':
            self.share.pp_raw_show.bind('<Button-3>', RightClickCmds)
            self.share.pp_plus_show.bind('<Button-3>', RightClickCmds)
            self.share.pp_short_show.bind('<Button-3>', RightClickCmds)
            self.share.pc_any_show.bind('<Button-3>', RightClickCmds)
            self.share.pc_some_show.bind('<Button-3>', RightClickCmds)
        elif MY_OS == 'dar':
            self.share.pp_raw_show.bind('<Button-2>', RightClickCmds)
            self.share.pp_plus_show.bind('<Button-2>', RightClickCmds)
            self.share.pp_short_show.bind('<Button-2>', RightClickCmds)
            self.share.pc_any_show.bind('<Button-2>', RightClickCmds)
            self.share.pc_some_show.bind('<Button-2>', RightClickCmds)

        # Create menu instance and add pull-down menus
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Need to show the system's native key binding the as menu accelerator.
        native_accelkey = ''
        if MY_OS in 'lin, win':
            native_accelkey = 'Ctrl'
        elif MY_OS == 'dar':
            native_accelkey = 'Command'

        file = tk.Menu(self.master, tearoff=0)
        menubar.add_cascade(label='Passphrase', menu=file)
        file.add_command(label='Generate', command=self.share.makepass,
                         accelerator=f'{native_accelkey}+G')
        file.add_command(label='Reset', command=self.share.reset,
                         accelerator=f'{native_accelkey}+R')
        file.add_command(label='Open a scratch pad', command=self.share.scratch,
                         accelerator=f'{native_accelkey}+O')
        file.add(tk.SEPARATOR)
        file.add_command(label='Quit', command=quit_gui,
                         # MacOS doesn't recognize 'Command+Q' as an accelerator
                         #   b/c can't override that system's native Command+Q,
                         #   so add Ctrl+Q to show something in the Passphrase menu.
                         accelerator=f'{native_accelkey}+Q')

        edit = tk.Menu(self.master, tearoff=0)
        menubar.add_cascade(label='Edit', menu=edit)
        edit.add_command(label='Select all',
                         command=lambda: app.focus_get().event_generate(
                             '<<SelectAll>>'),
                         accelerator=f'{native_accelkey}+A')
        edit.add_command(label='Copy',
                         command=lambda: app.focus_get().event_generate(
                             '<<Copy>>'), accelerator=f'{native_accelkey}+C')
        edit.add_command(label='Paste',
                         command=lambda: app.focus_get().event_generate(
                             '<<Paste>>'), accelerator=f'{native_accelkey}+V')
        edit.add_command(label='Cut',
                         command=lambda: app.focus_get().event_generate(
                             '<<Cut>>'), accelerator=f'{native_accelkey}+X')

        view = tk.Menu(self.master, tearoff=0)
        fontsize = tk.Menu(self.master, tearoff=0)
        menubar.add_cascade(label='View', menu=view)
        view.add_cascade(label='Font size', menu=fontsize)
        fontsize.add_command(label='Bigger font', command=self.share.growfont,
                             accelerator='Shift-Control-Up')
        fontsize.add_command(label='Smaller font', command=self.share.shrinkfont,
                             accelerator='Shift-Control-Down')

        help_menu = tk.Menu(self.master, tearoff=0)
        tips = tk.Menu(self.master, tearoff=0)
        menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_cascade(label='Tips', menu=tips)
        help_menu.add_command(label="What's going on here?",
                              command=self.share.explain)
        help_menu.add_command(label='About',
                              command=self.share.about)
        tips.add_command(label='Mouse right-click does stuff!')
        tips.add_command(label='Return/Enter key also Generates!')
        tips.add_command(label='Menu Passphrase>Open.. opens a scratch pad.')
        tips.add_command(label=f'Long results (L > {W}) turn blue.')
        tips.add_command(label='Esc key exits the program.')

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
        self.quit_button.configure(   style="G.TButton", text='Quit',
                                      width=0,
                                      command=quit_gui)

    def grid_all(self) -> None:
        """Grid all tkinter widgets.
        """
        # This self.grid fills out the inherited tk.Frame, padding gives border.
        # Padding depends on app.minsize/maxsize in if __name__ == "__main__"
        # Frame background color, self.master_bg, is set in config_master().
        self.grid(column=0, row=0, sticky=tk.NSEW, rowspan=12, columnspan=4,
                  padx=3, pady=3)

        # %%%%%%%%%%%%%%%%%%%%%%%% sorted by row number %%%%%%%%%%%%%%%%%%%%%%%
        # Passphrase widgets %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.pp_section_head.grid(      column=0, row=0, pady=(10, 5), padx=(10, 5),
                                        sticky=tk.W)
        self.share.choose_wordlist.grid(column=1, row=0, pady=(10, 5), padx=5,
                                        columnspan=2, sticky=tk.W)
        self.share.available_head.grid( column=3, row=0, pady=(10, 0),
                                        padx=(5, 0), sticky=tk.W)
        # Need separate Label spacing for each OS:
        if MY_OS == 'lin':
            self.share.available_show.grid(column=3, row=0, pady=(10, 0),
                                           padx=(130, 0), sticky=tk.W)
        elif MY_OS == 'win':
            self.share.available_show.grid(column=3, row=0, pady=(10, 0),
                                           padx=(117, 0), sticky=tk.W)
        elif MY_OS == 'dar':
            self.share.available_show.grid(column=3, row=0, pady=(10, 0),
                                           padx=(124, 0), sticky=tk.W)

        self.numwords_label.grid( column=0, row=1, padx=(10, 5), sticky=tk.W)
        self.share.numwords_entry.grid(
                                  column=0, row=1, padx=(10, 100), sticky=tk.E)
        self.l_and_h_header.grid( column=1, row=1, padx=0, sticky=tk.W)

        self.result_frame1.grid(    column=1, row=2, padx=(5, 10),
                                    columnspan=3, rowspan=3, sticky=tk.NSEW)
        # Results' _show will maintain equal widths with sticky=tk.EW.
        self.pp_raw_head.grid(      column=0, row=2, pady=(6, 0), padx=(10, 0),
                                    sticky=tk.E)
        self.pp_raw_h_lbl.grid(     column=1, row=2, pady=(5, 3), padx=(5, 0))
        self.pp_raw_len_lbl.grid(   column=2, row=2, pady=(5, 3), padx=(5, 0))
        self.share.pp_raw_show.grid(column=3, row=2, pady=(5, 3), padx=5,
                                    sticky=tk.EW)

        self.pp_plus_head.grid(      column=0, row=3, pady=(3, 0), padx=(10, 0),
                                     sticky=tk.E)
        self.pp_plus_h_lbl.grid(     column=1, row=3, pady=(5, 3), padx=(5, 0))
        self.pp_plus_len_lbl.grid(   column=2, row=3, pady=(5, 3), padx=(5, 0))
        self.share.pp_plus_show.grid(column=3, row=3, pady=(5, 3), padx=5,
                                     sticky=tk.EW)

        self.pp_short_head.grid(      column=0, row=4, pady=(3, 6), padx=(10, 0),
                                      sticky=tk.E)
        self.pp_short_h_lbl.grid(     column=1, row=4, pady=3, padx=(5, 0))
        self.pp_short_len_lbl.grid(   column=2, row=4, pady=3, padx=(5, 0))
        self.share.pp_short_show.grid(column=3, row=4, pady=6, padx=5,
                                      sticky=tk.EW)

        # Need to pad and span to center the button between two results frames.
        #   ...with different x padding to keep it aligned in different platforms.
        self.generate_btn.grid(    column=3, row=5, rowspan=2, pady=(10, 5),
                                   padx=(65, 0), sticky=tk.W)
        if MY_OS == 'win':
            self.generate_btn.grid(padx=(30, 0))
        if MY_OS == 'dar':
            self.generate_btn.grid(padx=(0, 0))

        # Passcode widgets %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.pc_section_head.grid( column=0, row=5, pady=(12, 6), padx=(10, 5),
                                   sticky=tk.W)

        self.numchars_label.grid( column=0, row=6, pady=0, padx=(10, 5),
                                  sticky=tk.W)
        self.share.numchars_entry.grid(
                                  column=0, row=6, pady=0, padx=(0, 65),
                                  sticky=tk.E)
        self.l_and_h_header2.grid(column=1, row=6, pady=0, padx=0,
                                  sticky=tk.W)

        self.result_frame2.grid(    column=1, row=7, padx=(5, 10),
                                    columnspan=3, rowspan=2, sticky=tk.NSEW)
        self.pc_any_head.grid(      column=0, row=7, pady=(6, 0), padx=(10, 0),
                                    sticky=tk.E)
        self.pc_any_h_lbl.grid(     column=1, row=7, pady=(6, 3), padx=(5, 0))
        self.pc_any_len_lbl.grid(   column=2, row=7, pady=(6, 3), padx=(5, 0))
        self.share.pc_any_show.grid(column=3, row=7, pady=(6, 3), padx=5,
                                    columnspan=2, sticky=tk.EW)

        self.pc_some_head.grid(      column=0, row=8, pady=(0, 6), padx=(10, 0),
                                     sticky=tk.E)
        self.pc_some_h_lbl.grid(     column=1, row=8, pady=3, padx=(5, 0))
        self.pc_some_len_lbl.grid(   column=2, row=8, pady=3, padx=(5, 0))
        self.share.pc_some_show.grid(column=3, row=8, pady=6, padx=5,
                                     columnspan=2, sticky=tk.EW)

        # Excluded character widgets %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.exclude_head.grid(  column=0, row=9, pady=(20, 0), padx=(17, 0),
                                 sticky=tk.W)
        self.share.exclude_entry.grid(
                                 column=0, row=9, pady=(20, 5), padx=(0, 15),
                                 sticky=tk.E)
        self.exclude_info_b.grid(column=1, row=9, pady=(20, 5), padx=(10, 0),
                                 sticky=tk.W)

        self.excluded_head.grid(column=0, row=10, pady=(0, 8), padx=(5, 0),
                                sticky=tk.E)
        self.reset_button.grid( column=0, row=10, pady=(0, 15), padx=(20, 0),
                                sticky=tk.W)
        self.excluded_show.grid(column=1, row=10, pady=(0, 8), sticky=tk.W)
        self.quit_button.grid(  column=3, row=10, pady=(0, 15), padx=(0, 15),
                                sticky=tk.E)

        # Need to adjust padding for MacOS b/c of different spacing.
        if MY_OS == 'dar':
            self.exclude_head.grid(padx=(13, 0))
            self.reset_button.grid( columnspan=2, padx=(20, 0))
            self.excluded_head.grid(columnspan=2, padx=(95, 0), sticky=tk.W)
            self.excluded_show.grid(column=0, columnspan=2, padx=(223, 0))


class PassController(tk.Tk):
    """
    The Controller through which other MVC Classes can interact.
    """
    def __init__(self):
        super().__init__()

        # pylint: disable=assignment-from-no-return
        container = tk.Frame(self).grid(sticky=tk.NSEW)
        PassViewer(master=container, share=self)

    def checkfiles(self):
        """
        Is called from the Viewer __init__, which should be the only
        call to check_files(). Exits if needed files not found,
        otherwise populates choose_wordlist Combobox.
        """
        PassModeler(share=self).check_files()

    #pylint: disable=unused-argument
    def getwords(self, *args):
        """Is called from the Viewer __init__.
        Populate lists with words to randomize in make_pass().

        :param args: a virtual event call from choose_wordlist Combobox.
        """
        PassModeler(share=self).get_words()

    def makepass(self, event=None) -> None:
        """
        Is called from the Viewer with "Generate" widgets and key
        bindings. make_pass() creates random pass-strings, which then
        calls set_entropy() and config_results().
        """
        PassModeler(share=self).make_pass()

    def scratch(self, event=None):
        """Is called from the Viewer Passphrase menu or key binding.
        """
        PassFyi(share=self).scratchpad()

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

    def reset(self, event=None) -> None:
        """
        Is called only in response to reset button in exclude section.
        """
        PassModeler(share=self).reset_exclusions()

    def growfont(self, event=None):
        """Is called from keybinding or View menu.
        """
        PassFonts(share=self).grow_font()

    def shrinkfont(self, event=None):
        """Is called from keybinding or View menu.
        """
        PassFonts(share=self).shrink_font()


class PassFyi:
    """
    Provide pop-up windows to provide usage information and offer help.
    """
    def __init__(self, share):
        self.share = share

    def scratchpad(self, event=None) -> None:
        """
        A text window for user to temporarily save results.
        Is called from Passphrase menu or keybinding.
        """
        # Separator dashes from https://coolsymbol.com/line-symbols.html.
        instruction = (
            'Paste here passphrases or passcodes that you are thinking of'
            ' using. You can then compare them, test typing them out, etc.'
            ' and see whether any work for you.\nAnything you paste or edit here'
            ' is GONE when this window is closed, so save what you want to keep'
            ' somewhere else.\n'
            '────────────────────────────────────────\n\n'
        )

        scratchwin = tk.Toplevel()
        scratchwin.title('Scratch Pad')
        scratchwin.minsize(300, 250)
        scratchwin.focus_set()
        scratchwin.bind('<Shift-Control-Up>', self.share.growfont)
        scratchwin.bind('<Shift-Control-Down>', self.share.shrinkfont)

        if MY_OS in 'lin, win':
            scratchwin.bind('<Button-3>', RightClickCmds)
            scratchwin.bind('<Control-w>', lambda q: close_toplevel(scratchwin))
        elif MY_OS == 'dar':
            scratchwin.bind('<Button-2>', RightClickCmds)
            scratchwin.bind('<Command-w>', lambda q: close_toplevel(scratchwin))

        # Need to specify Control-a for Linux b/c in tkinter windows that key
        #   is bound to <<LineStart>>, not <<SelectAll>>, for some reason?
        if MY_OS in 'lin':
            def select_all():
                app.focus_get().event_generate('<<SelectAll>>')
            scratchwin.bind('<Control-a>', lambda q: select_all())

        scratchtxt = tk.Text(scratchwin, width=75,
                             background='grey85', foreground='grey5',
                             relief='groove', borderwidth=4,
                             padx=10, pady=10, wrap=tk.WORD,
                             font=self.share.text_font)
        scratchtxt.insert(1.0, instruction)
        # Center all text in the window
        scratchtxt.tag_add('text1', 1.0, tk.END)
        scratchtxt.tag_configure('text1', justify='center')
        scratchtxt.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    def explain(self, selection: str, wordcount: int) -> None:
        """Provide information about words used to create passphrases.

        :param selection: User selected wordlist name.
        :param wordcount: Length of full selected wordlist list.
        :returns: An text window notice with current wordlist data.
        """

        explanation = (
"""A passphrase is a random string of words that can be more secure and
easier to remember than a passcode of random characters. For more
information on passphrases, see, for example, a discussion of word lists
and word selection at the Electronic Frontier Foundation (EFF):
https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases\n
On MacOS and Linux systems, the system dictionary wordlist is used by
default to provide words, though optional wordlists are available.
Windows users can use only the optional wordlists.\n
"""
f'     From the current selected wordlist, {selection},\n'
'     after subtracting words with excluded letters, if any,\n'
f'     there are {wordcount} words available to construct passphrases.\n'
"""
Passphrases and passcodes (pass-strings) are made by clicking the
Generate! button, or pressing Enter or Ctrl-G, or from the Passphrase
pull-down menu on the menu bar. The result you want can be cut and
pasted using standard keyboard commands, or right-clicking, or using
Edit from the menu bar.\n
There is an option to exclude any character or string of characters
from passphrase words and passcodes. Words with excluded letters are
not available to use. Multiple windows can remain open to compare
counts among different wordlists and exclusions.  (continued.........)\n
Optional wordfiles were derived from texts obtained from these sites:
      https://www.gutenberg.org
      https://www.archives.gov/founding-docs/constitution-transcript
      https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt
Although the EFF list contains 7776 selected words, only 7772 are used
here because hyphenated words are excluded from all wordlists.\n
Words with less than 3 letters are not used in any wordlist.
All wordlists except EFF were made with parser.py from the Project at
https://github.com/csecht/make_wordlist\n
To accommodate some passcode requirements, a choice is provided that
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

Font size can be changed with the Shift-Control-Up and Shift-Control-Up
     arrow keys or from the menu bar.
Mouse right-click opens edit options in results and pop-up windows.
"""
f'Pass-string color is BLUE when it is longer than {W} characters;\n'
'    so try dragging the window wider to see the full result.\n'
)
        explainwin = tk.Toplevel()
        explainwin.title('A word about words and characters')
        explainwin.minsize(595, 200)
        explainwin.focus_set()
        explainwin.bind('<Shift-Control-Up>', self.share.growfont)
        explainwin.bind('<Shift-Control-Down>', self.share.shrinkfont)

        os_width = 62
        if MY_OS in 'lin, win':
            explainwin.bind('<Button-3>', RightClickCmds)
            explainwin.bind('<Control-w>', lambda q: close_toplevel(explainwin))
        if MY_OS == 'dar':
            os_width = 55
            explainwin.bind('<Button-2>', RightClickCmds)
            explainwin.bind('<Command-w>', lambda q: close_toplevel(explainwin))

        explaintext = ScrolledText(explainwin, width=os_width, height=25,
                                   bg='dark slate grey', fg='grey95',
                                   relief='groove', borderwidth=8,
                                   padx=30, pady=30, wrap=tk.WORD,
                                   font=self.share.text_font)
        explaintext.insert(1.0, explanation)
        explaintext.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # If need to prevent all key actions:
        # explaintext.bind("<Key>", lambda e: "break")

    def about(self) -> None:
        """Basic information about the script; called from GUI Help menu.

        :return: Information window.
        """
        # msg separator dashes from https://coolsymbol.com/line-symbols.html.
        boilerplate = (
"""
passphrase.py and Passphrase generate random passphrases and passcodes.
"""
f'Download the most recent version from: {PROJ_URL}'
"""
──────────────────────────────────
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
──────────────────────────────────\n
                   Author:     cecht
                   Copyright: Copyright (C) 2021 C.S. Echt
                   Development Status: 4 - Beta
                   Version:    """  # __version__ is inserted here.
        )
        num_lines = boilerplate.count('\n')
        aboutwin = tk.Toplevel()
        aboutwin.title('About Passphrase')
        aboutwin.minsize(400, 200)
        aboutwin.focus_set()
        aboutwin.bind('<Shift-Control-Up>', self.share.growfont)
        aboutwin.bind('<Shift-Control-Down>', self.share.shrinkfont)

        os_width = 0
        if MY_OS in 'lin, win':
            os_width = 68
            aboutwin.bind('<Button-3>', RightClickCmds)
            aboutwin.bind('<Control-w>', lambda q: close_toplevel(aboutwin))
        elif MY_OS == 'dar':
            os_width = 60
            aboutwin.bind('<Button-2>', RightClickCmds)
            aboutwin.bind('<Command-w>', lambda q: close_toplevel(aboutwin))

        abouttxt = tk.Text(aboutwin, width=os_width, height=num_lines + 2,
                           bg=random_bkg(), fg='grey95',
                           relief='groove', borderwidth=8,
                           padx=30, pady=10, wrap=tk.WORD,
                           font=self.share.text_font)
        abouttxt.insert(1.0, boilerplate + __version__)
        abouttxt.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        # If need to prevent all key actions:
        # abouttxt.bind("<Key>", lambda e: "break")

    def exclude_msg(self) -> None:
        """A pop-up describing how to use excluded characters.
        Called only from a Button.

        :return: A message text window.
        """
        msg = (
"""
Any character(s) you enter will not appear in passphrase
words or passcodes. Multiple characters are treated as a
unit. For example, "es" will exclude "trees", not "eye"
and  "says". To exclude everything having "e" and "s",
enter "e", click Generate!, then enter "s" and Generate!

The Reset button (or Ctrl+R) removes all exclusions. A
space entered between characters will also do a reset.
"""
)
        exclwin = tk.Toplevel()
        exclwin.title('Exclude from what?')
        exclwin.minsize(300, 100)
        exclwin.focus_set()
        exclwin.bind('<Shift-Control-Up>', self.share.growfont)
        exclwin.bind('<Shift-Control-Down>', self.share.shrinkfont)

        os_width = 0
        if MY_OS in 'lin, win':
            os_width = 48
            exclwin.bind('<Button-3>', RightClickCmds)
            exclwin.bind('<Control-w>', lambda q: close_toplevel(exclwin))
        elif MY_OS == 'dar':
            os_width = 42
            exclwin.bind('<Button-2>', RightClickCmds)
            exclwin.bind('<Command-w>', lambda q: close_toplevel(exclwin))

        num_lines = msg.count('\n')
        excltext = tk.Text(exclwin, width=os_width, height=num_lines + 1,
                           bg='grey40', fg='grey95',
                           relief='groove', borderwidth=8,
                           padx=20, pady=10, wrap=tk.WORD,
                           font=self.share.text_font)
        excltext.insert(1.0, msg)
        excltext.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # If need to prevent all key actions:
        # excltext.bind("<Key>", lambda e: "break")


class PassFonts:
    """
    Change MVC font settings. Call with keybindings or menu commands.
    """
    # font.Font keywords are: family, font, size, weight, underline, overstrike.
    def __init__(self, share):
        self.share = share

    def grow_font(self, event=None):
        """Make the font size larger"""
        size = self.share.text_font['size']
        if size < 32:
            self.share.text_font.configure(size=size + 1)
        size2 = self.share.result_font['size']
        if size < 32:
            self.share.result_font.configure(size=size2 + 1)

    def shrink_font(self, event=None):
        """Make the font size smaller"""
        size = self.share.text_font['size']
        if size > 6:
            self.share.text_font.configure(size=size - 1)
        size2 = self.share.result_font['size']
        if size > 6:
            self.share.result_font.configure(size=size2 - 1)


if __name__ == "__main__":
    app = PassController()
    app.title("Passphrase Generator")
    app.minsize(650, 410)
    app.mainloop()

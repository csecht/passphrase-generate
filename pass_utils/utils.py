"""
Utilties and handlers called from the __main__ script, passphrase.
Functions:
manage_args -
quit_gui -
random_bkg -
toplevel_bindings -
close_toplevel -
click_cmds -
"""
# 'Copyright (C) 2021- 2022 C.S. Echt, under GNU General Public License'

# Standard library imports:
import argparse
import random
import sys
import tkinter as tk

# Local program imports:
import __main__
import pass_utils
from pass_utils import platform_check as chk


def manage_args() -> None:
    """Allow handling of common command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--about',
                        help='Provides description, version, GNU license',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    if args.about:
        print(__main__.__doc__)
        print(f'{"Author:".ljust(13)}', pass_utils.__author__)
        print(f'{"Version:".ljust(13)}', pass_utils.__version__)
        print(f'{"Status:".ljust(13)}', pass_utils.__status__)
        print(f'{"URL:".ljust(13)}', pass_utils.URL)
        print(pass_utils.__copyright__)
        print(pass_utils.LICENSE)
        print()
        sys.exit(0)


def quit_gui(mainloop: tk.Tk, gui=True, keybind=None) -> None:
    """Safe and informative exit from the program.

    :param mainloop: The main tk.Tk() window running the mainloop.
    :param gui: boolean flag for whether call is from gui or commandline
                argument.
    :param keybind: Needed for keybindings.
    :type keybind: Direct call from keybindings.
    """
    if gui:
        print('\n  *** User has quit the program. Exiting...\n'
              '  *** Clipboard contents have been cleared.')

        try:
            mainloop.update_idletasks()
            mainloop.after(100)
            mainloop.destroy()
        # pylint: disable=broad-except
        except Exception as unk:
            print('An unknown error occurred:', unk)
            sys.exit(0)
    else: # Expected when call --about cmdline argument.
        sys.exit(0)

    return keybind


def random_bkg() -> str:
    """Selects a random color; intended for Toplevel window backgrounds
    with a white or light grey foreground.

    :returns: A color name, as used in the tkinter color chart:
    http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
    :rtype: str
    """

    colour = ['blue4', 'dark olive green', 'dark slate grey',
              'DarkGoldenrod4', 'DarkOrange4', 'DarkOrchid4',
              'DarkSeaGreen4', 'DeepSkyBlue4', 'DodgerBlue4',
              'firebrick4', 'grey2', 'grey25', 'grey40',
              'MediumOrchid4', 'MediumPurple4', 'navy',
              'OrangeRed4', 'purple4', 'saddle brown',
              'SkyBlue4'
              ]
    # Deuteranopia simulated colors.
    # colour = ['blue4', '#646430', ''#444450';,
    #           '#727207', '#5c5c00', '#393989',
    #           '#80806a', '#46468e', '#39398d',
    #           '#3f3f17', 'grey2', 'grey25', 'grey40',
    #           '#4d4d89', '#4e4e8a', 'navy',
    #           '#474700', '#2e2e89', '#5c5c11',
    #           '#63638c'
    #           ]

    return random.choice(colour)


def toplevel_bindings(mainloop: tk, topwindow: tk.Toplevel) -> None:
    """
    Keybindings and button bindings for the named Toplevel window.

    :param mainloop: The main tk.Tk() window running the mainloop. Used
        as a passthrough to close_toplevel().
    :param topwindow: Name of the Toplevel window to bind
    """

    # Don't replace with bind_all() b/c not suitable for master window.
    if chk.MY_OS in 'lin, win':
        topwindow.bind('<Button-3>', lambda _: click_cmds(mainloop))
        topwindow.bind('<Control-w>', lambda _: close_toplevel(mainloop))
    elif chk.MY_OS == 'dar':
        topwindow.bind('<Button-2>', lambda _: click_cmds(mainloop))
        topwindow.bind('<Command-w>', lambda _: close_toplevel(mainloop))


def close_toplevel(mainloop: tk.Tk, keybind=None) -> None:
    """
    Close the toplevel window that has focus.
    Called locally from other utils.py functions.
    Used for Command-W or Control-W keybinding or right-click menu.

    :param mainloop: The main tk.Tk() window running the mainloop.
    :param keybind: Implicit bind() events.
    """
    # Based on https://stackoverflow.com/questions/66384144/
    # Need to cover all cases when the focus is on any toplevel window,
    #  or on a child of that window, i.e. .!text or .!frame.
    # There are many children in app and any toplevel window will be
    #   listed at or toward the end, so read children list in reverse
    #   Break loop when the focus toplevel parent is found to prevent all
    #   toplevel windows from closing.
    for widget in reversed(mainloop.winfo_children()):
        # pylint: disable=no-else-break
        if widget == mainloop.focus_get():
            widget.destroy()
            break
        elif '.!text' in str(mainloop.focus_get()):
            parent = str(mainloop.focus_get())[:-6]
            if parent in str(widget):
                widget.destroy()
                break
        elif '.!frame' in str(mainloop.focus_get()):
            parent = str(mainloop.focus_get())[:-7]
            if parent in str(widget):
                widget.destroy()
                break
    return keybind


def click_cmds(mainloop) -> None:
    """An event handler for custom mouse click events.
    """

    def right_click(command: str):
        """
        Sets menu command to the selected text editing action.

        :param command: A Tk predefined virtual event binding across
         multiple platforms. Ex.: 'SelectAll', 'Copy','Paste', 'Cut'.
        See https://www.tcl.tk/man/tcl8.6/TkCmd/event.htm#M7
        """

        # event_generate generates a Tk window event.
        #   See https://www.tcl.tk/man/tcl8.6/TkCmd/event.htm#M7
        mainloop.focus_get().event_generate(f'<<{command}>>')

    right_click_menu = tk.Menu(None, tearoff=0, takefocus=0)

    right_click_menu.add_command(
        label='Select all',
        command=lambda: right_click('SelectAll'))
    right_click_menu.add_command(
        label='Copy',
        command=lambda: right_click('Copy'))
    right_click_menu.add_command(
        label='Paste',
        command=lambda: right_click('Paste'))
    right_click_menu.add_command(
        label='Cut',
        command=lambda: right_click('Cut'))
    right_click_menu.add(tk.SEPARATOR)
    right_click_menu.add_command(label='Bigger font',
                                 command=mainloop.growfont)
    right_click_menu.add_command(label='Smaller font',
                                 command=mainloop.shrinkfont)
    right_click_menu.add_command(label='Default size',
                                 command=mainloop.defaultfontsize)

    # Need to suppress 'Close window' option for master (app) window,
    #   which does not have .!toplevel instances.
    #   Show it only for Toplevel windows and their children.
    if '.!toplevel' in str(mainloop.focus_get()):
        right_click_menu.add(tk.SEPARATOR)
        right_click_menu.add_command(label='Close window',
                                     command=lambda: close_toplevel(mainloop))

    right_click_menu.tk_popup(mainloop.winfo_pointerx(), mainloop.winfo_pointery())


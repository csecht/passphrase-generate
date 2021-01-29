# NOTICE:
As of 29 January 2021, I was not able to download the zipped distribution onto my Windows 10 machine using Microsoft Edge because it said it detected a virus. I had no problem downloading with Firefox browser, but you proceed with caution. Downloads from 28 Jan and earlier did not have this issue.
-------------

# general_utilities
Simple Python scripts and executables to make some things easier.

Developed with Python 3.8, under Ubuntu 20.04, Windows 10, and MacOS 10.13.6 - 11.1
For running the command line versions you may need to download or update to Python 3.6 or later. 
Recent Python packages can be downloaded from https://www.python.org/downloads/.

## pyPassphrase
A potential problem with an on-line password and passphrase generator it is on-line. Here is a command line generator that can be run locally and privately from a Terminal window. The different pass-strings generated are intended to comply with a range of websites and application password/passphrase requirements. 
Suggestions for improvement are welcome, especially any ideas to access the system dictionary on Windows.

### GUI Implementations of pyPassphrase
#### pygPassphrase.py
An interactive graphic window that has more options than the Terminal-only pyPassphrase version. On MacOS and Linux there is an option to create passphrases using the system dictionary, or the Electronic Frontier Foundation's long wordlist. On Windows, only the EFF word list is used (because I don't know how to access the Windows system dictionary.) The script is launched from a Terminal command line. A recent tkinter graphics module of Python is required, which is included in Python 3.7+; earlier versions will require installation of Tk/Tcl.

For Windows, the file eff_large_wordlist.txt, which is included in this distribution, must be kept in the general_utilities-master folder. Launching the program by double-clicking on the folder icon may work if .py is in your PATH list. Otherwise, launch from a Terminal window from the working folder using the command ```python3 pygPassphrase.py``` or ```python pygPassphrase.py``` or ```py pygPassphrase.py```, depending on your system environment. 

For Linux or Mac, the EFF wordlist file also needs to be in the working directory, but its use for generating passphrases is optional. Launch the script from a Terminal window within the general_utilities-master folder using the command 
```python3 ./pygPassphrase.py``` or ```./pygPassphrase.py```  On MacOS, the Python Launcher app, bundled with some Python installations, can be configured to run pygPassphrase.py by double-clicking on it.

### Stand-alone versions ( -- no Python installation needed!)
#### pygPassphrase.app - MacOS
A MacOS implementation of pygPassphrase.py. After downloading the GitHub distribution package (from the Code download button), unzipping the file will generate the general_utilities-master folder. Inside that is zip file, pygPassphrase.app.zip. Unzip that (just double click and follow prompts) to install pygPassphrase.app, which can then be place where ever you like. The first time you double-click on it, however, you will most likely need to go into System Preferences > Security & Privacy > General and allow the app to open (because it was not downloaded from the Apple Store or from a recognized Apple developer). Created with py2app from https://pypi.org/project/py2app/

#### pygPassphrase.exe - Windows
A Windows implementation of pygPassphrase.py. After downloading the GitHub distribution package (from the Code download button), unzipping the file will generate the general_utilities-master folder. That folder contains a pygPassphrase_win folder of distributable files for running the Windows executable, pygPassphrase_win.exe (the .exe extension may not show). Double-click that file to launch, but you will initially need to permit Windows to open it. From the pop-up warning, click on "more info", then follow the prompts to open the program. When the program window opens it will also open a Terminal console window, which can be ignored, although stdout will appear there if something goes wrong with program execution. The pygPassphrase_win folder can be placed anywhere and you may want to create an alias of pygPassphrase.exe to place in a convenient location for easy access. Created with py2exe from https://pypi.org/project/py2exe/

-------------------------

## pyPalindromes
Just something fun. I like the magical way that slice can work to test for and generate palindromes.

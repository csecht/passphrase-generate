# general_utilities
Simple Python scripts to make some things easier.
Developed with Python 3.8, under Ubuntu 20.04, Windows 10, and Mac OS 10.13.6
You may need to download or update to Python 3.6 or later. 
Recent Python packages can be downloaded from https://www.python.org/downloads/.

### pyPassphrase
A potential problem with on-line password and passphrase generators is that they are on-line. Here is a generator that can be run locally and privately. The different strings generated are intended to comply with a range of websites and application password/passphrase requirements. 
Suggestions for improvement are welcome, especially any ideas to implement on Windows.

### pygPassphrase
A GUI implementation of pyPassphrase. Runs on Windows, Linux and MacOS. 
For Windows, the file eff_large_wordlist.txt, which is included with this distribution, must be in the working folder. Launching the program by double-clicking on the folder icon requires that a .py extension be added to the program file.

On Linux or Mac, the eff wordlist file also needs to be in the working directory, but its use for generating passphrases is optional. 

The tkinter graphics module of Python is required, which is included in Python 3.7 and later. Earlier versions will require a separate installation of Tk/Tcl.

### pyPalindromes
Just something fun. I like the magical way that slice can work to test for and generate palindromes.

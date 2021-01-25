# general_utilities
Simple Python scripts to make some things easier.
Developed with Python 3.8, under Ubuntu 20.04, Windows 10, and MacOS 10.13.6 - 11.1
You may need to download or update to Python 3.6 or later. 
Recent Python packages can be downloaded from https://www.python.org/downloads/.

### pyPassphrase
A potential problem with on-line password and passphrase generators is that they are on-line. Here is a generator that can be run locally and privately. The different strings generated are intended to comply with a range of websites and application password/passphrase requirements. 
Suggestions for improvement are welcome, especially any ideas to implement on Windows.

### pygPassphrase.py
A GUI implementation of pyPassphrase.py. Runs on Windows, Linux and MacOS. 
For Windows, the file eff_large_wordlist.txt, which is included with this distribution, must be in the working folder. Launching the program by double-clicking on the folder icon may require add .py to your PATH list. Otherwise, launch from a Terminal window from the working folder using the command 
```python3 ./pygPassphrase.py```. 

On Linux or Mac, the EFF wordlist file also needs to be in the working directory, but its use for generating passphrases is optional. 

The tkinter graphics module of Python is required, which is included in Python 3.7 and later. Earlier versions will require a separate installation of Tk/Tcl.

#### pygPassphrase.app
A standalone MacOS implementation of pygPassphrase.py. After downloading, you will most likely need to go into System Preferences > Security & Privacy > General and allow the app to open because it is not from the Apple Store or an authorized Apple developer. Created with py2app obtained from https://pypi.org/project/py2app/

### pyPalindromes
Just something fun. I like the magical way that slice can work to test for and generate palindromes.

FAQ:

Q: How to build python27.exe and python27.zip ?
A: python pybuild.py -z python27.zip -i python27.ico python27.py

Q: How to build out a standalone python application ?
A: python pybuild.py python27.py

Q: How to reduce python27.zip size ?
A: extract python27.zip, delete some unused packages(email/unitest/unicodedata), then compress it with 7-Zip

Q: How to disassemble python27.exe bytecode ?
A: python -c "import sys,marshal,dis,py2exe.py2exe_util;dis.disassemble(marshal.loads(py2exe.py2exe_util.load_resource(sys.argv[1].decode(sys.getfilesystemencoding()), u'PYTHONSCRIPT', 1)[16:].partition('\x00')[2])[-1])" python27.exe

Q: What is the difference between this fork and origin one?
A: This fork add a feature that the binary will record all IO streams(sys.stdin, sys.stdout, sys.stderr, raw_input()) to a log file while the exe executing a python script.

Q: Are there any tips when I using the binary?
A: DO NOT call "reload(sys)" anywhere in your script, because the log feature base on a monkey patch of source code. 

Q: Can I disable this feature?
A: Why not use the origin one? Here is it: https://github.com/phuslu/pybuild
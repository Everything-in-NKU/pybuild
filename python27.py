#! /usr/bin/env python
"""interactive python prompt with tab completion"""

import sys
import os
sys.path.append(os.path.dirname(getattr(sys, 'executable', sys.argv[0])) or '.')
sys.path.append(os.path.join(sys.path[-1], 'python27.zip'))

# code inspired by bbfreeze
# (https://raw.github.com/schmir/bbfreeze/master/bbfreeze/py.py)

import sys
import zipimport
try:
    import zipextimporter
    zipextimporter.install()
except:
    pass
main = __import__("__main__")

def parse_options(args, spec):
    needarg = dict()

    for x in spec.split():
        if x.endswith("="):
            needarg[x[:-1]] = True
        else:
            needarg[x] = False

    opts = []
    newargs = []

    i = 0
    while i < len(args):
        a, v = (args[i].split("=", 1) + [None])[:2]
        if a in needarg:
            if v is None and needarg[a]:
                i += 1
                try:
                    v = args[i]
                except IndexError:
                    raise Exception("option %s needs an argument" % (a, ))
            opts.append((a, v))
            if a == "-c":
                break
        else:
            break

        i += 1

    newargs.extend(args[i:])
    return opts, newargs

opts, args = parse_options(sys.argv[1:], "-u -h -B -x -c=")
opts = dict(opts)
sys.argv = args
if not sys.argv:
    sys.argv.append("")

if "-h" in opts:
    sys.stdout.write("""
usage: python [option] ... [-c cmd | file | -] [arg] ...
Options and arguments (and corresponding environment variables):
-B     : don't write .py[co] files on import; also PYTHONDONTWRITEBYTECODE=x
-c cmd : program passed in as string (terminates option list)
-h     : print this help message and exit
-u     : unbuffered binary stdout and stderr; also PYTHONUNBUFFERED=x
         see man page for details on internal buffering relating to '-u'
-x     : skip first line of source, allowing use of non-Unix forms of #!cmd
file   : program read from script file
-      : program read from stdin (default; interactive mode if a tty)
arg ...: arguments passed to program in sys.argv[1:]
    """.strip()+os.linesep)
    sys.exit(0)

if "-B" in opts:
    sys.dont_write_bytecode = True

if opts.get("-c") is not None:
    exec opts.get("-c") in main.__dict__
    sys.exit(0)

if sys.argv[0] and os.path.exists(sys.argv[0]):
    if sys.argv[0].endswith('.zip'):
        importer = zipimport.zipimporter(sys.argv[0])
        sys.path.insert(0, sys.argv[0])
        main.__dict__['__file__'] = os.path.abspath(sys.argv[0])
        codeobj = importer.get_code('__main__')
        if codeobj:
            main.__dict__['__file__'] = os.path.join(os.path.abspath(sys.argv[0]), '__main__.py')
            exec codeobj in main.__dict__
    else:
        codeobj = None
        with open(sys.argv[0], 'r') as fp:
            if "-x" in opts:
                fp.readline()
            codeobj = compile(fp.read(), filename=sys.argv[0], mode='exec')
        if codeobj:
            main.__dict__['__file__'] = os.path.abspath(sys.argv[0])
            exec codeobj in main.__dict__
    sys.exit(0)


from code import InteractiveConsole
try:
    # rlcompleter also depends on readline
    import rlcompleter
    import readline
except ImportError:
    readline = None


class PythonConsole(InteractiveConsole):

    def __init__(self, *args, **kwargs):
        self.__class__.__name__ += ' [https://github.com/phus/pybuild]'
        InteractiveConsole.__init__(self, *args, **kwargs)

        if not readline:
            return

        self.completer = rlcompleter.Completer(self.locals)

        readline.set_completer(self.completer.complete)
        # Use tab for completions
        readline.parse_and_bind('tab: complete')
        # This forces readline to automatically print the above list when tab
        # completion is set to 'complete'.
        readline.parse_and_bind('set show-all-if-ambiguous on')
        # Bindings for incremental searches in the history. These searches
        # use the string typed so far on the command line and search
        # anything in the previous input history containing them.
        readline.parse_and_bind('"\C-r": reverse-search-history')
        readline.parse_and_bind('"\C-s": forward-search-history')


if readline:
    import os
    histfile = os.path.expanduser("~/.pyhistory")
    if os.path.exists(histfile):
        readline.read_history_file(histfile)

try:
    PythonConsole(locals={'__file__':sys.argv[0] or getattr(sys, 'frozen', sys.executable), '__name__':'__main__'}).interact()
finally:
    if readline:
        readline.write_history_file(histfile)

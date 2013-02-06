#! /usr/bin/env python
# inspired from https://raw.github.com/schmir/bbfreeze/master/bbfreeze/py.py

import sys
import os
#sys.path.append(os.path.dirname(getattr(sys,'executable',sys.argv[0])) or '.')
import zipimport
try:
    import zipextimporter
    zipextimporter.install()
except:
    pass
main = __import__('__main__')

def parse_options(args, spec):
    needarg = dict()
    for x in spec.split():
        if x.endswith('='):
            needarg[x[:-1]] = True
        else:
            needarg[x] = False
    opts = []
    newargs = []
    i = 0
    while i < len(args):
        a, v = (args[i].split('=', 1) + [None])[:2]
        if a in needarg:
            if v is None and needarg[a]:
                i += 1
                try:
                    v = args[i]
                except IndexError:
                    raise Exception('option %s needs an argument' % (a, ))
            opts.append((a, v))
            if a == '-c':
                break
        else:
            break
        i += 1
    newargs.extend(args[i:])
    return opts, newargs

opts, args = parse_options(sys.argv[1:], '-u -h -B -x -c=')
opts = dict(opts)
sys.argv = args or ['']

if '-B' in opts:
    sys.dont_write_bytecode = True

if '-h' in opts:
    print """
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
    """.strip()
elif opts.get('-c') is not None:
    exec opts.get('-c') in main.__dict__
elif sys.argv[0] and os.path.exists(sys.argv[0]):
    if sys.argv[0].endswith('.zip'):
        importer = zipimport.zipimporter(sys.argv[0])
        sys.path.insert(0, sys.argv[0])
        main.__dict__['__file__'] = os.path.join(os.path.abspath(sys.argv[0]), '__main__.py')
        exec importer.get_code('__main__') in main.__dict__
    else:
        with open(sys.argv[0], 'r') as fp:
            if '-x' in opts:
                fp.readline()
            main.__dict__['__file__'] = os.path.abspath(sys.argv[0])
            exec fp in main.__dict__
else:
    import code
    cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
    code.interact(banner='Python %s on %s\n%s' % (sys.version, sys.platform, cprt))

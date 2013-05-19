#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re
import time
import zipimport
import logging
import getpass
import select
import urllib2
import Queue

__file__ = os.path.abspath(sys.argv[0])


def execfilename(filename):
    if filename.endswith('.py'):
        execfile(filename)
    elif filename.endswith('.zip'):
        sys.path.insert(0, filename)
        exec zipimport.zipimporter(filename).get_code('__main__')
    else:
        raise ValueError('filename=%r is not a valid python file' % filename)


def main():
    mainname = os.path.splitext(os.path.abspath(sys.argv[0]))[0]
    for filename in (mainname+'.zip', mainname+'.py'):
        if os.path.isfile(filename):
            execfilename(filename)
            break


if __name__ == '__main__':
    main()

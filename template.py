#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re
import time
import logging

logging.basicConfig(level=0, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

def main():
    for filename in os.listdir(u'.'):
        logging.info(filename)

if __name__ == '__main__':
    main()


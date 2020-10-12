# -*- coding: utf-8 -*-
# cython: language_level=3

import os
import sys
import subprocess as sp
import re

def adb_file_size(file):
    p = sp.Popen(['adb','shell', 'ls -l '+file], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    output, err = p.communicate()
    output=output.decode('utf-8')
    print(output)
    print(err.decode('utf-8'))
    print(p.poll())
    print('Exit code:', p.returncode)
    if re.findall("^-", output):
        output=output.split()
        print(output)
        size=int(output[3].strip())
    else:
        size=-1
    return size

print(adb_file_size("/rsdcard/"))
    
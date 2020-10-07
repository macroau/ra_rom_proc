# -*- coding: utf-8 -*-
# cython: language_level=3

import os
from xpinyin import Pinyin
import re
import shutil
import sys

def mkdir(dir):
    try:
        os.mkdir(dir)
    except FileExistsError:
        print(dir, " exist!")



def copyfile(src, dest, display=True):
    try:
        shutil.copy(src, dest)
        if display:
            print('.',end="")
            sys.stdout.flush()
    except Exception as e:
        print(e)
        print(src, "->", dest)
        
def filename_ext(filename):
    if "." in filename:
        return (filename.split('.')[-1])
    else:
        return ""
        
def filename_main(filename):
    if "." in filename:
        ext_len=len(filename_ext(filename))
        return filename[:(-ext_len-1)]
    else:
        return filename




def strQ2B(ustring):
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ss

def Q2B(ustring):
    return "".join(strQ2B(ustring))

def add_1st_initial(s):
    if '\r' in s:
        raise ValueError("CR in the string.")
    if '\n' in s:
        raise ValueError("LF in the string.")

    if re.findall('^[0-9a-zA-Z]', s):
        return s
    elif re.findall('^[0-9a-zA-Z]', "".join(strQ2B(s))):
        return s
    else:
        py = Pinyin()
        initial=py.get_initials(s, '')[0]
        return initial + " " + s

def cmd(c, display=False):
    if display:
        print(c)
    r=os.system(c)
    return r
    
def log(s, logfile="log.txt"):
    fp = open(logfile, 'a', encoding='utf-8',newline='\n')
    fp.write(s+"\n")
    fp.close()
    print(s)

#EOF
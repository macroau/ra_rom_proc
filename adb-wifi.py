# -*- coding: utf-8 -*-
# cython: language_level=3

import time
import os
import sys
import re
from lib101 import *

  
print("检查ADB环境")
r=cmd("ADB devices")
if r!=0:
    print("检查ADB环境失败！")
    sys.exit()
    
print("请检查上面是否显示出连接到USB的RP2设备！")
print("如果没有显示出连接的RP2，请关闭窗口后检查连接，然后再试！")    
print("按回车键继续 ...")
input()

cnt=0
files_r = []

print("检测RP2的ip地址 ...")
r=cmd("adb shell \"ifconfig | grep Mask\" > ifconfig.txt")
if r!=0:
    print("检测RP2的ip地址失败！")
    sys.exit()
    
fp=open("ifconfig.txt", 'r')
lines=fp.readlines()
fp.close()
os.remove("ifconfig.txt")
for i in lines:
    ip_info=re.findall('inet addr:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',i)
    ip = ip_info[0].split(":")[1].strip()
    if re.findall("^127", ip):
        continue
    else:
        print("RP2的ip地址是：%s" % ip)
        r=cmd("adb tcpip 5555")
        if r!=0:
            print("打开adb网络接口失败！")
            sys.exit()    
            
        print("现在请拔掉连接RP2的USB线 ...")
        
        time.sleep(3)
        
        print("然后回车继续，以通过wifi连接RP2 ...")
        
        input()
        
        print("请稍后 ...")
        time.sleep(3)
        
        r=cmd("adb connect %s" % ip)
        if r!=0:
            print("连接失败！")
            sys.exit()    
        
        print("请稍后 ...")
        
        time.sleep(3)
        
        r=cmd("adb devices")
        if r!=0:
            print("连接后检测adb连接的设备失败！")
            sys.exit() 
        
        print("请观察上面是否列出通过wifi连接的RP2，如果没有请重来 ...")
        sys.exit() 
print("未检测到RP2的ip地址！")
sys.exit()                  
        
    

#EOF
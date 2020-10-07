# -*- coding: utf-8 -*-
# cython: language_level=3

IN_FILENAME = "MD1.lpl"
DIR = r"\\192.168.99.95\space2t\GameEmu\天马\增量包\Roms-v1.0"
OUT_FILENAME = "tm-test.lpl"
PATH_PREFIX = "/storage/sdcard1/roms101/"
DB_NAME=OUT_FILENAME
META_FILE='metadata.pegasus.txt'
LPL_DIR=r"playlist"

#DEST_ROM_DIR=r'\\192.168.99.95\space2t\GameEmu\天马\增量包\ra'
#DEST_THUMB_DIR=r'\\192.168.99.95\space2t\GameEmu\天马\增量包\th'
DEST_ROM_DIR=r'rom'
DEST_THUMB_DIR=r'thumbnail'

SD_INTL="/storage/sdcard0"
TF_ROOT="/storage/sdcard1"
FONT_FILE="sarasa-ui-sc-regular.ttf"
ADB_PLAYLIST_DIR=SD_INTL+"/RetroArch/playlists"
ADB_ROM_DIR=TF_ROOT+"/roms101"
#ADB_THUMB_DIR=SD_INTL+"/RetroArch/thumbnails"
ADB_THUMB_DIR=TF_ROOT+"/RetroArch/thumbnails"





BB_FILENAME="busybox-armv7l"

import json
import os
#from xpinyin import Pinyin
import sys
import re
#from strQ2B import strQ2B
import shutil
from lib101 import *


#py = Pinyin()
data = {
  "version": "1.4",
  "default_core_path": "",
  "default_core_name": "",
  "label_display_mode": 0,
  "right_thumbnail_mode": 0,
  "left_thumbnail_mode": 0,
  "sort_mode": 0,
  "items": [

  ]
}
item =     {
      "path": "/rsdcard/Roms/NES/1.FC经典游戏/1942 (JU).zip#1942 (JU).NES",
      "label": "1942 (Japan, USA)",
      "core_path": "DETECT",
      "core_name": "DETECT",
      "crc32": "DETECT",
      "db_name": "Sega MD - p.lpl"
    }
  
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


print("ROM包的分类")
print("-----------------------")
dirs=os.listdir(LPL_DIR)
lpl_files=[]
for i in dirs:
    if os.path.isfile(LPL_DIR+os.sep+i) and i[-4:]==".lpl":
        lpl_files.append(i)

n=0
for i in lpl_files:
    print("%d --- %s" %(n, filename_main(i)))
    
    n+=1
    
print(n, "--- 全部")

print("选择要删除的ROM包分类，输入数字后回车继续：")
while True:
    userinput=input()
    if userinput.isdigit():
        break

userinput=int(userinput)
if userinput>=len(lpl_files):
    trans_list=lpl_files
else:
    trans_list=[]
    trans_list.append(lpl_files[userinput])

print('ADB ROOT ...')
cmd('adb root')
cmd('adb remount')

print('安装BusyBox ...')
cmd("adb push %s /system/xbin/busybox" % BB_FILENAME)
cmd("adb shell chmod a+x /system/xbin/busybox")

cmd("adb push %s %s/" % (FONT_FILE, SD_INTL))

for i in trans_list:
    PLAYLIST_FILE = i
    MACHINE_NAME = filename_main(i)
    print()
    print('##### 即将删除 %s 分类的ROM包 #####' % MACHINE_NAME)
    
    ROM_PACK = MACHINE_NAME+'.tar.gz'
    THUMB_PACK = MACHINE_NAME+'.tar.gz'

    print(" *** 正在删除playlist文件，请稍后 ...")
    cmd('adb shell rm %s/\'%s\'' % (ADB_PLAYLIST_DIR, PLAYLIST_FILE))

    print(" *** 正在删除ROM包，请稍后 ...")
    cmd('adb shell "rm -rf %s/\'%s\'"' % (ADB_ROM_DIR, MACHINE_NAME))

    print(" *** 正在删除缩略图，请稍后 ...")
    cmd('adb shell "rm -rf %s/\'%s\'"' % (ADB_THUMB_DIR, MACHINE_NAME))
    print()

print()
cmd('adb shell mount -o ro,remount /system')
cmd('adb unroot')
print('所有工作已完成！请关闭RA后重新打开。')    
print()
sys.exit()


#EOF
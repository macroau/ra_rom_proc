# -*- coding: utf-8 -*-
# cython: language_level=3

IN_FILENAME = "MD1.lpl"
DIR = r"\\192.168.99.95\space2t\GameEmu\天马\增量包\Roms-v1.0"
OUT_FILENAME = "tm-test.lpl"
PATH_PREFIX = "/storage/sdcard1/roms101/"
DB_NAME=OUT_FILENAME
META_FILE='metadata.pegasus.txt'
LPL_DIR=r"\\192.168.99.95\space2t\GameEmu\天马\增量包\lpl"

DEST_ROM_DIR=r'\\192.168.99.95\space2t\GameEmu\天马\增量包\ra'
DEST_THUMB_DIR=r'\\192.168.99.95\space2t\GameEmu\天马\增量包\th'

import json
import os
from xpinyin import Pinyin
import sys
import re
from strQ2B import strQ2B
import shutil
from lib101 import *
from lib201 import *


py = Pinyin()
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
    
cnt=0
files_r = []


def count_rom(dir):
    meta_fp=open(DIR+os.sep+dir+os.sep+META_FILE, 'r', encoding='utf-8')
    cnt = 0
    for l in meta_fp.readlines():
        if re.findall("^game:", l):
            cnt+=1
    meta_fp.close()
    return cnt



for i in os.listdir(DIR):
    if not os.path.isdir(DIR+os.sep+i):
        continue
        
    if not os.path.isfile(DIR+os.sep+i+os.sep+META_FILE):
        continue
        
    rom_num=count_rom(i)
    log("%s    %d" % (i, rom_num))
    
    meta_fp=open(DIR+os.sep+i+os.sep+META_FILE, 'r', encoding='utf-8')
    game_name=""
    type_name=i+"-TM"+str(rom_num)
    db_name=type_name+".lpl"
    type_cnt=0
    
    type_rom_dir=DEST_ROM_DIR+os.sep+type_name
    mkdir(DEST_ROM_DIR+os.sep+type_name)
        
    type_th_dir=DEST_THUMB_DIR+os.sep+type_name
    mkdir(type_th_dir)
    
    
    mkdir(type_th_dir+os.sep+'Named_Boxarts')
    mkdir(type_th_dir+os.sep+'Named_Titles')

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
    
    for l in meta_fp.readlines():
        l=l.strip()



        if game_name=="":
            if re.findall("^game", l):
                game_name="".join(l.split(":")[1:]).strip()
                game_name= add_1st_initial(game_name)
                
            else:
                game_name=""
                file_name=""
                continue
        else:
            if re.findall("^file", l):
                file_name="".join(l.split(":")[1:]).strip()
                log("%s  :  %s" % (game_name, file_name))

                item["path"]=PATH_PREFIX+type_name+"/"+file_name
                item["label"]=game_name
                item["db_name"]=db_name
                data["items"].append(item.copy())  

                print('.',end="")
                sys.stdout.flush()                
                copyfile(DIR+os.sep+i+os.sep+file_name, type_rom_dir)

                    
                    
                
                media_dir=DIR+os.sep+i+os.sep+"media" +os.sep    +"".join(file_name.split('.')[:-1])
                
                box=media_dir+os.sep+"boxFront"
                #print(box)
                
                logo=media_dir+os.sep+"logo"

                print('.',end="")
                sys.stdout.flush()
                if os.path.isfile(box+'.jpg'):
                    #copyfile(box+'.jpg', type_th_dir+os.sep+'Named_Boxarts'+os.sep+game_name+'.jpg')
                    pil_conv_img(box+'.jpg', type_th_dir+os.sep+'Named_Boxarts'+os.sep+game_name+'.png')
                elif os.path.isfile(box+'.png'):
                    copyfile(box+'.png', type_th_dir+os.sep+'Named_Boxarts'+os.sep+game_name+'.png')
                else:
                    print("no box: ", box)
                        
                print('.',end="")
                sys.stdout.flush()
                if os.path.isfile(logo+'.jpg'):
                    #copyfile(logo+'.jpg', type_th_dir+os.sep+'Named_Boxarts'+os.sep+game_name+box[-4:])
                    pil_conv_img(logo+'.jpg', type_th_dir+os.sep+'Named_Titles'+os.sep+game_name+'.png')
                elif os.path.isfile(logo+'.png'):
                    copyfile(logo+'.png', type_th_dir+os.sep+'Named_Titles'+os.sep+game_name+'.png')  
                else:
                    print("no logo: ", logo)       
                
                
    
                

                
                game_name=""
                file_name=""
                type_cnt+=1
                cnt+=1                
            else:
                continue
    print("       ",type_cnt)
        
    meta_fp.close()
    data2 = json.dumps(data, ensure_ascii=False, indent=2)
    fp2 = open(LPL_DIR+os.sep+type_name+".lpl", 'w', encoding='utf-8',newline='\n')
    fp2.write(data2)
    fp2.close()      
        
print("Total: ",cnt)
sys.exit()
        
    
    


'''
for i in files:
    os.rename(DIR+os.sep+i, DIR+ os.sep + "".join(strQ2B(i)))
    cnt+=1
print(cnt)

sys.exit()
'''


#fp1=open(OUT_FILENAME, 'w', encoding='utf-8', newline='\n')


for i in files:
    #files_r.append(py.get_initials(i,'')[0] + ' ' + i)
    n = 0
    
    while True:
        if re.findall('^[0-9]', i[n:]):
            n+=1
        else:
            if n>0:
                n+=1
            break
    
    name= py.get_initials(i[n:-4],'')[0] + " " + i[n:-4]
    '''
    if re.findall("^[0-9a-zA-Z]", i):
        name=i[n:-4]
    else:
        name= py.get_initials(i,'')[0] + " " + i[n:-4]
    '''
    print(name)
    item["path"]=PATH_PREFIX+i
    item["label"]=name
    item["db_name"]=DB_NAME
    data["items"].append(item.copy())
    cnt+=1
print(cnt)
            
data2 = json.dumps(data, ensure_ascii=False, indent=2)
fp2 = open(OUT_FILENAME, 'w', encoding='utf-8',newline='\n')
fp2.write(data2)
fp2.close()       
        
    #if not re.findall('^[a-zA-Z0-9]',i):
    #    os.rename(DIR+os.sep+i, DIR+os.sep+py.get_initials(i,'')[0] + ' ' + i)

sys.exit()

files = os.listdir(DIR)


fp1=open(OUT_FILENAME, 'w', encoding='utf-8', newline='\n')



for i in files:
    if i[-3:]!='zip':
        continue
    cnt+=1
    name = i[:-4].strip()
    fp1.write(PATH_PREFIX + i + '\n')
    print(name)
    fp1.write(name + '\n')
    fp1.write("/data/data/com.gpsp/cores/gpsp_libretro_android.so\n")
    fp1.write("gpSP\n")
    fp1.write("\n\n")

fp1.close()
    
    
print(cnt)    

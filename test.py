# -*- coding: utf-8 -*-
# cython: language_level=3
# + the line above is needed for Cython. 
# + ref to https://cython.readthedocs.io/en/stable/src/reference/compilation.html#compiler-directives

# Only tested on Windows 10 platform

import configparser
import asyncio
import time
#from bleak import BleakScanner
#from bleak import BleakClient
#from bleak import discover
#import bleak
import msvcrt
import sys
import re
#from colorama import init, Fore, Back, Style
#init(autoreset=False)    # init and disable autoreset the colorama color setting

REV = "R20200925"

BTNAME_PREFIX   = "Hi-06B-12ARA00"

mac_addr = "CC:50:E3:98:4C:B6"
address = "CC:50:E3:98:4C:B6"

TEST = 0
if TEST:
    MODEL_NBR_UUID  = "57f18e22-5eb7-4b81-9398-e71b399cb189"
    SERVICE_UUID    = "da4ba3a4-4260-4426-b874-697ef03bcf4a"
    CHARACTERISTIC_UUID         = MODEL_NBR_UUID
    NOTIFY_CHARACTERISTIC_UUID  = MODEL_NBR_UUID
else:
    SERVICE_UUID                = "0000fff0-0000-1000-8000-00805f9b34fb"
    MODEL_NBR_UUID              = "0000fff2-0000-1000-8000-00805f9b34fb"
    CHARACTERISTIC_UUID         =  MODEL_NBR_UUID
    NOTIFY_CHARACTERISTIC_UUID  = "0000fff1-0000-1000-8000-00805f9b34fb"

DevList     = []
HiDevList   = []

CHARGE_STATUS = ['NO CHARGE', 'CHARGING', 'FINISH']
TIME_DELAY_MENU = 1
char_list={}

client_global   = ""
AUTO_REPLY66    = True
REPLY66_FLAG    = False
cnt_send        = 1
cnt_get         = 1
ble_connected   = False

CONFIG_INI = 'config.ini'

cf = configparser.ConfigParser()
cf.read(CONFIG_INI)
AUTO_REPLY66 = True if cf.get('blescan','auto_reply66')=='1' else False 
discover_time = cf.get('blescan','discover_time')
print(discover_time)

sys.exit()

# "303132" => "012" or "\x30\x31\x32"
def hexstr2str(data):
    r_str = ''.join(chr(int(data[i:i+2], 16)) for i in range(0, len(data), 2))
    return r_str

# "303132" => b"012" or b"\x30\x31\x32"
def hexstr2bstr(data):
    r_str = b''.join((int(data[i:i+2], 16)).to_bytes(1, "little") for i in range(0, len(data), 2))
    return r_str

# "\x30\x31\x32" => "30:31:32"
def str2hexwsep(data, sep=":"):
    r_str = sep.join("{:02x}".format(ord(c)) for c in data)
    return r_str

# b"\x30\x31\x32" => "30:31:32"    or
# bytearray(b"\x30\x31\x32") => "30:31:32"
def bstr2hexwsep(data,sep=":"):
    r_str = sep.join("{:02x}".format(c) for c in data)
    return r_str

def take2(elem):
    return elem[2]
    
def keypress():
    if msvcrt.kbhit():
        return msvcrt.getch()
    else:
        return ""

def clear_kbhit():
    while msvcrt.kbhit():
        msvcrt.getch()

def now_time():
    return time.strftime('[%H:%M:%S]')
        
def notification_handler(sender, data):
    global client_global
    global AUTO_REPLY66
    global REPLY66_FLAG
    global cnt_get
    
    """Simple notification handler which prints the data received."""
    print(Style.BRIGHT + Fore.YELLOW + "{0} ({1}) Get from {2}: \n---------- [{3}] ({4} bytes)  <- ".format(now_time(), cnt_get, char_list[sender], bstr2hexwsep(data), len(data)))
    cnt_get += 1

    if len(data)==12 and data[0]==0x11:
        print("Cup Temp:    %d" % data[1])
        print("PCB Temp:    %d" % data[2])
        print("Disp Temp:   %d" % data[3])
        print("Cap Open:    %d" % data[4])
        print("Err code:    %d" % data[5])
        print("Fw ver:      %d" % data[6])
        print("Strge time:  %d" % data[7])
        print("Lst50time:   %d" % data[8])
        print("Lst50Temp:   %d" % data[9])
        print("Battery Lvl: %d" % data[10])
        print("Charging:    %d      [%s]" % (data[11], CHARGE_STATUS[data[11]]))

    elif len(data)==15 and data[0]==0x12:
        print("Today drinks:    %d" % ((data[1]<<8) + data[2]))   # 注意运算优先级
        print("-1 day drinks:   %d" % ((data[3]<<8) + data[4]))
        print("-2 day drinks:   %d" % ((data[5]<<8) + data[6]))
        print("-3 day drinks:   %d" % ((data[7]<<8) + data[8]))
        print("-4 day drinks:   %d" % ((data[9]<<8) + data[10]))
        print("-5 day drinks:   %d" % ((data[11]<<8) + data[12]))
        print("-6 day drinks:   %d" % ((data[13]<<8) + data[14]))

    elif len(data)==8 and data[0]==0x16:
        print("Today temp:      %d" % (data[1]))
        print("-1 day temp:     %d" % (data[2]))
        print("-2 day temp:     %d" % (data[3]))
        print("-3 day temp:     %d" % (data[4]))
        print("-4 day temp:     %d" % (data[5]))
        print("-5 day temp:     %d" % (data[6]))
        print("-6 day temp:     %d" % (data[7]))
        
    elif len(data)==6 and data[0]==0x66:
        print("Disp Temp:   %d" % data[1])
        print("Cup Open:    %d" % data[2])
        print("Storg Time:  %d" % data[3])
        print("Battery Lvl: %d" % data[4])
        print("Chargin:     %d      [%s]" % (data[5], CHARGE_STATUS[data[5]]))
        if AUTO_REPLY66:
            print("[INFO] Will reply 0x66 automatically.")
            REPLY66_FLAG = True

    elif len(data)==3 and (data[0]==0x13 or data[0]==0x15):
        print("Hour:   %d" % data[1])
        print("Min:    %d" % data[2])

    print(Style.RESET_ALL, end="")

async def run():
    print("BLE Scan test " + REV)
    print("===================================")
    print(Style.BRIGHT + Fore.BLUE + Back.WHITE + ("Search BLE devices in %d s." % discover_time) + Style.RESET_ALL)
    print("===================================")
    #devices = await discover(discover_time)
    devices = await BleakScanner.discover(discover_time)

    print(Style.BRIGHT + Fore.BLUE + Back.WHITE + "Devices found" + Style.RESET_ALL)
    print("===================================")

    for d in devices:
        print(d.address, d.rssi, d.name, d.metadata)
        DevList.append((d.address, d.name, d.rssi))

loop = asyncio.get_event_loop()
loop.run_until_complete(run())

if len(DevList)<1:
    print(Style.BRIGHT + Fore.YELLOW + Back.RED + "No BLE devices found!" + Style.RESET_ALL)
    sys.exit(1)

print("===================================")
print(Style.BRIGHT + Fore.BLUE + Back.WHITE + "Sorted acc. to RSSI" + Style.RESET_ALL)
print("===================================")
DevList.sort(key=take2, reverse=True)   # 按rssi值由强到弱排序
for d in DevList:
    print(d)
    if d[1].find(BTNAME_PREFIX) == 0 and len(d[1]) == 18:
        HiDevList.append(d)


print("===================================")
print(Style.BRIGHT + Fore.BLUE + Back.WHITE + "HiLink Devices" + Style.RESET_ALL)
print("===================================")
for d in HiDevList:
    if d==HiDevList[0]:
        print(Style.BRIGHT + Fore.CYAN, end="")
    print(d)
    print(Style.RESET_ALL, end="")
    
if len(HiDevList)<1:
    print(Style.BRIGHT + Fore.YELLOW + Back.RED + "No HiLink devices found!" + Style.RESET_ALL)
    sys.exit(1)
    
mac_addr = HiDevList[0][0]
address = mac_addr

# connect
print("===================================")
print("Will connect HiLink Device with highest RSSI")

# Send func.
async def send_ble(client, data):
    global cnt_send
    print(Style.BRIGHT + Fore.GREEN + "%s (%d) Send to %s: \n---------- [%s] (%d bytes) ->" % (now_time(), cnt_send, MODEL_NBR_UUID, bstr2hexwsep(data), len(data)))
    print(Style.RESET_ALL, end="")
    await client.write_gatt_char(MODEL_NBR_UUID, data, response = False)
    cnt_send += 1

# disc. callback
disconnected_event = asyncio.Event()

def disconnected_callback(client):
    print(Style.BRIGHT + Fore.YELLOW + Back.RED + "Hi-Link device disconnected!\nPlease close the window." + Style.RESET_ALL)

    disconnected_event.set()

# Main Loop
async def run(address):
    global client_global
    global AUTO_REPLY66
    global REPLY66_FLAG
    global ble_connected

    #async with BleakClient(address, loop=loop, disconnected_callback=disconnected_callback) as client:
    
    client = BleakClient(address)
    retry = 0
    while retry < 20:
        try:
            print("Connecting ...")
            await client.connect()
            print("Connected!")
            break
        except bleak.exc.BleakError as e:
            print(e)
            retry += 1
            print("Will retry connecting ... %d" % retry)
            
    if retry>0:
        print(Style.BRIGHT + Fore.RED + ("Tried connecting %d times!" % (retry + 1)) + Style.RESET_ALL)
            
    ble_connected = await client.is_connected()
    if not ble_connected:
        print(Style.BRIGHT + Fore.YELLOW + Back.RED + "Connecting failed!" + Style.RESET_ALL)
        return False
    
    ble_connected = await client.is_connected()
    if not ble_connected:
        return False

    client_global = client

    print("===================================")
    print("HiLink device connected [%s]" % address)
    print("===================================")

    client.set_disconnected_callback(disconnected_callback)

    for service in client.services:
        #log.info("[Service] {0}: {1}".format(service.uuid, service.description))
        for char in service.characteristics:
            char_list[char.handle] = char.uuid
            #print(char.handle, char_list[char.handle])
            
    # model_number = await client.read_gatt_char(NOTIFY_CHARACTERISTIC_UUID)
    #print("Model Number: {0}".format("".join(map(chr, model_number))))
    # print("Read and get: [%s] (%d bytes) <= " % (bstr2hexwsep(model_number), len(model_number)))

    #await client.write_gatt_char(MODEL_NBR_UUID, b"\x02\x30", response = False)

    #await client.write_gatt_char(s.services[SERVICE_UUID].get_characteristic(MODEL_NBR_UUID).handle + 1, b"\x01\x00", True)
    #await client.write_gatt_descriptor(43, b"\x01\x00")

    # await client.start_notify(NOTIFY_CHARACTERISTIC_UUID, notification_handler)

    # print("Automatically send the Legal client message...")
    # await send_ble(client, b"\x55")
    # await asyncio.sleep(1.0)

    print("========================================")
    print(" Print all Services and Characteristics")
    print("========================================")
    
    for service in client.services:
        print("[Service] {0}: {1}".format(service.uuid, service.description))
        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = bytes(await client.read_gatt_char(char.uuid))
                except Exception as e:
                    value = str(e).encode()
            else:
                value = None
            print(
                "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                    char.uuid,
                    char.handle,
                    ",".join(char.properties),
                    char.description,
                    value,
                )
            )
            for descriptor in char.descriptors:
                value = await client.read_gatt_descriptor(descriptor.handle)
                print(
                    "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                        descriptor.uuid, descriptor.handle, bytes(value)
                    )
                )
    print()
    print()
    print()
    
    cnt = 99
    while cnt:

        if cnt<30:
            print("# %d rounds remains. #" % cnt)
        
        #model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        #print(model_number)
        #await client.write_gatt_char(MODEL_NBR_UUID, b"\x02\x30", response = False)
        #await asyncio.sleep(10.0, loop=loop)


        print("______________________________________________________________ " + REV)
        print(Style.BRIGHT + Fore.CYAN, end="")
        print("1. Check 0x11;   2. Check 0x12;      3. Set time;    4. Check time;")
        print("5. Send 0x55;    6. Check Avg Temp;  7. Reply 0x66;")
        print("8. Find the cup; 9. Manually input;  e. Disconnect and Exit; ")
        print("p. Options;")
        print(Style.RESET_ALL, end="")
        print("------------------------------------------------------------------------")
        print("Type your choice: ")
        clear_kbhit()
        user_key = ""
        while not re.match("[0-9\sEP]", user_key):
            #user_key = chr(msvcrt.getche()[0])
            
            if REPLY66_FLAG:                    # automatically send 0x66
                REPLY66_FLAG = False
                await send_ble(client, b"\x66")     
                await asyncio.sleep(0.5)                  
                
            await asyncio.sleep(0.2)        # change the above to this in order to 
            user_key=keypress().upper()     # allow the notification while waiting for input
            user_key=chr(user_key[0]) if len(user_key)>0 else ""

        print(user_key)
        print()

        if user_key=="1":
            await send_ble(client, b"\x01\x55\x00\x00\x00\x00\x32\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x00\x00")
            await asyncio.sleep(1.0)     

        elif user_key=="2":       
            await send_ble(client, b"\x12")
            await asyncio.sleep(1.0)
            
        elif user_key=="3":     
            print("Input the time:  [HHmm]")
            set_time = input()
            if len(set_time)==4 and set_time.isdigit():
                hour = int(set_time[0:2])
                minute = int(set_time[2:])
                
                if hour>24:
                    hour=24
                elif hour<0:
                    hour=0

                hour=hour.to_bytes(1,'little')
                
                if minute>59:
                    minute=59
                elif minute<0:
                    minute=0

                minute=minute.to_bytes(1,'little')

                await send_ble(client, b"\x13"+hour+minute)
                await asyncio.sleep(1.0)
            else:
                print("Illegal time value!")
                
        elif user_key=="4":        # Check time

            await send_ble(client, b"\x15")
            await asyncio.sleep(1.0)

        elif user_key=="5":    

            await send_ble(client, b"\x55")
            await asyncio.sleep(1.0)

        elif user_key=="6":       
            await send_ble(client, b"\x16")
            await asyncio.sleep(1.0)

        elif user_key=="7":    

            await send_ble(client, b"\x66")
            await asyncio.sleep(1.0)

        elif user_key=="8":    

            await send_ble(client, b"\x22")
            await asyncio.sleep(1.0)

        elif user_key=="9":     
            print("Input the command:  [AABBCCDD...]")
            cmd = input().upper()
            if len(cmd)<2 or len(cmd)/2!=int(len(cmd)/2):
                print("Wrong HEX string length!")
                
            elif not re.match("^[0-9a-fA-F]+$", cmd):
                print("Wrong HEX string! non-[0-9A-F] char exist.")

            else:
                await send_ble(client, hexstr2bstr(cmd))
                await asyncio.sleep(1.0)

        elif user_key=="E":        # Exit, uppercase
            break

        elif user_key=="P":        # Options, uppercase
            print("Auto reply 0x66 ?  (y/[N]) ")
            cmd = input().upper()
            if cmd=="Y":
                print(Style.BRIGHT + Fore.GREEN + "[Enable] auto reply 0x66." + Style.RESET_ALL)
                AUTO_REPLY66 = True
            else:
                print(Style.BRIGHT + Fore.RED + "[Disable] auto reply 0x66." + Style.RESET_ALL)
                AUTO_REPLY66 = False
                
            temp_ini = '1' if AUTO_REPLY66 else '0'
            cf.set('blescan', 'auto_reply66', temp_ini)
            cf.write(open(CONFIG_INI, 'w'))
            
        elif user_key==" ":        # SPACE, 跳回菜单
            continue

        time_delay = TIME_DELAY_MENU
        print("\nWill continue in %d s.   Press Ctrl+C to break, or SPACE to jump the delay." % time_delay)
        for i in range(0, time_delay):
            await asyncio.sleep(1)
            print(".", end="")
            sys.stdout.flush()      # 刷新上一个语句的输出

            if keypress()==b" ":    # 按 空格 可以跳过
                break
                
        print("\n")
        
        #cnt-=1     # comment out for loop forever

    await client.stop_notify(NOTIFY_CHARACTERISTIC_UUID)
    await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))

print("Press Enter to Exit...")
input()
# EOF
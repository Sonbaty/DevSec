from ast import And
from sqlite3 import connect
import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import pathlib
import os
import re


devices_file = open("cisco_devices.txt", 'r')  ## open the ip list file from root folder
Location = input('Enter The Switches Group Name First : ')
devices_file.seek(0)  ## put the first read on the begining
ip_list = devices_file.read().splitlines()  ## splite the ip's in a list
devices_file.close()
initial = 'Cisco'


def get_info(IP,any):
    switch = {
                    'device_type': 'cisco_ios_telnet',   ## For Cisco Telnet
                    'ip': IP,
                    #'username': '',           ##blank if no username
                    'password': 'Coral@sts123',   #telnet Pass
                    'secret': 'Coral@sts123',        ## Enable Pass
                    'global_delay_factor': 2,
        }

    connection = ConnectHandler(**switch)
    connection.conn_timeout = 10
    print('Connecting to ' + IP)
    print('-' * 79)
    print('waiting For Authentication ...')
    output = connection.send_command('sh version')
    print(output)
    print()
    print('-' * 79)
    connection.enable()

    device = connection.send_command('show run | i hostname')
    if device == "":
        device = "no_hostname"
        print('Notice : This switch has no hostname configured')
 
    print(f'Operating {device}')
    my_ip = IP.strip('\n')

    if not os.path.exists(Location):
        os.mkdir(Location)
        print("Directory ", Location, " Created ")
    else:
        print("Directory ", Location, " already exists")

    # filename = '/home/sonbaty/Automation/backups/' + device + '.txt'
    filename = f'{Location}/{device}-IP[{my_ip}]'+ '.txt'

    sw_uptime_query = connection.send_command('show version | i uptime')
    port_query = connection.send_command('sh ip int br')
    ou_List = port_query.splitlines()
    Nei_List = ou_List[1:]
    interface_list = []
    for line in Nei_List:
        int_line = str(line).split()
        interface = int_line[0]
        if (("FastEthernet" or "GigabitEthernet") and "/")in interface:
            interface_list.append(interface)
    
    sw_identifier = f'IP:{my_ip}, Host:{device}'
    #filename = initial + my_ip
    log_file = open(filename, "a")  # append mode
    log_file.write(sw_identifier)
    log_file.write("\n")
    log_file.write(sw_uptime_query)
    log_file.write("\n")
    for interface in interface_list:
        print(f'Checking port {interface} , Switch {device}')
        connection.enable()
        port_errors = connection.send_command(f'sh interfaces {interface} | i errors')  
        log_file.write(f'{interface} ----> : ' )
        log_file.write("\n")
        log_file.write(port_errors)
        log_file.write("\n")      

    connection.disconnect()
    print(f'{device} done ..')
    return



if __name__ == "__main__":
    que = Queue()

    def start():
        threads = []
        for ip in ip_list:
            # Test using sleep delays between devices to wait for writing outputs to text file in order
            try:
                t1 = threading.Thread(target=get_info, args=(ip, que))
                t1.start()
                threads.append(t1)
            except BaseException as e:
                continue
        for t in threads:
            t.join()
    start()


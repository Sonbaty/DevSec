import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import pathlib
import os
import re

print("Intiazing")
initials = 'vl_conf_details of '
devices_file = open("cisco_devices.txt")  ## open the ip list file from root folder
devices_file.seek(0)  ## put the first read on the begining
ip_list = devices_file.read().splitlines()  ## splite the ip's in a list
devices_file.close()


def conf_vlan(IP,any):
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
    print(f'Waiting For Authentication On IP :{IP} ...')
    output = connection.send_command('sh version')
    print('-' * 79)
    connection.enable()
    device = connection.send_command('show run | i hostname')
    print(f'Successful Connection to {IP} / {device}')
    my_ip = IP.strip('\n')
    connection.enable()
    device = connection.send_command('show run | i hostname')
    print(f'Detecting {my_ip} POE Cabapility........... ')
    poe_query_raw = connection.send_command('sh power inline | i Available')
    poe_query_1 = poe_query_raw.split(None, 1)[0]
    availabe, poe_value = poe_query_1.split(':')
    print(poe_value)
    if poe_value == '0.0(w)':
        print(f'Switch {my_ip} Is Not POE')
    else:
        print(f'Switch: {my_ip} is POE cabaple with budget of: {poe_value}')
        show_int = connection.send_command('sh interfaces trunk | i ^Fa.*116 ')
        ou_List = show_int.splitlines()
        int_list = ou_List[5:]   #delete unnecessary in fo and pop last line

        print(f'Query The Device IP: {IP}')
        print('Found The Following APs : ')
        vlan_116 = []

        for line in int_list:
        # interfaces_list = str(line).split(' ')
            interfaces_list = re.split(r'\s{2,}',line)
            InterfaceNum = interfaces_list[0]
            vlan_116.append(InterfaceNum)
        print(vlan_116)


if __name__ == "__main__":
    que = Queue()

    def start():
        threads = []
        for ip in ip_list:
            # Test using sleep delays between devices to wait for writing outputs to text file in order
            try:
                t1 = threading.Thread(target=conf_vlan, args=(ip, que))
                t1.start()
                threads.append(t1)
            except BaseException as e:
                continue
        for t in threads:
            t.join()
            print('Waiting For all switches to finish')
    start()

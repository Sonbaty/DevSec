from ast import And
import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import pathlib
import os
import re


# open the ip list file from root folder
devices_file = open("concord_scan.txt")
devices_file.seek(0)  # put the first read on the begining
ip_list = devices_file.read().splitlines()  # splite the ip's in a list
print(ip_list)
devices_file.close()
initial = 'HP'


def get_info(IP, any):
    switch = {
        'device_type': 'ruckus_fastiron_telnet',
        'ip': IP,
        'password': 'letmein',  # telnet Pass
        'secret': 'letmein',  # Enable Pass

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

    hostname = connection.send_command('show run | i hostname')
    hostname.split(" ")
    if hostname == "":
        device = "no_hostname"
        print('Notice : This switch has no hostname configured')
    else:
        hostname, device = hostname.split(" ")
    print(f'Operating {device}')
    my_ip = IP.strip('\n')

    sw_query = connection.send_command('show version | i SW')
    sw_uptime_query = connection.send_command('show version | i uptime')
    port_query = connection.send_command('sh int br')
    ou_List = port_query.splitlines()
    Nei_List = ou_List[1:]
    interface_list = []
    for line in Nei_List:
        int_line = str(line).split()
        interface = int_line[0]
        interface_list.append(interface)

    #sw_identifier = f'IP:{my_ip}, Host:{device}'
    for interface in interface_list:
        if '1/' in interface:
            connection.send_command(f'clear statistics ethernet {interface}')
            print(f'Resetting stats for ethernet {interface}')

    print(f'All ports on {device} is cleared..')
    connection.disconnect()
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
            print('Waiting For all switches to finish')

    start()

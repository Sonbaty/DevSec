from ast import And
import string
import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import pathlib
import os
import re


devices_file = open("test_dev.txt")  ## open the ip list file from root folder
devices_file.seek(0)  ## put the first read on the begining
ip_list = devices_file.read().splitlines()  ## splite the ip's in a list
print(ip_list)
devices_file.close()
initial = 'HP'


def get_info(IP,any):
    switch = {
            'device_type': 'ruckus_fastiron',
            'ip': IP,
            'username': 'super',
            'password': 'C0nc0rde'

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
    print(device)
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
    sw_identifier = f'IP:{my_ip}, Host:{device}'
    filename = initial + my_ip
    log_file = open(filename, "a")  # append mode
    log_file.write(sw_identifier)
    log_file.write("\n")
    log_file.write(sw_query)
    log_file.write("\n")
    log_file.write(sw_uptime_query)
    log_file.write("\n")
    
    for interface in interface_list:
        if "1/1/" in interface:
            print(f"Operating Port Eth {interface}")
            neighbor_mac_raw = connection.send_command(f'sh lldp neighbors detail ports ethernet {interface} | i Neighbor')
<<<<<<< HEAD
            if "+" in neighbor_mac_raw:
                query_identifier , neighbor_mac_ping = neighbor_mac_raw.split(":")
                neighbor_mac , ping = neighbor_mac_ping.split(",")
            neighbor_hostname_raw = connection.send_command(f'sh lldp neighbors detail ports ethernet {interface} | i System name')
            if "+" in neighbor_hostname_raw:
               qu_id, neighbor_hostname  = neighbor_hostname_raw.split(",")
=======
            query_identifier , neighbor_mac_ping = neighbor_mac_raw.split(":")
            neighbor_mac , ping = neighbor_mac_ping.split(",")

            neighbor_hostname = connection.send_command(f'sh lldp neighbors detail ports ethernet {interface} | i System name')
>>>>>>> fc8a1bcd2e4e6698f18cdf6443b9708c53e1fc3a
            log_file.write(f'Interface : Ethernet {interface}')
            log_file.write("\n")
            log_file.write(f'Attached Device MAC : {neighbor_mac} ')
            log_file.write("\n")
            log_file.write(f'Attached Device Hostname{neighbor_hostname} ')
            log_file.write("\n")

    connection.disconnect()
    return

def finalize():
    print('finalizing ...............')
    Path = str(pathlib.Path().resolve())
    print(Path)
    operated_file = open('Port_map.txt','a')
    filelist = os.listdir()
    for i in filelist:
        if i.startswith(initial):
            with open(Path + f'/{i}', 'r') as f:
                print(i)
                for line in f:
                    operated_file.write(line)
                os.remove(i)
            operated_file.write('\n')
            operated_file.write('-' * 79)
            operated_file.write('\n')


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
    finalize()
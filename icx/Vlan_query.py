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
    vlan_list = []
    def interface_type(q_lines):
        vlan_interfaces = []
        for line in q_lines:
            print(line)
            if 'M1' in line:
                for w in line.split():
                    if w.isdigit():
                        vlan_interfaces.append(f' 1/1/{int(w)}')
            elif 'M2' in line:
                for w in line.split():
                    if w.isdigit():
                        vlan_interfaces.append(f' 1/2/{int(w)}')
            elif 'M3' in line:
                for w in line.split():
                    if w.isdigit():
                        vlan_interfaces.append(f' 1/3/{int(w)}')
        return vlan_interfaces
    vlan_query = connection.send_command('sh vlan | i PORT-VLAN [0-9]')
    vl_q1 = vlan_query.splitlines()
    vl_list =vl_q1[1:]
    for line in vl_list:
        vl_line = str(line).split(' ')
        vlan = vl_line[1]
        vlan = vlan.replace(',','')
        vlan_list.append(vlan)
    log_file.write(f'ip : {my_ip}')
    log_file.write('\n')
    log_file.write(f'VLAN_list : {vlan_list}')
    log_file.write('\n')
    for vlan in vlan_list:
        Tagged_Ports_raw = connection.send_command(f'sh vlan {vlan} | i Tagged ')
        Tagged_Ports = Tagged_Ports_raw.splitlines()
        TaggedPortsList = interface_type(Tagged_Ports)
        log_file.write(f'VLAN: {vlan}')
        log_file.write("\n")
        log_file.write(f"Tagged Ports are : {TaggedPortsList}")
        log_file.write("\n")
        Untagged_Ports_raw = connection.send_command(f'sh vlan {vlan} | i Untagged ')
        Untagged_Ports = Untagged_Ports_raw.splitlines()
        Untagged_PortList = interface_type(Untagged_Ports)
        log_file.write(f"Untagged Ports are : {Untagged_PortList}")
        log_file.write("\n")
        log_file.write("\n")
        log_file.write("\n")
        log_file.write("\n")

    connection.disconnect()
    return

def finalize():
    print('finalizing ...............')
    Path = str(pathlib.Path().resolve())
    print(Path)
    operated_file = open('vlan_map.txt','a')
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
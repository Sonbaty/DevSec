from ast import And
import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import pathlib
import os
import re


devices_file = open("concord_cairo.txt")  ## open the ip list file from root folder
devices_file.seek(0)  ## put the first read on the begining
ip_list = devices_file.read().splitlines()  ## splite the ip's in a list
print(ip_list)
devices_file.close()
initial = 'ICX'


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
        if '1/1' in interface:
            print(f'Checking port {interface} , Switch {device}')
            port_downtime = connection.send_command(f'sh int ethernet {interface} | i Port down (.*)day')
            if 'day' in port_downtime:
                down_days = re.search(r'\d+', port_downtime).group()
                if int(down_days) > 7 :
                    print(f'Found Port {interface}, On Switch {device} Down For {down_days} days')
                    print(f'Disabling port {interface} On Switch {device}')
                    config_commands = [
                                    f'interface eth {interface}',
                                    f'disable',
                                    'exit'
                                ]
                    connection.send_config_set(config_commands)
        else:
            continue


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


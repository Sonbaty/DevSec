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
        if '1/' in interface:
            print(f'Checking port {interface} , Switch {device}')
            port_errors = connection.send_command(f'sh int ethernet {interface} | i error')
            port_uptime = connection.send_command(f'sh int ethernet {interface} | i minute')
            attached_device = connection.send_command(f'sh lldp neighbors detail ports ethernet {interface} | i System description')
        
        else:
            continue   
        

        ai = []
        def err_there(s):
            for i in s:
                if i.isdigit():
                    if int(i) > 0:
                        state = True
                    else:
                        state = False
                    ai.append(state)
            if True in ai:
                final_r = True
            else:
                final_r = False
            return final_r 
        err_string = ""
        for x in port_errors:
            err_string+=" "+x
        
        error_check = err_there(err_string)
        if error_check == True:
            log_file.write(interface)
            log_file.write(' --> : ')
            log_file.write(port_uptime)
            log_file.write("\n")
            log_file.write(f'Attached Device : {attached_device}')
            log_file.write("\n")
            log_file.write(port_errors)
            log_file.write("\n")
            if '1/1/' in interface:
                print(f'Running tdr on port {interface}, On Switch {device}')
                connection.send_command(f'phy cable-diagnostics tdr {interface}')
                tdr_result = connection.send_command(f' sh cable-diagnostics tdr {interface}')
                log_file.write(tdr_result)
                log_file.write("\n")
            else:
                print('Not running my tdr on the uplinks :')
                print(interface)
            
        else:
            tdr_result = "no errors in that port"
            

        
    connection.disconnect()
    print(f'{device} done ..')
    return

def finalize():
    print('finalizing ...............')
    Path = str(pathlib.Path().resolve())
    print(Path)
    operated_file = open('Diagnostic_results.txt','a')
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

    start()
    finalize()

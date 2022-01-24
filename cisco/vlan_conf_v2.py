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
    print('Enabling LLDP ........... ')
    config_commands = [

                        'conf t',
                        'lldp run',
                        'exit'  ]
    print('lldp enabled successfully , waiting 5 seconds ... ')
    connection.send_config_set(config_commands, delay_factor=7)
    time.sleep(7)
    print(device)
    MyIP = IP.strip('\n')
    filename = initials +" "+MyIP
    show_int = connection.send_command('sh lldp Neighbors')
    ou_List = show_int.splitlines()
    int_list = ou_List[5:]   #delete unnecessary in fo and pop last line

    print(f'Query The Device IP: {IP}')
    print('Found The Following APs : ')
    log_file = open(filename, "a")  # append mode
    log_file.write(device)
    log_file.write(" ")
    log_file.write(f'IP : {IP}')

    for line in int_list:
        # interfaces_list = str(line).split(' ')
        interfaces_list = re.split(r'\s{2,}',line)
        Criteria = interfaces_list[3]
        InterfaceNum = interfaces_list[1]
        Device_Name = interfaces_list[0]
        Device_MAC = interfaces_list[4]
        int_ss = (f'{InterfaceNum} | {Device_Name} | {Device_MAC} | {Criteria} |')
        if Criteria == 'B,W':
            print(int_ss)
            log_file = open(filename, "a")  # append mode
            log_file.write(int_ss)
            log_file.write("\n")
            config_commands = [

                            'conf t',
                            f'int {InterfaceNum}',
                            'switchport trunk allowed vlan add 116',
                            'exit'   ]
            print(f'Configuring Vlan For Port {InterfaceNum}')
            connection.send_config_set(config_commands,delay_factor=4)

    log_file.write("\n")
    log_file.write('-' * 79)
    log_file.write("\n")
    print('Saving Configuration .....')
    connection.send_command('show run | i hostname')
    print('Configuration Saved ..')


def finalize():
    print('finalizing ...............')
    Path = str(pathlib.Path().resolve())
    print(Path)
    operated_file = open('Result.txt','a')
    filelist = os.listdir()
    for i in filelist:
        if i.startswith(initials):
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
                t1 = threading.Thread(target=conf_vlan, args=(ip, que))
                t1.start()
                threads.append(t1)
            except BaseException as e:
                continue
        for t in threads:
            t.join()
            print('Waiting For all switches to finish')
    start()

    finalize()

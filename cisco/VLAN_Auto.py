import paramiko
from netmiko import ConnectHandler

import time
import os
import re

def Gathering_facts():
    print("running ...")
    with open('all_devices.txt') as switches:
        for IP in switches:
            Switch = {
                    'device_type': 'cisco_ios_telnet',   ## For Cisco Telnet
                    'ip': IP,
                    #'username': '',           ##blank if no username
                    'password': 'Coral@sts123',   #telnet Pass
                    'secret': 'Coral@sts123',        ## Enable Pass
                    'global_delay_factor': 2,


                }

            try:
                for i in range(1):
                    try:
                        net_connect = ConnectHandler(**Switch)
                        print('Connecting to ' + IP)
                        print('-' * 79)
                        print('waiting For Authentication ...')
                        output = net_connect.send_command('sh version')
                        print()
                        print('-' * 79)
                        net_connect.enable()
                        device = net_connect.send_command('show run | i hostname')
                        print('Enabling LLDP ........... ')
                        config_commands = [

                                           'conf t',
                                           'lldp run',
                                           'exit'  ]
                        net_connect.send_config_set(config_commands, delay_factor=4)


                        time.sleep(4)
                        print(device)
                        MyIP = IP.strip('\n')
                        filename = 'vl_conf_details.txt'
                        show_int = net_connect.send_command('sh lldp Neighbors')
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
                               net_connect.send_config_set(config_commands,delay_factor=4)

                        log_file.write("\n")
                        log_file.write('-' * 79)
                        log_file.write("\n")


                    except paramiko.ssh_exception.SSHException as err:
                        print(f"Oops! {err}")
                        continue

            except BaseException as e:
                continue
    print('done')
    net_connect.disconnect()
    return


Gathering_facts()

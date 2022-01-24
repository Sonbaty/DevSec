import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import os
import re


devices_file = open("icx_devices.txt")  ## open the ip list file from root folder
devices_file.seek(0)  ## put the first read on the begining
ip_list = devices_file.read().splitlines()  ## splite the ip's in a list
print(ip_list)
devices_file.close()


def get_info(IP,any):
    switch = {
            'device_type': 'ruckus_fastiron',
            'ip': IP,
            'username': 'super',
            'password': 'P@$$w0rd',
            # 'banner_timeout': 80
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

    hostname = connection.send_command('show run | i hostname')
    hostname.split(" ")
    if hostname == "":
        device = "no_hostname"
        print('Notice : This switch has no hostname configured')
    else:
        hostname, device = hostname.split(" ")
    print(device)
    my_ip = IP.strip('\n')

    query = connection.send_command('sh vlan 100 | i Untagged')
    print(query)
    q_lines = query.splitlines()
    vlan_interfaces = []
    final_result =[]
    for line in q_lines:
        print(line)
        if 'U1' in line:
            for w in line.split():
                if w.isdigit():
                    vlan_interfaces.append(f'eth 1/1/{int(w)}')
        elif 'U2' in line:
            for w in line.split():
                if w.isdigit():
                    vlan_interfaces.append(f'eth 2/1/{int(w)}')
        elif 'U3' in line:
            for w in line.split():
                if w.isdigit():
                    vlan_interfaces.append(f'eth 3/1/{int(w)}')
    print(vlan_interfaces)

    sw_identifier = f'IP:{my_ip}, Host:{device}'
    filename = f'mac_report[{my_ip}].txt'
    log_file = open(filename, "a")  # append mode
    log_file.write(sw_identifier)
    log_file.write("\n")
    log_file.write("Ports ON VLAN 100 :")
    log_file.write('\n')

    for i in vlan_interfaces:
        neighbour_query = connection.send_command(f'sh mac-address {i}')
        ou_List = neighbour_query.splitlines()
        Nei_List = ou_List[1:]
        Nei_List2 = ou_List[2:]
        if Nei_List2 == []:
            mac = 'none'
        else:
            mac_line = str(Nei_List2[0]).split(" ")
            mac = mac_line[0]
        print(mac)
        log_file.write(f'Interface : {i}, MAC:{mac}')
        log_file.write('\n')

    connection.disconnect()
    return


if __name__ == "__main__":
    que = Queue()

    def start():
        for ip in ip_list:
            # Test using sleep delays between devices to wait for writing outputs to text file in order
            try:
                time.sleep(2)
                print(f'waiting for 2 Seconds before connecting to sw {ip}')
                t1 = threading.Thread(target=get_info, args=(ip, que))
                t1.start()
            except BaseException as e:
                continue


    # For Testing
    start()
    #schedule.every().day.at('01:00').do(daily_backup, 'Backing Up Its 1 AM')
    # while True:
        # schedule.run_pending()

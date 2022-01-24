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
devices_file.close()
initial = 'ICX'
Location = input('Enter The Switches Group Name First : ')


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
    
    
    now = datetime.now()
    CurrTime = now.strftime("%Y-%m-%d %H-%M-%S")
    print("Backing up " + device)

    if not os.path.exists(Location):
        os.mkdir(Location)
        print("Directory ", Location, " Created ")
    else:
        print("Directory ", Location, " already exists")

    if not os.path.exists(f'{Location}/{device}-IP[{my_ip}]'):
        os.makedirs(f'{Location}/{device}-IP[{my_ip}]')
        print("Directory ", device, " Created ")
    else:
        print("Directory ", device, " already exists")

    # filename = '/home/sonbaty/Automation/backups/' + device + '.txt'
    filename = f'{Location}/{device}-IP[{my_ip}]/' + f'{device} AT {CurrTime}' + '.txt'
    

    run_query = connection.send_command('sh run')
   
    sw_identifier = f'IP:{my_ip}, Host:{device}'
    #filename = initial + my_ip
    log_file = open(filename, "a")  # append mode
    log_file.write(run_query)
    log_file.write("\n")


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


import time
from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import threading
import pathlib
import os
import re


devices_file = open("icx_devices.txt")  ## open the ip list file from root folder
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
            'password': 'P@$$w0rd'

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


    model_query = connection.send_command('show version | i UNIT')
    sw_identifier = f'IP:{my_ip}, Host:{device}'
    filename = initial + my_ip
    log_file = open(filename, "a")  # append mode
    log_file.write(sw_identifier)
    log_file.write("\n")
    log_file.write(model_query)
    log_file.write("\n")





    connection.disconnect()
    return

def finalize():
    print('finalizing ...............')
    Path = str(pathlib.Path().resolve())
    print(Path)
    operated_file = open('SW_Models.txt','a')
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

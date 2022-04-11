from netmiko import ConnectHandler
from datetime import datetime
from multiprocessing import Queue
import os
import keyring as kr


Srx_ip = "10.2.100.1"
username= "sonbaty"
key = kr.get_password(Srx_ip, username)
Location = 'X:\Backup_auto_test'
def get_backup(IP,any):
    
    Srx = {
        'device_type': 'cisco_ios',
        'host': Srx_ip,
        'username': username,         
        'password': key, 
        'conn_timeout':60, 
        'auth_timeout':60,
        'global_delay_factor': 2,

    }

    connection = ConnectHandler(**Srx)
    connection.conn_timeout = 200
    print('Connecting to ' + IP)
    print('-' * 79)
    print('waiting For Authentication ...')
    output = connection.send_command('show version', read_timeout=90)
    print(output)
    print()
    print('-' * 79)
    device = "SRX"
    print(device)
    my_ip = IP.strip('\n')
    now = datetime.now()
    curr_time = now.strftime("%Y-%m-%d %H-%M-%S")
    print("Backing up Node 0 ..." + device)

    if not os.path.exists(Location):
        os.mkdir(Location)
        print("Directory ", Location, " Created ")
    else:
        print("Directory ", Location, " already exists")

    if not os.path.exists(f'{Location}/{device}-[Node0]-IP[{my_ip}]'):
        os.makedirs(f'{Location}/{device}-[Node0]-IP[{my_ip}]')
        print("Directory ", device, " Created ")
    else:
        print("Directory ", device, " already exists")


    filename = f'{Location}/{device}-[Node0]-IP[{my_ip}]/'+f'{curr_time}' + '.txt'
    #filename = 'deviceNames.txt'
    run_query = connection.send_command('show configuration | display set | no-more', read_timeout=90)
    log_file = open(filename, "a")  # append mode
    log_file.write(run_query)
    log_file.write("\n")
    print("Jumping to node 1 ,,,,")
    #connection.send_command(f'copy run tftp {tftp_Srx_ipr} {date}/{filename}')
    print("Backing up Node 1 ..." + device)
#------------------------------------------------------------------------------------------------------

    print("SRX done ,,,,")
    connection.disconnect()
    return
get_backup(Srx_ip,any)

from netmiko import ConnectHandler
from datetime import datetime
import schedule
from multiprocessing import Queue
import threading
import os

Location = input('Enter The Switches Group Name First : ')
print("Backup Is EveryDay at 1 AM")

ips_file = open("Devices.txt", 'r')  ## open the ip list file from root folder
ips_file.seek(0)  ## put the first read on the begining
ip_list = ips_file.read().splitlines()  ## splite the ip's in a list
ips_file.close()


def get_backup(IP,any):
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
    print('waiting For Authentication ...')
    output = connection.send_command('sh version')
    print(output)
    print()
    print('-' * 79)

    hostname = connection.send_command('show run | i hostname')
    hostname.split(" ")
    if hostname == "":
        device = "SW_name"
        print('Notice : This switch has no hostname configured')
    else:
        hostname, device = hostname.split(" ")
    print(device)
    my_ip = IP.strip('\n')
    now = datetime.now()
    curr_time = now.strftime("%Y-%m-%d %H-%M-%S")
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
    tftp_srvr = 'test'
    date = f'{Location}/{device}-IP[{my_ip}]/'
    filename = f'{device} AT {curr_time}' + '.txt'
    connection.enable()
    filename = 'deviceNames.txt'
    log_file = open(filename, "a")  # append mode
    log_file.write(device)
    log_file.write("\n")
    #connection.send_command(f'copy run tftp {tftp_srvr} {date}/{filename}')
    connection.disconnect()
    print('Next Backup Is Tomorrow At 01:00 AM')
    print('Waiting  ...')
    return


if __name__ == "__main__":
    que = Queue()

    def daily_backup():
        for ip in ip_list:
            thred = threading.Thread(target=get_backup, args=(ip, que))
            thred.start()


    # For Testing
    daily_backup()
    #schedule.every().day.at('01:00').do(daily_backup, 'Backing Up Its 1 AM')
    # while True:
        # schedule.run_pending()






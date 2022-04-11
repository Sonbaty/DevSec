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
        'timeout':2000, 
        'conn_timeout':None, 
        'auth_timeout':None,
        'global_delay_factor': 2,

    }
    print('Connecting to ' + IP)
    connection = ConnectHandler(**Srx)
    print('Connected to ' + IP)
    print('-' * 79)
    print('waiting For Authentication ...')
    output = connection.send_command('show version',read_timeout=90)
    print(output)
    print()
    print('-' * 79)
    device = "SRX"
    print(device)
    my_ip = IP.strip('\n')


    #filename = 'deviceNames.txt'
    address_book_query = connection.send_command('show configuration |display set |match momk | match address-book | no-more',read_timeout=90)
    policies_query = connection.send_command('show configuration | display set | match policies | match momk | no-more',read_timeout=90)
    policy_list = policies_query.splitlines()[:-2]
    output_List = address_book_query.splitlines()[:-2]
    address_dict = {}
    filename = 'Address_set.txt'
    filename2 = 'Address_book.txt'
    filename3 = "policies.txt"
    log_file = open(filename, "a")
    log_file2 = open(filename2, "a")
    log_file3 = open(filename3, "a") 
    pol_li = []
    for line in output_List:
        if "address-set" in line:
            address_set_raw = str(line).split()
            address_set_name = address_set_raw[7]
            address_set_ip = address_set_raw[9]
            #print(f"found {address_set_name}--> {address_set_ip}")
            log_file.write(f'{address_set_name} : {address_set_ip}')
            log_file.write("\n")
        else:
            address_book_raw = str(line).split()
            address_book_name = address_book_raw[7]
            address_book_ip = address_book_raw[8]
            #print(f"found {address_book_name}--> {address_book_ip}")
            log_file2.write(f'{address_book_name} : {address_book_ip}')
            log_file2.write("\n")

    
    for policy in policy_list:
        policy_raw = str(policy).split()
        policy_name = policy_raw[8]
        if not policy_name in pol_li:
            pol_li.append(policy_name)
    for pol in pol_li:
        print(f"querying policy {pol} ")
        log_file3.write(f"Policy : {pol } ->")
        log_file3.write("\n")
        policy_detail_query = connection.send_command(f'show configuration | display set | match policies | match {pol} | no-more',read_timeout=90)
        policy_detail = policy_detail_query.splitlines()[:-2]
        src_zone=""
        dst_zone=""
        src_add=[]
        dst_add=[]
        pol_app=[]
        for line in policy_detail:
            print("getting policy list")
            policy_raw = str(policy).split()
            if src_zone == "":
                src_zone = policy_raw[4]
            else:
                continue
            if dst_zone == "":
                dst_zone = policy_raw[6]
            else:
                continue
            log_file3.write(f'Source-Zone : {src_zone}')
            log_file3.write("\n")
            log_file3.write(f'Destination-Zone : {dst_zone}')
            log_file3.write("\n")
            if "source-address" in policy_detail:
                src_add = src_add.append(policy_raw[11])
            elif "destination-address" in policy_detail:
                dst_add = dst_add.append(policy_raw[11])
            elif "application" in policy_detail:
                pol_app = pol_app.append(policy_raw[11])
            elif "then" in policy_detail:
                action = policy_raw[11]
            else:
                continue
            log_file3.write(f'Source-Address(s) : {src_add}')
            log_file3.write("\n")
            log_file3.write(f'Destination-Address(s) : {dst_add}')
            log_file3.write("\n")
            log_file3.write(f'Application(s) : {pol_app}')
            log_file3.write("\n")
            log_file3.write(f'Action : {action}')
            log_file3.write("\n")
            log_file3.write("-------------------------------------------------------------------------------------")
            

            

#------------------------------------------------------------------------------------------------------

    print("SRX done ,,,,")
    connection.disconnect()
    return
get_backup(Srx_ip,any)



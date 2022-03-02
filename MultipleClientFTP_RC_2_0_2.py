import os
from pickle import TRUE
# os.system("mode con cols=51 lines=16")
from platform import platform
import socket
import sys 
import platform
from time import sleep
from ftplib import FTP
import shutil
import logging
from datetime import datetime
import time
import asyncio

os_name = platform.system()
print(f"Platform is {os_name}")

if os_name != "Darwin":
    clear = 'cls'
else:
    clear = 'clear'
os.system(clear)

with open("datalog.log", "a") as file:
    logging.basicConfig(filename='datalog.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s\n')
logger = logging.getLogger(__name__)

try:
    HEADER = 1024
    ##Keyence port number need to check with KV Studio at Unit Editor --> check socket function need to be used --> Check Port No. (host link) --> 8501
    PORT = 8501 
    FORMAT = 'utf-8'
    LIST_SERVER = []
    FTP_USERNAME = []
    FTP_PASSWORD = []
    CURRENT_PATH = os.getcwd()
    STOR_PATH = []
    FTP_PATH = []
    
    FTP_Setting = []
    with open("ftp_setting.ini", "r") as ftpSetting:
        count = 0
        for line in ftpSetting:
            if line[0:1] == ";" or line[0:1] == "\n":
                count += 1
            else:
                count+= 1
                list_of_item = line.strip()
                FTP_Setting.append(list_of_item)
                # print(f"lines {count}:", line.strip())
    print(FTP_Setting)
    

    ##Define FTP username and Password Program Location and Stor Location
    FTP_USERNAME = FTP_Setting[0].split(":")
    FTP_PASSWORD = FTP_Setting[1].split(":")
    FTP_COPY = FTP_Setting[2].split(":")
    FTP_DELETE = FTP_Setting[3].split(":")
    STOR_PATH = FTP_Setting[4].split(":", 1)
    FTP_PATH = FTP_Setting[5].split(":",1)
    LOT_SAVE = FTP_Setting[6].split(":")

    

    if FTP_USERNAME[0].strip() == "USER" and FTP_PASSWORD[0].strip() == "PASS" and FTP_COPY[0].strip() == "COPY" and FTP_DELETE[0].strip() == "DELETE" and STOR_PATH[0].strip() == "STOR_PATH" and FTP_PATH[0].strip() == "FTP_PATH" and LOT_SAVE[0].strip() == "LOT_NUM": 
    # if FTP_USERNAME[0] == "USER" and FTP_PASSWORD[0] == "PASS":
        FTP_USER = FTP_USERNAME[1].strip()
        FTP_PASS = FTP_PASSWORD[1].strip()
        FTP_CPY = FTP_COPY[1].strip().upper()
        FTP_DLT = FTP_DELETE[1].strip().upper() 
        PATH_PROG = CURRENT_PATH + "\\"
        PATH_STOR = STOR_PATH[1].strip() + "/"
        PATH_FTP = FTP_PATH[1].strip() + "/"
        SAVE_LOT = LOT_SAVE[1].strip()

    else:
        print("PLEASE CHECK "'ftp_setting.ini'" Content")
        sleep(50)
        sys.exit()

    ##STARTING to real list of IP registered #Reading IP and Put into ARRAY 
    with open("list_server_kv8000_vt5.csv","r") as file:
        count = 0 
        for line in file:
            if line[0:1] == ";" or line[0:1] == "\n":
                count += 1
            else:
                count+= 1
                list_of_item = line.strip()
                LIST_SERVER.append(list_of_item)
                print(f"lines {count-1}:", line.strip())
                print(len(LIST_SERVER))

except Exception as error:
    print("Program cannot be execute (!_-) ")
    print(f"[ERROR]: {error}")
    logger.error(error)
    sleep(50)
    sys.exit()

async def run_task(list_server_index):
    ## Record error print data 
    def log_record(error_msg):
        pass
        log_data_collect = []
        with open ("datalog.log", "r") as file:
            for log_data_content in file:
                log_data_collect.append(log_data_content)

        with open("datalog.log", "w") as file:
            len_of_log_data_collect = len(log_data_collect)
            for items in log_data_collect: 
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ERROR RECORDED]:{error_msg}")
                msg_will_write = " " + error_msg + "\n"
                if log_data_collect[len_of_log_data_collect-1][20:] == msg_will_write:
                    file.write(date_time + " " + error_msg + "\n")
                    pass
                else:
                    # now = datetime.now()
                    # date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    # print(f"[ERROR RECORDED]:{error_msg}")
                    # file.write(date_time + " " + error_msg + "\n")
                    file.write(str(items))

    def writing_file(write_msg):
        with open("filemakingtime.log", "a") as file:
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[msg]:{write_msg}")
            file.write(date_time + " " + write_msg + "\n")

    ###START MOVING COPIED FILE ,TO SERVER/LOCAL COMPUTER
    def copyingdata(msg, file_list_in_vt5, transferPathTemp, machineName, lot_num_received_string, type_received_string):
        try:
            print("[COPY] DATA TO SERVER......")
            # CHECK IF FILE APPEAR OR NOT
            checkfile = PATH_STOR + machineName + "/"
            checkDir = os.path.isdir(checkfile)

            if checkDir == False:
                os.mkdir(checkfile)   
            else:
                count = 0
                while count < len(file_list_in_vt5):
                    try:
                        fileCopyFrom = transferPathTemp + lot_num_received_string + "-" + file_list_in_vt5[count]
                        if SAVE_LOT.upper() == "YES":
                            fileMovingTo = PATH_STOR + machineName + "/" + lot_num_received_string + "-" + file_list_in_vt5[count]
                        else:
                            fileMovingTo = PATH_STOR + machineName + "/" + file_list_in_vt5[count]
                        
                        shutil.move(fileCopyFrom, fileMovingTo)
                        writing_finish = f"[LOT NUM] {lot_num_received_string} \n                    [TYPE] {type_received_string}"
                        writing_file(writing_finish)

                    except Exception as Error:
                        logger.error(Error)
                        log_record(Error)  
                    count += 1

                msg = "WR DM508.H 0\r"
                message = msg.encode(FORMAT)
                client.send(message)
                print("Freezing for 30s")
                client.close()

        except Exception as Error:
            logger.error(Error)

    ## DO FTP Operation which is Transferr data from PANEL to SERVER or LOCAL Computer
    def ftpOperation(msg, machineName, transferHostname, status,  lot_num_received_string, type_received_string):
        
        print("[STATUS]:" + status)
        if status == "230 Login successful.":
            print('[LOGIN SUCCESS]')
            state = ftp.cwd(PATH_FTP)
            print(f"[DIRECTORY CHANGE]:{str(state)}")

            # dirfilelist = ftp.nlst()
            file_list_in_vt5 = []
            # for file_name in dirfilelist:
            for file_name in ftp.nlst():
                file_list_in_vt5.append(file_name)

            ##IF NEEDED
            local_temp_file_name = f"TEMP_{machineName}"
            print(f"[COPY] from {local_temp_file_name} :: {transferHostname}")

            
            transferPathTemp = os.path.join(PATH_PROG, f"{local_temp_file_name}\\")
            # CHECK IF FILE APPEAR OR NOT
            checkdir = os.path.isdir(transferPathTemp)

            if checkdir == False:
                os.makedirs(transferPathTemp)
            else:    
                # LOOP TO TRANSFER EVERY FILE FILE FROM SD CARD VT5 KEYENCE TOUCH PANEL TO LOCAL COMPUTER
                count = 0
                while count < len(file_list_in_vt5):
                    file_write_with_rename = transferPathTemp + lot_num_received_string + "-" + file_list_in_vt5[count]
                    if FTP_COPY == "YES" or FTP_DLT == "YES":

                        with open(file_write_with_rename,"wb" ) as filer:
                            # RETRIEVE DATA FROM FTP SERVER
                            ftpcommand = ftp.retrbinary(f"RETR {file_list_in_vt5[count]}", filer.write)
                            print(file_list_in_vt5[count] + " ->> " + ftpcommand)
                            # DELETE FILE IN SD CARD KEYENCE VT5 IF NEEDED
                            ftpResponse = ftp.delete(file_list_in_vt5[count])
                            print(file_list_in_vt5[count] + " ->> " + ftpResponse)
                            

                    elif FTP_CPY == "YES" and FTP_DLT == "NO":
                        
                        with open(file_write_with_rename,"wb" ) as filer:
                            # RETRIEVE DATA FROM FTP SERVER
                            ftpcommand = ftp.retrbinary(f"RETR {file_list_in_vt5[count]}", filer.write)
                            print(file_list_in_vt5[count] + " ->> " + ftpcommand)
                        
                    else:
                        error_msg = f"[ERROR] FTP don't copy and delete anything from this {machineName}, {transferHostname}"
                        print(error_msg)
                        log_record(error_msg)
                        error_msg = f"[ERROR] FTP COPY :{FTP_CPY} FTP DELETE :{FTP_DLT}"
                        log_record(error_msg)
                    count += 1
            ftp.close()

            copyingdata(msg ,file_list_in_vt5 ,transferPathTemp, machineName, lot_num_received_string, type_received_string)
            client.close()        
        else:
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            client.close()

    ## SEND COMMAND TO SERVER KV-8000
    def send(msg, machineName, hostName, transferHostname):
        message = msg.encode(FORMAT)
        client.send(message)
        ReceivedData = client.recv(2048).decode(FORMAT)

        if ReceivedData == "0000" or "0001":
            datareceived = int(ReceivedData)

            get_lot_num = "RDS DM30.H 6\r"
            lot_num_req = get_lot_num.encode(FORMAT)
            client.send(lot_num_req)
            lot_num_received_hex = client.recv(2048).decode(FORMAT)
            hex_to_string = lot_num_received_hex
            bytes_object = bytes.fromhex(hex_to_string)
            lot_num_received_string = bytes_object.decode("ASCII")

            print(f"[LOT NUMBER]:{lot_num_received_string}")

            get_type = "RDS DM10274.H 10\r"
            type_req = get_type.encode(FORMAT)
            client.send(type_req)
            type_received_hex = client.recv(2048).decode(FORMAT)
            type_hex_to_string = type_received_hex
            type_bytes_object = bytes.fromhex(type_hex_to_string)
            type_received_string = type_bytes_object.decode("ASCII")

            print(f"[TYPE]:{type_received_string}")
            sleep(0.01)

            print(f"[RESPONSE] from {hostName} : {datareceived}")
            
            if datareceived == 0:
                print("DO NOT COPY DATA ==> MOVE TO OTHERS")
                client.close()

            elif datareceived == 1:
                
                try:
                    log_record(f"[KEYENCE RESPONSE] {datareceived}")
                    global ftp
                    ftp = FTP(transferHostname)
                    status = ftp.login(FTP_USER, FTP_PASS)
                    print(" \|^_^|/  \|^_^|/  \|^_^|/  \|^_^|/ ")
                    print(f"\n[LOGIN INTO {transferHostname} SUCCESS] MACHINE:{machineName[:6]}")
                    ftpOperation(msg, machineName, transferHostname, status, lot_num_received_string, type_received_string)

                except Exception as error:
                        error_msg = f"Error --> {error} At PANEL FTP:{transferHostname} MACHINE:{machineName[:6]}"
                        print(error_msg)
                        logger.error(error)
                        log_record(error_msg)
                        # sleep(1)
                        msg = "WR DM508.H 0\r"
                        message = msg.encode(FORMAT)
                        client.send(message)
                        client.close()
            else:       
                error_msg = f"[INVALID VALIDATION] KV-8000 response other command :--> {ReceivedData}"
                print(error_msg)
                log_record(error_msg)
                
        else:
            error_msg = f"[INVALID] Keyence send : {ReceivedData}"
            log_record(error_msg)
            print(f"Response : {ReceivedData}")
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            client.close()

    ## START SOCKET CONNECTION BETWEEN CLIENT AND SERVER KEYENCE KV-8000
    def start(list_server_index):
        print(f"[START]:{str(list_server_index + 1)}")
        # os.system(clear)

        ActiveAddress = []
        ActiveAddress = LIST_SERVER[list_server_index].split(",")
        machineName = ActiveAddress[0]
        hostName = ActiveAddress[1]
        transferHostname = ActiveAddress[2]
        ADDR = (hostName, PORT)

        try:
            print(f"[CONNECTING] to {machineName[:6]} \n[KEYENCE PLC]:{hostName} \n[PANEL]:{transferHostname}")
            print(f"[ROUND]:{str(list_server_index + 1)}")

            global client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR)
            print(" \|^_^|/  \|^_^|/  \|^_^|/  \|^_^|/ ")
            print(f"[CONNECTED] to {hostName} port {PORT}")
            COMMAND = "RD DM508.H"
            send(COMMAND + "\r",  machineName, hostName, transferHostname)

        except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError, OSError) as Error:
                print("(-_-!) (-_-!) (-_-!) (-_-!) (-_-!) (-_-!) ")
                error_msg = f"[FAILED to CONNECT] MACHINE:{machineName.strip()[:6]} SERVER:{hostName} PORT:{PORT} "
                logger.error(Error)
                print(error_msg)
                log_record(error_msg)

    start_time = time.time()
    sleep(0.10)  
    start(list_server_index)
    end_time = time.time()
    print(f"[EXECUTE]TIME:{str(round(end_time - start_time,3))}s\n")
    await asyncio.sleep(len(LIST_SERVER))
    # print(f"DONE {str(list_server_index)}")

async def main():
    threads = []
    count = 0
    START_time = time.time()

    while count < len(LIST_SERVER):
        t = run_task(count)
        threads.append(t)
        count+=1

    await asyncio.gather(*threads)

    print(f"[{str(len(threads))} THREADS RUNNING FINISH]")
    END_time = time.time()
    sleep(1)
    print(f"[ALL EXECUTE]TIME:{str(round(END_time - START_time, 3))}s\n")


def start_all():
    while True:
        asyncio.run(main())

# START OPERATION
try:
    start_all()
except Exception as Error:
    print(f"[ERROR]: {Error}")
    logger.error(Error)
    sleep(50)

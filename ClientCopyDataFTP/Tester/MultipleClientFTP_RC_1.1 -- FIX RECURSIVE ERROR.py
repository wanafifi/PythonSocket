from platform import platform
import socket
import sys 
import platform
import os
from time import sleep
from ftplib import FTP
import shutil
import logging
from datetime import datetime


file = open("datalog.log", "a")
file.close()
logging.basicConfig(filename='datalog.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s\n')
logger=logging.getLogger(__name__)



try:
    os_name = platform.system()
    print(f"Platform is {os_name}")

    if os_name != "Darwin":
        clear = 'cls'
    else:
        clear = 'clear'
    os.system(clear)

    HEADER = 1024
    ##Keyence port number need to check with KV Studio at Unit Editor --> check socket function need to be used --> Check Port No. (host link) --> 8501
    PORT = 8501 
    FORMAT = 'utf-8'
    LIST_SERVER = []
    FTP_USERNAME = []
    FTP_PASSWORD = []
    CURRENT_PATH = os.getcwd()
    print(CURRENT_PATH)
    # PROGRAM_PATH = []
    STOR_PATH = []

    FTP_Setting = []
    ftpSetting = open("ftp_setting.ini", "r")
    count = 0
    for line in ftpSetting:
        count+= 1
        list_of_item = line.strip()
        FTP_Setting.append(list_of_item)
        print(f"lines {count}:", line.strip())
        print(FTP_Setting)
    ftpSetting.close()

    ##Define FTP username and Password Program Location and Stor Location
    FTP_USERNAME = FTP_Setting[0].split(":")
    FTP_PASSWORD = FTP_Setting[1].split(":")
    FTP_COPY = FTP_Setting[2].split(":")
    FTP_DELETE = FTP_Setting[3].split(":")
    # PROGRAM_PATH = FTP_Setting[4].split(":", 1)
    STOR_PATH = FTP_Setting[5].split(":", 1)

    if FTP_USERNAME[0] == "USER" and FTP_PASSWORD[0] == "PASS":
        FTP_USER = FTP_USERNAME[1].strip()
        FTP_PASS = FTP_PASSWORD[1].strip()
        FTP_CPY = FTP_COPY[1].strip().upper()
        FTP_DLT = FTP_DELETE[1].strip().upper()
        # PATH_PROG = PROGRAM_PATH[1].strip()
        PATH_PROG = CURRENT_PATH + "/"
        PATH_STOR = STOR_PATH[1].strip()

    else:
        print("PLEASE CHECK ftp_setting.ini")
        # sleep(10)
        sys.exit()

    ##STARTING to real list of IP registered
    file = open("server_and_ftp_list_ip.ini","r")
    #Reading IP and Put into ARRAY 
    count = 0 
    for line in file:
        count+= 1
        list_of_item = line.strip()
        LIST_SERVER.append(list_of_item)
        print(f"lines {count-1}:", line.strip())
    file.close()

except Exception as error:
    print("Program cannot be execute (!_-) ")
    logger.error(error)
    sleep(1)

###START MOVING COPIED FILE ,TO SERVER/LOCAL COMPUTER
def copyingdata(msg , list_SERVER, filelist, machineName):
            print("[COPY] DATA TO SERVER......")    
            count = 0
            while count < len(filelist):
                try:
                    shutil.move(PATH_PROG + filelist[count], PATH_STOR + machineName + "/" + filelist[count])
                except FileNotFoundError:
                    newPath = os.path.join(PATH_STOR, f"{machineName}")
                    os.makedirs(newPath)
                    shutil.move(PATH_PROG + filelist[count], PATH_STOR + machineName + "/" + filelist[count])   
                count+=1
            
            if msg != False:
                msg = "WR DM508.H 0\r"
                message = msg.encode(FORMAT)
                client.send(message)
                print("Freezing for 10s")
                sleep(5)
                client.close()
                return list_SERVER + 1
            else:
                # sleep(1)
                return False

## Record error print data 
def log_record(error_msg):
    file = open("datalog.log", "a")
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("[ERROR RECORDED]")
    file.write(date_time + " " + error_msg + "\n")
    file.close()

## DO FTP Operation which is Transferr data from PANEL to SERVER or LOCAL Computer
def ftpOperation(msg, list_SERVER, machineName, transferHostname, status, datareceived):
    print("[STATUS]:" + status)
    if (msg, list_SERVER, machineName, transferHostname, status, datareceived) == False:
        client.close()
        return False
    else:
        if status == "230 Login successful.":
            print('[LOGIN SUCCESS]')
            # ftp.retrlines('LIST')
            state = ftp.cwd("/VTWS/ID1/00000_00999/")
            print(f"[DIRECTORY CHANGE]:{str(state)}")
            # ftp.retrlines('LIST')

            # print(ftp.retrlines('LIST'))
            # print(ftp.cwd("/VTWS/ID1/00000_00999/"))
            # print(ftp.retrlines('LIST'))

            dirfilelist = ftp.nlst()
            filelist = []

            for file in dirfilelist:
                filelist.append(file)

            ##IF NEEDED
            print(f"[COPY] from {machineName} :: {transferHostname}")

            ##START TRANSFER FILE FROM SD CARD VT5 KEYENCE TOUCH PANEL TO LOCAL COMPUTER
            count = 0
            while count < len(filelist):
                with open(filelist[count],"wb") as file:
                    if FTP_COPY == "YES" or FTP_DLT == "YES":
                        ftpcommand = ftp.retrbinary(f"RETR {filelist[count]}", file.write)
                        print(filelist[count] + " ->> " + ftpcommand)
                        #DELETE FILE IN SD CARD KEYENCE VT5 IF NEEDED
                        ftpResponse = ftp.delete(filelist[count])
                        print(filelist[count] + " ->> " + ftpResponse)

                    elif FTP_CPY == "YES" and FTP_DLT == "NO":
                        ftpcommand = ftp.retrbinary(f"RETR {filelist[count]}", file.write)
                        print(filelist[count] + " ->> " + ftpcommand)

                    else:
                        error_msg = f"[ERROR] FTP don't copy and delete anything from this {machineName}, {transferHostname}"
                        print(error_msg)
                        log_record(error_msg)
                        error_msg = f"[ERROR] FTP COPY : {FTP_CPY} FTP DELETE :{FTP_DLT}"
                        log_record(error_msg)
                        sleep(10)
                        sys.exit()
                count+=1
            ftp.close()

            result = copyingdata(msg , list_SERVER, filelist , machineName)
            client.close()
            return result         
        else:
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            client.close()
            return list_SERVER + 1

## START SOCKET CONNECTION BETWEEN CLIENT AND SERVER KEYENCE KV-8000
def start():
    OPERATION_COUNT = 0 
    count = 1
    while count < len(LIST_SERVER):
        OPERATION_COUNT += 1
        sleep(0.02)
        operation_file = open("operationcount.log", "w")
        sleep(0.02)
        os.system(clear)
        print(f"\n[OPERATION COUNT]:{str(OPERATION_COUNT)}")
        operation_file.write(f"[OPERATION COUNT] is : {str(OPERATION_COUNT)} Times ")
        operation_file.close()

        # print("LISTSERVER :", len(LIST_SERVER))
        # print("COUNT:", count)

        ActiveAddress = []
        ActiveAddress = LIST_SERVER[count].split("|")
        machineName = ActiveAddress[0]
        hostName = ActiveAddress[1]
        transferHostname = ActiveAddress[2]
        ADDR = (hostName, PORT)
        # sleep(1)

        try:
            ServerCategory = []
            ServerCategory = LIST_SERVER[count].split("|")
            print(f"[CONNECTING] to {ServerCategory[0][:6]} \n[KEYENCE PLC]:{ServerCategory[1]} \n[PANEL]:{ServerCategory[2]}")
            print(f"[ROUND]:{str(count)}")

            global client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR)
            print(f"[CONNECTED] to {hostName} port {PORT} -->> \|^_^|/ ")
            if (count, machineName, hostName, transferHostname) == False:
                client.close()
                start()
            else:
                COMMAND = "RD DM508.H"
                count = send(COMMAND + "\r", count, machineName, hostName, transferHostname)
                if count == len(LIST_SERVER):
                    count = 1
                else:
                    pass
            
        except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError, OSError) as Error:
            error_msg = f"[FAILED to CONNECT] MACHINE:{machineName.strip()[:6]} SERVER:{hostName} PORT:{PORT} -->> (-_-!)"
            logger.error(Error)
            print(error_msg)
            log_record(error_msg)
            # sleep(1)
            if count < len(LIST_SERVER):
                count = 1
            else:
                count += 1
    

## SEND COMMAND TO SERVER KV-8000
def send(msg, list_SERVER, machineName, hostName, transferHostname):
    # print(f"send msg : {msg} to {hostName}")
    if (msg, list_SERVER, machineName, hostName, transferHostname) == False:
        return list_SERVER + 1
    else:
        message = msg.encode(FORMAT)
        client.send(message)
        ReceivedData = client.recv(2048).decode(FORMAT)

        if ReceivedData == "0000" or "0001":
            datareceived = int(ReceivedData)
            print(f"[RESPONSE] from {hostName} : {datareceived}")
            
            if datareceived == 0:
                print("DO NOT COPY DATA ==> MOVE TO OTHERS\n")
                client.close()
                # sleep(1)
                return list_SERVER + 1

            elif datareceived == 1:
                try:
                    if list_SERVER > len(LIST_SERVER) - 1:
                        return list_SERVER + 1
                    else:                
                        global ftp
                        ftp = FTP(transferHostname)
                        status = ftp.login(FTP_USER, FTP_PASS)
                        print(f"\n[LOGIN INTO {transferHostname}] MACHINE:{machineName[:6]}")
                        list_SERVER = ftpOperation(msg, list_SERVER, machineName, transferHostname, status, datareceived)
                        if list_SERVER != False:
                            return list_SERVER + 1
                        else:
                            return 1

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
                    return list_SERVER + 1
            else:       
                error_msg = f"[INVALID VALIDATION] KV-8000 response other command :--> {ReceivedData}"
                print(error_msg)
                log_record(error_msg)
                return list_SERVER + 1
        else:
            error_msg = f"[INVALID] Keyence send : {ReceivedData}"
            log_record(error_msg)
            print(f"Response : {ReceivedData}")
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            client.close()
            return list_SERVER + 1

#START THE PROGRAM    
try:
    start()
except Exception as Error:
    logger.error(Error)
    print("Error occur :", Error)
    sleep(10)
    start()
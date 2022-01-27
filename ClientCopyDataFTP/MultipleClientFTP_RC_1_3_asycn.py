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
import time
import asyncio

os_name = platform.system()
print(f"Platform is {os_name}")

if os_name != "Darwin":
    clear = 'cls'
else:
    clear = 'clear'
os.system(clear)

file = open("datalog.log", "a")
file.close()
logging.basicConfig(filename='datalog.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s\n')
logger=logging.getLogger(__name__)

try:
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
    FTP_PATH = []

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
    FTP_PATH = FTP_Setting[6].split(":",1)

    if FTP_USERNAME[0] == "USER" and FTP_PASSWORD[0] == "PASS":
        FTP_USER = FTP_USERNAME[1].strip()
        FTP_PASS = FTP_PASSWORD[1].strip()
        FTP_CPY = FTP_COPY[1].strip().upper()
        FTP_DLT = FTP_DELETE[1].strip().upper()
        # PATH_PROG = PROGRAM_PATH[1].strip()
        PATH_PROG = CURRENT_PATH + "/"
        PATH_STOR = STOR_PATH[1].strip()
        PATH_FTP = FTP_PATH[1].strip()

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


async def create_task(list_server_index):
    ###START MOVING COPIED FILE ,TO SERVER/LOCAL COMPUTER
    def copyingdata(msg , list_SERVER, filelist, machineName):
        print("[COPY] DATA TO SERVER......")    
        count = 0
        while count < len(filelist):
            try:
                shutil.move(PATH_PROG + filelist[count], PATH_STOR + machineName + "/" + filelist[count])
            except Exception as Error:
                logger.error(Error)
                Error = f"[Error] try create folder {machineName}"
                log_record(Error)
                newPath = os.path.join(PATH_STOR, f"{machineName}")
                os.makedirs(newPath)
                Error = f"[Error] making folder {machineName} success"
                log_record(Error)
                shutil.move(PATH_PROG + filelist[count], PATH_STOR + machineName + "/" + filelist[count])   
            count+=1
        
        if msg != False:
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            print("Freezing for 30s")
            sleep(1)
            client.close()
        else:
            pass

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

        if status == "230 Login successful.":
            print('[LOGIN SUCCESS]')
            # ftp.retrlines('LIST')
            state = ftp.cwd(PATH_FTP)
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
                        error_msg = f"[ERROR] FTP COPY :{FTP_CPY} FTP DELETE :{FTP_DLT}"
                        log_record(error_msg)
                        # sleep(10)
                        # sys.exit()
                count+=1
            ftp.close()

            copyingdata(msg , list_SERVER, filelist , machineName)
            client.close()        
        else:
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            client.close()

    ## SEND COMMAND TO SERVER KV-8000
    def send(msg, list_SERVER, machineName, hostName, transferHostname):
        # print(f"send msg : {msg} to {hostName}")
        message = msg.encode(FORMAT)
        client.send(message)
        ReceivedData = client.recv(2048).decode(FORMAT)

        if ReceivedData == "0000" or "0001":
            datareceived = int(ReceivedData)
            print(f"[RESPONSE] from {hostName} : {datareceived}")
            
            if datareceived == 0:
                print("DO NOT COPY DATA ==> MOVE TO OTHERS\n")
                client.close()

            elif datareceived == 1:
                try:
                    if list_SERVER == len(LIST_SERVER):
                        return False
                    else:                
                        global ftp
                        ftp = FTP(transferHostname)
                        status = ftp.login(FTP_USER, FTP_PASS)
                        print(f"\n[LOGIN INTO {transferHostname}] MACHINE:{machineName[:6]}")
                        ftpOperation(msg, list_SERVER, machineName, transferHostname, status, datareceived)

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
        print(list_server_index)
        count = list_server_index
        end_time = time.time()
        # os.system(clear)

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

            COMMAND = "RD DM508.H"
            
            send(COMMAND + "\r", count, machineName, hostName, transferHostname)

            start_time = time.time()
            print(f"[EXECUTE] TIME:{str(round(start_time - end_time,3))}s")
            
            
        except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError, OSError) as Error:
            error_msg = f"[FAILED to CONNECT] MACHINE:{machineName.strip()[:6]} SERVER:{hostName} PORT:{PORT} -->> (-_-!)"
            logger.error(Error)
            print(error_msg)
            log_record(error_msg)
            # sleep(1)
        return False


    #START THE PROGRAM    
    start(list_server_index)
    await asyncio.sleep(1)
    print(f"DONE {str(list_server_index)}")

async def main():
    threads = []
    count = 1
    while count <= len(LIST_SERVER)-1:
        t = asyncio.create_task(create_task(count))
        threads.append(t)
        count+=1
    print(len(threads))
    await asyncio.sleep(10)

    

def start_all():
    round = 1
    while round <= len(LIST_SERVER) - 1:
        print("RUNNING1")
        if round > len(LIST_SERVER) -1:
            print("RUNNING2")
            round = 1
        else:
            print("RUNNING3")
            asyncio.run(main())
            sleep(1)
        round += 1

start_all()
# async def starting_point():
#     while True:
#         main()
#         await asyncio.sleep(30)

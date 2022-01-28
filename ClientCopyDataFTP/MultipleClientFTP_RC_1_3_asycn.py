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
    STOR_PATH = FTP_Setting[5].split(":", 1)
    FTP_PATH = FTP_Setting[6].split(":",1)

    if FTP_USERNAME[0] == "USER" and FTP_PASSWORD[0] == "PASS":
        FTP_USER = FTP_USERNAME[1].strip()
        FTP_PASS = FTP_PASSWORD[1].strip()
        FTP_CPY = FTP_COPY[1].strip().upper()
        FTP_DLT = FTP_DELETE[1].strip().upper()
        PATH_PROG = CURRENT_PATH + "\\"
        PATH_STOR = STOR_PATH[1].strip()
        PATH_FTP = FTP_PATH[1].strip()

    else:
        print("PLEASE CHECK ftp_setting.ini")
        sleep(10)
        sys.exit()

    ##STARTING to real list of IP registered
    file = open("listServerIndex.ini","r")
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


async def run_task(list_server_index):
    ## Record error print data 
    def log_record(error_msg):
        file = open("datalog.log", "a")
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print("[ERROR RECORDED]")
        file.write(date_time + " " + error_msg + "\n")
        file.close()

    ###START MOVING COPIED FILE ,TO SERVER/LOCAL COMPUTER
    def copyingdata(msg , filelist, transferPathTemp, machineName):
        print("[COPY] DATA TO SERVER......")
        # CHECK IF FILE APPEAR OR NOT
        checkDir = os.path.isdir(PATH_STOR + machineName + "/")
        if checkDir == False:
            os.mkdir(checkDir)
            pass    
        else:
            pass

        count = 0
        while count < len(filelist):
            try: 
                shutil.move(transferPathTemp+filelist[count], PATH_STOR + machineName+ "/" + filelist[count])
            except Exception as Error:
                logger.error(Error)
                # Error = f"[Error] try create folder {machineName}"
                # log_record(Error)
                # newPath = os.path.join(PATH_STOR, f"{machineName}")
                # os.makedirs(newPath)
                # Error = f"[Error] making folder {machineName} success"
                log_record(Error) 
                # shutil.move(transferPathTemp+filelist[count], PATH_STOR + machineName+ "/" + filelist[count]) 
            count+=1
        
        if msg != False:
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            print("Freezing for 30s")
            client.close()
        else:
            pass

    ## DO FTP Operation which is Transferr data from PANEL to SERVER or LOCAL Computer
    def ftpOperation(msg, list_SERVER, machineName, transferHostname, status, datareceived):
        
        print("[STATUS]:" + status)
        if status == "230 Login successful.":
            print('[LOGIN SUCCESS]')
            state = ftp.cwd(PATH_FTP)
            print(f"[DIRECTORY CHANGE]:{str(state)}")

            dirfilelist = ftp.nlst()
            filelist = []

            for file in dirfilelist:
                filelist.append(file)

            ##IF NEEDED
            print(f"[COPY] from {machineName} :: {transferHostname}")

            
            transferPathTemp = os.path.join(PATH_PROG, f"{machineName}\\")
            # CHECK IF FILE APPEAR OR NOT
            checkdir = os.path.isdir(transferPathTemp)
            if checkdir == False:
                os.makedirs(transferPathTemp)
            else:
                pass
            # LOOP TO TRANSFER EVERY FILE FILE FROM SD CARD VT5 KEYENCE TOUCH PANEL TO LOCAL COMPUTER
            count = 0
            while count < len(filelist):
                file = open(transferPathTemp + filelist[count],"wb" )
                if FTP_COPY == "YES" or FTP_DLT == "YES":
                    # RETRIEVE DATA FROM FTP SERVER
                    ftpcommand = ftp.retrbinary(f"RETR {filelist[count]}", file.write)
                    print(filelist[count] + " ->> " + ftpcommand)
                    # DELETE FILE IN SD CARD KEYENCE VT5 IF NEEDED
                    ftpResponse = ftp.delete(filelist[count])
                    print(filelist[count] + " ->> " + ftpResponse)

                elif FTP_CPY == "YES" and FTP_DLT == "NO":
                    # RETRIEVE DATA FROM FTP SERVER
                    ftpcommand = ftp.retrbinary(f"RETR {filelist[count]}", file.write)
                    print(filelist[count] + " ->> " + ftpcommand)

                else:
                    error_msg = f"[ERROR] FTP don't copy and delete anything from this {machineName}, {transferHostname}"
                    print(error_msg)
                    log_record(error_msg)
                    error_msg = f"[ERROR] FTP COPY :{FTP_CPY} FTP DELETE :{FTP_DLT}"
                    log_record(error_msg)
                count+=1
            file.close()
            ftp.close()

            copyingdata(msg , filelist, transferPathTemp , machineName)
            client.close()        
        else:
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            client.close()

    ## SEND COMMAND TO SERVER KV-8000
    def send(msg, list_SERVER, machineName, hostName, transferHostname):
        message = msg.encode(FORMAT)
        client.send(message)
        ReceivedData = client.recv(2048).decode(FORMAT)

        if ReceivedData == "0000" or "0001":
            datareceived = int(ReceivedData)
            print(f"[RESPONSE] from {hostName} : {datareceived}")
            
            if datareceived == 0:
                print("DO NOT COPY DATA ==> MOVE TO OTHERS")
                client.close()

            elif datareceived == 1:
                try:
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
        print(f"[START]:{str(list_server_index)}")
        os.system(clear)

        ActiveAddress = []
        ActiveAddress = LIST_SERVER[list_server_index].split("|")
        machineName = ActiveAddress[0]
        hostName = ActiveAddress[1]
        transferHostname = ActiveAddress[2]
        ADDR = (hostName, PORT)

        try:
            ServerCategory = []
            ServerCategory = LIST_SERVER[list_server_index].split("|")
            print(f"[CONNECTING] to {ServerCategory[0][:6]} \n[KEYENCE PLC]:{ServerCategory[1]} \n[PANEL]:{ServerCategory[2]}")
            print(f"[ROUND]:{str(list_server_index)}")

            global client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR)
            print(f"[CONNECTED] to {hostName} port {PORT} -->> \|^_^|/ ")
            COMMAND = "RD DM508.H"
            send(COMMAND + "\r", list_server_index, machineName, hostName, transferHostname)

        except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError, OSError) as Error:
            error_msg = f"[FAILED to CONNECT] MACHINE:{machineName.strip()[:6]} SERVER:{hostName} PORT:{PORT} -->> (-_-!)"
            logger.error(Error)
            print(error_msg)
            log_record(error_msg)

    start_time = time.time()  
    start(list_server_index)
    end_time = time.time()
    print(f"[EXECUTE]TIME:{str(round(end_time - start_time,3))}s\n")
    await asyncio.sleep(43)
    print(f"DONE {str(list_server_index)}")

async def main():
    threads = []
    count = 1
    START_time = time.time()
    while count <= len(LIST_SERVER)-1:
        t = run_task(count)
        threads.append(t)
        count+=1
    await asyncio.gather(*threads)
    print(f"[THREADS]:{str(len(threads))}")
    END_time = time.time()
    sleep(1)
    print(f"[ALL EXECUTE]TIME:{str(round(END_time - START_time,3))}s\n")


def start_all():
    asyncio.run(main())

start_all()

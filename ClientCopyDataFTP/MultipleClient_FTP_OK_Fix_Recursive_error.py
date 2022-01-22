import socket
import sys
import os
from time import sleep
from ftplib import FTP
import shutil
import logging
from datetime import datetime

os.system('cls')

file = open("datalog.log", "a")
file.close()
logging.basicConfig(filename='datalog.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s\n\n')
logger=logging.getLogger(__name__)

HEADER = 1024
##Keyence port number need to check with KV Studio at Unit Editor --> check socket function need to be used --> Check Port No. (host link) --> 8501
PORT = 8501 
FORMAT = 'utf-8'
LIST_SERVER = []
FTP_USERNAME = []
FTP_PASSWORD = []
PROGRAM_PATH = []
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
PROGRAM_PATH = FTP_Setting[2].split(":", 1)
STOR_PATH = FTP_Setting[3].split(":", 1)

if FTP_USERNAME[0] == "USER" and FTP_PASSWORD[0] == "PASS":
    FTP_USER = FTP_USERNAME[1].strip()
    FTP_PASS = FTP_PASSWORD[1].strip()
    PATH_PROG = PROGRAM_PATH[1].strip()
    PATH_STOR = STOR_PATH[1].strip()

else:
    print("PLEASE CHECK ftp_setting.ini")
    sleep(10)
    sys.exit()

##STARTING to real list of IP registered
file = open("server_and_ftp_list_ip.ini","r")
#Reading IP and Put into ARRAY 
count = 0 
for line in file:
    count+= 1
    list_of_item = line.strip()
    LIST_SERVER.append(list_of_item)
    print(f"lines {count}:", line.strip())
file.close()

def log_record(error_msg):
    file = open("datalog.log", "a")
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Data recorded")
    file.write(date_time + " " + error_msg + "\n")
    file.close()

## DO FTP Operation which is Transferr data from PANEL to SERVER or LOCAL Computer
def ftpOperation(msg, list_SERVER, machineName, transferHostname, status, datareceived):
    print("status :" + status)
    if status == "230 Login successful.":
        print('Login Success')
        print(ftp.retrlines('LIST'))
        print(ftp.cwd("/VTWS/ID1/00000_00999/"))
        print(ftp.retrlines('LIST'))

        dirfilelist = ftp.nlst()
        filelist = []

        for file in dirfilelist:
            filelist.append(file)

        print('COPYING DATA .........')
        
        #IF NEEDED
        #print(filelist)

        ##IF NEEDED
        print(f"Copy data from {machineName} :: {transferHostname}")
        
        
        ##START TRANSFER FILE FROM SD CARD VT5 KEYENCE TOUCH PANEL TO LOCAL COMPUTER
        count = 0
        while count < len(filelist):
            with open(filelist[count],"wb") as file:
                ftpcommand = ftp.retrbinary(f"RETR {filelist[count]}",file.write)
                print(filelist[count] + " ->> " + ftpcommand)

                ##DELETE FILE IN SD CARD KEYENCE VT5 IF NEEDED
                # ftpResponse = ftp.delete(filelist[count])
                # print(filelist[count] + " ->> " + ftpResponse)
            count+=1
        ftp.close()

        ###START MOVING COPIED FILE TO SERVER/LOCAL COMPUTER
        count = 0
        while count < len(filelist):
            try:
                shutil.move(PATH_PROG + filelist[count], PATH_STOR + machineName + "/" + filelist[count])
            except FileNotFoundError:
                newPath = os.path.join(PATH_STOR, f"{machineName}")
                os.makedirs(newPath)
                shutil.move(PATH_PROG + filelist[count], PATH_STOR + machineName + "/" + filelist[count])   
            count+=1

        msg = "WR DM508.H 0\r"
        message = msg.encode(FORMAT)
        client.send(message)
        print("Freezing for 10s")
        sleep(10)
        client.close()
        return starto(list_SERVER + 1)

    else:
        msg = "WR DM508.H 0\r"
        message = msg.encode(FORMAT)
        client.send(message)
        client.close()
        return starto(list_SERVER + 1)


## FUNCTION NOT USED
def exit_ka(get):
    if get == "y":
        start()
    else:
        sys.exit()

## START SOCKET CONNECTION BETWEEN CLIENT AND SERVER KEYENCE KV-8000
def start(list_SERVER):
    ActiveAddress = []
    ActiveAddress = LIST_SERVER[list_SERVER].split("|")
    machineName = ActiveAddress[0]
    hostName = ActiveAddress[1]
    transferHostname = ActiveAddress[2]
    ##PRINT IF NEEDED
    # print(LIST_SERVER[list_SERVER])
    ADDR = (hostName, PORT)
    sleep(1)
    try:
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"[CONNECTED] to {hostName} port {PORT} -->> \|^_^|/ ")
        return main(list_SERVER, machineName, hostName, transferHostname)

    except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError, OSError):
        os.system('cls')
        error_msg = f"[FAILED to CONNECT] SERVER:{hostName} PORT:{PORT} -->> (-_-!)"
        print(error_msg)
        log_record(error_msg)
        sleep(2)
        starto(list_SERVER + 1)

#FUNCTION NOT USED
def hextostring(data):
    hex_string = data
    bytes_object = bytes.fromhex(hex_string)
    ascii_string = bytes_object.decode("ASCII")
    return ascii_string

#CREATE UPPER CASE COMMAND
def upperEverything(thingsToUpper):
    totalchar = ""
    for char in thingsToUpper:
        if char.isnumeric() == False:
            temp = char
            char = temp.upper()
            
        elif char.isnumeric() == True:
            pass

        else:
            pass
        totalchar = totalchar + char

    return totalchar

## SEND COMMAND TO SERVER KV-8000
def send(msg, list_SERVER, machineName, hostName, transferHostname):
    # print(f"send msg : {msg} to {hostName}")
    message = msg.encode(FORMAT)
    client.send(message)
    ReceivedData = client.recv(2048).decode(FORMAT)

    if ReceivedData.isdigit() == True:
        datareceived = int(ReceivedData)
        print(f"Response from {hostName} is {datareceived}")
        
        if datareceived == 0:
            print("DO NOT COPY DATA ==> MOVE TO OTHERS\n")
            return starto(list_SERVER + 1)

        elif datareceived == 1:
            try:
                global ftp
                ftp = FTP(transferHostname)
                status = ftp.login(FTP_USER, FTP_PASS)
                return ftpOperation(msg, list_SERVER, machineName, transferHostname, status, datareceived)
            except Exception as error:
                error_msg = f"FTP ERROR PLEASE CHECK USERNAME AND PASSWORD is it true username is {FTP_USER} pass is {FTP_PASS} ??"
                print(error_msg)
                logger.error(error)
                log_record(error_msg)
                sleep(10)
                msg = "WR DM508.H 0\r"
                message = msg.encode(FORMAT)
                client.send(message)
                return starto(list_SERVER + 1)
        else:       
            error_msg = f"Validation Invalid, Keyence Send Response other commad\nWhich is :{ReceivedData}"
            print(error_msg)
            log_record(error_msg)
            print(f"Response : {datareceived}")
            print(type(datareceived))
            msg = "WR DM508.H 0\r"
            message = msg.encode(FORMAT)
            client.send(message)
            return starto(list_SERVER + 1)
    else:
        error_msg = f"[INVALID] Keyence send : {ReceivedData}"
        log_record(error_msg)
        return starto(list_SERVER + 1)
   

##STARING POINT TO SEND COMMAND AND CONVERT INTO UPPERCASE COMMAND
def main(list_SERVER, machineName, hostName, transferhostName):
    getdata = "RD DM508.H"
    # getdata = input("Please input Command : ")
    getdata = upperEverything(getdata)
    
    if getdata == "EXIT":
        sys.exit()
    elif getdata == "PROGRAM MODE":
        send("M\r")
    else:        
        send(getdata + "\r", list_SERVER, machineName, hostName, transferhostName)

##STARTING PROGRAM
def starto(starting_number):
    os.system("cls")
    countdown = starting_number
    server_list_count = len(LIST_SERVER)-1
    if countdown > server_list_count:
        print(f"--------------------")
        print("___ROUND FINISHED___")
        print(f"[START AGAIN] (^_^)")
        print(f"--------------------")
        countdown = 1
        sleep(2)
    os.system("cls")
    ServerCategory = []
    ServerCategory = LIST_SERVER[countdown].split("|")
    print(f"[CONNECTING] to {ServerCategory[0][:6]} \n[KEYENCE PLC]:{ServerCategory[1]} \n[PANEL]:{ServerCategory[2]}")
    print("[ROUND]:" + str(countdown))
    start(countdown)

#START THE PROGRAM    
starto(1)
import socket
import sys
import os
from time import sleep
from ftplib import FTP
import shutil

os.system('cls')

HEADER = 1024
PORT = 8501 ##Keyence port number need to check with KV Studio at Unit Editor --> check socket function need to be used --> Check Port No. (host link) --> 8501
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
LIST_SERVER = []

file = open("listIp.txt","r")

count = 0 
for line in file:
    count+= 1
    list_of_item = line.strip()
    LIST_SERVER.append(list_of_item)
    print(f"lines {count}:", line.strip())
file.close()

print(LIST_SERVER)

def exit_ka(get):
    if get == "y":
        start()
    else:
        sys.exit()

def start(list_SERVER):
    ActiveAddress = []
    ActiveAddress = LIST_SERVER[list_SERVER].split("|")
    machineName = ActiveAddress[0]
    hostName = ActiveAddress[1]
    transferHostname = ActiveAddress[2]
    
    print(LIST_SERVER[list_SERVER])
    ADDR = (hostName, PORT)
    try:
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"[CONNECTED] to {hostName} port {PORT} -->> \|^_^|/ ")
        return main(list_SERVER, machineName, hostName, transferHostname)
    except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError):
        print(f"[NO CONNECTION] SERVER:{hostName} PORT:{PORT} -->> (-_-!)")
        # get = input(f"[NO CONNECTION] SERVER:{SERVER} PORT:{PORT} -->> (-_-!)\nWant to Retry? :")
        sleep(1)
        starto(list_SERVER + 1)

def hextostring(data):
    hex_string = data
    bytes_object = bytes.fromhex(hex_string)
    ascii_string = bytes_object.decode("ASCII")
    return ascii_string

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

def send(msg, list_SERVER, machineName, hostName, transferHostname):
    # print(f"send msg : {msg} to {hostName}")
    message = msg.encode(FORMAT)
    client.send(message)
    ReceivedData = client.recv(2048).decode(FORMAT)
    datareceived = int(ReceivedData)
    print(f"Response from {hostName} is {datareceived}")

    if datareceived == 0:
        print("DO NOT COPY DATA ==> MOVE TO OTHERS\n")
        return starto(list_SERVER + 1)

    elif datareceived == 1:
        print('COPYING DATA .........')
        ftp = FTP(transferHostname)
        ftp.login('VT', 'VT')
        print('Login Success')
        print(ftp.retrlines('LIST'))
        print(ftp.cwd("/VTWS/ID1/00000_00999/"))
        print(ftp.retrlines('LIST'))

        # dirfilelist = ftp.retrlines('LIST')
        dirfilelist = ftp.nlst()
        filelist = []

        for file in dirfilelist:
            filelist.append(file)

        print(filelist)
        print(f"Copy data from {machineName} :: {transferHostname}")
        count = 0
        while count < len(filelist):
            with open(filelist[count],"wb") as file:
                ftpcommand = ftp.retrbinary(f"RETR {filelist[count]}",file.write)
                print(filelist[count] + " ->> " + ftpcommand)
                # ftpResponse = ftp.delete(filelist[count])
                # print(filelist[count] + " ->> " + ftpResponse)
            count+=1

        ftp.close()
        path = "C:/Users/Admin/Desktop/ClientCopyDataFTP/"
        count = 0
        while count < len(filelist):
            try:
                shutil.move(path + filelist[count], path + machineName + "/" +filelist[count])
            except FileNotFoundError:
                newPath = os.path.join(path, f"{machineName}")
                os.makedirs(newPath)
                shutil.move(path + filelist[count], path + machineName + "/" +filelist[count])   
            count+=1

        msg = "WR DM508.H 0\r"
        message = msg.encode(FORMAT)
        client.send(message)
        print("Freezing for 10s")
        sleep(10)

        return starto(list_SERVER + 1)
    
    elif msg == "RDS DM10268.H 68\r":
        print("masuk3")
        data = hextostring(datareceived)
        print(f"Response : {data}")
        print(len(data))
        return main()
    else:
        print("masuk4")
        print(f"Response : {datareceived}")
        print(type(datareceived))
        msg = "WR DM508.H 0\r"
        message = msg.encode(FORMAT)
        client.send(message)
        return starto(list_SERVER + 1)

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



def starto(starting_number):
    countdown = starting_number
    server_list_count = len(LIST_SERVER)-1
    if countdown > server_list_count:
        print(f"[FAILED] (!_-)")
        # sys.exit()
        countdown = 0
    ServerCategory = []
    ServerCategory = LIST_SERVER[countdown].split("|")
    print(f"[CONNECTING] to {ServerCategory[1]}")
    print(countdown)
    start(countdown)

#START THE PROGRAM    
starto(0)
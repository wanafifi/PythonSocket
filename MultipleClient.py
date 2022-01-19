import socket
import sys
from types import TracebackType
import os
from time import sleep

os.system('cls')

HEADER = 1024
PORT = 8501 ##Keyence port number need to check with KV Studio at Unit Editor --> check socket function need to be used --> Check Port No. (host link) --> 8501
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = []
# SERVER = "10.30.34.5"


file = open("listIp.txt","r")

count = 0 
for line in file:
    count+= 1
    list_of_item = line.strip()
    SERVER.append(list_of_item)
    print(f"lines {count}:", line.strip())
file.close()

print(SERVER)

def exit_ka(get):
    if get == "y":
        start()
    else:
        sys.exit()

def start(list_SERVER):
    print(SERVER[list_SERVER])
    ADDR = (SERVER[list_SERVER], PORT)
    try:
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"[CONNECTED] to {SERVER[list_SERVER]} port {PORT} -->> \|^_^|/ ")
        return main(list_SERVER)
    except (ConnectionRefusedError, TimeoutError, ConnectionAbortedError):
        print(f"[NO CONNECTION] SERVER:{SERVER[list_SERVER]} PORT:{PORT} -->> (-_-!)")
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

def send(msg, list_SERVER):
    print(msg)
    message = msg.encode(FORMAT)
    client.send(message)
    ReceivedData = client.recv(2048).decode(FORMAT)
    
    datareceived = int(ReceivedData)
    print(datareceived)

    if datareceived == 0:
        print("masuk1")
        print("Do not Copy the pass to Others")
        return starto(list_SERVER + 1)

    elif datareceived == 1:
        print("masuk2")
        print('Kena Copy')
        #Put Copy Coommad here


        msg = "WR DM508.H 0\r"
        message = msg.encode(FORMAT)
        client.send(message)

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

def main(list_SERVER):
    getdata = "RD DM508.H"
    # getdata = input("Please input Command : ")
    getdata = upperEverything(getdata)
    
    if getdata == "EXIT":
        sys.exit()
    elif getdata == "PROGRAM MODE":
        send("M\r")
    else:        
        send(getdata + "\r", list_SERVER)



starting_number = 0

def starto(starting_number):
    countdown = starting_number
    server_list_count = len(SERVER)-1
    if countdown > server_list_count:
        print(f"[FAILED] (!_-)")
        # sys.exit()
        countdown = 0
    print(f"[CONNECTING] to {SERVER[countdown]}")
    print(countdown)
    start(countdown)
    
starto(starting_number)
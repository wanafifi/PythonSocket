import socket
from types import TracebackType
import sys, time, threading


HEADER = 1024
PORT = 8501 ##Keyence port number need to check with KV Studio at Unit Editor --> check socket function need to be used --> Check Port No. (host link) --> 8501
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "10.30.34.51"
ADDR = (SERVER, PORT)

def exit_ka():
    get = input(f"[NO CONNECTION] SERVER:{SERVER} PORT:{PORT} -->> (-_-!)\nWant to Retry? :")
    if get == "y":
        start()
    else:
        sys.exit()

def start():
    try:
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        # print(client)
        # print(type(client))
        print(f"[CONNECTED] to {SERVER} port {PORT} -->> \|^_^|/ ")
        return main()
    except :
        exit_ka()

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

def send(msg):
    print(msg)
    message = msg.encode(FORMAT)
    client.send(message)
    datareceived = client.recv(2048).decode(FORMAT)
    if msg == "RDS DM10268.H 68\r":
        data = hextostring(datareceived)
        print(f"Response : {data}")
        print(len(data))
        return main()
    else:
        print(f"Response : {datareceived}")
        print(type(datareceived))
        return main()

def main():
    getdata = input("Please input Command : ")
    getdata = upperEverything(getdata)
    
    if getdata == "EXIT":
        sys.exit()
    elif getdata == "PROGRAM MODE":
        send("M\r")
    else:        
        send(getdata + "\r")
        
start()

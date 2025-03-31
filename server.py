
import socket

def createsockets(count,port):
    opensockets = []
    while count != 0:
        s = socket.socket()
        s.bind(('',port))
        s.listen()
        opensockets.append(socket)
        print("Socket created and listening")
        count = count - 1
    return opensockets

createsockets(2,12345)
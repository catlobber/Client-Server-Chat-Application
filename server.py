
import socket
import select

def createwelcomingsocket(port):
        s = socket.socket()
        s.bind(('',port))
        s.listen()
        print("Welcoming Socket created and listening")
        return s


def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(messagesize)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

welcomingsocket = createwelcomingsocket(12345)
socketlist = [welcomingsocket]
clients = {}
messagesize = 4

while True:
 available, sending, errors = select.select(socketlist, clients, [])
 for connected in available:
    if connected == welcomingsocket:
         client_socket, client_address = welcomingsocket.accept()
         user = recieve_message(client_socket)
                  

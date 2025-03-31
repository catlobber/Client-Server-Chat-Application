
import socket
import select

def createwelcomingsocket(port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE,1)
        s.bind(('',port))
        s.listen()
        print("Welcoming Socket created and listening")
        return s

welcomingsocket = createwelcomingsocket(12345)
socketlist = [welcomingsocket]
clients = {}
headersize = 4

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(headersize)
        if not message_header:
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False



while True:
 read, _, exceptions = select.select(socketlist, [], socketlist)
 for connected in read:
    if connected == welcomingsocket:
         client_socket, client_address = welcomingsocket.accept()
         user = recieve_message(client_socket)
         if user is False:
             continue
         socketlist.append(client_socket)
         clients[client_socket] = user
         print(f"Accepted connection from {client_address}, username: {user}")
    else:
        message = recieve_message(connected)

        if message is False or message['data'].decode('utf-8') == '.exit':
            print("Closed connection from: {}".format(clients[connected]['data'].decode('utf-8')))
            socketlist.remove(connected)
            connected.close()
            del clients[connected]
            continue

        user = clients[connected]
        print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
        for client_socket in clients:
            if client_socket != connected:
                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                  

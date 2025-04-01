
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
userlist = {}

def recieve_message(client_socket):
    try:
        message_type = client_socket.recv(headersize)
        if not message_type:
            return False
        message_type_length = int(message_type.decode('utf-8').strip())
        
        message_header = client_socket.recv(headersize)
        if not message_header:
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'typeheader': message_type, 'type': client_socket.recv(message_type_length), 'header': message_header, 'data': client_socket.recv(message_length)}

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
         userlist.update({user['data'].decode('utf-8'): client_socket})
         print(f"Accepted connection from {client_address}, username: {user['data'].decode('utf-8')}")

         #welcomemessage = f"Welcome to #Python. Currently Connected Users: {','.join(userlist.keys())}"
         #welcomemessageheader = f"{len(welcomemessage):<{headersize}}".encode('utf-8')
         #client_socket.send(welcomemessageheader + welcomemessage.encode('utf-8'))
         #Make this send message types too
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
            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                  


import socket
import select

def createwelcomingsocket(port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE,1) #setsockopts makes a persistent connection w/ client and allows reuse of the same server address for every client
        s.bind(('',port)) #binds to the next available ip address and port which is specified
        s.listen() #open up the socket and tell it to listen for incoming connections
        print("Welcoming Socket created and listening.")
        return s

headersize = 4 #set headersize to 4 byte (which allows for messages up to 4gb)

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(headersize) #when a message is recieved, the header should be 4 bytes
        if not message_header: #if no header was recieved/empty then the client has disconnected
            return False
        message_length = int(message_header.decode('utf-8').strip()) #gets the length of the message
        return {'header': message_header, 'data': client_socket.recv(message_length)} #return the message header and the actual message

    except: #if any error occurs return False
        return False

#set instance variables
welcomingsocket = createwelcomingsocket(12345)
socketlist = [welcomingsocket]
clients = {}
userlist = {}
servername = '-!-'
servernameheader = f"{len(servername):<{headersize}}".encode('utf-8')


while True:
 #select.select which allows the handling of several clients simultaneously
 read, _, exceptions = select.select(socketlist, [], socketlist)
 for connected in read: 
    if connected == welcomingsocket: #once a client connects, the welcoming socket will be notified and will run this if statement
         client_socket, client_address = welcomingsocket.accept()
         user = recieve_message(client_socket) #handles the username recieved from client
         if user is False: #if no username then continue
             continue
         socketlist.append(client_socket) #add the client to the list of sockets able to be read/written to 
         clients[client_socket] = user #update the key, value pair to identify client by username
         userlist.update({user['data'].decode('utf-8'): client_socket}) #list of users which are currently connected to the server, used mainly for the userlist sent to users
         print(f"Accepted connection from {client_address}, username: {user['data'].decode('utf-8')}")

         welcomemessage = f"Welcome to #Python."
         welcomemessageheader = f"{len(welcomemessage):<{headersize}}".encode('utf-8')
         client_socket.send(servernameheader + servername.encode('utf-8') + welcomemessageheader + welcomemessage.encode('utf-8'))
         currentusers = f'Currently Connected Users: {', '.join(userlist.keys())}'
         currentuserheader = f"{len(currentusers):<{headersize}}".encode('utf-8')

         for client_socket in clients: #every time a client connects, send the connected users a list of all clients connected
          client_socket.send(servernameheader + servername.encode('utf-8') + currentuserheader + currentusers.encode('utf-8'))
         #here would be if a client talks to another
    else:
        message = recieve_message(connected) #recieve message from client
        user = clients[connected] #get the client's user

        if message is False or message['data'].decode('utf-8') == '.exit': #if .exit is recieved, close the connection, remove them from the socket and user lists.
            print("Closed connection from: {}".format(clients[connected]['data'].decode('utf-8')))
            socketlist.remove(connected)
            del userlist[user["data"].decode("utf-8")]
            connected.close()
            del clients[connected]
            continue

        print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

        for client_socket in clients:
            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                  

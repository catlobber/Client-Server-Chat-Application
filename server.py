import socket
import select
import random
import string
import re

def generate_id() -> str:
    rand_num = ''.join(random.choices(string.digits, k = 2))
    rand_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    return rand_num + rand_letters

def createwelcomingsocket(port):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE,1) # setsockopts makes a persistent connection w/ client and allows reuse of the same server address for every client
        s.bind(('',port)) #binds to the next available ip address and port which is specified
        s.listen() # open up the socket and tell it to listen for incoming connections
        print("Welcoming Socket created and listening.")
        return s

headersize = 4 # set headersize to 4 byte (which allows for messages up to 4gb)

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(headersize) # when a message is recieved, the header should be 4 bytes
        if not message_header: # if no header was recieved/empty then the client has disconnected
            return False
        message_length = int(message_header.decode('utf-8').strip()) # gets the length of the message
        return {'header': message_header, 'data': client_socket.recv(message_length)} # return the message header and the actual message

    except: # if any error occurs return False
        return False

# set instance variables
welcomingsocket = createwelcomingsocket(12345)
socketlist = [welcomingsocket]
clients = {}
userlist = {}
servername = '-!-'
servernameheader = f"{len(servername):<{headersize}}".encode('utf-8')


while True:
 # select.select which allows the handling of several clients simultaneously
 read, _, exceptions = select.select(socketlist, [], socketlist)
 for pinged in read: 
    if pinged == welcomingsocket: # once a client connects, the welcoming socket will be pinged and will run this if statement
         client_socket, client_address = welcomingsocket.accept()
         generated_username = generate_id()
         username_header = f"{len(generated_username):<{headersize}}".encode('utf-8')

         socketlist.append(client_socket) # add the client to the list of sockets able to be read/written to 
         clients[client_socket] = {'header': username_header, 'data':generated_username.encode('utf-8')} # update the key, value pair to identify client by username
         userlist[generated_username] = client_socket # list of users which are currently connected to the server, used mainly for the userlist sent to users
         print(f"Accepted connection from {client_address}, assigned username: {generated_username}")
         
         welcomemessage = f"Welcome to #General. Your Assigned username is: {generated_username}. Your messages are broadcast to all connected users. If you would like to message someone directly, please use /whisper @username."
         welcomemessageheader = f"{len(welcomemessage):<{headersize}}".encode('utf-8')
         client_socket.send(servernameheader + servername.encode('utf-8') + welcomemessageheader + welcomemessage.encode('utf-8'))
         currentusers = f'Currently Connected Users: {', '.join(userlist.keys())}'
         currentuserheader = f"{len(currentusers):<{headersize}}".encode('utf-8')

         for client_socket in clients: #every time a client connects, send the connected users a list of all clients connected
          client_socket.send(servernameheader + servername.encode('utf-8') + currentuserheader + currentusers.encode('utf-8'))
    else:
        message = recieve_message(pinged) # recieve message from client
        user = clients[pinged] # get the client's user

        if message is False or message['data'].decode('utf-8') == '.exit': #if .exit is recieved, close the connection, remove them from the socket and user lists.
            print("Closed connection from: {}".format(clients[pinged]['data'].decode('utf-8')))
            socketlist.remove(pinged)
            del userlist[user["data"].decode("utf-8")]
            pinged.close()
            del clients[pinged]
            continue

        print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

        #Message handling
        usermessage = message['data'].decode('utf-8')
        found = 0
        #If message starts with whisper then handle appropriately
        if re.search("^/whisper", usermessage):
            #split the user's message into individual parts (i.e '/whisper', '@id', 'Message')
            usermessageparts = re.split(r"\s",usermessage)
            for client_socket in clients:
                #go through clients, checking if they match the /whisper @id
                if f"/whisper @{clients[client_socket]['data'].decode("utf-8")}" == f'{usermessageparts[0]} {usermessageparts[1]}':
                    #if they do then make sure the user's message has (WHISPER) attached and send it to appropriate user. Also update found variable.
                    found = 1
                    usermessage = ("(WHISPER)" + ((re.split(r"^/whisper @\d{2}[a-zA-Z]{3}", usermessage))[1]))
                    usermessageheader =  f"{len(usermessage):<{headersize}}".encode('utf-8')
                    client_socket.send(user['header'] + user['data'] + usermessageheader + usermessage.encode('utf-8'))
                    break
            #else tell the sender that there was a problem in sending the message
            if found == 0:
                noclientfoundmsg = "There was a problem in finding the user. Make sure that the user exists."
                noclientfoundmsgheader = f"{len(noclientfoundmsg):<{headersize}}".encode('utf-8')
                userlist[user["data"].decode("utf-8")].send(servernameheader + servername.encode('utf-8') + noclientfoundmsgheader + noclientfoundmsg.encode('utf-8'))
        #If message doesn't start with any command then just send it to everyone
        else:
            for client_socket in clients:
             client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                  

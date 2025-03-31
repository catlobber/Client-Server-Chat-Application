import socket
import threading
import time

HOST = ''  # Server address
PORT = 12345
headersize = 4
running = True #Set variable so we can stop recieve message across all threads


def currenttime():
    epoch = time.time()
    local = time.localtime(epoch)
    hour = local.tm_hour
    minute = local.tm_min
    second = local.tm_sec
    return [hour,minute,second]


# Receive messages from the server
# Messages come with different types (i.e SERVER/MSG)
def receive_message(client_socket):
    global running
    while running:
        try:
            username_header = client_socket.recv(headersize)
            if not len(username_header):
                print('Connection closed by server.')
                running = False
                break
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            
            
            message_header = client_socket.recv(headersize)
            if not message_header:
                break
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            t = currenttime()
            print(f"{t[0]:02}:{t[1]:02}:{t[2]:02} <@{username}> {message}")
        except Exception as e:
            print(f'Error handling message from server: {e}')
            break

def client() -> None:
    global running
    try:
        # instantiate (create) socket and start server connection 
        socket_instance = socket.socket()
        socket_instance.connect((HOST, PORT))
        threading.Thread(target=receive_message, args=[socket_instance]).start()

        print(f'Client has connected.')
        
        message = input("Please enter your username: ")
        message_header = f"{len(message):<{headersize}}".encode('utf-8')
        socket_instance.send(message_header + message.encode())
        
        # read the user until the .exit prompt
        while True:
            message = input()

            if message == '.exit':
                message_header = f"{len(message):<{headersize}}".encode('utf-8') #Sends the .exit message with correct format
                socket_instance.send(message_header + message.encode())
                break
            
            # parse message to utf-8 and send message header first because server expects the size to be sent first
            message_header = f"{len(message):<{headersize}}".encode('utf-8')
            socket_instance.send(message_header + message.encode())

        running = False #Tell all threads to stop running recieve message loop
        socket_instance.close()
        print("Client has been disconnected.")
        
    
    except Exception as e:
        print(f'Error connecting to server: {e}')
        socket_instance.close()

if __name__ == "__main__":
    client()  


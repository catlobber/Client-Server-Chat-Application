import socket
import threading
import time
import sys
import re

HOST = ''  # Server address
PORT = 12345
headersize = 4
running = True #Set variable so we can stop recieve message across all threads
message_history = [] # store received messages


def currenttime():
    epoch = time.time()
    local = time.localtime(epoch)
    hour = local.tm_hour
    minute = local.tm_min
    second = local.tm_sec
    return [hour,minute,second]


# Receive messages from the server
# Messages come with different types depending on username (i.e. server messages have the name '-!-' and user messages just are a username)
def receive_message(client_socket):
    global running, message_history
    while running:
        try:
            client_socket.setblocking(True) #makes it so we don't have to wait for the message to be recieved 
            username_header = client_socket.recv(headersize)
            if not username_header: #if there is nothing in the header, then the server has disconnected and we close our connection with the server.
                print('Connection closed by server.')
                running = False
                break
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            
            
            message_header = client_socket.recv(headersize)
            if not message_header: #if there is no message header, then server disconnected and we close our connection
                running = False
                break
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            if username == '-!-': #if statement differentiates between client and server messages
                t = currenttime()
                formatted_message = (f"{t[0]:02}:{t[1]:02}:{t[2]:02} <{username}> {message}")
            else:
                t = currenttime()
                formatted_message = (f"{t[0]:02}:{t[1]:02}:{t[2]:02} <@{username}> {message}")
            
            print(formatted_message)
            message_history.append(formatted_message) # add message to history
        except BlockingIOError:
            continue
        except Exception as e:
            print(f'Error handling message from server: {e}')
            break

def send_message(socket_instance):
    global running, message_history
    while running:
        
            message = input()

            if message == '.exit':
                message_header = f"{len(message):<{headersize}}".encode('utf-8') #Sends the .exit message with correct format
                socket_instance.send(message_header + message.encode())
                break
            elif message.startswith('/search'):
                search_term = message[8:] # extract search term
                include_whispers = False
                if search_term.startswith("/whisper "):
                    include_whispers = True
                    search_term = search_term[len("/whisper "):].strip() # remove /whipser and any whitespace
                search_results = []
                if include_whispers:
                    search_results = [m for m in message_history if re.search(search_term, m, re.IGNORECASE) and "(WHISPER)" in m]
                else:
                    search_results = [m for m in message_history if re.search(search_term, m, re.IGNORECASE) and "(WHISPER)" not in m]


                if search_results:
                    print("Search Results: ")
                    for result in search_results:
                        print(result)
                else:
                    print("No matching messages found. ")
                continue
            
            # parse message to utf-8 and send message header first because server expects the size to be sent first
            try:
             message_header = f"{len(message):<{headersize}}".encode('utf-8')
             socket_instance.send(message_header + message.encode())
             sys.stdout.write("\033[F")
             sys.stdout.write("\033[K")
            except BrokenPipeError:
                print(f"Server has closed connection unexpectedly.")
                running = False
                socket_instance.close()

    running = False # tell all threads to stop running recieve message loop
    socket_instance.close()
    print("Client has been disconnected.")

def client() -> None:
    global running
    try:
        # instantiate (create) socket and start server connection 
        socket_instance = socket.socket()
        socket_instance.connect((HOST, PORT))
        threading.Thread(target=receive_message, args=[socket_instance]).start()

        print(f'Client has connected.') 
       #INSTEAD PRINT OUT THE USERNAME THE SERVER GIVES YOU
        # read the user until the .exit prompt
        threading.Thread(target=send_message, args=[socket_instance]).start()
    
    except Exception as e:
        print(f'Error connecting to server: {e}')
        socket_instance.close()

if __name__ == "__main__":
    client()  


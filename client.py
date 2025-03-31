import socket
import threading

HOST = ''  # Server address
PORT = 12345
headersize = 4
running = True #Set variable so we can stop recieve message across all threads
# Receive messages from the server
def receive_message(client_socket):
    global running
    while running:
        try:
            msg = client_socket.recv(headersize).decode()
            if msg == '.exit':
                print("Client disconnected successfully")
                break
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
        print("Please input your username.")
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


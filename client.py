import socket
import threading

HOST = '127.0.0.1'  # Server address
PORT = 65432

# Receive messages from the server
def receive_message(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
        except Exception as e:
            print(f'Error handling message from server: {e}')
            break

def client() -> None:

    try:
        # instantiate (create) socket and start server connection 
        socket_instance = socket.socket()
        socket_instance.connect(HOST, PORT)
        threading.Thread(target=receive_message, args=[socket_instance]).start()

        print(f'Client has connected.')

        # read the user until the .exit prompt
        while True:
            message = input()

            if message == '.exit':
                break
            
            # parse message to utf-8
            socket_instance.send(message.encode())

        socket_instance.close()
    
    except Exception as e:
        print(f'Error connecting to server: {e}')
        socket_instance.close()

if __name__ == "__main__":
    client()  


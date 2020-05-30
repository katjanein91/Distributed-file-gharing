"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import os
import multiprocessing

#Receive buffer size
BUFFER_SIZE = 1024

def send_message(server_address, server_port):
    print('This is client 1 process ' + str(os.getpid()))
    try:
        #Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        message = 'file'
        #Send data
        client_socket.sendall(message.encode())
        print('Sent to server: ', message)
        
        while True:
            # Receive response
            print('Waiting for response...')
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            print('Received message from server: ', data.decode())

    finally:
        client_socket.close()
        print('Socket closed')
        
if __name__ == "__main__":
    server_address = '127.0.0.1' 
    server_port = 3000

    for i in range(3):
        p = multiprocessing.Process(target=send_message, args=(server_address, server_port))
        p.start()
        p.join


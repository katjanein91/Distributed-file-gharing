"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import os
import multiprocessing

def send_message(server_address):
    print('This is client ' + str(os.getpid()))
    try:
        #Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        message = 'file'
        #Send data
        client_socket.sendall(message.encode())
        print('Sent to server: ', message)
        
        while True:
            # Receive response
            print('Waiting for response...')
            data = client_socket.recv(buffer_size)
            if not data:
                break
            print('Received message from server: ', data.decode())

    finally:
        client_socket.close()
        print('Socket closed')
        
if __name__ == "__main__":
    server_address = ('127.0.0.1', 3000)
    #Receive buffer size
    buffer_size = 1024

    for i in range(3):
        p = multiprocessing.Process(target=send_message, args=(server_address))
        p.start()
        p.join


"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import os
import time
import sys
import multiprocessing

NUMBER_CLIENTS = 3
#Define a timeout for connections
TIMEOUT = 5000
#Receive buffer size
BUFFER_SIZE = 1024

def send_message(client_id, server_address, server_port):
    client_id += 1
    print('This is client ' + str(client_id) + ' with process id ' + str(os.getpid()))
    try:
        #Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)

    except socket.error:
        print("Error creating socket")
        sys.exit(1)

    try:
        client_socket.connect((server_address, server_port))

    except socket.error:
        print("Error connecting to server socket")
        sys.exit(1)

    try:
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

    except socket.error:
        print("Error sending data")
        sys.exit(1)

    if client_id == 3:
        client_socket.close()
        print('Socket closed')
        
if __name__ == "__main__":
    server_address = '127.0.0.1' 
    server_port = 3000
    p = None

    for i in range(NUMBER_CLIENTS):
        client_id = i 
        p = multiprocessing.Process(target=send_message, args=(client_id, server_address, server_port))
        p.start()
        p.join
    time.sleep(2)
    print("finished")
    p.terminate()
    


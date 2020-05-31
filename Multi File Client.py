"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import os
import time
import multiprocessing
from Checksum import Checksum
from pathlib import Path

SERVER_IP = "127.0.0.1"
NUMBER_CLIENTS = 3
#Define a timeout for connections
TIMEOUT = 5000
#Receive buffer size
BUFFER_SIZE = 1024
FILENAME = Path("C:/DistributedSystem/test_received.txt")
CS = Checksum(FILENAME)

def send_message(client_id, server_address, server_port):
    client_id += 1
    print('This is client ' + str(client_id) + ' with process id ' + str(os.getpid()))
    try:
        #Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)

    except socket.error:
        print("Error creating socket")

    try:
        client_socket.connect((server_address, server_port))

    except socket.error:
        print("Couldnt connect to the server: %s\n terminating program")
        
    except socket.gaierror:
        print ("Address-related error connecting to server")

    try:
        message = 'file'
        #Send data
        client_socket.sendall(message.encode())
        print('Sent to server: ', message)
    
    except socket.error:
        print("Error sending file request")

    try: 
        while True:
            # Receive response
            print('Waiting for response...')

            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                print('Received message from server: ', data.decode())                
                if data.decode() == 'This is a test':
                    f = open(FILENAME, "w")
                    f.write(data.decode())
                    f.close()
                if "checksum" in data.decode():
                    received_checksum = data.decode().split("=")[1]
                    checksum = CS.generate_digest()
                    if received_checksum == checksum:
                        print("file transmitted without errors")
                    else:
                        print("file corrupted while transmitting!!")

            except socket.error:
                print("Error receiving data")

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        client_socket.close()

    if client_id == 3:
        client_socket.close()
        print('Socket closed')
        
if __name__ == "__main__":
    server_address = SERVER_IP
    server_port = 3000
    p = None

    for i in range(NUMBER_CLIENTS):
        client_id = i 
        p = multiprocessing.Process(target=send_message, args=(client_id, server_address, server_port))
        p.start()
        p.join
    time.sleep(TIMEOUT)
    print("finished")
    p.terminate()
    


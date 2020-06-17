"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import struct
import sys
import os
import time
import multiprocessing
from Checksum import Checksum
from pathlib import Path

#IP Multicast group
MULTICAST_GROUP="224.0.0.0"
MULTICAST_SERVER_ADDR = ("", 10000)
NUMBER_CLIENTS = 3
#Define a timeout for connections
TIMEOUT = 5000
#Receive buffer size
BUFFER_SIZE = 1024
#Use path of FritzBox NAS space 
FILENAME = Path("Y:/Gastbereich/test.txt")
CS = Checksum(FILENAME)

def create_tcp_socket():
    try: 
        #Create a TCP socket
        print('Create TCP socket')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)
        return client_socket
    except socket.error:
        print("Error creating tcp socket")

def create_udp_receive_socket():
    try:
        multicast_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        multicast_receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
        multicast_receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        #allow reuse of socket (to allow another instance of python running this
        #script binding to the same ip/port)
        multicast_receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #Bind to the server address
        multicast_receive_socket.bind(MULTICAST_SERVER_ADDR)
        host = socket.gethostbyname(socket.gethostname())
        multicast_receive_socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        multicast_receive_socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                        socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton(host))
        return multicast_receive_socket
    except socket.error:
        print("Error creating udp socket")

def send_message(client_id, server_address, server_port):
    client_id += 1
    print('This is client ' + str(client_id) + ' with process id ' + str(os.getpid()))

    client_socket = create_tcp_socket()
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

                #Check received checksum             
                if "checksum" in data.decode():
                    received_checksum = data.decode().split("=")[1]
                    checksum = CS.generate_digest()
                    if received_checksum == checksum:
                        print("file transmitted without errors")
                    else:
                        print("file corrupted while transmitting!!")

                #Write txt content to file
                else:
                    f = open(FILENAME, "w")
                    f.write(data.decode())
                    f.close()
                        
            except socket.timeout:
                print("Timeout for receiving data")
            except socket.error:
                print("Error receiving data")

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        client_socket.close()

    #Operations are finished, Socket can be closed
    if client_id == 3:
        client_socket.close()
        print('Socket closed')
        
if __name__ == "__main__":
    server_address = ""
    server_port = 3000
    p = None

    multicast_socket = create_udp_receive_socket()

    #Wait for Leader message on multicast channel
    while True:
        if multicast_socket != None:
            print('Waiting for message on multicast channel...')
            data, address = multicast_socket.recvfrom(1024)
            print('received %s from %s' % (data, address))
            multicast_socket.sendto(b'ack', address)
            if b"LEADER" in data:
                server_address = address[0]
                break
        
    try:
        #Start 1 process of each client
        for i in range(NUMBER_CLIENTS):
            client_id = i 
            p = multiprocessing.Process(target=send_message, args=(client_id, server_address, server_port))
            p.start()
            p.join
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        p.terminate()
        sys.exit(1)

"""     time.sleep(3)
    print("finished")
    p.terminate() """
    


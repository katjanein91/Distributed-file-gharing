"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import multiprocessing
import socket
import struct
import tqdm
import os
import sys
from Checksum import Checksum
from pathlib import Path

#Transfer socket
IP=socket.gethostbyname(socket.gethostname())
TCP_PORT = 3000
#IP Multicast group with UDP socket port
MULTICAST_GROUP=("224.0.0.0", 10000)
FILENAME = Path("C:/DistributedSystem/test.txt")
CS = Checksum(FILENAME)
# get the file size
FILESIZE = os.path.getsize(FILENAME)
#Receive buffer size
BUFFER_SIZE = 1024

class Server(multiprocessing.Process):
    def __init__(self, connection, received_data, client_address):
        super(Server, self).__init__()
        self.connection = connection
        self.received_data = received_data
        self.msg = self.received_data.decode()
        self.client_address = client_address
        self.server_id = 1

    def run(self):
        print('This is server ' + str(self.server_id) + ' with process id ' + str(os.getpid()))
        if self.received_data and self.msg=='file':
            #Transmit file over socket
            send_file(self.connection, self.client_address)

def send_file(connection, client_address):
    checksum = CS.generate_digest()
    
    print("sending file", f"{FILENAME}".encode(), "with filesize", FILESIZE, "kb", "to client", client_address)
    print("\n")
    progress = tqdm.tqdm(range(FILESIZE), f"Sending {FILENAME}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(FILENAME, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            
            try:
                # we use sendall to assure transimission in 
                # busy networks
                connection.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
                
            except socket.error:
                print("Error sending file")

        try:
            connection.send(b"checksum=" + str.encode(checksum))
            
        except socket.error:
            print("Error sending checksum")

def read_from_socket(connection, client_address):
    try:
        data = connection.recv(BUFFER_SIZE)
        msg = data.decode()
        print('Received message from client: ', client_address)
        print('Message: ', msg)
        p = Server(connection, data, client_address)
        p.start()
        p.join()
            
    except socket.error:
        print("Error receiving data")

def create_tcp_socket():
    try: 
        #Create a TCP socket
        print('Create TCP socket')
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Accept connections from any host
        listener_socket.bind(("", TCP_PORT))
        listener_socket.listen()
        return listener_socket
    except socket.error:
        print("Error creating tcp socket")

def create_udp_socket():
    try: 
        #Create a UDP socket
        print('Create UDP socket')
        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        multicast_socket.settimeout(2.0)
        #Set the time-to-live for messages to 1 so they do not go past the
        #local network segment.
        ttl = struct.pack('b', 1)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        return multicast_socket
    except socket.error:
        print("Error creating udp socket")

if __name__ == "__main__":
    #Create multicast socket 
    multicast_socket = create_udp_socket()
    try:
        # Look for responses from all recipients
        while True:
            print('\nWaiting to receive message...\n')
            try:
                data, server = multicast_socket.recvfrom(16)

                #Send data to the multicast group
                multicast_message = b'Hello world, I am server with IP' + bytes(IP)
                print("Send message to multicast group: ", multicast_message)
                sent = multicast_socket.sendto(multicast_message, MULTICAST_GROUP)
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print('received "%s" from %s' % (data, server))
    
    finally:
        print('closing udp socket')
        multicast_socket.close()

    #Create transfer socket 
    listener_socket = create_tcp_socket()
    
    print('Server up and running at {}:{}'.format(IP, TCP_PORT))

    try:
        while True:
            print('\nWaiting to receive message...\n')
            connection, client_address = listener_socket.accept()
            read_from_socket(connection, client_address)
            
    except socket.error:
        print("Connect from client failed")

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        listener_socket.close()
        sys.exit(1)

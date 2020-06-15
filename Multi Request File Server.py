"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import multiprocessing
import socket
import struct
import time
import os
import sys
from Checksum import Checksum
from MulticastGroup import MulticastGroup
from pathlib import Path
import threading

#Pass Server ID string from command line argument
SERVER_ID = "1"
if((len(sys.argv) - 1) >= 1):
    SERVER_ID = sys.argv[1]  
#Transfer socket
IP=socket.gethostbyname(socket.gethostname())
TCP_PORT = 3000
#IP Multicast group with UDP socket port
MULTICAST_GROUP=("224.0.0.0", 10000)
#Use path of FritzBox NAS space 
FILENAME = Path("Y:/Gastbereich/test.txt")
CS = Checksum(FILENAME)
MG = MulticastGroup()
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

    def run(self):
        print('This is server ' + SERVER_ID + ' with process id ' + str(os.getpid()))
        if self.received_data and self.msg=='file':
            #Transmit file over socket
            send_file(self.connection, self.client_address)

#Thread 
class Multicast(object):
        def __init__(self, *args):
                """ Constructor
                :type interval: int
                :param interval: Check interval, in seconds
                """
                self.args = args
                thread = threading.Thread(target=self.run, args=())
                thread.daemon = True                            # Daemonize thread
                thread.start()                                  # Start the execution

        def run(self):
            try:
                while True:
                    #Send data to the multicast group
                    multicast_message = b'Server ' + bytes(SERVER_ID, 'utf-8')
                    print("Send message to multicast group: ", multicast_message)
                    sent = multicast_socket.sendto(multicast_message, MULTICAST_GROUP)
                    time.sleep(1)
                    #Update the group view
                    group_view = MG.update_group()
                    print(group_view)
            except KeyboardInterrupt:
                print("caught keyboard interrupt, exiting")


def send_file(connection, client_address):
    checksum = CS.generate_digest()
    
    print("sending file", f"{FILENAME}".encode(), "with filesize", FILESIZE, "kb", "to client", client_address)
    print("\n")
    with open(FILENAME, "rb") as f:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        
        try:
            # we use sendall to assure transimission in 
            # busy networks
            connection.sendall(bytes_read)
                
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
        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket.settimeout(20.0)
        #Set the time-to-live for messages to 1 so they do not go past the
        #local network segment.
        ttl = struct.pack('b', 1)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        return multicast_socket
    except socket.error:
        print("Error creating udp socket")

if __name__ == "__main__":
    #Create transfer socket 
    listener_socket = create_tcp_socket()

    print('Server up and running at {}:{}'.format(IP, TCP_PORT))

    multicast_socket = create_udp_socket()
    Multicast()
    
    try:
        while True:
            print('\nWaiting to receive message on tcp socket...\n')
            connection, client_address = listener_socket.accept()
            read_from_socket(connection, client_address)
            
    except socket.error:
        print("Connect from client failed")

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        listener_socket.close()
        sys.exit(1)

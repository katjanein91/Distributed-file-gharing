"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import multiprocessing
import socket
import tqdm
import os
import sys
from Checksum import Checksum
from pathlib import Path

IP = "127.0.0.1"
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
            #Check server is running before transmitting
            host_check()
            #Transmit file over socket
            send_file(self.connection, self.client_address)

def host_check():
    HOST_UP = True if os.system("ping -n 1 " + IP) is 0 else False
    print(IP, " is up = ", HOST_UP)

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

if __name__ == "__main__":
    host, port = IP, 3000
    try: 
        #Create a TCP socket
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener_socket.bind((host, port))
        listener_socket.listen()
    
    except socket.error:
        print("Error creating socket")

    print('Server up and running at {}:{}'.format(host, port))

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

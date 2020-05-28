"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import tqdm
import os
import sys
from Checksum import Checksum

def send_file():
    checksum = cs.generate_digest()
    
    print("sending file", f"{filename}".encode(), "with filesize", filesize, "kb", "to client", client_address)
    print("\n")
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(buffer_size)
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
                sys.exit(1)
        try:
            connection.send(b"checksum=" + str.encode(checksum))
            
        except socket.error:
            print("Error sending checksum")
            sys.exit(1)


def read_from_socket(connection, client_address):
    try:
        data = connection.recv(buffer_size)
        msg = data.decode()
        print('Received message from client: ', client_address)
        print('Message: ', msg)
            
        if data and msg=='file':
            send_file()
            
    except socket.error:
        print("Error receiving data")
        sys.exit(1)

if __name__ == "__main__":
    
    filename = r"C:\Users\Tobi\Desktop\test.txt"
    cs = Checksum(filename)
    # get the file size
    filesize = os.path.getsize(filename)
    
    host, port = "127.0.0.1", 3000
    #Receive buffer size
    buffer_size = 1024
    #Define a timeout for connections
    timeout = 5000 
    try: 
        #Create a TCP socket
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #listener_socket.settimeout(timeout)
        listener_socket.bind((host, port))
        listener_socket.listen()
    
    except socket.error:
        print("Error creating socket")
        sys.exit(1)

    print('Server up and running at {}:{}'.format(host, port))

    try:
        while True:
            print('\nWaiting to receive message...\n')
            connection, client_address = listener_socket.accept()
            read_from_socket(connection, client_address)
            
    except socket.error:
        print("Connect from client failed: %s\n terminating program")
        sys.exit(1)

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        listener_socket.close()

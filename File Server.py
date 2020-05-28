"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket
import tqdm
import os
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
            # we use sendall to assure transimission in 
            # busy networks
            connection.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
        
        connection.send(b"File sent, checksum=" + str.encode(checksum))


def read_from_socket(connection, client_address):
    data = connection.recv(buffer_size)
    msg = data.decode()
    print('Received message from client: ', client_address)
    print('Message: ', msg)
        
    if data and msg=='file':
        send_file()

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
    #Create a TCP socket
    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #listener_socket.settimeout(timeout)
    listener_socket.bind((host, port))
    listener_socket.listen()
    print('Server up and running at {}:{}'.format(host, port))

    try:
        while True:
            print('\nWaiting to receive message...\n')
            connection, client_address = listener_socket.accept()
            read_from_socket(connection, client_address)

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
        print("Closing socket")
        listener_socket.close()

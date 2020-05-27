"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket

def read_from_socket(connection, client_address):
    data = connection.recv(buffer_size)
    print('Received message from client: ', client_address)
    print('Message: ', data.decode())

    if data:
        print("Send acknowledgement to", client_address)
        connection.send(b"Data received")

if __name__ == "__main__":
    
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

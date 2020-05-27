"""
@authors: Group 10
Tobias Meinhardt
Katja Haas
Tolga Camlice
"""

import socket

if __name__ == "__main__":
    
    #Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 3000)
    #Receive buffer size
    buffer_size = 1024

    message = 'Hello world!'

    try:
        client_socket.connect(server_address)
        #Send data
        client_socket.sendall(message.encode())
        print('Sent to server: ', message)

        # Receive response
        print('Waiting for response...')
        data = client_socket.recv(buffer_size)
        print('Received message from server: ', data.decode())

    finally:
        client_socket.close()
        print('Socket closed')
